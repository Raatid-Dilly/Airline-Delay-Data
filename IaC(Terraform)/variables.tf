locals {
  data_lake_bucket = "<NAME OF YOUR GOOGLE CLOUD STORAGE DATA LAKE>"
}

variable "project" {
    description = "Domestic Airline On-Time Statistics and Analysis"
    default = "<NAME OF YOUR GOOGLE CLOUD PLATFORM PROJECT/ID>"
}

variable "region" {
  default = "<REGION FOR GOOOGLE CLOUD PLATFORM SERVICES. SHOULD BE CHOSEN BASAED ON YOUR LOCATION>"
  type = string
}

variable "storage_class" {
  description = "Data Lake Storage Class"
  default = "STANDARD"
}

variable "BQ_DATASET" {
  type = string
  default = "<NAME OF BIGQUERY DATASET THAT WILL BE USED TO STORE DATA>"
}