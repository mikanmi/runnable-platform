# RunnablePlatform

[RPZ-IR-Sensor]: https://www.indoorcorgielec.com/products/rpz-ir-sensor/
[IndoorCorgi]: https://github.com/IndoorCorgi
[IndoorCorgi-cgir]: https://github.com/IndoorCorgi/cgir
[IndoorCorgi-cgsensor]: https://github.com/IndoorCorgi/cgsensor
[Homebridge-Service-Type]: https://developers.homebridge.io/#/service

RunnablePlatform is the Homebridge plugin that connects many infrared home devices with Homebridge using Custom-Command.

RunnablePlatform and Custom-Command communicate through Custom-Command’s standard input and output with each other.

My Custom-Command, InfraredRunnable, controls some infrared home devices.

You can enjoy controlling your infrared home devices, a ceiling light, an air conditioner, or more joyful devices on Apple Home app on iPhone or Siri, using RunnablePlatform and your Custom-Command.

![RunnablePlatform shows accessories](https://github.com/patineboot/runnable-platform/blob/main/apple-home-app.png "RunnablePlatform shows accessories")

- Development Webpage: <https://github.com/patineboot/runnable-platform>
- Publishing Webpage: <https://www.npmjs.com/package/homebridge-runnable-platform>

## Feature

RunnablePlatform supports:

- All [Service Types][Homebridge-Service-Type] of Homebridge.
- All Characteristics of [Service Types][Homebridge-Service-Type] on Homebridge.

e.g., My Custom-Command, InfraredRunnable, support LightBulb, Heater Cooler, Humidifier Dehumidifier, Humidity Sensor, Light Sensor, Temperature Sensor. You can create a Custom-Command supports all sorts of [Homebridge API Service Types][Homebridge-Service-Type] with all Characteristics.

## Install

Search **patineboot's** RunnablePlatform with the "RunnablePlatform" word on Homebridge.

Install RunnablePlatform you found on Homebridge.

## Usage

### Config the config.json file of Homebridge

The example of the element of RunnablePlatform on config.json.

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
|run|string|Input the absolute path of the Custom-Command to control the infrared home devices.|
|time|number|Input the millisecond time to finish handling a JSON message on the Custom-Command.|
|accessories|array of any type|See the following accessories element of RunnablePlatform|

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

RunnablePlatform and Custom-Command communicate through Custom-Command’s standard input and output with each other.

Custom-Command should have the two features:

- Send infrared codes to infrared home devices
- Post and Receive a JSON message to RunnablePlatform

The JSON message format on the standard input and output:
|Attribute|Type|Description|
|-|-|-|
|method|string|Set '_SET_' only.|
|name|string|The name of your infrared home device .|
|characteristic|string|The characteristic will change the new value.|
|value|string|The new value of the characteristic.|
|status|array of any|The current characteristics of the device specified with name attribute.|

e.g., the JSON message that RunnablePlatform turns on the '_Your Light_' Lightbulb.

_Custom-Command_'s standard input:  
_RunnablePlatform_ **--[JSON message]->** _Custom-Command_

```json
{
    "method": "SET",
    "name": "Your Light",
    "id": 1,
    "characteristic": "On",
    "value": true,
    "status": {
        "On": false,
        "Brightness": 100,
        "ColorTemperature": 500,
        "Hue": 360,
        "Saturation": 100
    }
}
```

```json
{
    "method": "ACK",
    "name": "Your Light",
    "id": 1,
    "status": {
        "On": true,
        "Brightness": 100,
        "ColorTemperature": 500,
        "Hue": 360,
        "Saturation": 100
    }
}
```

e.g., the JSON message that the '_Your AirConditioner_' HeaterCooler notifies the current temperature.

_Custom-Command_'s standard output:  
_Custom-Command_ **--[JSON message]-->** _RunnablePlatform_

```json
{
    "method": "SET",
    "name": "Your AirConditioner",
    "characteristic": "CurrentTemperature",
    "value": 20
}
```

## My Custom-Command, InfraredRunnable

My Custom-Command, InfraredRunnable, sends some infrared codes registered previous to my infrared home devices with [RPZ-IR-Sensor][RPZ-IR-Sensor].

InfraredRunnable uses hardware and software:

- [RPZ-IR-Sensor][RPZ-IR-Sensor]: is an infrared sender of the Raspberry Pi HAT.
- [cgir][IndoorCorgi-cgir]: is a tool in Python to control RPZ-IR-Sensor.
- [cgsensor][IndoorCorgi-cgsensor]: is a tool to get the sensor data from RPZ-IR-Sensor.

My list of infrared home devices:

|Product Name|Constructor|Service Type|
|-|-|-|
|RPZ-IR-Sensor|Indoor Corgi|HumiditySensor and TemperatureSensor|
|A ceiling light|Panasonic|LightBulb|
|A ceiling light|Panasonic|LightBulb|
|An air-conditioner|N/A|HeaterCooler|

## Misc

InfraredRunnable involves some useful files:

- _codes.json_  
  involves some infrared codes of '[cgir][IndoorCorgi-cgir].'

- *example.install_runnable.sh*  
  installs InfraredRunnable on Ubuntu Linux.  
  Run the install script after changing masked as `XXX` to your sensitive information of the devices or some.

Homebridge UI provides Swagger:

- Swagger URL  
  http:// [homebrdige domain or IP] /swagger

- The cached accessories URL  
  We get the current state of 'the cached accessories' on  
  http:// [homebrdige domain or IP] /swagger/static/index.html#/Homebridge/ServerController_getCachedAccessories

### Patineboot's ideas about RunnablePlatform

1. I may add the new communication to RunnablePlatform.
   - RESTful API  
     - GET - get the state of RunnablePlatform accessory on the Homebridge.
     - POST - notify the state to the Homebridge  
       Memo: We already get 'the cached accessories' with Swagger on Homebridge.
   - Web socket  
     RunnablePlatform sends the state to change by user interaction on Apple Home app or Siri.
1. RunnablePlatform supports updating the properties for some characteristics in the future.

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

## Environment

RunnablePlatform is running as Homebridge Plugin.

My Custom-Command, InfraredRunnable, is running but not limited:

- Raspberry Pi OS: GNU/Linux 10 (buster) 10.11
- Python: 3.7.3
- [cgir][IndoorCorgi-cgir]: 1.0
- [cgsensor][IndoorCorgi-cgsensor]: 1.0

## Thanks

@[IndoorCorgi][IndoorCorgi]

They created a nice Raspberry Pi HAT, [RPZ-IR-Sensor][RPZ-IR-Sensor], and good tools, '[cgir][IndoorCorgi-cgir] and [cgsensor][IndoorCorgi-cgsensor].'

@[IndoorCorgi][IndoorCorgi]'s '[RPZ-IR-Sensor][RPZ-IR-Sensor]': <https://www.indoorcorgielec.com/products/rpz-ir-sensor/>

I strongly recommend [RPZ-IR-Sensor][RPZ-IR-Sensor] to send infrared codes because of my good experience.

## No Thanks

[Homebridge and its Organization Collaborators](https://github.com/homebridge)  
Overall, The Verified By Homebridge program is a FRAUD.

> I solved my plugin soon from the requests of @donavanbecker.  
> @donavanbecker respond very late and is ignoring the import bug at Homebridge.

The member of Homebridge replied very late every time, and 3 months later, finally, He ignored my proposal.

[Bit Trade One, LTD.](https://bit-trade-one.co.jp) (ADRSIR design, manufacturing, and sales) provides **NO** supports and the **USELESS** scripts. Bit Trade One provides bad and poor deliverables.

## Publish RunnablePlatform on NPM for patine

1. Update  
   1. Update the value of 'version' on `package.json`.
   1. Update the `package-lock.json`.  
      ```bash
      rm -rf node_modules
      rm package-lock.json
      npm install ../runnable-platform/
      ```
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

## Install Local RunnablePlatform

1. Clone

   ```bash
   git clone https://github.com/patineboot/runnable-platform.git
   ```

1. Install

   ```bash
   sudo npm --location=global install ./runnable-platform/
   ```
