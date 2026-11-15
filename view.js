import { html, render } from 'lit-html';
import { WIDTH, HEIGHT } from './model.js';

const range = n => [...Array(n).keys()];

const template = m => html`
  <table class="matrix">
    ${range(HEIGHT).map(r => html`<tr>
      ${range(WIDTH).map(c => html`<td class=${r === m.row.value && c === m.col.value ? 'on' : ''}></td>`)}
    </tr>`)}
  </table>
  <output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>`;

export function viewUpdate(m, container) {   // view_update()
  render(template(m), container);
}
