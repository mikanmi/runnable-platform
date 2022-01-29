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

import EventEmitter from 'events';

export class Lock {
    /** @type {boolean} */
    #acquired;
    /** @type {EventEmitter} */
    #eventEmitter;

    constructor() {
        this.#acquired = false;
        this.#eventEmitter = new EventEmitter();
    }

    /**
     * Acquire the lock.
     * Wait on the release if anyone has acquired it already.
     */
    acquire() {
        return new Promise((resolve) => {

            const notifier = () => {
                if (!this.#acquired) {
                    this.#acquired = true;
                    this.#eventEmitter.removeListener('released', notifier);
                    return resolve();
                }
            }

            if (!this.#acquired) {
                this.#acquired = true;
                return resolve();
            }
            this.#eventEmitter.on('released', notifier);
        });
    }

    /**
     * Release the lock gotten on the acquire method after waiting in 'waitTime.'
     * @param {number} waitTime
     */
    release(waitTime = 0) {
        setTimeout(() => {
            this.#acquired = false;
            this.#eventEmitter.emit('released');
        },
        waitTime);
    }
}
