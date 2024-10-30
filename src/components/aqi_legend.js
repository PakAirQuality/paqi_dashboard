import {html} from "npm:htl";
import { aqiLevels } from "./aqi_levels.js"

export function aqiLegend() {
  const totalWidth = 900;
  const cellWidth = totalWidth / 10;  

  return html`
    <table style="
      width: ${totalWidth}px;
      border-collapse: collapse;
      margin: 20px auto;
      table-layout: fixed;
    ">
      <tr>
        ${aqiLevels.map(item => html`
          <td style="
            width: ${cellWidth}px;
            background: ${item.color};
            color: white;
            padding: 6px;
            text-align: left;
            font-size: 11px;
            line-height: 1.2;
            height: 40px;
          ">
            ${item.max === Infinity ? '300+' : `${item.min}-${item.max}`}<br>
            ${item.level}
          </td>
        `)}
      </tr>
    </table>
  `;
}