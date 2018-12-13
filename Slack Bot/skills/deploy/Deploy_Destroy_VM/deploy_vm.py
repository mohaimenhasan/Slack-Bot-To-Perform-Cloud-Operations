from subprocess import *
import sys
import argparse
import os
import json
import ssl
import humanize
import warnings
from pyVim.connect import SmartConnect, Disconnect
"""
    usage: deploy [-h] -flavor FLAVOR [-version VERSION] [-suffix SUFFIX]
             [-buildnum BUILDNUM] [-name NAME] [-ip4 IP4]
             [-datastore DATASTORE]
"""
def GetArgs():

    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')
    parser.add_argument('-flavor', '--flavor', required=True, action='store',
                        help='Type of product')
    parser.add_argument('-version', '--version', required=True, action='store',
                        help='Product version')
    parser.add_argument('-suffix', '--suffix', required=True, action='store',
                        help='QA/GA')
    parser.add_argument('-buildnum', '--buildnum', required=True, action='store',
                        help='Build Number')
    parser.add_argument('-name', '--name', required=True, action='store',
                        help='Name of the custom VM')
    parser.add_argument('-ip4', '--ip_address', required=True, action='store',
                        help='IPv4 of the VM')
    parser.add_argument('-datastore', '--datastore', required=True, action='store',
                        help='Used to only fetch information related to specified datastore name')
    parser.add_argument('-size', '--asking_size', required=True, action='store',
                        help='How much space the VM would take')
    args = parser.parse_args()
    return args

def create_module(vm_name, template, ip_address, datastore, flavor, asking_size):
    """
    Creates the module for applying to terraform
    :return:
    """
    status = True
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if os.path.exists('main.tf.json'):
        os.remove('main.tf.json')

    print('Creating a module for terraform deployment')

    data = {
        "module": {
            "Deploy_BPC_BAM_VM": {

            }
        }
    }
    data['module']['Deploy_BPC_BAM_VM']['vm_count'] = 1
    data['module']['Deploy_BPC_BAM_VM']['source'] = "http://10.244.105.32/modules/1.0/bpc_singlenic_bam_bdds.zip"
    data['module']['Deploy_BPC_BAM_VM']['vsphere_vm_name'] = vm_name
    data['module']['Deploy_BPC_BAM_VM']['vsphere_vm_template'] = template
    data['module']['Deploy_BPC_BAM_VM']['vsphere_ipv4_address'] = ip_address
    data['module']['Deploy_BPC_BAM_VM']['vsphere_datastore'] = datastore
    data['module']['Deploy_BPC_BAM_VM']['vsphere_ipv4_gateway'] = "10.244.104.1"
    data['module']['Deploy_BPC_BAM_VM']['vsphere_ipv4_netmask'] = "22"
    if flavor.upper() == "BAM":
        data['module']['Deploy_BPC_BAM_VM']['License_activation_key'] = "18933-87600-78BAE-F857A-28164"
    else:
        data['module']['Deploy_BPC_BAM_VM']['License_activation_key'] = "15778-54800-D679F-3484E-46FDC"
    data['module']['Deploy_BPC_BAM_VM']['vsphere_vcpu_number'] = "1"
    data['module']['Deploy_BPC_BAM_VM']['vsphere_memory_size'] = asking_size
    data['module']['Deploy_BPC_BAM_VM']['vsphere_datacenter'] = "CEL"
    data['module']['Deploy_BPC_BAM_VM']['vsphere_vm_folder'] = "Tenants-Internal/Integrity/Hackathon Slackbot"
    data['module']['Deploy_BPC_BAM_VM']['vsphere_port_group'] = "integrity|integrity-anp|integrity-net002"
    data['module']['Deploy_BPC_BAM_VM']['vsphere_resource_pool'] = "bcl-internal-integrity"
    try:
        with open('main.tf.json', "w") as write:
            json.dump(data, write)
            print('Terraform module created under main.tf.json')

    except Exception as e:
        print('Writing to file failed '+str(e))
        exit(1)

def deploy_vm(vm_name, flavor, version, suffix, buildnum, ip_address, datastore, asking_size):
    os.environ["VSPHERE_SERVER"]="vcenter.bluecatlabs.net"
    os.environ["VSPHERE_USER"]="mohaimen.khan@bluecatlabs.net"
    os.environ["VSPHERE_PASSWORD"]="Tumikisaradibe1"
    os.environ["VSPHERE_ALLOW_UNVERIFIED_SSL"]="true"

    template = "Tenants-Internal/Lego/Build_VM_Templates"
    template += ("/%s/%s/%s/" % (flavor.upper(), version, suffix.upper()))
    product_name = flavor.lower()+"_esx_"+version+"-"+str(buildnum)+"."+suffix.upper()+".bcn_amd64.ova"
    template += product_name
    create_module(vm_name, template, ip_address, datastore, flavor, asking_size)
    try:
        call("terraform init", shell=True)
    except Exception as error:
        print("Terraform init failed %s" % error)
        exit(1)
    try:
        call("terraform apply -state=terraform.tfstate -auto-approve", shell=True)
    except Exception as error:
        print("Terraform apply failed %s" % error)
        exit(1)

def calculate_space(datastoreName, asking_size):
    asking_size = int(asking_size)
    if (asking_size%1024) != 0:
        print("Assigned memory must in power of 2")
        exit(1)
    asking_size_in_bytes = asking_size * 1024 * 1024
    sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslContext.verify_mode = ssl.CERT_NONE
    si = SmartConnect(host="vcenter.bluecatlabs.net", user="bclsvcintegritybot@bluecatlabs.net",
                      pwd="eeBieF2eeth7qui!yeexai(S7hae2O", port=int(443),
                      sslContext=sslContext)
    content = si.RetrieveContent()
    for datacenter in content.rootFolder.childEntity:
        print ("DATACENTER Name: %s" %datacenter.name)
        datastores = datacenter.datastore
        for ds in datastores:
            try:
                if ds.summary.name == datastoreName:
                    print("DATASTORE Name: %s" % ds.summary.name)
                    summary = ds.summary
                    capacity = summary.capacity
                    freeSpace = summary.freeSpace
                    freeSpacePercentage = (float(freeSpace) / capacity) * 100
                    print("DATASTORE Capacity: %s" % str(humanize.naturalsize(capacity, binary=True)))
                    print("DATASTORE Freespace: %s" % str(humanize.naturalsize(freeSpace)))
                    print("DATASTORE Freespace Percentage: "+str(freeSpacePercentage) + "%")
                    if asking_size_in_bytes >= freeSpace:
                        print ("STOP: NOT ENOUGH SPACE AVAILABLE ON DATASTORE FOR THIS OPERATION")
                        print ("""
                        This action will result in %s free space on BPC.
                        It will take down DS: %s
                        """ % (str(humanize.naturalsize(freeSpacePercentage - asking_size_in_bytes)),
                              ds.name))
                        exit(1)
                    if freeSpacePercentage < 1:
                        warnings.warn("Less than 1% free space left")
            except Exception as error:
                print "Unable to access summary for datastore: ", ds.name
                print error
                exit(1)

def main():
    args = GetArgs()
    calculate_space(args.datastore, args.asking_size)
    deploy_vm(args.name, args.flavor, args.version, args.suffix, args.buildnum, args.ip_address, args.datastore, args.asking_size)
if __name__ == "__main__":
    sys.exit(main())
