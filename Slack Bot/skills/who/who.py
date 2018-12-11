#TODO : code

import os



def invoke(slack_client=None, args = None):
	print("My args are:")
	print(args)
	slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="/remind")
	#slack_token = os.environ["SLACK_BOT_TOKEN"]
	return
