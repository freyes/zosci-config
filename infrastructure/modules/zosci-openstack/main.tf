terraform {
required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.53.0"
    }
  }
}

# Create a SSH key for zosci.
resource "openstack_compute_keypair_v2" "zosci-keypair" {
  name       = "${var.keypair_name}"
  public_key = "${var.keypair_public_key}"
}

# Create a security group for nodepool managed instances
resource "openstack_networking_secgroup_v2" "zosci_secgroup" {
  name = "${var.secgroup_name}"
  description = "Security group for nodepool instances"
}

# Security group associated to the juju model where the k8s cluster is deployed
data "openstack_networking_secgroup_v2" "k8s_cluster_secgroup" {
  name = "${var.k8s_cluster_secgroup}"
}

resource "openstack_networking_secgroup_rule_v2" "zosci_secgroup_rule_allow_k8s" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  security_group_id = openstack_networking_secgroup_v2.zosci_secgroup.id
  remote_group_id   = "${data.openstack_networking_secgroup_v2.k8s_cluster_secgroup.id}"
}

# # data sources
# data "openstack_images_image_v2" "ubuntu_noble" {
#   name        = "auto-sync/ubuntu-noble-24.04-amd64-server-20240710-disk1.img"
#   most_recent = true

#   properties = {
#     os_distro    = "ubuntu"
#     os_version   = "24.04"
#     product_name = "com.ubuntu.cloud:server:24.04:amd64"
#   }
# }
