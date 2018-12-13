#!/usr/bin/env python3.5

import os
import logging.config
import daemon
import argparse
import configparser
import lockfile
import signal
import time

from bpcbot import BPCBot


def run_in_background(bpcbot, log_conf_file, start_dir):
    context = daemon.DaemonContext(
        working_directory=start_dir,
        umask=0o005,
        pidfile=lockfile.FileLock(start_dir + '/bpcbot.pid')
        )

    context.signal_map = {
        # signal.SIGTERM: program_cleanup,
        signal.SIGHUP: 'terminate',
        signal.SIGUSR1: bpcbot.reload_skills
        }

    context.stderr = open(start_dir + '/bpcbot.err', 'wb')

    with context:
        logging.config.fileConfig(log_conf_file)
        logging.info('Running BPCBot in background (pid=%d)', os.getpid())
        bpcbot.run()


def run_in_foreground(bpcbot, log_conf_file):
    logging.config.fileConfig(log_conf_file)
    logging.info('Running BPCBot in foreground')
    bpcbot.run()


def main():
    parser = argparse.ArgumentParser(description="BPCBot: to make our digital lives easier")
    parser.add_argument("-c", "--config", default="./bpcbot.conf", help="Configuration file")
    parser.add_argument("-d", "--daemon", action="store_true", help="Run as daemon")

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read_file(open(args.config))

    bpcbot_start_dir = os.path.dirname(os.path.realpath(__file__))
    log_conf_file = config.get('bpcbot', 'log-configuration-file', fallback=bpcbot_start_dir + '/bpcbot-log.conf')
    skills = config.get('bpcbot', 'skills', fallback=bpcbot_start_dir + '/skills')
    api_token = config.get('bpcbot', 'api-token')

    bpcbot = BPCBot(skills, api_token)

    run_in_background(bpcbot, log_conf_file, bpcbot_start_dir) if args.daemon else run_in_foreground(bpcbot, log_conf_file)


if __name__ == "__main__":
    main()
    