provider "vsphere" {

}

data "vsphere_datacenter" "dc" {
  name = "${var.vsphere_datacenter}"
}

data "vsphere_datastore" "datastore" {
  name          = "${var.vsphere_datastore}"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_resource_pool" "pool" {
  name          = "${var.vsphere_resource_pool}"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_network" "network" {
  name          = "${var.vsphere_port_group}"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_virtual_machine" "template" {
  name          = "${var.vsphere_vm_template}"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

data "template_file" "cloud_config" {
  count    = "${var.vm_count}"
  template = <<EOF
#cloud-config
bluecat_license:
    id: 123456789012345
    key: $${ key }
bluecat_netconf:
    ipaddr: "$${ ipaddr }"
    cidr: "$${ cidr }"
    gateway: "$${ gateway }"
    hostname: "new"
EOF

  vars {
    key = "${var.License_activation_key}"
    ipaddr = "${join(".",concat(slice(split(".", "${var.vsphere_ipv4_address}"), 0,3), list("${(element(split(".", "${var.vsphere_ipv4_address}"),3) + count.index)}")))}"
    gateway = "${var.vsphere_ipv4_gateway}"
    cidr = "${var.vsphere_ipv4_netmask}"
  }
}

resource "vsphere_virtual_machine" "vm" {
  count            = "${var.vm_count}"
  name             = "${var.vm_count > 1 ? format("${var.vsphere_vm_name}-%03d", count.index+1) : var.vsphere_vm_name }"
  resource_pool_id = "${data.vsphere_resource_pool.pool.id}"
  datastore_id     = "${data.vsphere_datastore.datastore.id}"
  folder = "${var.vsphere_vm_folder}"

  num_cpus = "${var.vsphere_vcpu_number}"
  memory = "${var.vsphere_memory_size}"
  #wait_for_guest_net_timeout = 0

  guest_id = "${data.vsphere_virtual_machine.template.guest_id}"
  scsi_type = "${data.vsphere_virtual_machine.template.scsi_type}"

  network_interface {
    network_id   = "${data.vsphere_network.network.id}"
    adapter_type = "${data.vsphere_virtual_machine.template.network_interface_types[0]}"
  }

  disk {
    label            = "disk0"
    size             = "${data.vsphere_virtual_machine.template.disks.0.size}"
    eagerly_scrub    = "${data.vsphere_virtual_machine.template.disks.0.eagerly_scrub}"
    thin_provisioned = "${data.vsphere_virtual_machine.template.disks.0.thin_provisioned}"
  }

  clone {
    template_uuid = "${data.vsphere_virtual_machine.template.id}"
  }

  extra_config {
    "guestinfo.cloudinit.userdata" = "${base64encode(data.template_file.cloud_config.*.rendered[count.index])}"
    "guestinfo.cloudinit.userdata.encoding" = "base64"
  }
}
