#!/usr/bin/env python3.5
import os
import sys
import time
import json
import threading
import logging
import sqlite3
import socket
import websocket
import pkgutil
import inspect
import pprint
import skill

from threading import Thread
from slackclient import SlackClient


class BPCBot:

    """
    BPCBot - To make our digital lives easier
    """

    VERSION = '0.1'

    def __init__(self, skills, api_token):
        self.sig_stop = threading.Event()
        self._sleep_time = 1
        self._active_channel = None
        self._bot_id = "BEKJUJQQY"
        self._at_bot = "<@{}>".format(self._bot_id)
        # self._slack_client = SlackClient(api_token)
        self._slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
        self._skills_dir = skills
        self._skills = None
        self._user_list = {}
        self._channels_list = []

    def reload_skills(self, signum, frame):
        logging.info('Reloading skills: signal=%d', signum)
        self._reload_skills()

    def _reload_skills(self):
        for s in self._skills.values():
            logging.info('Reloading skill: %s', s)
            s.reload_skill(self._skills_dir)

    def run(self):
        """
        Public interface
        """
        self._skills = self._load_skills(self._skills_dir)
        if self._start():
            self._run()
        else:
            logging.error('Cannot connect to Slack!')

    def _start(self):
        count = 3

        while count > 0:
            try:
                self._connect_bot()
                logging.info('Bot successfully connected to Slack!')
                return True
            except ConnectionError as err:
                logging.exception(err)
                count -= 1

        return False

    def _connect_bot(self):
        logging.info('Starting %s (version=%s)', self.__class__.__name__, BPCBot.VERSION)
        logging.info('Testing slack API\n%s', self._slack_client.api_call('api.test'))
        logging.info('Testing authentication & identity\n%s', self._slack_client.api_call('auth.test'))

        if not self._slack_client.rtm_connect():
            raise ConnectionError("Bot can't connect to Slack!")

    def _run(self):
        logging.info('[OK] - Bot is ready to operate')
        # self._user_list = self._get_users()

        while not self.sig_stop.is_set():
            try:
                self._run_event_loop()
            except socket.timeout:
                logging.error("socket timeout!")
                self.sig_stop.wait(30)
            except (websocket._exceptions.WebSocketConnectionClosedException, ConnectionError, ConnectionResetError) as ex:
                logging.exception(repr(ex))
                self.sig_stop.wait(30)
                self._connect_bot()
            except Exception as ex:
                logging.exception(repr(ex))
                self._reply(":lol: something went wrong!")

            self.sig_stop.wait(self._sleep_time)

    def stop(self):
        logging.info('Stopping %s (tid %s)', self.__class__.__name__, threading.current_thread().name)
        self.sig_stop.set()

    def _run_event_loop(self):
        input = self._parse_input(self._slack_client.rtm_read())
        if input:
            logging.debug(pprint.PrettyPrinter(indent=2).pformat(input))
            self._handle_skill(skill=input['skill'], args=input)

    def _handle_skill(self, skill, args):
        logging.debug('Handling skill: %s with args: %s', skill, args)
        try:
            self._skills[skill](args=args, slack_client=self._slack_client)
            return
        except KeyError as err:
            logging.error('Unknown skill: %s', skill)

        msg = self._help_message(sorted(self._skills.values(), key=lambda s: s.name)) if skill == "help" else self._disappointed_message(skill)
        self._slack_client.api_call("chat.postMessage",
                                    channel=args['channel'],
                                    as_user=True,
                                    text=msg)

    def _help_message(self, known_skills):
        msg = "I have the following skills:"
        for skill in known_skills:
            msg += f"\n`{skill.name}` - {skill.description}"
        msg += "\nTo get help message for a specific skill, just do: `skill-name --help`"
        return msg

    def _disappointed_message(self, unknown_skill):
        return "Sorry, I don't have that skill.."
        # return f"Sorry, I don't have that skill: `{unknown_skill}` ... :disappointed:"

    def _parse_input(self, slack_rtm_input):
        input_list = slack_rtm_input
        if input_list and len(input_list) > 0:
            #logging.debug('Slack message: %s', slack_rtm_input)
            for input in input_list:
                try:
                    if not self._is_message(input) or 'user' not in input or self._is_sent_to_self(input):
                        continue
                except KeyError as err:
                    logging.exception(err)
                    continue
                print('userlist = ', self._user_list)
                # logging.debug('Message recieved (user=%s):\n%s', self._user_list[input['user']]['name'], slack_rtm_input)
                skill, args = None, None

                if self._is_mention(input):
                    logging.debug('This is @mention')
                    skill, args = self._split_text(input['text'])
                    return {'skill': skill, 'user': input['user'], 'channel': input['channel'], 'args': ' '.join(args)}
                elif self._is_direct_msg(input):
                    logging.debug('This is a direct message')
                    skill, args = self._split_text(input['text'], start_pos=0)
                    return {'skill': skill, 'user': input['user'], 'channel': input['channel'], 'args': ' '.join(args)}

    def _is_message(self, msg):
        if 'type' not in msg:
            return False
        return msg['type'] == 'message'

    def _is_mention(self, msg):
        return self._is_message(msg) and 'text' in msg.keys() and self._at_bot in msg['text']

    def _is_direct_msg(self, msg):
        return self._is_message(msg) and msg['channel'].startswith('D')

    def _is_sent_to_self(self, msg):
        if 'user' not in msg:
            return False
        return self._is_message(msg) and msg['user'] == self._bot_id

    def _split_text(self, text, start_pos=1):
        s = text.split()
        cmd = s[start_pos].strip().lower()
        args = s[start_pos + 1:] if len(s) > start_pos else s[start_pos:]
        return cmd, args

    def _reply(self, msg):
        logging.debug('Replying to {} with message:\n{}'.format(self._active_channel, msg))
        try:
            if msg:
                self._slack_client.api_call("chat.postMessage", channel=self._active_channel, as_user=True, text=msg)
        except Exception as ex:
            logging.exception(repr(ex))

    def _get_users(self):
        logging.debug('Getting list of users (for quick mapping of user IDs to user names)')
        users_list_all = self._slack_client.api_call("users.list")
        users_list = {user['id']: user for user in users_list_all['members'] if user['deleted'] is False}
        logging.debug('Got %d users', len(users_list))
        logging.debug('Quick self-check: %s', pprint.PrettyPrinter(indent=2).pformat(users_list[self._bot_id]))
        return users_list

    def _load_skills(self, skills):
        logging.info('Loading skills from: %s', skills)
        bpcbot_potential_skills = [s for s in os.scandir(skills) if s.is_dir()]
        logging.info('Found these potential skills: %s', bpcbot_potential_skills)
        skill_set = {}

        def _load_skill(s):
            logging.info('Probing skill: %s', s)
            description_file = s.path + '/skill.json'
            description_file_exists = os.path.isfile(description_file)
            logging.info('Skill description file found? %s', description_file_exists)

            if description_file_exists:
                logging.info('Loading skill: %s', s)
                sk = skill.create_skill(description_file)
                logging.info('Loaded skill: %s', str(sk))
                skill_set[sk.name] = sk

        for s in bpcbot_potential_skills:
            try:
                _load_skill(s)
            except Exception as ex:
                logging.error(ex)

        logging.info('Loaded %d skills', len(skill_set))
        return skill_set
        