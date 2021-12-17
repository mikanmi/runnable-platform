#!/usr/bin/env python3

# Copyright (c) 2020, 2021 Patineboot. All rights reserved.
# HomeRemote software is licensed under BSD 2-Clause license.

import os
import sys
import time
import subprocess
import fcntl
import logging
from logging.handlers import RotatingFileHandler

from device_state import DeviceState


######################
# Advanced Configure #
######################
# The directory of homeremote stored.
SCRIPT_DIRECTORY = os.path.dirname(__file__)

# The paths to infrared HAT tool.
CGIRTOOL: str = "/var/opt/cgir/cgirtool.py send"
IRCONTROL: str = "/var/opt/adrsirlib/ircontrol send"

# infrared codes json file.
CGIRTOOL_CODE_JSON = os.path.join(SCRIPT_DIRECTORY, "codes.json")

LOGGER = logging.getLogger(__name__)

#####################
#     Configure     #
#####################
# The command of Infrared sending
SEND_INFRARED_COMMAND: str = CGIRTOOL + " -c " + CGIRTOOL_CODE_JSON

# Log Settings
LOGGER_LOG_LEVEL = logging.INFO
LOGGER_LOG_FILENAME = os.path.join(SCRIPT_DIRECTORY, "homeremote.log")

# The persistent state file of devices.
STATE_FILE = os.path.join(SCRIPT_DIRECTORY, "device_state.json")

# The lock file for semaphore.
LOCK_FILE = os.path.join(SCRIPT_DIRECTORY, "infrared_device.lock")

# Read config.json for the default value if getting a value not to set yet.
# config.json contains "platforms" attribute.
# "platforms" contains "platform" attribute with "Cmd4" value, like as "platform": "Cmd4".
# See more infomation, read config.json.
CONFIG_JSON_FILE = os.path.join(SCRIPT_DIRECTORY, "config.json")


