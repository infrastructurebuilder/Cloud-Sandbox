#!/usr/bin/env bash
# Apply the roles that need no kernel module, no EFS and no AWS to a container,
# the way a head node applies them to itself at first boot, and then apply them
# again to prove that a second run changes nothing.
#
#   tests/container/converge.sh            run, and remove the container
#   KEEP=1 tests/container/converge.sh     leave the container for a look
#
# Not exercised here: efa_driver, fsx_lustre_client, spack_environment,
# hpc_tuning and node-image.yml. See docs/LIVE-PROOF.md.

set -euo pipefail

unit=$(cd "$(dirname "$0")/../.." && pwd)
image=sandbox-provisioning-test:alma10
container=sandbox-provisioning-test-$$
logs=$(mktemp -d)
roles=${ROLES:-sandbox_paths,user_shell,base_system,prefect_server,mpi_ssh,python_user_env,spack,intel_oneapi}

cleanup() {
    if [ "${KEEP:-0}" = 1 ]; then
        echo "container kept: $container; logs in $logs"
    else
        docker rm --force "$container" >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT

# A process started in this container gets a umask of 0000. Files made with it
# are writable by anyone, and Ansible ignores an ansible.cfg in a directory
# like that. Cloud-init runs with 022, so that is what is used here.
in_container() { docker exec "$container" bash -c 'umask 022; exec "$@"' -- "$@"; }

echo "== building the image"
docker build --quiet --tag "$image" "$unit/tests/container" >/dev/null

echo "== starting the container"
docker run --detach --name "$container" --privileged --cgroupns=host \
    --volume /sys/fs/cgroup:/sys/fs/cgroup:rw "$image" >/dev/null
for _ in $(seq 1 60); do
    state=$(in_container systemctl is-system-running 2>/dev/null || true)
    case "$state" in running | degraded) break ;; esac
    sleep 1
done
echo "   systemd is $state"

echo "== what the first-boot template does before the playbook: the shared directories"
in_container bash -c '
    set -e
    mkdir -p /mnt/efs/fs1/save
    chgrp wheel /mnt/efs/fs1/save
    chmod 777 /mnt/efs/fs1/save
    ln -s /mnt/efs/fs1/save /save
    mkdir /mnt/efs/fs1/save/ec2-user
    chown ec2-user:ec2-user /mnt/efs/fs1/save/ec2-user
'

echo "== putting the playbooks in a git repository inside the container"
in_container mkdir -p /srv/provisioning
# ustar: no extended attributes from the host. Extracted as root's own files,
# or git refuses to work in a directory that someone else owns.
tar -C "$unit" --format ustar --exclude=.venv --exclude=.collections --exclude=.pytest_cache \
    --exclude=.ruff_cache --exclude=__pycache__ -cf - . |
    docker exec --interactive "$container" tar -C /srv/provisioning --no-same-owner -xf -
in_container bash -c '
    set -e
    cd /srv/provisioning
    git init --quiet --initial-branch main
    git add --all
    git -c user.name=test -c user.email=test@example.invalid commit --quiet --message "under test"
'

# ansible-pull hands the extra variables to its checkout step too, so the file
# has to exist before the checkout does: it is read from the source repository.
apply() {
    in_container env ANSIBLE_CONFIG=/opt/sandbox-provisioning/ansible.cfg ansible-pull \
        --url /srv/provisioning --checkout main --directory /opt/sandbox-provisioning \
        --inventory inventories/local/hosts.yml \
        --tags "$roles" \
        --extra-vars @/srv/provisioning/tests/container/vars.yml \
        site.yml
}

recap() { grep -E '^localhost +: ok=' "$1" | tail -1; }
count() { recap "$1" | sed -E "s/.* $2=([0-9]+).*/\1/"; }

echo "== first apply (roles: $roles)"
if ! apply >"$logs/first.log" 2>&1; then
    tail -60 "$logs/first.log"
    echo "FAILED: the first apply did not finish; full log in $logs/first.log"
    KEEP=${KEEP:-0}
    exit 1
fi
echo "   $(recap "$logs/first.log")"

echo "== second apply"
if ! apply >"$logs/second.log" 2>&1; then
    tail -60 "$logs/second.log"
    echo "FAILED: the second apply did not finish; full log in $logs/second.log"
    exit 1
fi
echo "   $(recap "$logs/second.log")"
if [ "$(count "$logs/second.log" changed)" != 0 ]; then
    grep -B1 -A6 '^changed:' "$logs/second.log" | head -80
    echo "FAILED: the second apply changed something"
    exit 1
fi

echo "== checking what the roles left behind"
if ! in_container bash -c 'cd /opt/sandbox-provisioning && ansible-playbook tests/container/verify.yml' \
    >"$logs/verify.log" 2>&1; then
    tail -60 "$logs/verify.log"
    echo "FAILED: the result is not what the roles should leave"
    exit 1
fi
grep -E 'OBSERVED|^localhost +: ok=' "$logs/verify.log" | sed -E 's/^ *(msg: )?/   /'

echo "PASSED: applied twice, second run changed nothing, result verified"
