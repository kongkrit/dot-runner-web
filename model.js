import { signal, computed } from '@preact/signals-core';

export const WIDTH = 16, HEIGHT = 8;
export const Cmd = Object.freeze({ NONE: 0, STOP: 1, LEFT: 2, RIGHT: 3, UP: 4, DOWN: 5 });

export function createModel() {
  const row = signal(4), col = signal(7);   // private, like fields of model_t
  let cmd = Cmd.STOP;                       // not shown on screen, so plain variable
  return {
    row: computed(() => row.value),         // read-only to outsiders: const model_t *
    col: computed(() => col.value),
    hex: computed(() => (row.value << 4) | col.value),
    update(c) {                             // model_update()
      if (c !== Cmd.NONE) cmd = c;
      switch (cmd) {
        case Cmd.LEFT:  col.value = (col.value + WIDTH - 1) % WIDTH; break;
        case Cmd.RIGHT: col.value = (col.value + 1) % WIDTH;         break;
        case Cmd.UP:    row.value = (row.value + HEIGHT - 1) % HEIGHT; break;
        case Cmd.DOWN:  row.value = (row.value + 1) % HEIGHT;        break;
      }
    },
  };
}
