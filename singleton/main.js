import { effect } from '@preact/signals-core';
import { model } from './model.js';
import { viewUpdate } from '../view.js';
import { controller } from './controller.js';

window.addEventListener('keydown', controller.keydown);  // the browser calls it on each key press

setInterval(() => {                          // the NMI tick
  model.update(controller.read());
}, 150);

effect(() => viewUpdate(model, document.querySelector('#app-singleton')));  // redraw only on change
