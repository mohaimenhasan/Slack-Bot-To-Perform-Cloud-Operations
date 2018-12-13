import os
import argparse
import textwrap
import io

def _print_help(parser):
	out = io.StringIO()
	parser.print_help(file=out)
	return out.getvalue()

def invoke(slack_client=None, args = None):
	print("My args are:")
	print(args)
	parser = argparse.ArgumentParser(
		prog='alert',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="Provide recurring alerts to user for reminding them when they should shut off their VMs",
		epilog=textwrap.dedent("""Example: Until Dec 10, 2018, user wants to be reminded every hour with the message "Hello there"
			alert -f 1h -m "Hello there" -d 12/10/2018
		"""))
	parser.add_argument("-f", required=True, help="Frequency of reminder (m - minutes, h - hour)")
	parser.add_argument("-m", required=True, help="Message you wish to be reminded of")
	parser.add_argument("-d", required=True, help="Specify up until what date you want to be reminded (mm/dd/yyyy format)")

	try:
		bpc_args = parser.parse_args(args['args'].split())
		dict_of_args = vars(bpc_args)
	except SystemExit:
		formatted_text="```\n %s \n```" % (_print_help(parser))
		slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text=formatted_text)
		#slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text=f"```\n{_print_help(parser)}\n```")
		return

	frequency = dict_of_args['f']
	message = dict_of_args['m']
	date = dict_of_args['d']
	slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="I will alert you every %s hour(s), until %s, about %s" % (frequency, date, message))
	return
