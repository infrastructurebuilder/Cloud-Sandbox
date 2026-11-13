# Read by OpenTofu only: it ignores required_version in .tf files, which are
# written for Terraform, and enforces it in .tofu files. The version is the
# one the operator chose (2026-11-13); keep it equal to TOFU_VERSION in the
# Justfile.
terraform {
  required_version = "1.13.9"
}
