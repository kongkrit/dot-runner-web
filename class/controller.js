import { Cmd } from './model-controller-common.js';

const KEYMAP = Object.freeze({ ArrowUp: Cmd.UP, ArrowDown: Cmd.DOWN, ArrowLeft: Cmd.LEFT,
                               ArrowRight: Cmd.RIGHT, ' ': Cmd.STOP });

export class Controller {
  #pending = Cmd.NONE;                       // latched key, like KEYPAD bit 7

  keydown(e) {                               // the keypad latching a key
    if (Object.hasOwn(KEYMAP, e.key)) { this.#pending = KEYMAP[e.key]; e.preventDefault(); }
  }

  read() {                                   // controller_read(): the latched key, or NONE
    const c = this.#pending;
    this.#pending = Cmd.NONE;
    return c;
  }
}
