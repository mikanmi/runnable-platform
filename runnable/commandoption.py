#!/usr/bin/env python3

# Copyright (c) 2021, 2022, Patineboot. All rights reserved.
# CommandOption is licensed under CC BY-NC-ND 4.0.

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

import argparse

LOGGER = None


class CommandOption:

    def __init__(self, logger):
        global LOGGER
        LOGGER = logger

        # add command options to the argument parser.
        parser = argparse.ArgumentParser(
            description="Infrared Remote is a firmware to send an infrared code on Raspberry Pi with an infrared HAT."
        )
        parser.add_argument("-t", "--test", action="store_true", help="Run on the test mode for Runnable Platform.")
        parser.add_argument("-v", "--verbose", action="store_true", help="run with verbose mode.")
        parser.add_argument("-n", "--dry-run", dest='dry_run', action="store_true", help="run with no changes mode.")

        self.__options = parser.parse_args()

    def get_test(self):
        LOGGER.debug(f"STR")
        test = self.__options.test
        LOGGER.debug(f"END {test}")
        return test

    def get_dryrun(self):
        LOGGER.debug(f"STR")
        dryrun = self.__options.dry_run
        LOGGER.debug(f"END {dryrun}")
        return dryrun

    def get_verbose(self):
        LOGGER.debug(f"STR")
        verbose = self.__options.verbose
        LOGGER.debug(f"END {verbose}")
        return verbose


if __name__ == "__main__":
    print("CommandOption is an Import Module.")
