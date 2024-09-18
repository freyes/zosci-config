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
# data "openstack_networking_network_v2" "ext_net" {
#   name = "ext_net"
# }

# data "openstack_networking_secgroup_v2" "default" {
#   name = "default"
# }

# # openstack router create zuul_router
# resource "openstack_networking_router_v2" "zuul_router" {
#   name                = "zuul_router"
#   admin_state_up      = true
#   external_network_id = data.openstack_networking_network_v2.ext_net.id
# }

# # openstack network create --disable-port-security zuul_admin_net
# resource "openstack_networking_network_v2" "zuul_tests_admin_net" {
#   name           = "zuul-tests_admin_net"
#   admin_state_up = "true"
#   dns_domain = "zuul-tests.project.serverstack."
# }
