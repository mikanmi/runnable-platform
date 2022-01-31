#!/usr/bin/env python3

# Copyright (c) 2021, 2022, Patineboot. All rights reserved.
# Runnable is licensed under CC BY-NC-ND 4.0.

# Attribution-NonCommercial-NoDerivatives 4.0 International

# Under the following terms:
# Attribution — You must give appropriate credit, provide a
# link to the license, and indicate if changes were made. You
# may do so in any reasonable manner, but not in any way that
# suggests the licensor endorses you or your use.
# NonCommercial — You may not use the material for
# commercial purposes.
# NoDerivatives — If you remix, transform, or build upon the
# material, you may not distribute the modified material.
# No additional restrictions — You may not apply legal terms
# or technological measures that legally restrict others from
# doing anything the license permits.

# Notices:
# You do not have to comply with the license for elements of
# the material in the public domain or where your use is
# permitted by an applicable exception or limitation.

# No warranties are given. The license may not give you all of
# the permissions necessary for your intended use. For
# example, other rights such as publicity, privacy, or moral
# rights may limit how you use the material.

# Python 3.8 or later supports the Final feature
# from typing import Final

import os
import sys
import logging
import json
from threading import Thread

from multilogger import MultiLogger
from commandoption import CommandOption
from infraredrunnable import InfraredRunnable


######################
# Advanced Configure #
######################
# LOGGER_LOG_ROOT_PATH: Final[str] = "/var/log/"
# LOGGER_LOG_USER_PATH: Final[str] = os.environ.get("HOME") + "/"
# LOGGER_LOG_FILENAME: Final[str] = "runnable.log"
LOGGER_LOG_ROOT_PATH = "/var/log/"
LOGGER_LOG_USER_PATH = os.environ.get("HOME") + "/"
LOGGER_LOG_FILENAME = "runnable.log"


######################
#    Script Code     #
######################
# Parse the command options
logging.setLoggerClass(MultiLogger)
# LOGGER: Final[MultiLogger] = logging.getLogger(__name__)
LOGGER = logging.getLogger(__name__)

comand_options = CommandOption(LOGGER)


class Runnable:
    def __init__(self):
        LOGGER.debug(f"STR")

    def run(self):
        LOGGER.debug(f"STR")

        thread = Thread(target=self.__loop)
        thread.start()

        # wait for closing stdin
        thread.join()

        LOGGER.debug(f"END")

    def __loop(self):
        LOGGER.debug(f"STR")
        for line in sys.stdin:
            LOGGER.info(f"received: {line.strip()}")
            message = json.loads(line)
            self.__send(message)
        LOGGER.debug(f"END")

    def __send(self, message):
        text = json.dumps(message)
        LOGGER.info(f"send: {text}")
        sys.stdout.write(text + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    # check the root user
    is_root = os.geteuid() == 0 and os.getuid() == 0

    log_filename = (LOGGER_LOG_ROOT_PATH if is_root else LOGGER_LOG_USER_PATH) + LOGGER_LOG_FILENAME
    LOGGER.enable_filehandler(log_filename)

    LOGGER.debug("LOG START")

    if comand_options.get_verbose():
        LOGGER.set_verbose()

    runnable = None
    if comand_options.get_test():
        runnable = Runnable()
    else:
        runnable = InfraredRunnable(LOGGER, comand_options.get_dryrun())

    runnable.run()
