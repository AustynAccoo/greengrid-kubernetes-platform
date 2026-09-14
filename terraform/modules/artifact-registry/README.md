# Artifact Registry

Creates one regional Docker repository for `telemetry-api` and `telemetry-generator`. CI must publish Git-SHA tags such as `git-a1b2c3d...`; environment promotion reuses the same digest and never uses `latest`.

The repository enables `docker_config { immutable_tags = true }` so published Docker tags cannot be reassigned to a different digest. This complements Git-SHA naming and build-once promotion; enforcement begins after an approved Terraform apply. The existing repository is expected to update in place.
