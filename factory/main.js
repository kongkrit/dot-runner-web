import { effect } from '@preact/signals-core';
import { createModel } from './model.js';
import { viewUpdate } from '../view.js';
import { createController } from './controller.js';

const model = createModel();
const controller = createController();

window.addEventListener('keydown', controller.keydown);  // the browser calls it on each key press

setInterval(() => {                          // the NMI tick
  model.update(controller.read());
}, 150);

effect(() => viewUpdate(model, document.querySelector('#app-factory')));  // redraw only on change
