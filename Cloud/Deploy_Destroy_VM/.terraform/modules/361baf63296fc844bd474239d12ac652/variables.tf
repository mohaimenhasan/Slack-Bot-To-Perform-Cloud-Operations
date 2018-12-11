
# VM specifications

variable "vsphere_datacenter" {
	description = "In which datacenter the VM will be deployed"
}

variable "vsphere_vm_template" {
	description = "Where is the VM template located"
}

variable "vsphere_vm_folder" {
	description = "In which folder the VM will be store"
}

variable "vsphere_resource_pool" {
        description = "In which resource pool the VM will be deployed"
}

variable "vsphere_vcpu_number" {
        description = "How many vCPU will be assigned to the VM (default: 1)"
	default = "1"
}

variable "vsphere_memory_size" {
    description = "How much RAM will be assigned to the VM (default: 1024)"
	default = "1024"
}

variable "vsphere_datastore" {
        description = "What is the name of the VM datastore"
}

variable "vsphere_port_group" {
    description = "In which port group the VM NIC will be configured (default: VM Network)"
	default = "VM Network"
}

variable "License_activation_key" {
        description = "license key for BAM/BDDS product"
}

variable "vm_count" {
    description = "The number of vms to deploy"
    default = "1"
}

variable "vsphere_ipv4_address" {
    description = "enter starting ipv4 address number of vms to deploy"
}

variable "vsphere_ipv4_gateway" {
    description = " enter ipv4 gateway "
}

variable "vsphere_ipv4_netmask" {
    description = " enter ipv4 netmask "
}

variable "vsphere_vm_name" {
        description = "What is the name of the VM"
}
