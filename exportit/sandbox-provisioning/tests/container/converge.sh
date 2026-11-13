#!/usr/bin/env bash
# Apply the roles that need no kernel module, no EFS and no AWS to a container,
# the way a head node applies them to itself at first boot, and then apply them
# again to prove that a second run changes nothing.
#
#   tests/container/converge.sh            run, and remove the container
#   KEEP=1 tests/container/converge.sh     leave the container for a look
#   PLAYS="site users" ROLES=sandbox_paths tests/container/converge.sh
#                                          a part: some plays, some roles of site.yml
#
# The plays are site.yml (with the roles below), users.yml (with the users of
# tests/container/users.yml) and jupyterhub.yml, in that order.
#
# Not exercised here: efa_driver, fsx_lustre_client, spack_environment,
# hpc_tuning and node-image.yml. See docs/LIVE-PROOF.md.

set -euo pipefail

unit=$(cd "$(dirname "$0")/../.." && pwd)
image=sandbox-provisioning-test:alma10
container=sandbox-provisioning-test-$$
logs=$(mktemp -d)
roles=${ROLES:-sandbox_paths,user_shell,base_system,prefect_server,mpi_ssh,python_user_env,spack,intel_oneapi}
plays=${PLAYS:-site users jupyterhub}

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

# ansible-pull hands the extra variables to its checkout step too, so the files
# have to exist before the checkout does: they are read from the source repository.
apply_play() {
    local play=$1
    local -a extra=(--extra-vars @/srv/provisioning/tests/container/vars.yml)
    case "$play" in
        site) extra+=(--tags "$roles") ;;
        users) extra+=(--extra-vars @/srv/provisioning/tests/container/users.yml) ;;
    esac
    in_container env ANSIBLE_CONFIG=/opt/sandbox-provisioning/ansible.cfg ansible-pull \
        --url /srv/provisioning --checkout main --directory /opt/sandbox-provisioning \
        --inventory inventories/local/hosts.yml "${extra[@]}" "$play.yml"
}

recap() { grep -E '^localhost +: ok=' "$1" | tail -1; }
count() { recap "$1" | sed -E "s/.* $2=([0-9]+).*/\1/"; }

# Apply every play once; the run is named by $1 (first, second).
apply() {
    local run=$1 play
    for play in $plays; do
        if ! apply_play "$play" >"$logs/$run.$play.log" 2>&1; then
            tail -60 "$logs/$run.$play.log"
            echo "FAILED: the $run apply of $play.yml did not finish; full log in $logs/$run.$play.log"
            return 1
        fi
        echo "   $play.yml: $(recap "$logs/$run.$play.log")"
    done
}

echo "== first apply (plays: $plays; roles of site.yml: $roles)"
apply first || exit 1

echo "== second apply"
apply second || exit 1
for play in $plays; do
    if [ "$(count "$logs/second.$play.log" changed)" != 0 ]; then
        grep -B1 -A6 '^changed:' "$logs/second.$play.log" | head -80
        echo "FAILED: the second apply of $play.yml changed something"
        exit 1
    fi
done

echo "== checking what the roles left behind"
# shellcheck disable=SC2016 # $1 is expanded by the shell in the container
if ! in_container bash -c 'cd /opt/sandbox-provisioning && exec ansible-playbook tests/container/verify.yml --extra-vars "verify_plays=$1"' _ "$plays" \
    >"$logs/verify.log" 2>&1; then
    tail -60 "$logs/verify.log"
    echo "FAILED: the result is not what the roles should leave"
    exit 1
fi
grep -E 'OBSERVED|^localhost +: ok=' "$logs/verify.log" | sed -E 's/^ *(msg: )?/   /'

case " $plays " in
    *" users "*)
        echo "== removing the test user"
        if ! in_container env ANSIBLE_CONFIG=/opt/sandbox-provisioning/ansible.cfg bash -c '
            cd /opt/sandbox-provisioning &&
            ansible-playbook -i inventories/local/hosts.yml users.yml \
                -e "{\"sandbox_users_present\": [], \"sandbox_users_absent\": [\"jdoe\"]}" &&
            ! id jdoe 2>/dev/null && ! getent group jdoe && [ ! -e /home/jdoe ]' >"$logs/remove.log" 2>&1; then
            tail -40 "$logs/remove.log"
            echo "FAILED: the test user was not removed"
            exit 1
        fi
        echo "   jdoe, the group and the home directory are gone"
        ;;
esac

echo "PASSED: applied twice, second run changed nothing, result verified"
