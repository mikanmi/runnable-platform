# HomeRemote Software

[RPZ-IR-Sensor]: https://www.indoorcorgielec.com/products/rpz-ir-sensor/
[cgir]: https://github.com/patineboot/cgir
[ADRSIR]: https://bit-trade-one.co.jp/product/module/adrsir/
[adrsirlib]: https://github.com/tokieng/adrsirlib
[Homebridges-cmd4]: https://github.com/ztalbot2000/homebridge-cmd4

HomeRemote is a smart infrared remote controller.

You can enjoy to control many infrared home devices and use Siri with Homebridge and Cmd4.

I strongly recommend [RPZ-IR-Sensor][RPZ-IR-Sensor] from Raspberry Pi HATs to send an infrared code.

## Support Raspberry Pi HATs

- [RPZ-IR-Sensor][RPZ-IR-Sensor] with [cgir][cgir] is the good product.
- [ADRSIR][ADRSIR] with [adrsirlib][adrsirlib] has some problems that it fails to send an infrared code to the device on long distances.

## HomeRemote Features

HomeRemote controls the infrared home devices.

- Send an infrared code to the infrared home device.
- Set the state of the infrared home device.
- Get the state of the infrared home device.
- Choose an infrared code from the infrared codes registered in HomeRemote.

## Usage

HomeRemote works well with Homebridge and [Homebridge-Cmd4][Homebridges-cmd4].

HomeRemote controls the infrared home device via voice through Siri on HomePod.

I explain _config.json_ and *infrared_device.py* of HomeRemote.

### General Usage

Describe _config.json_ contained in Homebridge.

You add *infrared_device.py* of the absolute path to the **state_cmd** attribute.

The example for _config.json_:

```javascript:config.json
{
    "state_cmd": "/var/opt/homeremote/infrared_device.py"
}
```

## Port HomeRemote to your environment

1. Describe your infrared home devices into _config.json_.
1. Configure and port *infrared_device.py* to your environment.

## config.json

Add your infrared home devices to _config.json_:

```javascript:config.json
{
    "type": "HeaterCooler",
    "displayName": "AirConditioner",
    "name": "AirConditioner",
    "temperatureDisplayUnits": "CELSIUS",
    "active": "INACTIVE",
    "currentHeaterCoolerState": "INACTIVE",
    "targetHeaterCoolerState": "AUTO",
    "currentTemperature": 20,
    "coolingThresholdTemperature": 35,
    "heatingThresholdTemperature": 25,
    "Manufacturer": "MITSUBISHI",
    "Model": "Cmd4 model",
    "SerialNumber": "Patineboot",
    "stateChangeResponseTime": 1,
    "state_cmd": "/var/opt/homeremote/infrared_device.py"
}
```

## infrared_device.py

### Configuration

Change *SEND_INFRARED_COMMAND* variable to a command sending an infrared code.

```python:infrared_device.py
# The command of Infrared sending
SEND_INFRARED_COMMAND: str = CGIRTOOL + " -c " + CGIRTOOL_CODE_JSON
```

The command for RPZ-IR-Sensor is available to set *SEND_INFRARED_COMMAND*.

|Recommend|Command|Description
|:----------|:-----------|:------------
|YES|CGIRTOOL|Send command that `cgirtool.py` contained in cgir with `send` followed.
||IRCONTROL|Send command that `ircontrol` contained in adrsirlib with `send` followed.

### Porting

You must rewrite the implementation of the *__choose_infrared_code* function.

**Function Signature:**

```python:infrared_device.py
    def __choose_infrared_code(self, interaction, level):
        """ Choose the infrared code name to build a command line.
        Args:
            interaction: is an action of the infrared home device.
                which is bound for the user interaction on Home app on iOS.
                The first character of the name is LOWERCASE
            level: is a level of the ``interaction`` parameter.
        Returns:
            str: The name of the infrared code.
        """
```

### Implementation

You should implement the following behavior for your preference and environment:

1. You can get the current state of the infrared home device by calling the *self.__device.get_value()* method with interaction (same as the name of the attribute on *config.json*).

1. Choose the infrared code with the parameters *self*, *interaction*, and *level*.

1. Return the infrared code.

HomeRemote will send the infrared code and change the *interaction* state to the *level* level.

*e.g.) __choose_infrared_aircon(self, interaction, level)* function:

```python:infrared_device.py
        LOGGER.debug(f"STR: {interaction}, {level}")

        # The special code to fix a bug of Homebridge or CMD4.
        # Not clear Homebridge passing the *CASE* of the names of the attributes and the values.
        # I must compare the attribute on UPPERCASE.
        interaction = interaction.upper()

        if interaction != "ACTIVE" and interaction != "TARGETHEATERCOOLERSTATE":
            return

        infrared_aircon = None
        active: str
        heater_cooler_state: str

        # Get the value of the 'on' and the 'brightness' attributes
        if interaction == "ACTIVE":
            active = level
            heater_cooler_state = self.__device.get_value("targetHeaterCoolerState")
        elif interaction == "TARGETHEATERCOOLERSTATE":
            active = self.__device.get_value("active")
            heater_cooler_state = level

        # The special code to fix a bug of Homebridge or CMD4.
        # Not clear Homebridge passing the *CASE* of the names of the attributes and the values.
        # I must compare the attribute on UPPERCASE.
        active = active.upper()
        heater_cooler_state = heater_cooler_state.upper()

        # INACTIVE
        if active == "INACTIVE":
            infrared_aircon = "aircon_off"
        # ACTIVE
        elif active == "ACTIVE":
            # AUTO, if INACTIVE or IDLE comes, perhaps Homebridge or CMD4 have some bugs.
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
```

## Misc

I explain the useful files included in HomeRemote.

- codes.json  
  Some infrared codes of cgir.
- example.install_homeremote.sh  
  The install script contains that the replacement process of the sensitive information.  
  Run the install script after changing sensitive information (as `XXX`) to your information of the devices.

## Thanks

### @IndoorCorgi

@IndoorCorgi developed [RPZ-IR-Sensor][RPZ-IR-Sensor] and [cgir][cgir].

They have done great work on hardware and software.

[Their GitHub page is here.][cgir]

### @ztalbot2000

@ztalbot2000 provides us better homebridge plugin, Homebridges-cmd4.

I hope that he provides documentations and examples of Homebridges-cmd4 more.

[ztalbot2000's GitHub page is here.][Homebridges-cmd4]

## No Thanks

[Bit Trade One, LTD.(ADRSIR design, manufacturing and sales)](https://bit-trade-one.co.jp) provides USELESS scripts and NO support.

## Environment

HomeRemote is running but not limited with the following.

- Raspberry Pi OS: GNU/Linux 10 (buster) 10.11
- Python: 3.7.3
- cgir: trunk on main branch
- HomeRemote: trunk on main branch
- Node.js: 16.13.1
- Homebridge: 1.3.9
  - Homebridge UI: 4.41.5
  - Homebridge Cmd4: 4.0.1
  - Homebridge Hue: 0.13.32
  - Homebridge Dyson Link: 2.5.6
