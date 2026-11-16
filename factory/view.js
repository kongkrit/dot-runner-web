import { html, render } from 'lit-html';

const range = n => [...Array(n).keys()];

const template = m => html`
  <table class="matrix">
    ${range(m.height).map(r => html`<tr>
      ${range(m.width).map(c => html`<td class=${r === m.row.value && c === m.col.value ? 'on' : ''}></td>`)}
    </tr>`)}
  </table>
  <output>${m.hex.value.toString(16).toUpperCase().padStart(2, '0')}</output>`;

export function createView(container) {     // each view keeps only where it draws
  return {
    update(m) {                             // view_update()
      render(template(m), container);
    },
  };
}
