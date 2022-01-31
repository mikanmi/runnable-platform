#!/usr/bin/env python3

# Copyright (c) 2020, 2021, 2022, Patineboot. All rights reserved.
# InfraredRunnable is licensed under CC BY-NC-ND 4.0.

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
import subprocess
import json

from threading import Thread

######################
#      Configure     #
######################
# The infrared HAT tools and commands.
# CGIRTOOL: Final[str] = "/var/opt/cgir/cgirtool.py send"
# IRCONTROL: Final[str] = "/var/opt/adrsirlib/ircontrol send"
CGIRTOOL = "/var/opt/cgir/cgirtool.py send"
IRCONTROL = "/var/opt/adrsirlib/ircontrol send"


# CGIRTOOL configure
# the directory which contains infraredRunnable.py.
# SCRIPT_DIRECTORY: Final[str] = os.path.dirname(__file__)
# infrared codes json file.
# CGIRTOOL_CODE_JSON: Final[str] = os.path.join(SCRIPT_DIRECTORY, "codes.json")
# The command of Infrared sending
# SEND_INFRARED_COMMAND: str = CGIRTOOL + " -c " + CGIRTOOL_CODE_JSON

SCRIPT_DIRECTORY = os.path.dirname(__file__)
CGIRTOOL_CODE_JSON = os.path.join(SCRIPT_DIRECTORY, "codes.json")
SEND_INFRARED_COMMAND = CGIRTOOL + " -c " + CGIRTOOL_CODE_JSON

######################
#    Script Code     #
######################
LOGGER = None


