# Artifact Registry

Creates one regional Docker repository for `telemetry-api` and `telemetry-generator`. CI must publish Git-SHA tags such as `git-a1b2c3d...`; environment promotion reuses the same digest and never uses `latest`.

