import { html } from 'lit-html';
import { WIDTH, HEIGHT } from './model.js';

const range = n => [...Array(n).keys()];

export const view = m => html`
  <table class="matrix">
    ${range(HEIGHT).map(r => html`<tr>
      ${range(WIDTH).map(c => html`<td class=${r === m.row.value && c === m.col.value ? 'on' : ''}></td>`)}
    </tr>`)}
  </table>
  <output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>`;
