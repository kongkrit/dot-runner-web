import { effect } from '@preact/signals-core';
import { createModel } from './model.js';
import { viewUpdate } from '../view.js';
import { controller } from './controller.js';

const model = createModel();

window.addEventListener('keydown', controller.keydown);  // the browser calls it on each key press

setInterval(() => {                          // the NMI tick
  model.update(controller.read());
}, 150);

effect(() => viewUpdate(model, document.querySelector('#app-mixed')));  // redraw only on change
