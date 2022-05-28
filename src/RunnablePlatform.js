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
    #skeltonMode = false;

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

        // verify the my 'platform' element on the config.json file.
        if (!this.#verifyElement(CONFIG)) {
            this.#skeltonMode = true;
            LOG.warn('Missing the mandatory element[s] of RunnablePlatform.');
            LOG.warn('Add the mandatory elements of RunnablePlatform to the Config of Homebridge.');
            return;
        }

        // set a command and an interval time to communicator.
        Communicator.setCommandLine(CONFIG.run, CONFIG.time);

        /**
         * Platforms should wait until the "didFinishLaunching" event has fired before
         * registering any new accessories.
         */
        HAPI.on('didFinishLaunching', () => {
            if (this.#skeltonMode) {
                LOG.warn('RunnablePlatform Plugin is running on the Skelton mode.');
                return;
            }
            this.#didFinishLaunching();
        });

        /**
         * This event is fired when homebridge got shutdown.
         */
        HAPI.on('shutdown', () => {
            if (this.#skeltonMode) {
                LOG.warn('RunnablePlatform Plugin is running on the Skelton mode.');
                return;
            }
            const comm = Communicator.getInstance();
            comm.disconnect();
        });
    }

    /**
     * REQUIRED - Homebridge will call the "configureAccessory" method once for every cached
     * accessory restored
     * @param {import("homebridge").PlatformAccessory<import("homebridge").UnknownContext>} accessory
     */
    configureAccessory(accessory) {
        if (this.#skeltonMode) {
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
            valid = 'VOID';
        }
        LOG.info(`Configure Accessory ${valid}: ${accessory.displayName}`);
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
     * @returns {boolean}
     */
    #verifyElement(config) {
        // the platform element must have the these elements on config file.
        if (!('run' in config &&
                'time' in config &&
                'accessories' in config)) {
            LOG.error("missing the 'run', 'time', or 'accessories' elements in the platform element on the config file.");
            return false;
        }

        LOG.info(`${PLATFORM_NAME} element has them on config.json`);
        LOG.info('  name: ' + config.name);
        LOG.info('  run: ' + config.run);
        LOG.info('  time(ms): ' + config.time);
        LOG.info('  accessories length: ' + config.accessories.length);

        // an element of the 'accessories' array must have the these elements on config file.
        const corrects = config.accessories
                .filter((/** @type {any} */ acc) => 'name' in acc)
                .filter((/** @type {any} */ acc) => 'service' in acc)
                .filter((/** @type {any} */ acc) => 'characteristics' in acc);

        if (corrects.length != config.accessories.length) {
            LOG.error("missing the 'name', 'service', or 'characteristics' element on the config file.");
            return false;
        }

        return true;
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

                LOG.info(`Cached Accessory name:[${runnable.name}] type:[${runnable.serviceType}]`);
            }
            // otherwise, we create a new platform accessory
            else {
                // create a new platform accessory
                const uuid = HAPI.hap.uuid.generate(runnable.name);
                accessory = new HAPI.platformAccessory(runnable.name, uuid);
                runnable.startService(accessory);
                // register the new platform accessory
                HAPI.registerPlatformAccessories(PLUGIN_NAME, PLATFORM_NAME, [accessory]);

                LOG.info(`New Accessory name:[${runnable.name}] type:[${runnable.serviceType}]`);
            }
        }
    }
}
