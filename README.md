# HomeRemote Software

[RPZ-IR-Sensor]: https://www.indoorcorgielec.com/products/rpz-ir-sensor/
[cgir]: https://github.com/patineboot/cgir
[ADRSIR]: https://bit-trade-one.co.jp/product/module/adrsir/
[adrsirlib]: https://github.com/tokieng/adrsirlib
[Homebridges-cmd4]: https://github.com/ztalbot2000/homebridge-cmd4

HomeRemote is a smart infrared remote controller.

You can enjoy to control many Home Electronics and use Siri with Homebridge and Cmd4.

I strongly recommend [RPZ-IR-Sensor] from Raspberry Pi HATs to send infrared code.

## Support Raspberry Pi HATs

- [RPZ-IR-Sensor][RPZ-IR-Sensor] with [cgir][cgir] is the great product.
- [ADRSIR][ADRSIR] with [adrsirlib][adrsirlib] has problems with frequently failing to send infrared codes and furthermore lack to send them to sufficient distance.

## HomeRemote Features

HomeRemote controls infrared devices.

- Send infrared codes to Home Electronics.
- Get a state of Home Electronics.
- Choose a infrared code from infrared codes registered in infrared devices.

## Usage

HomeRemote works well with Homebridge and [Homebridge-Cmd4][Homebridges-cmd4].

HomeRemote controls Home Electronics via voice through Siri on HomePod.

I explain config.json infrared_device.py of HomeRemote.

### General Usage

Describe `config.json` contained in Homebridge.

You add `infrared_device.py` of absolute path to **state_cmd** attribute.

An example for `config.json`:

**e.g.**

```javascript:config.json
{
    "state_cmd": "/var/opt/homeremote/infrared_device.py"
}
```

## Port HomeRemote to your environment

1. Describe `config.json` of your preference.
1. Configure and port `infrared_device.py` to your environment.

The present files both are for my environment and preference.

## config.json

Add your Home Electronics joining your Home Network.

**e.g.**

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

Change `SEND_INFRARED_COMMAND` variable to a command that sends infrared codes.

```python:infrared_device.py
# The command of Infrared sending
SEND_INFRARED_COMMAND: str = CGIRTOOL + " -c " + CGIRTOOL_CODE_JSON
```

Commands to infrared HAT tools are available to set `SEND_INFRARED_COMMAND`.

|Recommend|Command|Description
|:----------|:-----------|:------------
|YES|CGIRTOOL|Send command that `cgirtool.py` contained in cgir with `send` followed.
||IRCONTROL|Send command that `ircontrol` contained in adrsirlib with `send` followed.

### Porting

I require that your code conforms the following function signature.

You will rewrite implementation of this function. The present implementation is for my environment.

**Function Signature:**

```python:infrared_device.py
class InfraredDevice:
    def __choose_infrared_code(self, interaction, level)
        """ Choose the infrared code name to build a command line.
        Args:
            interaction: is an action of Home Electronics
                which is bound for user interaction on Home app on iOS.
                The first character of the name is LOWERCASE
                due to a bug of Homebridge or CMD4.
            level: is a level of ``interaction`` parameter.
        Returns:
            str: The name of infrared code
        """
```

**Function Specification:**

Choose the infrared code name to build a command line.

|Parameter|Description
|:----------|:-----------
|`self (InfraredDevice)`|is an instance of InfraredDevice class which contains current state of Home Electronics.
|`interaction (str)`|is an action of Home Electronics which is bound for user interaction on Home app on iOS.<br>The first character of the name is LOWERCASE due to a bug of Homebridge or CMD4.
|`level (Any)`|is a level of `interaction` parameter.

**Function Return:**

`Return (str)`: The name of infrared code.

### Implementation

You should implement the following behavior for your preference and environment:

1. Choose the infrared data code by parameters `self`, `interaction` and `level`.  
  You can get the current device state from calling self.__device.get_value() method with interaction(same as the name of the attribute).

1. Return the infrared data code.

HomeRemote will send the infrared code and change `interaction` to `level`.

**`e.g.) __choose_infrared_aircon(self, interaction, level)` function**

```python:infrared_device.py
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
        if heater_cooler_state == "AUTO" or \
                heater_cooler_state == "INACTIVE" or \
                heater_cooler_state == "IDLE":
            infrared_aircon = "aircon_off"
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

I explain useful files included.

- codes.json  
  Some infrared codes for cgir.
- example.install_homeremote.sh  
  The install script contains replacement process of sensitive information.  
  Run the install script after change dummy-word(as `XXX`) to your real information.

## Thanks

### @IndoorCorgi

@IndoorCorgi developed [RPZ-IR-Sensor][RPZ-IR-Sensor] and [cgir][cgir].

They have done great work on hardware and software.

[Their GitHub page is here.][cgir]

### @tokieng

@tokieng created the python script which great and helpful.

I was happy to find adrsirlib before.

[tokieng's GitHub page is here.][adrsirlib]

### @ztalbot2000

@ztalbot2000 provides us better homebridge plugin, Homebridges-cmd4.

I hope that he provides documentations and examples of Homebridges-cmd4 more.

[ztalbot2000's GitHub page is here.][Homebridges-cmd4]

## No Thanks

[Bit Trade One, LTD.(ADRSIR design, manufacturing and sales)](https://bit-trade-one.co.jp) provides USELESS scripts and NO support.

## Environment

HomeRemote is running but not limited with the followings.

- Python 3.7.3
- Homebridge-Cmd4 3.10.1
- Homebridge 1.3.4
