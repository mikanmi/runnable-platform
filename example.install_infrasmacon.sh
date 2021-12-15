#!/usr/bin/env sh

echo "Start to install homeremote."

echo "  Copying homeremote to /var/opt/"
cp -R ../homeremote /var/opt

echo "  Changing Owner and Group of homeremote directory"
chown -R pi:pi /var/opt/homeremote

echo "  Copying 'config.json' file to /var/lib/homebridge/"
cp ./config.json /var/lib/homebridge/

echo "  Replacing dyson-tag to sensitive information in config.json"
sed -i -e 's/DYSON-IP/XXX.XXX.XXX.XXX/g' /var/lib/homebridge/config.json
sed -i -e 's/DYSON-SERIALNUMBER/XXXXX-XXX-XX-XXXXXXXX-XXX/g' /var/lib/homebridge/config.json
sed -i -e 's/DYSON-PASSWORD/XXXXXXXXXXXXXXXX/g' /var/lib/homebridge/config.json

echo "  Replacing hue-tag to sensitive information in config.json"
sed -i -e 's/HUE-ATTRIBUTE/XXXXXXXXXXXXXXXX/g' /var/lib/homebridge/config.json
sed -i -e 's/HUE-VALUE/XXXXXXXXXX/g' /var/lib/homebridge/config.json

echo "Installing homeremote is finished."