class InfraredDevice:
    """Infrared Device class.

    This class has the following features.
    - Send infrared codes to Home Electronics.
    - Get a state of Home Electronics.
    """

    @classmethod
    def initialize(cls):
        DeviceState.initialize(LOGGER, CONFIG_JSON_FILE)

    def __init__(self, state_file, device_name):
        """Create a infrared device specified ``state_file`` and ``device_name``.
        Args:
            state_file: The name of state file.
            device_name: The name of device.
        """
        super().__init__()
        LOGGER.debug(f"STR: {state_file}, {device_name}")
        self.__device = DeviceState(state_file, device_name)
        LOGGER.debug(f"END")

    def set(self, interaction, level):
        """ Send a infrared code made of ``interaction``, ``level``
        Args:
            interaction: The action of Home Electronics.
            level: The level of ``interaction``
        """
        LOGGER.debug(f"STR: {interaction}, {level}")

        # ``level`` of ``interaction`` is already set to Infrared Device.
        previous_level = self.__device.get_value(interaction)
        if level == previous_level:
            return

        infrared_code = self.__choose_infrared_code(interaction, level)

        if infrared_code is not None:
            self.__send(infrared_code)

        # store state as value of attribute
        self.__device.set_value(interaction, level)

        LOGGER.debug(f"END")

    def get(self, interaction):
        """Get the level of the specified interaction.
        """
        return self.__device.get_value(interaction)

    def save(self):
        """Save the device state into persistent memory.
        """
        self.__device.save()

    def __send(self, infrared_code):
        LOGGER.debug(f"STR: {infrared_code}")

        send_command_line = f"{SEND_INFRARED_COMMAND} {infrared_code}"

        send_command = send_command_line.split()
        process = subprocess.run(send_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if process.returncode != 0:
            LOGGER.error(f"command line: {send_command}")
            LOGGER.error(f"error code: {process.returncode}")
            LOGGER.error(f"error message: {process.stdout}")
            process.check_returncode()
        LOGGER.info(f"Command rc: {process.returncode} cl: {send_command_line}")

        # sleep for 300ms
        time.sleep(0.300)

        LOGGER.debug(f"END")

    def __choose_infrared_code(self, interaction, level):
        """ Choose the infrared code name to build a command line.
        Args:
            interaction: is an action of Home Electronics
                which is bound for user interaction on Home app on iOS.
                The first charactor of the name is LOWERCASE
                due to a bug of Homebridge or CMD4.
            level: is a level of ``interaction`` parameter.
        Returns:
            str: The name of infrared code
        """
        LOGGER.debug(f"STR: {interaction}, {level}")

        choose_code: classmethod
        device_name = self.__device.get_name()

        if device_name == "BrightLight":
            choose_code = self.__choose_infrared_brightlight
        elif device_name == "DimLight":
            choose_code = self.__choose_infrared_dimlight
        elif device_name == "AirConditioner":
            choose_code = self.__choose_infrared_aircon

        infrared_code = choose_code(interaction, level)

        LOGGER.debug(f"STR: {infrared_code}")
        return infrared_code

    def __choose_infrared_brightlight(self, interaction, level):
        LOGGER.debug(f"STR: {interaction}, {level}")
        result = self.__choose_infrared_light_common(interaction, level, "brightlight")
        LOGGER.debug(f"STR: {result}")
        return result

    def __choose_infrared_dimlight(self, interaction, level):
        LOGGER.debug(f"STR: {interaction}, {level}")
        result = self.__choose_infrared_light_common(interaction, level, "dimlight")
        LOGGER.debug(f"STR: {result}")
        return result

    def __choose_infrared_light_common(self, interaction, level, name_prefix):
        LOGGER.debug(f"STR: {interaction}, {level}, {name_prefix}")

        # The special code to fix a bug of Homebridge.
        # Not clear Homebridge passing the *CASE* of name of attributes and values.
        # I must compare attributes on UPPERCASE.
        interaction: str = interaction.upper()

        if interaction != "ON" and interaction != "BRIGHTNESS":
            return

        infrared_bright = None
        on: str
        brightness_str: str

        # Get values of on and brightness attributes
        if interaction == "ON":
            on = level
            brightness_str = self.__device.get_value("brightness")
        elif interaction == "BRIGHTNESS":
            on = self.__device.get_value("on")
            brightness_str = level

        # The special code to fix a bug of Homebridge.
        # Not clear Homebridge passing the *CASE* of values.
        # I must compare attributes on UPPERCASE.
        on = on.upper()
        brightness = int(brightness_str)

        # On interaction is false
        if on == "FALSE":
            infrared_bright = name_prefix + "_off"
        # On interaction is true
        elif on == "TRUE":
            # choose infrared name on Brightness.
            # Brightness 100%.
            if brightness == 100:
                infrared_bright = name_prefix + "_full"
            # Brightness 0%.
            elif brightness == 0:
                infrared_bright = name_prefix + "_off"
            # Brightness <= 20%.
            elif brightness <= 20:
                infrared_bright = name_prefix + "_night"
            # 20% < Brightness < 100%
            else:
                infrared_bright = name_prefix + "_preference"

        LOGGER.debug(f"END: {infrared_bright}")
        return infrared_bright

    def __choose_infrared_aircon(self, interaction, level):
        LOGGER.debug(f"STR: {interaction}, {level}")

        # The special code to fix a bug of Homebridge.
        # Not clear Homebridge passing the *CASE* of name of attributes and values.
        # I must compare attributes on UPPERCASE.
        interaction = interaction.upper()

        if interaction != "ACTIVE" and interaction != "TARGETHEATERCOOLERSTATE":
            return

        infrared_aircon = None
        active: str
        heater_cooler_state: str

        # Get values of on and brightness attributes
        if interaction == "ACTIVE":
            active = level
            heater_cooler_state = self.__device.get_value("targetHeaterCoolerState")
        elif interaction == "TARGETHEATERCOOLERSTATE":
            active = self.__device.get_value("active")
            heater_cooler_state = level

        # The special code to fix a bug of Homebridge.
        # Not clear Homebridge passing the *CASE* of values.
        # I must compare attributes on UPPERCASE.
        active = active.upper()
        heater_cooler_state = heater_cooler_state.upper()

        # INACTIVE
        if active == "INACTIVE":
            infrared_aircon = "aircon_off"
        # ACTIVE
        elif active == "ACTIVE":
            # AUTO, if INACTIVE or IDLE comes, perhaps Homebridge has some bugs.
            if heater_cooler_state == "AUTO":
                infrared_aircon = "aircon_dehumidify-auto-auto"
            # HEAT
            elif heater_cooler_state == "HEAT":
                infrared_aircon = "aircon_warm-22-auto"
            # COOL
            elif heater_cooler_state == "COOL":
                infrared_aircon = "aircon_cool-26-auto"

        LOGGER.debug(f"STR: {infrared_aircon}")
        return infrared_aircon


def start_process(value):
    LOGGER.debug(f"STR: {value}")

    LOGGER.info(f"Launched with: {value}")

    InfraredDevice.initialize()

    # Depend on adrsirlib and the specification required on state_cmd of homebridge-cmd4.
    # calling ./ircontrol contained in adrsirlib, see more comments on send_infrared_data().

    # value[1]: is "Set" or "Get".
    # value[2]: is value of "displayName" attribute. It is NOT "name" attribute.
    #           "displayName" is attribute name on config.json in homebridge.
    #           homebridge-cmd4 use "displayName" in wrong.
    # value[3]: is name of attribute which is bound to user interaction.
    #           First charactor of the name is UPPERCASE.
    #           Homebridge converts the character to uppercase in wrong.
    # value[4]: is value of value[3] attribute if value[1] is "Set", otherwise nothing.
    method: str = value[1]
    device: str = value[2]

    # Note:
    # Homebridge has a bug that the first character is Uppercase.
    # We must add special code to fix the bug of Homebridge.
    # Notice: Some attributes has uppercase at first character really.
    interaction = value[3][0].lower() + value[3][1:]

    infrared_device = InfraredDevice(STATE_FILE, device)
    print_value: str

    if method == "Set":
        level: str = value[4]

        infrared_device.set(interaction, level)

        print_value = "0"

    elif method == "Get":
        # put the level of interaction to stdout
        # Cmd4 retrieves the level from stdout
        print_value = infrared_device.get(interaction)

    # save state in persistent storage.
    infrared_device.save()

    # Cmd4 strangely gets the result from stdout instead of return code.
    # So, print a result to stdout.
    print(print_value)
    LOGGER.info(f"Result value: {print_value}")
    LOGGER.debug(f"END")


if __name__ == "__main__":
    # Initialize logger
    LOGGER.setLevel(LOGGER_LOG_LEVEL)
    format = logging.Formatter("[%(asctime)s][%(levelname)-5.5s][%(name)s]%(filename)s:%(lineno)d %(funcName)s: %(message)s")

    logfile_handler = RotatingFileHandler(LOGGER_LOG_FILENAME, maxBytes=(1048576 * 5), backupCount=2)
    logfile_handler.setFormatter(format)
    LOGGER.addHandler(logfile_handler)

    LOGGER.debug(f"LOG START")

    # for debug
    if False:
        LOGGER.info(f"Start with: {sys.argv}")

    with open(LOCK_FILE, "r") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            start_process(sys.argv)
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
