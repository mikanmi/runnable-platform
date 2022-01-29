# RunnablePlatform

[RPZ-IR-Sensor]: https://www.indoorcorgielec.com/products/rpz-ir-sensor/
[cgir]: https://github.com/IndoorCorgi/cgir
[ADRSIR]: https://bit-trade-one.co.jp/product/module/adrsir/
[adrsirlib]: https://github.com/tokieng/adrsirlib
[Homebridges-cmd4]: https://github.com/ztalbot2000/homebridge-cmd4
[Homebridge-Service-Type]: https://developers.homebridge.io/#/service

RunnablePlatform is a software program to provide connections using your Custom-Command command between infrared devices and Homebridge.

My Custom-Command, InfraredRunnable, sends infrared codes to connect two LightBulb devices and a HeaterCooler device with the Homebridge service.

You can enjoy controlling your infrared home devices, a ceiling light, an air conditioner, or more joyful devices on Apple Home app on iPhone or Siri, using RunnablePlatform and your Custom-Command.

## Feature

RunnablePlatform supports:

- All [Service Types][Homebridge-Service-Type] of Homebridge.
- All Characteristics of [Service Types][Homebridge-Service-Type] on Homebridge.

e.g., LightBulb, Heater Cooler, Humidifier Dehumidifier, Humidity Sensor, Light Sensor, Temperature Sensor, or all sort of [Homebridge API Service Types][Homebridge-Service-Type] with all Characteristics.

## Install

Search patineboot's RunnablePlatform with the 'Homebridge RunnablePlatform' words on npm or Homebridge.

Install RunnablePlatform you found on npm or Homebridge.

## Usage

### Config the config.json file of Homebridge

The example of a part of RunnablePlatform on config.json.

```bash
{
    "platform": "RunnablePlatform",
    "name": "RunnablePlatform",
    "run": "/var/opt/infrared-runnable/runnable.py",
    "time": 300,
    "accessories": [
        {
            "name": "DimLight",
            "service": "Lightbulb",
            "characteristics": [
                "On",
                "Brightness"
            ]
        },
    ]
}
```

The RunnablePlatform platform element.
|Attribute|Type|Description|
|-|-|-|
|platform|string|Set "_RunnablePlatform_" only.|
|name|string|Set "_RunnablePlatform_" only.|
|run|string|Input the absolute path of your Custom-Command to control the accessories.|
|time|number|Input the millisecond time to finish handling a message on the Custom-Command.|
|accessories|array of any type|See the following:|

The accessories element of RunnablePlatform.
|Attribute|Type|Description|
|-|-|-|
|name|string|The name of an infrared home device.|
|service|string|The service type of the infrared home device.|
|characteristics|array of string|The characteristics of the service.|

Refer to Homebridge Service Types:

- [Service Types][Homebridge-Service-Type]: <https://developers.homebridge.io/#/service>

Get service and characteristics, e.g., Heater Cooler:

