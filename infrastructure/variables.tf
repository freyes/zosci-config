variable "kubeconfig" {
  type = string
  default = "~/.kube/config"
  description = "Path to kubectl configuration file"
}

variable "storage_class_name" {
  type = string
  default = "csi-cinder-default"
  description = "Storage class name to use when creating volumes"
}

variable "docker-username" {
  type = string
  default = ""
  description = "Dockerhub username"
}

variable "docker-password" {
  type = string
  default = ""
  description = "Dockerhub password"
}

variable "docker-server" {
  type = string
  default = "https://index.docker.io/v1"
  description = "Dockerhub server"
}

variable "docker-email" {
  type = string
  default = ""
  description = "Dockerhub email"
}

variable "ingress_class_name" {
  type = string
  default = "nginx-ingress-controller"
  description = "Ingress Class Name"
}
