# Deploy Zuul CI, MariaDB, and Apache Zookeeper

This repo contains a [Terraform](https://www.terraform.io) plan and
configuration files you can use to deploy [Zuul CI](zuul-ci.org/) 9.1 and its
dependencies - [MariaDB](https://mariadb.com) and [Apache
Zookeeper](https://zookeeper.apache.org/) - to
[Kubernetes](https://kubernetes.io) using [the Kubernetes Terraform
provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest).


## Deployment


1. Deploy a Kubernetes cluster on top of a OpenStack cloud.

``` bash
juju deploy ./kubernetes-core/bundle.yaml
```

2. Get the kubeconfig file

``` bash
juju run-action \
    --format json \
    --wait \
    kubernetes-control-plane/leader get-kubeconfig \
    | jq -r '.[]|.results.kubeconfig' > kubeconfig

```

3. Run the terraform plan
``` bash
terraform init
terraform apply
```

## Variables

The terraform plan offers the following variables to be overridden:

| Name               | Default Value              | Description                                     |
|--------------------|----------------------------|-------------------------------------------------|
| kubeconfig         | ~/.kube/config             | Path to kubectl configuration file              |
| storage_class_name | csi-cinder-default         | Storage class name to use when creating volumes |
| docker-username    |                            | Dockerhub username                              |
| docker-password    |                            | Dockerhub password (or token)                   |
| docker-server      | https://index.docker.io/v1 | Dockerhub server                                |
| docker-email       |                            | Dockerhub email                                 |
| ingress_class_name | nginx-ingress-controller   | Ingress class name                              |
