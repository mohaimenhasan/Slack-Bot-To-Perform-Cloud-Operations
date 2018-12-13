import os
import time
import re
import skill
from slackclient import SlackClient
#from bpcbot import BPCBot


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
bot_id = "BEKJUJQQY"
at_bot = "<@{}>".format(bot_id)
bot_skills = []

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "help"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):

    # If it is a valid command, return it to be handled, otherwise return None, None
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            skill, args = _split_text(event["text"])
            if _check_if_valid_skill(skill):
                return event["channel"], event["text"]
    return event["channel"], None

# def parse_direct_mention(message_text):
#     """
#         Finds a direct mention (a mention that is at the beginning) in message text
#         and returns the user ID which was mentioned. If there is no direct mention, returns None
#     """
#     matches = re.search(MENTION_REGEX, message_text)
#     print(matches)
#     # the first group contains the username, the second group contains the remaining message
#     return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(channel, command):
    """
        Executes bot command if the command is known
    """
    print("Channel = ", channel)
    print("Command = ", command)
 
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command == "help":
        response = "Sure...write some more code then I can do that!"
    #help command lists all possible commands
    # if command == "help":
    # 	response = ""
    #report command 
    elif command == "report":
        response = "Here I will report on stuff..."
    else:
        response = "Try typing help to see valid commands"

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


def handle_skill(skill, args):
    try:
        if skill == 'help':
            slack_client.api_call("chat.postMessage", channel=args["channel"], as_user=False, text="Hey I am WALL-E! I can help you with BPC. Use `report` , `graph` , `deploy` , or `destroy` to interact with me")
        bot_skills[skill](args=args, slack_client=slack_client)
        return
    except KeyError as err:
        print('Unknown skill: ', skill)

'''
 Filter the input the bot gets to make sure it only acts and reports 
 when a user has specifically mentioned the bot or has sent the bot a DM
'''
def filter_input(slack_rtm_input):
    input_list = slack_rtm_input
    if input_list and len(input_list) > 0:
        for input in input_list:
                try:
                    if not _is_message(input) or 'user' not in input or _is_sent_to_self(input):
                        continue
                except KeyError as err:
                    logging.exception(err)
                    continue
                # logging.debug('Message recieved (user=%s):\n%s', self._user_list[input['user']]['name'], slack_rtm_input)
                skill, args = None, None

                if _is_mention(input):
                    print("This is @mention")
                    #logging.debug('This is @mention')
                    skill, args = _split_text(input['text'])
                    return {'skill': skill, 'user': input['user'], 'channel': input['channel'], 'args': ' '.join(args)}
                    #return input_list
                elif _is_direct_msg(input):
                    print("This is a direct message")
                    #logging.debug('This is a direct message')
                    skill, args = _split_text(input['text'], start_pos=0)
                    return {'skill': skill, 'user': input['user'], 'channel': input['channel'], 'args': ' '.join(args)}
                    #return input_list

def load_skills(bot_skills_dir):
    print('Loading skills from: %s', bot_skills_dir)
    bpcbot_potential_skills = [s for s in os.scandir(bot_skills_dir) if s.is_dir()]
    print('Found these potential skills: ', bpcbot_potential_skills)
    skill_set = {}

    def _load_individual_skill(s):
        print('Checking for skill: ', s)
        description_file = s.path + '/skill.json'
        description_file_exists = os.path.isfile(description_file)

        if description_file_exists:
            print('Found description file for skill ', s)
            print('Loading ', s)
            sk = skill.create_skill(description_file)
            print('Loaded skill %s', str(sk))
            skill_set[sk.name] = sk

    for s in bpcbot_potential_skills:
        try:
            _load_individual_skill(s)
        except Exception as ex:
            print('--- ERROR ---')
            print(ex)
            print("")

    print('Loaded ', len(skill_set), ' skills')
    return skill_set

def _is_message(msg):
        if 'type' not in msg:
            return False
        return msg['type'] == 'message'

def _is_mention(msg):
    return _is_message(msg) and 'text' in msg.keys() and at_bot in msg['text']

def _is_direct_msg(msg):
    return _is_message(msg) and msg['channel'].startswith('D')

def _is_sent_to_self(msg):
    if 'user' not in msg:
        return False
    return _is_message(msg) and msg['user'] == bot_id

def _split_text(text, start_pos=0):
        s = text.split()
        cmd = s[start_pos].strip().lower()
        args = s[start_pos + 1:] if len(s) > start_pos else s[start_pos:]
        return cmd, args

def _help_message():
    print("AAAAAAH")

def _check_if_valid_skill(skill):
    print("checking for: ", skill.strip())
    print(bot_skills);
    for known_skill in bot_skills:
        print("known skill : ", known_skill.strip())
        if skill.strip() == known_skill.strip():
            return True
    return False

def bot_load_skills():
    #Load skills that should be supported by bot
    bot_skills_dir = "/home/ubuntu/bpcbot/skills"
    global bot_skills
    bot_skills = load_skills(bot_skills_dir)

def bot_connect():
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        bot_id = slack_client.api_call("auth.test")["user_id"]
        return bot_id
    else:
        print("Connection failed.")
        return None

def bot_eventloop():
    # Event loop
    while True:
            # Read the next event and send it off to parse_bot_commands
            filtered_input = filter_input(slack_client.rtm_read())
            if filtered_input:
                handle_skill(skill=filtered_input['skill'], args=filtered_input)


                # print("filtered input - ", filtered_input)
                # channel, command = parse_bot_commands(filtered_input)
                # print("The channel: ", channel)
                # print("The command: ", command)
                # if command:
                #     handle_command(channel, command)
                # else:
                #     # Sends the response back to the channel
                #     slack_client.api_call("chat.postMessage",channel=channel,text="I don't know what you mean. Try `help` to see all the ways I can help you :smile: ")
                # print("")
                time.sleep(RTM_READ_DELAY)


if __name__ == "__main__":
    bot_load_skills()
    bot_id = bot_connect()
    if bot_id:
        bot_eventloop()
    else:
        print("ERROR connecting to Slack") 

    
