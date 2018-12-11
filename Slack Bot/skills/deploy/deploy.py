import io
import textwrap
import argparse
import logging

from subprocess import *

'''
deploy a BAM or BDDS vm
deploy 
-f BAM or BDDS
-v version (default latest)
-s QA or GA
'''


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

		"""))
	parser.add_argument("-flavor", required=True, help="Product flavor: bam or bdds")
	parser.add_argument("-version", required=False, default="9.1.0", help="Product version (default is 9.1.0)")
	parser.add_argument("-suffix", required=False, default="QA", help="Product suffix: QA or GA (default is QA)")
	parser.add_argument("-buildnum", default="latest", help="Build number (e.g., 68). Default is 'latest'")
	parser.add_argument("-name", required=False, help="Name of the VM. If VM's name is omitted, the flavor-version-suffix-build name will be given")
	parser.add_argument("-ip4", required=False, help="Assign this IPv4 address to the VM")
	parser.add_argument("-datastore", required=True, help="Datastore the VM will be using")
	parser.add_argument("-size", required=False, help="The size of the VM you are trying to deploy")
	try:
		bpc_args = parser.parse_args(args['args'].split())
		dict_of_args = vars(bpc_args)
		print(dict_of_args['flavor'])
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
		finalCommand="python deploy_vm.py -flavor %s -version %s -suffix %s -buildnum %s -name %s -ip4 %s -datastore %s -size %s" % (flavor, version, suffix, buildnum, name, ip4, datastore, size)
		print(finalCommand)
		call('pwd', shell=True)
