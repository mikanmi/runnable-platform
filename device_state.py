#!/usr/bin/env python3

# Copyright (c) 2021, Patineboot. All rights reserved.
# homeremote software is licensed under BSD 2-Clause license.

import json
import logging

LOGGER = logging.getLogger(__name__)


class DeviceState:

    @classmethod
    def initialize(cls, logger, config_name):
        """ Initialize this class.
        Args:
            logger: logging by this ``logger``
            config_name: "config.json" with a path
        """
        global LOGGER
        LOGGER = logger

        LOGGER.debug(f"STR: {logger} {config_name}")
        cls.__config_name = config_name
        LOGGER.debug(f"END")

    def __init__(self, state_file, device_name):
        """Create a device state specified ``json_name`` and ``device_name``.
        Args:
            state_file (str): The name of state file.
            device_name (str): The name of device.
        """
        super().__init__()
        LOGGER.debug(f"STR: {state_file}, {device_name}")

        # use state only including device if loading json is failed.
        state = {device_name: {}}

        # load state from the state file.
        # add device dictionary in state dictionary if not exist
        try:
            with open(state_file, mode="r") as state_handle:
                state = json.load(state_handle)

            # add device dictionary if not exist
            state.setdefault(device_name, {})

        except (json.JSONDecodeError, FileNotFoundError) as error:
            LOGGER.info(f"Loading JSON is failed: {error}")

        LOGGER.info(f"Loaded JSON: {state}")

        self.__state = state
        self.__state_file = state_file
        self.__device_name = device_name

        LOGGER.debug(f"END")

    def save(self):
        """Save device state itself into state file
        """
        LOGGER.debug(f"STR")

        with open(self.__state_file, mode="w") as state_handle:
            json.dump(self.__state, state_handle)

        LOGGER.debug(f"END")

    def get_name(self):
        """Get the device name of this instance
        Returns:
            str: The name of this instance
        """
        return self.__device_name

    def get_state(self):
        """Get the state of this instance
        Returns:
            dict: the state of this instance
        """
        return self.__state[self.__device_name]

    def get_value(self, attribute):
        """Get the value of ``attribute`` of this instance.

        Read config.json for the default value if getting a value not to set yet.

        Args:
            attribute (str): The attribute coresponding the value.
        Returns:
            str: The value of ``attribute``
        """
        # Get the initial value from config.json if never before set a value
        if attribute not in self.__state[self.__device_name].keys():
            with open(self.__config_name, mode="r") as config:
                config_values = json.load(config)

            platforms = config_values["platforms"]
            for platform in platforms:
                if "Cmd4" == platform["platform"]:
                    accessories = platform["accessories"]
                    for accessory in accessories:
                        if self.__device_name == accessory["displayName"]:
                            self.__state[self.__device_name][attribute] = accessory[attribute]
                            LOGGER.info(f"Use default value: {attribute}={accessory[attribute]}")

        value = self.__state[self.__device_name][attribute]
        return value

    def set_value(self, attribute, value):
        """Set the ``value`` of ``attribute`` into this instance.
        Args:
            attribute (str): The attribute coresponding the ``value``.
            value (str): The value of ``attribute``.
        """
        LOGGER.debug(f"STR: {attribute} {value}")

        self.__state[self.__device_name][attribute] = value

        # Simulate current state.
        # When set target state, set current state in the same time.
        current_attribute = "currentHeaterCoolerState"
        current_value = None

        if attribute == "active":
            if value == "INACTIVE":
                current_value = "INACTIVE"

        elif attribute == "targetHeaterCoolerState":
            if value == "AUTO":
                current_value = "IDLE"
            elif value == "HEAT":
                current_value = "HEATING"
            elif value == "COOL":
                current_value = "COOLING"

        if current_value is not None:
            self.__state[self.__device_name][current_attribute] = current_value
            LOGGER.info(f"Change current state: {current_attribute}={current_value}")

        LOGGER.debug(f"END")


if __name__ == "__main__":
    print("This module is Import Module.")
