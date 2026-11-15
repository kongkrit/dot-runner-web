import { signal, computed } from '@preact/signals-core';
import { Cmd } from '../model-controller-common.js';

const WIDTH = 16, HEIGHT = 8;               // grid size, owned by the model
const row = signal(4), col = signal(7);     // file-level, like static variables in C
let cmd = Cmd.STOP;                         // not shown on screen, so plain variable

export const model = {
  width: WIDTH, height: HEIGHT,             // the view draws whatever size the model says
  row: computed(() => row.value),           // read-only to outsiders: const model_t *
  col: computed(() => col.value),
  hex: computed(() => (row.value << 4) | col.value),
  update(c) {                               // model_update()
    if (c !== Cmd.NONE) cmd = c;
    switch (cmd) {
      case Cmd.LEFT:  col.value = (col.value + WIDTH - 1) % WIDTH; break;
      case Cmd.RIGHT: col.value = (col.value + 1) % WIDTH;         break;
      case Cmd.UP:    row.value = (row.value + HEIGHT - 1) % HEIGHT; break;
      case Cmd.DOWN:  row.value = (row.value + 1) % HEIGHT;        break;
    }
  },
};
