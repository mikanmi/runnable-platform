/* 
Attribution-NonCommercial-NoDerivatives 4.0 International

Copyright (c) 2022 Patineboot. All rights reserved.
RunnablePlatform is licensed under CC BY-NC-ND 4.0.

Under the following terms:
Attribution — You must give appropriate credit, provide a
link to the license, and indicate if changes were made. You
may do so in any reasonable manner, but not in any way that
suggests the licensor endorses you or your use.
NonCommercial — You may not use the material for
commercial purposes.
NoDerivatives — If you remix, transform, or build upon the
material, you may not distribute the modified material.
No additional restrictions — You may not apply legal terms
or technological measures that legally restrict others from
doing anything the license permits.

Notices:
You do not have to comply with the license for elements of
the material in the public domain or where your use is
permitted by an applicable exception or limitation.

No warranties are given. The license may not give you all of
the permissions necessary for your intended use. For
example, other rights such as publicity, privacy, or moral
rights may limit how you use the material.
*/

"use strict";

import { LOG, HAPI } from './index.js';
import { Communicator } from './Communicator.js';
import { Lock } from './Lock.js';

export class RunnableAccessory {

    /** @type {any} */
    #accessoryConfig;

    /** @type {import("homebridge").Service} */
    #service;

    /** @type {Lock} */
    #lock;

    /**
     * Constructor
     * @param {any} accessoryConfig
     */
    constructor(accessoryConfig) {
        LOG.debug(`Enter ${this.constructor.name}: ${accessoryConfig} -> name: ${accessoryConfig.name}`);

        this.#lock = new Lock();

        this.#accessoryConfig = accessoryConfig;

        const comm = Communicator.getInstance();
        comm.on('message', (message) => {
            if (message.name !== this.name) {
                return;
            }
            this.updateCharacteristic(message.characteristic, message.value);
        });
    }

    /**
     * Get the name of this accessory.
     * @returns {string}
     */
    get name() {
        return this.#accessoryConfig.name;
    }

    /**
     * Get the service type of this accessory.
     * @returns {string}
     */
    get serviceType() {
        return this.#service.constructor.name;
    }

    /**
     * set Accessory Information
     * @param {any} accessory to set the Accessory Information Characteristics
     */
    #patineInformation(accessory) {
        // add an Accessory Information service
        const service = this.#getService(accessory, "AccessoryInformation");

        service.setCharacteristic(HAPI.hap.Characteristic.Manufacturer, 'Patineboot')
                .setCharacteristic(HAPI.hap.Characteristic.Model, 'Patineboot Custom')
                .setCharacteristic(HAPI.hap.Characteristic.SerialNumber, 'Patineboot First');
    }

    /**
     * Start the services specified with config on specified accessory.
     * @param {import("homebridge").PlatformAccessory} accessory the platform accessory created from createPlatformAccessory() on this instance.
     */
    startService(accessory) {
        LOG.debug(`Enter ${this.constructor.name}#startService: ${accessory}`);

        accessory.context.device = this;
        this.#patineInformation(accessory);

        // add an accessory service
        this.#service = this.#getService(accessory, this.#accessoryConfig.service);

        // bind setter/getter on each of the characteristics of the service
        for (let characteristic of this.#accessoryConfig.characteristics) {
            this.#service.getCharacteristic(HAPI.hap.Characteristic[characteristic])
            //.onGet(this.#handleCharacteristicGet.bind(this, characteristic))
            .onSet(this.#handleCharacteristicSet.bind(this, characteristic));
        }
    }

    /**
     * Update to the specified value in the specified characteristic of the accessory.
     * @param {string} attribute the name of characteristic.
     * @param {any} value  the new value .
     */
    updateCharacteristic(attribute, value) {
        LOG.debug(`Enter ${this.constructor.name}#updateCharacteristic: ${attribute}, ${value}`);

        const characteristic = this.#service.getCharacteristic(HAPI.hap.Characteristic[attribute]);
        if (!characteristic) {
            LOG.warn(`No ${attribute} on the characteristics of ${this.name}`)
        }
        characteristic.updateValue(value);
    }

    /**
     * @param {import("homebridge").PlatformAccessory} accessory
     * @param {string} type
     * @returns {import("homebridge").Service}
     */
    #getService(accessory, type) {
        const serviceClass = HAPI.hap.Service[type];
        // get the service if it exists
        let service = accessory.getService(serviceClass);
        // otherwise create a new service
        if (!service) {
            service = accessory.addService(serviceClass);
        }
        return service;
    }

     /**
     * Handle requests to get the current value of the characteristic
     * @param {string} characteristic
     */
     async #handleCharacteristicGet(characteristic) {
        LOG.debug(`Enter ${this.constructor.name}##handleCharacteristicGet: ${characteristic}`);
    }

    /**
     * Handle requests to set the characteristic
     * @param {string} characteristic
     * @param {any} value
     */
    async #handleCharacteristicSet(characteristic, value) {
        LOG.debug(`Enter ${this.constructor.name}##handleCharacteristicSet: ${characteristic}, ${value}`);

        const comm = Communicator.getInstance();
        const intervalTime = Communicator.getIntervalTime();

        await this.#lock.acquire();
        try {
            let status = {};
            for (let charName of this.#accessoryConfig.characteristics) {
                const char = this.#service.getCharacteristic(HAPI.hap.Characteristic[charName]);
                status[char.constructor.name] = char.value;
            }

            // construct a SET message.
            const message = {
                method: 'SET',
                name: this.name,
                characteristic,
                value,
                status,
            }

            comm.send(message);
        }
        finally{
            this.#lock.release(intervalTime);
        }
    }
}
