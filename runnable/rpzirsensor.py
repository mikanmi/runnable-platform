#!/usr/bin/env python3

# Copyright (c) 2022, Patineboot. All rights reserved.
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

import os
import subprocess
from time import sleep
from threading import Thread

import cgsensor

######################
#      Configure     #
######################
# The infrared HAT tools and commands.
# the directory which contains infraredRunnable.py.
SCRIPT_DIRECTORY = os.path.dirname(__file__)
# infrared codes json file.
CGIRTOOL_CODE_JSON = os.path.join(SCRIPT_DIRECTORY, "codes.json")
# The command of Infrared sending
SEND_INFRARED_COMMAND = "cgir send" + " -c " + CGIRTOOL_CODE_JSON

######################
#    Script Code     #
######################
LOGGER = None


class RpzIrSensor:
    def __init__(self, logger, dryrun, sender):
        super().__init__()
        global LOGGER
        LOGGER = logger

        LOGGER.debug(f"STR")

        self.__dryrun = dryrun
        self.__sender = sender
        self.__stopped = True

        LOGGER.debug(f"END")

    def start(self):
        thread = Thread(target=self.run)
        thread.start()
        return thread

    def stop(self):
        self.__stopped = True

    def run(self):
        LOGGER.debug(f"STR")
        self.__stopped = False

        bme280 = cgsensor.BME280(i2c_addr=0x76)

        while not self.__stopped:
            bme280.forced()
            humidity_message = self.__make_message("Bikini Humidity", "CurrentRelativeHumidity", bme280.humidity)
            self.__sender.send(humidity_message)

            temperature_message = self.__make_message("Bikini Temperature", "CurrentTemperature", bme280.temperature)
            self.__sender.send(temperature_message)

            sleep(10)

        LOGGER.debug(f"END")

    def __make_message(self, name, characteristic, value):
        message = {
            "method": "SET",
            "name": name,
            "characteristic": characteristic,
            "value": value
        }
        return message

    def flash(self, infrared_code):
        LOGGER.debug(f"STR: {infrared_code}")

        if infrared_code is None:
            LOGGER.warn(f"Not found any infrared codes")

        send_command_line = f"{SEND_INFRARED_COMMAND} {infrared_code}"
        LOGGER.info(f"Infrared: {send_command_line}")
        if self.__dryrun:
            return

        send_command = send_command_line.split()
        process = subprocess.run(send_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if process.returncode != 0:
            LOGGER.error(f"command line: {send_command}")
            LOGGER.error(f"error code: {process.returncode}")
            LOGGER.error(f"error message: {process.stdout}")
            process.check_returncode()

        LOGGER.debug(f"END")


if __name__ == "__main__":
    print("IrSensor is an Import Module.")
