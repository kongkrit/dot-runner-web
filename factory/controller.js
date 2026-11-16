import { Cmd } from './model-controller-common.js';

const KEYMAP = Object.freeze({ ArrowUp: Cmd.UP, ArrowDown: Cmd.DOWN, ArrowLeft: Cmd.LEFT,
                               ArrowRight: Cmd.RIGHT, ' ': Cmd.STOP });

export function createController() {
  let pending = Cmd.NONE;                    // latched key, like KEYPAD bit 7
  return {
    keydown(e) {                             // the keypad latching a key
      if (e.key in KEYMAP) { pending = KEYMAP[e.key]; e.preventDefault(); }
    },
    read() {                                 // controller_read(): the latched key, or NONE
      const c = pending;
      pending = Cmd.NONE;
      return c;
    },
  };
}
