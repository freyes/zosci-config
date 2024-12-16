#!/bin/bash -x

for PREFIX in auto-sync/ubuntu-xenial-16.04-amd64-server- \
              auto-sync/ubuntu-bionic-18.04-amd64-server- \
              auto-sync/ubuntu-focal-20.04-amd64-server- \
              auto-sync/ubuntu-jammy-22.04-amd64-server- \
              auto-sync/ubuntu-noble-24.04-amd64-server- ; do
    SRC_IMAGE=$(openstack image list | grep $PREFIX | tail -1 | awk '{print $4}')
    DST_IMAGE="zosci/$(echo $SRC_IMAGE | cut -d'/' -f2)"
    openstack image show $DST_IMAGE
    if [ "$?" -ne 0 ]; then
        echo "copying from $SRC_IMAGE to $DST_IMAGE"
        openstack image save $SRC_IMAGE | openstack image create --disk-format qcow2 --container-format bare --private $DST_IMAGE
    else
        echo "$DST_IMAGE already exists ... skipping"
    fi
done
openstack image list | zosci
