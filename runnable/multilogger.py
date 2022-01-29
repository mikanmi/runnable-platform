#!/usr/bin/env python3

# Copyright (c) 2021, 2022, Patineboot. All rights reserved.
# MultiLogger is licensed under CC BY-NC-ND 4.0.

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

import sys
import logging
from logging.handlers import RotatingFileHandler

# LOGGER_LOG_LEVEL: Final[int] = logging.DEBUG
LOGGER_LOG_LEVEL = logging.DEBUG


class MultiLogger(logging.getLoggerClass()):
    """MultiLogger is a logger class.
    """

    def __init__(self, name):
        super().__init__(name)

        logger = self
        logger.setLevel(logging.DEBUG)

        self.__logger = logger
        self.__stdout_handler = None
        self.__logfile_handler = None

    def enable_stouthandler(self):

        if self.__stdout_handler:
            self.warning("stouthandler is already enabled.")
            return

        # initialize logger for standard out
        stout_formatter = logging.Formatter(
            fmt="[%(asctime)s][%(levelname)-3.3s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(stout_formatter)
        stdout_handler.setLevel(logging.WARN)
        self.__logger.addHandler(stdout_handler)

        self.__stdout_handler = stdout_handler

    def enable_filehandler(self, filename):

        if self.__logfile_handler:
            self.warning("filehandler is already enabled.")
            return

        # initialize logger for the log file
        logfile_formatter = logging.Formatter(
            fmt="[%(asctime)s][%(levelname)-3.3s][%(filename)s:%(lineno)d] %(funcName)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
        log_filename = filename
        logfile_handler = RotatingFileHandler(log_filename, maxBytes=(1048576 * 5), backupCount=2)
        logfile_handler.setFormatter(logfile_formatter)
        logfile_handler.setLevel(logging.INFO)
        self.__logger.addHandler(logfile_handler)

        self.__logfile_handler = logfile_handler

    def set_verbose(self):
        if self.__stdout_handler is not None:
            self.__stdout_handler.setLevel(logging.INFO)

        if self.__logfile_handler is not None:
            self.__logfile_handler.setLevel(logging.DEBUG)

    def set_simple_stdout(self):
        formatter = logging.Formatter("%(message)s")
        self.__stdout_handler.setFormatter(formatter)

    def notice(self, message):
        """Notice a message to a user.
        Args:
            message: the message to notice to the user.
        """
        self.__logger.log(100, message)
