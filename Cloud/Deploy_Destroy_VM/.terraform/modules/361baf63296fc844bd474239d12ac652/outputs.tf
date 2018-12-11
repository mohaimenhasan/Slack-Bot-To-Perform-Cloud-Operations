output "nic1_ip_address" {
  description = "private ip addresses of the vm nic1"
  value = "${vsphere_virtual_machine.vm.*.default_ip_address}"
}
