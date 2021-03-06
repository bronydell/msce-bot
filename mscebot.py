#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MSCE Schedule Telegram bot
# by Alexander Zakharenko
#

import logging
import time
from threading import Thread, Event

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import schedule
import cmd_admin
import cmd_user
import utils

updater = None
config = None
logger = None


def schedule_monitor(bot, run):
    logger.debug('Starting schedule monitor...')

    while run.is_set():
        try:
            if schedule.update_student():
                cmd_admin.schedule_broadcast_student(bot)

            if schedule.update_teacher():
                cmd_admin.schedule_broadcast_teacher(bot)

            time.sleep(config['updateSleep'])
        except:
            logger.error('Schedule monitor exception')

    logger.debug('Stopping schedule monitor...')


def main():
    # INIT #
    global config, logger, updater

    config = utils.get_config()
    logger = logging.getLogger(__name__)
    updater = Updater(config['token'])

    logging.basicConfig(format='[%(asctime)s] [%(levelname)s:%(name)s] %(message)s', level=logging.INFO,
                        handlers=[logging.FileHandler(config['logFileName'], 'w', 'utf-8')])

    # User commands
    updater.dispatcher.add_handler(CommandHandler('start', cmd_user.default_menu))
    updater.dispatcher.add_handler(CommandHandler('cancel', cmd_user.close_keyboard))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, cmd_user.processor))

    # Admin commands
    updater.dispatcher.add_handler(CommandHandler('help', cmd_admin.help))
    updater.dispatcher.add_handler(CommandHandler('stop', cmd_admin.stop))
    updater.dispatcher.add_handler(CommandHandler('tbcast', cmd_admin.text_broadcast))
    updater.dispatcher.add_handler(CommandHandler('sbcast', cmd_admin.schedule_broadcast))
    updater.dispatcher.add_handler(CommandHandler('get_config', cmd_admin.get_config))
    updater.dispatcher.add_handler(MessageHandler(Filters.document, cmd_admin.set_config))

    updater.start_polling(timeout=config['poolTimeout'])

    run = Event()
    run.set()

    th = Thread(target=schedule_monitor, args=(updater.bot, run))
    th.start()

    updater.idle()

    # Stopping thread
    run.clear()
    th.join()


if __name__ == '__main__':
    main()
