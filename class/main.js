import { effect } from '@preact/signals-core';
import { Model } from './model.js';
import { View } from './view.js';
import { Controller } from './controller.js';

const model = new Model();
const view = new View(document.querySelector('#app-class'));
const controller = new Controller();

window.addEventListener('keydown', e => controller.keydown(e));  // wrapped: passed alone, keydown would lose `this`

setInterval(() => {                          // the NMI tick
  model.update(controller.read());
}, 150);

effect(() => view.update(model));            // redraw only on change