class InfraredRunnable:
    """InfraredRunnable class.

    The InfraredRunnable class sends some infrared codes to home devices.
    - Send the infrared codes pre-registered with an infrared HAT.
    """

    def __init__(self, logger, dryrun):
        """Create a infrared home device specified ``state_file`` and ``device_name``.
        Args:
            state_file: The name of the state file.
            device_name: The name of the infrared home device.
        """
        super().__init__()
        global LOGGER
        LOGGER = logger

        LOGGER.debug(f"STR")

        self.__dryrun = dryrun

        LOGGER.debug(f"END")

    def run(self):
        LOGGER.debug(f"STR")

        def loop():
            LOGGER.debug(f"STR")
            for line in sys.stdin:
                LOGGER.info(f"received: {line.strip()}")
                self.__handle(line)
            LOGGER.debug(f"END")

        thread = Thread(target=loop)
        thread.start()

        # wait for closing stdin
        thread.join()

        LOGGER.debug(f"END")

    def __handle(self, line):
        message = json.loads(line)

        if message["method"] != "SET":
            return

        # the prefix names of Lightbulb
        lightbulb_name = {
            "BrightLight": "brightlight",
            "DimLight": "dimlight",
        }

        heatercooler_name = [
            "AirConditioner",
        ]

        humidifierdehumidifier_name = [
            "SIRENE",
        ]

        device_name = message["name"]
        if device_name in lightbulb_name:
            self.__handle_lightbulb(message, lightbulb_name)
        elif device_name in heatercooler_name:
            self.__handle_heatercooler(message)
        elif device_name in humidifierdehumidifier_name:
            self.__handle_humidifierdehumidifier(message)

    def __handle_lightbulb(self, message, lightbulb_name):
        LOGGER.debug(f"STR: {message}, {lightbulb_name}")

        prefix = lightbulb_name[message["name"]]

        # chaneg the device state to the status.
        state = {
            "On": message["status"]["On"],
            "Brightness": message["status"]["Brightness"],
        }
        state[message["characteristic"]] = message["value"]

        infrared = self.__select_lightbulb_code(state, prefix)
        self.__flash(infrared)

    def __select_lightbulb_code(self, state, prefix):
        LOGGER.debug(f"STR: {state} {prefix}")

        # select an infrared code with the 'On' and 'Brightness' attributes.
        selected_code = None

        on = state["On"]
        brightness = state["Brightness"]

        # the 'On' element
        if on:
            # the 'Brightness' element.
            # 100% Brightness.
            if brightness == 100:
                selected_code = prefix + "_full"
            # 0% Brightness.
            elif brightness == 0:
                selected_code = prefix + "_off"
            # Brightness less than 20%.
            elif brightness <= 20:
                selected_code = prefix + "_night"
            # 20% < Brightness < 100%
            else:
                selected_code = prefix + "_preference"
        else:
            selected_code = prefix + "_off"

        return selected_code

    def __handle_heatercooler(self, message):
        LOGGER.debug(f"STR: {message}")

        # chaneg the device state to the status.
        state = {
            "Active": message["status"]["Active"],
            # "CurrentHeaterCoolerState": message["status"]["CurrentHeaterCoolerState"],
            "TargetHeaterCoolerState": message["status"]["TargetHeaterCoolerState"],
            # "CurrentTemperature": message["status"]["CurrentTemperature"],

            "HeatingThresholdTemperature": message["status"]["HeatingThresholdTemperature"],
        }
        state[message["characteristic"]] = message["value"]

        infrared, current_state, temperature = self.__select_airconditioner_code(state)
        self.__flash(infrared)

        # make the message to send the device status from the receive message
        # update the status in the message
        message["status"][message["characteristic"]] = message["value"]
        # send CurrentHeaterCoolerState due to changing TargetHeaterCoolerState
        message["characteristic"] = "CurrentHeaterCoolerState"
        message["value"] = current_state
        self.send(message)

        # update the status in the message
        message["status"][message["characteristic"]] = message["value"]
        # send CurrentTemperature due to changing TargetHeaterCoolerState
        message["characteristic"] = "CurrentTemperature"
        message["value"] = temperature
        self.send(message)

    def __select_airconditioner_code(self, state):
        LOGGER.debug(f"STR: {state}")

        # select an infrared code with
        # the 'Active' and 'TargetHeaterCoolerState' and HeatingThresholdTemperature attributes.
        selected_code = None
        temperature = 0
        current_state = 0

        active = state["Active"]
        target_heater_cooler_state = state["TargetHeaterCoolerState"]
        heating_threshold_temperature = state["HeatingThresholdTemperature"]

        # the 'Active' element is 'INACTIVE'
        if active == 0:
            selected_code = "aircon_off"
            current_state = 0  # INACTIVE
            temperature = 0
        # the 'Active' element is 'ACTIVE'
        else:
            # 'AUTO' in 'TargetHeaterCoolerState'
            if target_heater_cooler_state == 0:
                selected_code = "aircon_dehumidify-auto-auto"
                current_state = 1  # IDLE
                temperature = 25
            # 'HEAT' in 'TargetHeaterCoolerState'
            elif target_heater_cooler_state == 1:
                current_state = 2  # HEATING
                if heating_threshold_temperature == 25:
                    selected_code = " aircon_warm-26-full-swing"
                    temperature = 25
                else:
                    selected_code = "aircon_warm-22-auto"
                    temperature = 22
            # 'COOL' in 'TargetHeaterCoolerState'
            elif target_heater_cooler_state == 2:
                selected_code = "aircon_cool-26-auto"
                current_state = 3  # COOLING
                temperature = 26

        LOGGER.debug(f"END: {selected_code}, {current_state}, {temperature}")
        return selected_code, current_state, temperature

    def __handle_humidifierdehumidifier(self, message):
        LOGGER.debug(f"STR: {message}")

        active_status = message["status"]["Active"]

        # chaneg the device state to the status.
        state = {
            "Active": message["status"]["Active"],
            "TargetHumidifierDehumidifierState": message["status"]["TargetHumidifierDehumidifierState"],
            "RelativeHumidityHumidifierThreshold": message["status"]["RelativeHumidityHumidifierThreshold"],
        }
        state[message["characteristic"]] = message["value"]

        infrareds, current_state, current_humidity = \
            self.__select_humidifierdehumidifier_code(state, active_status)

        for infrared in infrareds:
            self.__flash(infrared)

        # make the message to send the device status from the receive message
        # update the status in the message
        message["status"][message["characteristic"]] = message["value"]
        # send CurrentHumidifierDehumidifierState due to TargetHumidifierDehumidifierState
        message["characteristic"] = "CurrentHumidifierDehumidifierState"
        message["value"] = current_state
        self.send(message)

        # update the status in the message
        message["status"][message["characteristic"]] = message["value"]
        # send CurrentRelativeHumidity
        message["characteristic"] = "CurrentRelativeHumidity"
        message["value"] = current_humidity
        self.send(message)

    def __select_humidifierdehumidifier_code(self, state, active_status):
        LOGGER.debug(f"STR: {state}")

        # select an infrared code with the 'Active' and 'TargetHumidifierDehumidifierState' attributes.
        selected_code = []
        current_state = 0
        current_humidity = 0

        active = state["Active"]
        target_humidifier_dehumidifier_state = state["TargetHumidifierDehumidifierState"]
        relative_humidity_humidifier_threshold = state["RelativeHumidityHumidifierThreshold"]

        # toggle the power switch
        if active != active_status:
            selected_code.append("sirene_off")
            current_state = active  # ACTIVE or INACTIVE
            current_humidity = 0

        # the 'Active' element is 'ACTIVE'
        if active == 1:
            # AUTO or HUMIDIFIER_OR_DEHUMIDIFIER
            if target_humidifier_dehumidifier_state == 0:
                selected_code.append("sirene_auto")
                current_state = 2  # HUMIDIFYING
                current_humidity = 0
            # HUMIDIFIER
            elif target_humidifier_dehumidifier_state == 1:
                current_state = 2  # HUMIDIFYING
                current_humidity = 0
                if relative_humidity_humidifier_threshold < 34:
                    selected_code.append("sirene_minus")
                    selected_code.append("sirene_minus")
                elif relative_humidity_humidifier_threshold < 67:
                    selected_code.append("sirene_minus")
                    selected_code.append("sirene_minus")
                    selected_code.append("sirene_plus")
                else:
                    selected_code.append("sirene_plus")
                    selected_code.append("sirene_plus")
            # DEHUMIDIFIER
            elif target_humidifier_dehumidifier_state == 2:
                # nothing to do
                LOGGER.warn(f"SIRENE does not have the DEHUMIDIFIER feature")

        LOGGER.debug(f"END: {selected_code}, {current_state}, {current_humidity}")
        return selected_code, current_state, current_humidity

    def __flash(self, infrared_code):
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

    def send(self, message):
        text = json.dumps(message)
        LOGGER.info(f"send: {text}")
        sys.stdout.write(text + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    print("InfraredRunnable is an Import Module.")
