#!/usr/bin/env sh

# Copyright (c) 2020, 2021, 2022, Patineboot. All rights reserved.
# RunnablePlatform is licensed under CC BY-NC-ND 4.0.

echo "Start to install RunnablePlatform."

echo "  Copying InfraredRunnable to /var/opt/."
cp -R ../runnable ../infrared-runnable
cp -R ../infrared-runnable /var/opt
rm -rf ../infrared-runnable

echo "  Changing the owner and group of the infrared-runnable directory."
chown -R pi:pi /var/opt/infrared-runnable

echo "  Copying the 'config.json' file to /var/lib/homebridge/"
cp ./config.json /var/lib/homebridge/

echo "  Replacing hue-tag in config.json"
sed -i -e 's/HUE-HOST/XXXXXXXXXXXXXXXX/g' /var/lib/homebridge/config.json
sed -i -e 's/HUE-ATTRIBUTE/XXXXXXXXXXXXXXXX/g' /var/lib/homebridge/config.json
sed -i -e 's/HUE-VALUE/XXXXXXXXXX/g' /var/lib/homebridge/config.json

echo "  Replacing dyson-tag in config.json"
sed -i -e 's/DYSON-IP/XXX.XXX.XXX.XXX/g' /var/lib/homebridge/config.json
sed -i -e 's/DYSON-SERIALNUMBER/XXXXX-XXX-XX-XXXXXXXX-XXX/g' /var/lib/homebridge/config.json
sed -i -e 's/DYSON-PASSWORD/XXXXXXXXXXXXXXXX/g' /var/lib/homebridge/config.json

echo "Installing RunnablePlatform is finished."
