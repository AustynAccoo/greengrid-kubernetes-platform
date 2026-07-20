locals {
  zone = "${var.region}-b"

  labels = merge(
    var.labels,
    {
      project      = "greengrid"
      environment  = var.environment
      "managed-by" = "terraform"
      purpose      = "portfolio"
      owner        = "austyn-accoo"
    }
  )
}