1. Visit [Heater Cooler](https://developers.homebridge.io/#/service/HeaterCooler)
2. Find the service name of Heater Cooler on the Example code.
   Get the service name, **HeaterCooler**, from the 'this.Service.HeaterCooler' code snippet.

   ```bash
   // create a new Heater Cooler service
   this.service = new this.Service(this.Service.HeaterCooler);
   ```

3. Get the Characteristics
   1. Find 'Required Characteristics' and 'Optional Characteristics.'
   1. Click the Active link to Characteristic.
   1. Get the name, **Active**, from the 'Characteristic.Active' on the Name item.

## Program the Custom-Command

RunnablePlatform communicates with Custom-Command through the standard input and output.

Custom-Command has the features:

- Send an infrared code to your infrared home device
- Communicate the JSON messages to RunnablePlatform.

The JSON message format:
|Attribute|Type|Description|
|-|-|-|
|method|string|Set '_SET_' only.|
|name|string|The name which you describe your infrared home device on _config.json_.|
|characteristic|string|The request that the receiver changes the characteristic.|
|value|string|The changed value of the characteristic.|
|status|array of any|The current characteristics of your infrared home device.|

e.g., the _SET_ message that RunnablePlatform turns on the '_Your Light_' Lightbulb.

_RunnablePlatform_ **--[JSON message]->** _Custom-Command_

```json
{
    "method": "SET",
    "name": "Your Light",
    "characteristic": "On",
    "value": true,
    "status" {
        "On": false,
        "Brightness": 100,
        "ColorTemperature": 500,
        "Hue": 360,
        "Saturation": 100
    }
}
```

e.g., the _SET_ message that the '_Your AirConditioner_' HeaterCooler notifies the current temperature.

_Custom-Command_ **--[JSON message]-->** _RunnablePlatform_

```json
{
    "method": "SET",
    "name": "Your AirConditioner",
    "characteristic": "CurrentTemperature",
    "value": 20,
}
```

## My Custom-Command, InfraredRunnable

### Support Raspberry Pi HATs

- [RPZ-IR-Sensor][RPZ-IR-Sensor] with '[cgir][cgir]' is a good product.
- [ADRSIR][ADRSIR] with [adrsirlib][adrsirlib] has some problems that it fails to send an infrared code to the device on long distances.

I strongly recommend [RPZ-IR-Sensor][RPZ-IR-Sensor] to send infrared codes because of my good experience.

### Change Raspberry Pi HATs

Change *SEND_INFRARED_COMMAND* variable to a command sending an infrared code.

```python
# the default is to use RPZ-IR-Sensor
SEND_INFRARED_COMMAND: str = CGIRTOOL + " -c " + CGIRTOOL_CODE_JSON
```

RPZ-IR-Sensor is available on *SEND_INFRARED_COMMAND* default.

|Recommend|Command|Description
|:----------|:-----------|:------------
|YES|`CGIRTOOL`|Send command that `cgirtool.py` contained in 'cgir' with _send_ followed.
||`IRCONTROL`|Send command that `ircontrol` contained in adrsirlib with _send_ followed.

## Misc

InfraredRunnable involves some useful files:

- *codes.json*  
  involves some infrared codes of 'cgir.'

- *example.install_runnable.sh*  
  installs InfraredRunnable on Ubuntu.  
  Run the install script after changing masked as `XXX` to your sensitive information of the devices or some.

Homebridge UI provides Swagger:

- Swagger URL  
  http:// [homebrdige domain or IP] /swagger

- The cached accessories URL  
  We get the current state of 'the cached accessories' on  
  http:// [homebrdige domain or IP] /swagger/static/index.html#/Homebridge/ServerController_getCachedAccessories

### Ideas of RunnablePlatform feature

I may or not add the RESTful API to RunnablePlatform.

- RESTfulAPI  
  - GET - get the state of RunnablePlatform accessory on the Homebridge.
  - POST - notify the state to the Homebridge  
    Memo: We already get 'the cached accessories' with Swagger on Homebridge.

- Web socket  
  RunnablePlatform sends the state to change by user interaction on Apple Home app or Siri.

RunnablePlatform supports of updating the properties for some characteristics in  future.

```json
{
"method": "PROPERTY",
"name": "My Temperature",
"characteristic": "TargetTemperature",
"properties": [
    "minValue": "18",
    "maxValue": "30",
    "minStep": "1"
]
}
```

## Thanks

[@IndoorCorgi](https://github.com/IndoorCorgi)

They created a nice Raspberry Pi HAT, [RPZ-IR-Sensor][RPZ-IR-Sensor], and a good tool, '[cgir][cgir].'

@IndoorCorgi's '[cgir][cgir]': <https://github.com/IndoorCorgi/cgir>


## No Thanks

[Bit Trade One, LTD.](https://bit-trade-one.co.jp) (ADRSIR design, manufacturing, and sales) provides **NO** supports and the **USELESS** scripts. Bit Trade One is bad and poor from two facts.

## Environment

RunnablePlatform is running as Homebridge Plugin.

My Custom-Command, InfraredRunnable, is running but not limited:

- Raspberry Pi OS: GNU/Linux 10 (buster) 10.11
- Python: 3.7.3
- cgir: trunk on the main branch

## Publish RunnablePlatform on NPM

1. Login

   ```bash
   npm login
   ```

   npm asks

   ```bash
   Username: patine
   Password: <your password>
   Email: (this IS public) <your email address>
   Enter one-time password: <one time password on received email>
   ```

1. Publish

   ```bash
   npm publish
   ```

1. Logout

   ```bash
   npm logout
   ```
