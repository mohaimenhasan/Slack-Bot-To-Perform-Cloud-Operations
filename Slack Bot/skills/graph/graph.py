#TODO : code
import os
import sys
#from shellCommand import *
#scriptpath = "../../shellCommand.py"
# print(os.path.abspath(scriptpath))
# Add the directory containing your module to the Python path (wants absolute paths)
# sys.path.append(os.path.abspath(scriptpath))

#from shellCommand import *
from subprocess import *

DATASTORE = "datastore"
CPU = "cpu"

def invoke(slack_client=None, args = None):

	for x in args:
		print(x)
	print()

	command = args.get('args')
	print(command)
	
	command = command.split(" ")
	print(command)
				
	if command[0] == DATASTORE:
		
		#show all data store info
		if len(command) == 1:
			
			print("LENGTH 1")
			initcmd = "python ~/bpcbot/skills/graph/bpc.py -host 'vcenter.bluecatlabs.net' -u 'jeanlouis.rebello@bluecatlabs.net' -password '!@12qwJR' -SSL False -option 'datastore'"
			call(initcmd, shell = True)

			output = open('./output', 'r')
			dataStoreJson = output.read()

			initcmd = "python ~/bpcbot/skills/graph/visualize.py -b " + "'" + dataStoreJson + "'"
			print("ABOUT TO VISUALIZE THIS SHITZ")
			
			print(initcmd) 
			call(initcmd, shell = True)
			
			slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="You want info about datastore")
			slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text=dataStoreJson)
		
		elif len(command) == 2:
			
			
			initcmd = "python ~/bpcbot/skills/graph/bpc.py -host 'vcenter.bluecatlabs.net' -u 'jeanlouis.rebello@bluecatlabs.net' -password '!@12qwJR' -SSL False -option 'datastore' -ds " + command[1]
			call(initcmd, shell = True)

			output = open('./output', 'r')
			dataStoreJson = output.read()
			
			initcmd = "python ~/bpcbot/skills/graph/visualize.py -b " + "'" + dataStoreJson + "'"
			print("ABOUT TO VISUALIZE THIS SHITZ")
			print(initcmd) 
			call(initcmd, shell = True)
			
			slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="You want info about datastore")
			slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text=dataStoreJson)

	elif command[0] == CPU:
		slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="You want info about CPU")
	else:
		slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="Must enter either datastore or cpu as the first argument.")
	#slack_token = os.environ["SLACK_BOT_TOKEN"]
	return
