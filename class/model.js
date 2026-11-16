import { signal, computed } from '@preact/signals-core';
import { Cmd } from './model-controller-common.js';

const WIDTH = 16, HEIGHT = 8;               // grid size, owned by the model

export class Model {
  #row = signal(4); #col = signal(7);       // private (#), like fields of model_t
  #cmd = Cmd.STOP;                          // not shown on screen, so plain variable
  width = WIDTH; height = HEIGHT;           // the view draws whatever size the model says
  row = computed(() => this.#row.value);    // read-only to outsiders: const model_t *
  col = computed(() => this.#col.value);
  hex = computed(() => (this.#row.value << 4) | this.#col.value);

  update(c) {    // model_update(); a method on Model.prototype, shared by all models
    if (c !== Cmd.NONE) this.#cmd = c;
    switch (this.#cmd) {
      case Cmd.LEFT:  this.#col.value = (this.#col.value + WIDTH - 1) % WIDTH; break;
      case Cmd.RIGHT: this.#col.value = (this.#col.value + 1) % WIDTH;         break;
      case Cmd.UP:    this.#row.value = (this.#row.value + HEIGHT - 1) % HEIGHT; break;
      case Cmd.DOWN:  this.#row.value = (this.#row.value + 1) % HEIGHT;        break;
    }
  }
}
