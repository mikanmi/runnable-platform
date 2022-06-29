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

import { RunnableAccessory } from './RunnableAccessory.js';
import { Communicator } from './Communicator.js';

import { PLATFORM_NAME, PLUGIN_NAME, LOG, CONFIG, HAPI, setHomebridge } from './index.js';


export class RunnablePlatform {

    /**
     * this instance.
     * @type {RunnablePlatform}
     */
    static #instance;

    /**
     * Inactive mode.
     * @type {boolean}
     */
    #skeletonMode = false;

    /**
     * store restored cached accessories here.
     * @type {import("homebridge").PlatformAccessory<import("homebridge").UnknownContext>[]}
     */
    #accessories = [];

    /**
     * store cached accessories to unregister here.
     * @type {import("homebridge").PlatformAccessory<import("homebridge").UnknownContext>[]}
     */
     #invalidAccessories = [];

     /**
      * Get the singleton instance.
      * @returns {RunnablePlatform} the instance.
      */
    static getInstance() {
        return RunnablePlatform.#instance;
    }

    /**
     * @param {import("homebridge").Logger} log
     * @param {import("homebridge").PlatformConfig} config
     * @param {import("homebridge").API} api
     */
    constructor(log, config, api) {

        setHomebridge(log, config, api);
        LOG.debug('RunnablePlatform Plugin Loaded');

        RunnablePlatform.#instance = this;

        /**
         * Platforms should wait until the "didFinishLaunching" event has fired before
         * registering any new accessories.
         */
        HAPI.on('didFinishLaunching', () => {
            try {
                if (this.#skeletonMode) {
                    LOG.warn('RunnablePlatform Plugin is running on the Skelton mode.');
                    return;
                }
                this.#didFinishLaunching();
            }
            catch (error) {
                LOG.error('Unexpected error occurs.', error);
                return;
            }
        });

        /**
         * This event is fired when homebridge got shutdown.
         */
        HAPI.on('shutdown', () => {
            try {
                if (this.#skeletonMode) {
                    LOG.warn('RunnablePlatform Plugin is running on the Skelton mode.');
                    return;
                }
                const comm = Communicator.getInstance();
                comm.disconnect();
                LOG.info('Bye.');
            }
            catch (error) {
                LOG.error('Unexpected error occurs.', error);
                return;
            }
        });

        // verify the RunnablePlatform platform element of the platforms element on the config.json file.
        try {
            this.#verifyConfig(CONFIG);
        }
        catch (error) {
            this.#skeletonMode = true;
            LOG.error('RunnablePlatform found the incorrected element on the config.json file.');
            LOG.error(error);
            LOG.error("Correct your description of the RunnablePlatform platform element.");
            return;
        }

        // set a command and an interval time to communicator.
        Communicator.setCommandLine(CONFIG.run, CONFIG.time);
    }

    /**
     * REQUIRED - Homebridge will call the "configureAccessory" method once for every cached
     * accessory restored
     * @param {import("homebridge").PlatformAccessory<import("homebridge").UnknownContext>} accessory
     */
    configureAccessory(accessory) {
        try {
            if (this.#skeletonMode) {
                LOG.warn('RunnablePlatform Plugin is running on the Skelton mode.');
                return;
            }

            // check the restored accessory is not described on the config file
            let valid = '';
            const found = this.#findConfigAccessory(accessory.UUID);
            if (found) {
                this.#accessories.push(accessory);
                valid = 'restored';
            }
            else {
                // remove the accessory from cache later.
                this.#invalidAccessories.push(accessory);
                valid = 'disposed';
            }
            LOG.info(`Saved accessory: ${accessory.displayName} is ${valid}`);
        }
        catch (error) {
            LOG.error('Unexpected error occurs.', error);
            return;
        }
    }
    
