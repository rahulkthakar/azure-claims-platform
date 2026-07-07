variable "prefix" {
  default = "azclaims"
}
variable "location" {
  default = "canadacentral"
}
variable "env" {
  default = "dev"
}
variable "monthly_budget" {
  default = 15
}
variable "alert_email" {
  description = "Email for budget alerts"
  type        = string
}
