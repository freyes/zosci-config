variable "keypair_name" {
  type = string
  description = "Keypair name when uploading the public key to OpenStack"
}

variable "keypair_public_key" {
  type = string
  description = "Public key to be upload to OpenStack"
}
