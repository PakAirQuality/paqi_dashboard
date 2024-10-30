import {html} from "npm:htl";

export function aqiLegend() {
  const legendItems = [
    { level: "Good", color: "#97C93D" },
    { level: "Moderate", color: "#FFCF01" },
    { level: "Unhealthy for Sensitive Groups", color: "#FF9933" },
    { level: "Unhealthy", color: "#FF3333" },
    { level: "Very Unhealthy", color: "#A35DB5" },
    { level: "Hazardous", color: "#8B3F3F" }
  ];

  return html`
    <div style="
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      margin: 20px 0;
      max-width: 900px;
    ">
      ${legendItems.map(item => html`
        <div style="display: flex; align-items: center; gap: 4px;">
          <div style="
            width: 16px;
            height: 16px;
            background: ${item.color};
            border-radius: 2px;
          "></div>
          <span style="font-size: 14px;">${item.level}</span>
        </div>
      `)}
    </div>
  `;
}