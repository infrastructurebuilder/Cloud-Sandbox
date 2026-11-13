#!/usr/bin/env bash
# The head node's first-boot script, for Terraform's templatefile().
#
# This is init_template.tpl, beside it, with its last step replaced. Where that
# file runs scripts/setup-instance.sh from the clone of the monorepo, this one
# applies the Ansible playbooks, fetched by ansible-pull from their own
# repository, and stops without making an image if they fail.
#
# The other differences: ansible-core is installed along with git, the umask
# is set, and Terraform's project tag is handed on (the script has a TODO for
# that and uses a fixed name). The playbooks' collections are installed before
# site.yml runs, because ansible-pull installs none and site.yml needs one
# (sandbox-provisioning's stage 10).
#
# Terraform has to pass two values more than it does today:
#   provisioning_repo     where the playbooks are, as a git URL
#   provisioning_version  the branch, tag or commit to apply
#
# Not run anywhere yet: it needs a real EFS volume. The ansible-pull command
# is the one that sandbox-provisioning/tests/container/converge.sh runs.
set -x

# Files made with a looser umask would make Ansible ignore its own ansible.cfg.
umask 022

echo `date` > ~/setup.log

BRANCH=${sandbox_version}

RUNUSER="ec2-user"

EFS_VERS='v3.1.3'

# EFS_VERS 3.1.2 added RHEL 10 support"
# EFS v3 adds s3files support - no breaking changes with v2
# EFS v2 supports TSL encryption

sudo mkdir -p /mnt/efs/fs1

sudo dnf -y -q install git ansible-core

## Install EFS utilities
########################

cd /tmp
curl -s https://amazon-efs-utils.aws.com/efs-utils-installer.sh | sh -s -- --install

# Issues building from source on RHEL 10, the above works perfectly
# https://github.com/aws/efs-utils/
# dnf -y install amazon-efs-utils


## Mount the EFS volume
#######################

echo "efs_name: ${efs_name}"

mount -t efs "${efs_name}:/" /mnt/efs/fs1
echo "${efs_name}:/ /mnt/efs/fs1 efs defaults,_netdev 0 0" >> /etc/fstab

cd /mnt/efs/fs1
if [ ! -d save ] ; then
  mkdir save
  chgrp wheel save
  chmod 777 save
  ln -s /mnt/efs/fs1/save /save
fi


## git clone the Cloud-Sandbox repository
#########################################

# Still needed: cloudflow is run from this checkout. Provisioning no longer
# uses it.

cd /mnt/efs/fs1/save
mkdir $RUNUSER
chown $RUNUSER:$RUNUSER $RUNUSER
cd $RUNUSER
sudo -u $RUNUSER git clone https://github.com/ioos/Cloud-Sandbox.git
cd Cloud-Sandbox
sudo -u $RUNUSER git checkout $BRANCH


## Install all of the software and drivers
##########################################

PROVISIONING=/opt/sandbox-provisioning
export ANSIBLE_CONFIG=$PROVISIONING/ansible.cfg

# The checkout first, then its requirements.yml, then the plays: ansible-pull
# updates the same checkout.
if ! { git clone --quiet --branch "${provisioning_version}" "${provisioning_repo}" $PROVISIONING &&
       ( cd $PROVISIONING && ansible-galaxy collection install -r requirements.yml ) ; } >> ~/setup.log 2>&1
then
  echo "Fetching the playbooks or their collections FAILED. No node image was created." >> ~/setup.log
  echo `date` >> ~/setup.log
  exit 1
fi

if ! ansible-pull \
       --url "${provisioning_repo}" --checkout "${provisioning_version}" \
       --directory $PROVISIONING \
       --inventory inventories/local/hosts.yml \
       --extra-vars "sandbox_user=$RUNUSER project_tag=${project}" \
       site.yml >> ~/setup.log 2>&1
then
  echo "Installation FAILED. No node image was created." >> ~/setup.log
  echo `date` >> ~/setup.log
  exit 1
fi


## Create the node image
########################

# ami_name is defined in main.tf user_data
echo "ami name : ${ami_name}"

cd $PROVISIONING
if ! { ansible-galaxy collection install -r requirements.yml &&
       ansible-playbook node-image.yml \
         --extra-vars "sandbox_user=$RUNUSER project_tag=${project} ami_name=${ami_name}" ; } >> ~/setup.log 2>&1
then
  echo "The software is installed but creating the node image FAILED." >> ~/setup.log
  echo `date` >> ~/setup.log
  exit 1
fi

echo "Installation completed!" >> ~/setup.log
echo `date` >> ~/setup.log
