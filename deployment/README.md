# Deployment Directory

This folder contains all infrastructure-as-code and configuration files required to deploy VisionSpec QC to production environments.

## Usage
* Kubernetes manifests (`deployment.yaml`, `service.yaml`, `ingress.yaml`) if deploying to a cluster.
* NGINX configurations for reverse proxies.
* CI/CD pipeline definitions (e.g., GitHub Actions workflows or Jenkins pipelines).
* Note: The root `docker-compose.yml` is used for local full-stack execution, while this folder handles scalable cloud deployment setups.
