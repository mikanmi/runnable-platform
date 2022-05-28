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

import { ChildProcess, exec } from 'child_process';
import { EventEmitter } from 'events';
import * as readline from 'node:readline';

import { LOG } from './index.js';

/** @type {number} */
const RETRY_COUNT = 3;

// for async/await
// import util  from 'util';
// import childProcess from 'child_process';
// const spawn = util.promisify(childProcess.spawn);

export class Communicator extends EventEmitter
{
    /**
     * The command to run a sub process
     * @type {string}
     */
    static #commandLine;

   /**
     * The command to run a sub process
     * @type {number}
     */
    static #time;

    /**
     * The singleton instance
     * @type {Communicator}
     */
     static #instance = new Communicator();

    /**
     * The sub process to run #commandLine.
     * @type {Subprocess}
     */
    #subprocess;

    /**
     * @param {string} commandLine
     * @param {number} time
     */
    static setCommandLine(commandLine, time) {
        Communicator.#commandLine = commandLine;
        Communicator.#time = time;
    }

    static getInstance() {
        return Communicator.#instance;
    }

    static getIntervalTime() {
        return Communicator.#time;
    }

    /**
     * Constructor
     */
    constructor() {
        super()
    }

    connect() {
        LOG.debug(`Enter ${this.constructor.name}#connect`);

        const subprocess = new Subprocess(Communicator.#commandLine, this);
        subprocess.run();

        this.#subprocess = subprocess;
    }

    disconnect() {
        LOG.debug(`Enter ${this.constructor.name}#disconnect`);

        if (!this.#subprocess) {
            return;
        }
        this.#subprocess.terminate();
        this.#subprocess = null;
    }

    /**
     * @param {any} message
     */
    send(message) {
        LOG.debug(`Enter ${this.constructor.name}#send: ${message}`);

        // not run a sub process yet.
        if (!this.#subprocess) {
            LOG.warn(`send a message before running a sub process`);
            return;
        }
        this.#subprocess.send(message);
    }
}

class Subprocess
{
    /** @type {string} */
    #commandLine;
    /** @type {EventEmitter} */
    #emitter
    /** @type {ChildProcess} */
    #runnable;

    /** @type {number} */
    #retry;

    /**
     * @param {string} commandLine
     * @param {EventEmitter} emitter
     */
    constructor(commandLine, emitter) {
        this.#commandLine = commandLine;
        this.#emitter = emitter;
        this.#retry = 0;
    }

    run() {
        LOG.debug(`Enter ${this.constructor.name}#run`);

        LOG.info(`Running command: ${this.#commandLine}`);

        const runnable = exec(this.#commandLine);
        runnable.on('spawn', () => {
            LOG.info(`sub process spawned`);
        });
        runnable.on('close', this.#closeListener.bind(this));
        runnable.on('exit', this.#exitListener.bind(this));
        runnable.on('error', this.#errorListener.bind(this));

        // handle the stderr of the sub process.
        runnable.stderr.on('data', (chunk) => {
            LOG.error(`sub process stderr: ${chunk}`);
        });

        // handle the stdout of the sub process.
        const rl = readline.createInterface( {input: runnable.stdout} );
        let chunkLines = '';
        rl.on('line', (line) => {
            LOG.debug(`Received message: ${line}`);

            chunkLines += line;
            try {
                // may throw SyntaxError
                const message = JSON.parse(chunkLines);
                // got an JSON message.
                this.#retry = 0;
                this.#emitter.emit('message', message);
                chunkLines = '';
            }
            catch(_) {
                // JSON.parse throws SyntaxError if any line of JSON message does not arrive yet.
            }
        });
        rl.on('close', () => {
            LOG.info(`readline closed`);
        });

        this.#runnable = runnable;
    }

    /**
     * @param {any} message
     */
    send(message) {
        LOG.debug(`Enter ${this.constructor.name}#send: ${message}`);
        if (!this.#runnable) {
            LOG.warn(`Not established a connection`);
            return;
        }

        // handle the stdin of the sub process.
        const text = JSON.stringify(message);
        const succeeded = this.#runnable.stdin.write(text + '\n');

        LOG.info(`Send message [${succeeded}]: ${text}`);

        if (succeeded) {
            this.#retry = 0;
        }
        else {
            // the text is wrote but failed.
            // establish a new connection to a sub process.
            LOG.warn(`writing in subprocess stdin might fail due to full`);
            this.terminate();
            this.#rerun();
        }
    }

    terminate() {
        LOG.debug(`Enter ${this.constructor.name}#terminate`);
        if (!this.#runnable) {
            LOG.warn(`Not established a connection`);
            return;
        }

        this.#runnable.removeAllListeners();
        this.#runnable.kill();
        this.#runnable = null;
    }

    #rerun() {
        this.terminate();
        if(this.#retry < RETRY_COUNT) {
            LOG.info(`retry run [${this.#retry}]: ${this.#commandLine}`);
            this.run();
            this.#retry++;
        }
        else {
            LOG.error(`Not established the connection to the subprocess.`);
        }
    }

    /**
     * @param {number} code
     * @param {string} signal
     */
    #closeListener(code, signal) {
        LOG.info(`sub process closed the stdio with code ${code} and signal ${signal}`);
        this.#rerun();
    }
    /**
     * @param {number} code
     * @param {string} signal
     */
     #exitListener(code, signal) {
        LOG.info(`sub process exited with code ${code} and signal ${signal}`);
        this.#rerun();
    }
    /**
     * @param {number} code
     */
     #errorListener(code) {
        LOG.error(`sub process occurs error[s] with code ${code}`);
        this.#rerun();
    }
}
