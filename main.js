import { effect } from '@preact/signals-core';
import { render } from 'lit-html';
import { createModel, Cmd } from './model.js';
import { view } from './view.js';

const KEYMAP = { ArrowUp: Cmd.UP, ArrowDown: Cmd.DOWN, ArrowLeft: Cmd.LEFT,
                 ArrowRight: Cmd.RIGHT, ' ': Cmd.STOP };

const m = createModel();
let pending = Cmd.NONE;                      // latched key, like KEYPAD bit 7

window.addEventListener('keydown', e => {    // controller_read(), but the browser calls you
  if (e.key in KEYMAP) { pending = KEYMAP[e.key]; e.preventDefault(); }
});

setInterval(() => {                          // the NMI tick
  m.update(pending);
  pending = Cmd.NONE;
}, 150);

effect(() => render(view(m), document.querySelector('#app')));  // view_update(), only on change
