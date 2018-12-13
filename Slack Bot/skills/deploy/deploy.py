import io
import textwrap
import argparse
import logging
import sys
import os
import json
import ssl
import humanize
import warnings
from pyVim.connect import SmartConnect, Disconnect
from subprocess import *
from time import sleep

'''
deploy a BAM or BDDS vm
deploy 
-f BAM or BDDS
-v version (default latest)
-s QA or GA
'''

"""
    usage: deploy [-h] -flavor FLAVOR [-version VERSION] [-suffix SUFFIX]
             [-buildnum BUILDNUM] [-name NAME] [-ip4 IP4]
             [-datastore DATASTORE]
"""

#MOHAIMEN's CODE
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
#MOHAIMEN's CODE
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
#MOHAIMEN's CODE
def deploy_vm(slack_client, args, vm_name, flavor, version, suffix, buildnum, ip_address, datastore, asking_size):
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
#MOHAIMEN's CODE
def calculate_space(slack_client, args, datastoreName, asking_size):
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
                    slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="DATASTORE Name: %s" % ds.summary.name)
                    summary = ds.summary
                    capacity = summary.capacity
                    freeSpace = summary.freeSpace
                    freeSpacePercentage = (float(freeSpace) / capacity) * 100
                    slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="DATASTORE Capacity: %s" % str(humanize.naturalsize(capacity, binary=True)))
                    slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="DATASTORE Freespace: %s" % str(humanize.naturalsize(freeSpace)))
                    slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="DATASTORE Freespace Percentage: "+str(freeSpacePercentage) + "%")
                    print("DATASTORE Capacity: %s" % str(humanize.naturalsize(capacity, binary=True)))
                    print("DATASTORE Capacity: %s" % str(humanize.naturalsize(capacity, binary=True)))
                    print("DATASTORE Freespace: %s" % str(humanize.naturalsize(freeSpace)))
                    print("DATASTORE Freespace Percentage: "+str(freeSpacePercentage) + "%")
                    if asking_size_in_bytes >= freeSpace:
                    	slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="STOP: NOT ENOUGH SPACE AVAILABLE ON DATASTORE FOR THIS OPERATION")
                    	print ("STOP: NOT ENOUGH SPACE AVAILABLE ON DATASTORE FOR THIS OPERATION")
                    	textToPrint = "This action will result in %s free space on BPC. It will take down DS: %s " % (str(humanize.naturalsize(freeSpacePercentage - asking_size_in_bytes)), ds.name)
                    	slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text=textToPrint)
                    	exit(1)
                    if freeSpacePercentage < 1:
                        warnings.warn("Less than 1% free space left")
            except Exception as error:
                print("Unable to access summary for datastore: %s") % ds.name
                print(error)
                exit(1)


def _print_help(parser):
	out = io.StringIO()
	parser.print_help(file=out)
	return out.getvalue()

def validate_arguments(slack_client, args, given_arguments):
	flavor = given_arguments['flavor']
	if not flavor == "bam" and not flavor == "bdds":
		slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="That's not a valid flavor...I only support bam or bdds")
		return False

	version = given_arguments['version']
	if not version == "9.0.0" and not version == "9.1.0":
		slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="That's not a valid version...I only support 9.0.0 or 9.1.0")
		return False

	suffix = given_arguments['suffix']
	if not suffix == "QA" and not suffix == "GA":
		slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="That's not a valid suffix...I only support QA (by default) or GA")
		return False

	buildnum = given_arguments['buildnum']
	name = given_arguments['name']
	ip4 = given_arguments['ip4']
	datastore = given_arguments['datastore']
	vmsize = given_arguments['size']

	return True;


def invoke(slack_client=None, args = None):
	print("My args are:")
	print(args)
	parser = argparse.ArgumentParser(
		prog='deploy',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="Deploy BAM or BDDS VM to BPC",
		epilog=textwrap.dedent("""Examples:
			deploy -flavor bam -version 9.1.0 -suffix QA -buildnum 058 -name testname -ip4 10.244.105.85 -datastore BCL-SIO-VOL-INTEGRITY-101 -size 2048
		"""))
	parser.add_argument("-flavor", required=False, help="Product flavor: bam or bdds")
	parser.add_argument("-version", required=False, default="9.1.0", help="Product version (default is 9.1.0)")
	parser.add_argument("-suffix", required=False, default="QA", help="Product suffix: QA or GA (default is QA)")
	parser.add_argument("-buildnum", default="latest", help="Build number (e.g., 68). Default is 'latest'")
	parser.add_argument("-name", required=False, help="Name of the VM. If VM's name is omitted, the flavor-version-suffix-build name will be given")
	parser.add_argument("-ip4", required=False, help="Assign this IPv4 address to the VM")
	parser.add_argument("-datastore", required=False, help="Datastore the VM will be using")
	parser.add_argument("-size", required=False, help="The size of the VM you are trying to deploy in MB")
	try:
		bpc_args = parser.parse_args(args['args'].split())
		dict_of_args = vars(bpc_args)
		print(bpc_args)
		other_args = parser.parse_args() # USE THIS FOR MOHAIMEN's CODE
	except SystemExit:
		formatted_text="```\n %s \n```" % (_print_help(parser))
		slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text=formatted_text)
		#slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text=f"```\n{_print_help(parser)}\n```")
		return

	if validate_arguments(slack_client, args, dict_of_args):
		#All arguments were valid so proceed to make the call
		flavor = dict_of_args['flavor']
		version = dict_of_args['version']
		suffix = dict_of_args['suffix']
		buildnum = dict_of_args['buildnum']
		name = dict_of_args['name']
		ip4 = dict_of_args['ip4']
		datastore = dict_of_args['datastore']
		size = dict_of_args['size']
		finalCommand="cd skills/deploy/Deploy_Destroy_VM && python deploy_vm.py -flavor %s -version %s -suffix %s -buildnum %s -name %s -ip4 %s -datastore %s -size %s && cd /home/ubuntu/bpcbot" % (flavor, version, suffix, buildnum, name, ip4, datastore, size)
		
		#print(finalCommand)
		mo_args = bpc_args
		calculate_space(slack_client, args, datastore, size)
		deploy_vm(slack_client, args, name, flavor, version, suffix, buildnum, ip4, datastore, size)# print(finalCommand)
		
		# call("cd skills/deploy/Deploy_Destroy_VM", shell=True)
		#returncode = call(finalCommand, shell=True)
		print("return code is: ", returncode)
		# call("cd /home/ubuntu/bpcbot", shell=True)
		if returncode == 0:
			sleep(180)
			slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="Your VM %s has been deployed to BPC " % (name))
		else:
			slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="There was a problem...VM was not deployed ")
