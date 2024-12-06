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
