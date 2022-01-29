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

import { RunnablePlatform } from './RunnablePlatform.js';

export const PLATFORM_NAME = 'RunnablePlatform';
export const PLUGIN_NAME = 'homebridge-runnable-platform';

/**
 * @type {import("homebridge").Logger}
 */
export let LOG;
/**
 * @type {import("homebridge").API}
 */
export let HAPI;
/**
 * @type {import("homebridge").PlatformConfig}
 */
export let CONFIG;

/**
 * @param {import("homebridge").API} api
 */
export default function (api) {
    api.registerPlatform(PLATFORM_NAME, RunnablePlatform);
}

/**
 * @param {import("homebridge").Logger} log
 * @param {import("homebridge").PlatformConfig} config
 * @param {import("homebridge").API} api
 */
export function setHomebridge(log, config, api) {
    LOG = log;
    CONFIG = config;
    HAPI = api;
}
