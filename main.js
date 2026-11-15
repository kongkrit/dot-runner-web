import { effect } from '@preact/signals-core';
import { render } from 'lit-html';
import { createModel } from './model.js';
import { view } from './view.js';
import { controllerKeydown, controllerRead } from './controller.js';

const m = createModel();

window.addEventListener('keydown', controllerKeydown);  // the browser calls it on each key press

setInterval(() => {                          // the NMI tick
  m.update(controllerRead());
}, 150);

effect(() => render(view(m), document.querySelector('#app')));  // view_update(), only on change
