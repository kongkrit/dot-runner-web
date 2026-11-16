import { effect } from '@preact/signals-core';
import { createModel } from './model.js';
import { createView } from './view.js';
import { createController } from './controller.js';

const model = createModel();
const view = createView(document.querySelector('#app-factory'));
const controller = createController();

window.addEventListener('keydown', controller.keydown);  // the browser calls it on each key press

setInterval(() => {                          // the NMI tick
  model.update(controller.read());
}, 150);

effect(() => view.update(model));            // redraw only on change
