import { Cmd } from './model.js';

const KEYMAP = { ArrowUp: Cmd.UP, ArrowDown: Cmd.DOWN, ArrowLeft: Cmd.LEFT,
                 ArrowRight: Cmd.RIGHT, ' ': Cmd.STOP };

let pending = Cmd.NONE;                      // latched key, like KEYPAD bit 7

export function controllerKeydown(e) {       // the keypad latching a key
  if (e.key in KEYMAP) { pending = KEYMAP[e.key]; e.preventDefault(); }
}

export function controllerRead() {           // controller_read(): the latched key, or NONE
  const c = pending;
  pending = Cmd.NONE;
  return c;
}