    /**
     * @param {string} name
     */
    #findAccessory(name) {
        const uuid = HAPI.hap.uuid.generate(name);
        return this.#accessories.find((accessory) => accessory.UUID === uuid);
    }

    /**
     * @param {string} uuid
     */
    #findConfigAccessory(uuid) {
        let result = null;
        for (let configAccessory of CONFIG.accessories) {
            const configUuid = HAPI.hap.uuid.generate(configAccessory.name);
            if (configUuid === uuid) {
                result = configAccessory;
                break;
            }
        }
        return result;
    }

    #didFinishLaunching() {
        for (let invalid of this.#invalidAccessories) {
            HAPI.unregisterPlatformAccessories(PLUGIN_NAME, PLATFORM_NAME, [invalid]);
        }

        // start the services on Homebridge.
        this.#startServices();

        // establish a connection with the command.
        Communicator.getInstance().connect();
    }

    /**
     * @param {import("homebridge").PlatformConfig} config
     * @returns {boolean} true if config is corrected.
     * @throws {Error} occur if config is invalid.
     */
    #verifyConfig(config) {
        const platResult = this.#verifyPlatform(config);

        let accResult = false;
        for (let configAccessory of config.accessories) {
            accResult = this.#verifyAccessory(configAccessory);
        }

        return platResult && accResult;
    }

    /**
     * @param {import("homebridge").PlatformConfig} configPlatform
     * @returns {boolean} always true.
     * @throws {Error} occur if configPlatform is invalid.
     */
    #verifyPlatform(configPlatform) {
        // the platform element must have the these elements on config file.
        if (!('run' in configPlatform &&
                'time' in configPlatform &&
                'accessories' in configPlatform)) {
            throw new Error(
                "missing the 'run', 'time', or 'accessories' elements in the platform element on the config file."
            );
        }

        LOG.info(`${PLATFORM_NAME} element has them on config.json`);
        LOG.info('  name: ' + configPlatform.name);
        LOG.info('  run: ' + configPlatform.run);
        LOG.info('  time(ms): ' + configPlatform.time);
        LOG.info('  accessories length: ' + configPlatform.accessories.length);

        // an element of the 'accessories' array must have the these elements on config file.
        const corrects = configPlatform.accessories
                .filter((/** @type {any} */ acc) => 'name' in acc)
                .filter((/** @type {any} */ acc) => 'service' in acc)
                .filter((/** @type {any} */ acc) => 'characteristics' in acc);

        if (corrects.length != configPlatform.accessories.length) {
            throw new Error(
                "missing the 'name', 'service', or 'characteristics' element on the config file."
            );
        }
        return true;
    }

    /**
     * @param {any} configAccessory
     * @returns {boolean} always true
     * @throws {Error} occur if configAccessory is invalid.
     */
    #verifyAccessory(configAccessory) {
        const serviceResult = configAccessory.service in HAPI.hap.Service;
        if (!serviceResult) {
            throw new Error(
                `Found the incorrected service name on the config file: "${configAccessory.service}"`
            );
        }

        let charaResult = false;
        for (let characteristic of configAccessory.characteristics) {
            charaResult = characteristic in HAPI.hap.Characteristic;
            if (!charaResult) {
                throw new Error(
                    `Found the incorrected characteristic name on the config file: "${characteristic}"`
                );
            }
        }
        return serviceResult && charaResult;
    }

    #startServices() {
        // start the services of the accessories described on the config file.
        for (let configAccessory of CONFIG.accessories) {



            // create the device accessory from the config
            const runnable = new RunnableAccessory(configAccessory);
            let accessory = this.#findAccessory(configAccessory.name);
            // if Homebridge restored the platform accessory from cache
            if (accessory) {
                runnable.startService(accessory);
                // update the new platform accessory
                HAPI.updatePlatformAccessories([accessory]);
            }
            // otherwise, we create a new platform accessory
            else {
                // create a new platform accessory
                const uuid = HAPI.hap.uuid.generate(runnable.name);
                accessory = new HAPI.platformAccessory(runnable.name, uuid);
                runnable.startService(accessory);
                // register the new platform accessory
                HAPI.registerPlatformAccessories(PLUGIN_NAME, PLATFORM_NAME, [accessory]);

                LOG.info(`New accessory is added: name:[${runnable.name}] service:[${runnable.serviceType}]`);
            }
            LOG.info(`accessory started. name:[${runnable.name}] service:[${runnable.serviceType}]`);
        }
    }
}
