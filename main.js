import { effect } from '@preact/signals-core';
import { createModel } from './model.js';
import { viewUpdate } from './view.js';
import { createController } from './controller.js';

const m = createModel();
const ctrl = createController();

window.addEventListener('keydown', ctrl.keydown);  // the browser calls it on each key press

setInterval(() => {                          // the NMI tick
  m.update(ctrl.read());
}, 150);

effect(() => viewUpdate(m, document.querySelector('#app')));  // redraw only on change
