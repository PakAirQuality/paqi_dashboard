import * as Plot from "npm:@observablehq/plot";
import * as Inputs from "npm:@observablehq/inputs";
import * as d3 from "npm:d3";
import { aqiLevels } from "./aqi_levels.js";

const METRICS = {
  "PM2.5": "pm25",
  "AQI US": "aqius",
  "AQI CN": "aqicn"
};
export function cityComparison(aqi, {width} = {}) {
  const today = new Date();
  const twoDaysFromNow = new Date(today);
  twoDaysFromNow.setDate(today.getDate() + 2);
  
  const filteredData = aqi.filter(d => 
    d.data_type !== "forecast" || 
    (d.data_type === "forecast" && new Date(d.ts) <= twoDaysFromNow)
  );

  // Filter for current readings
  const currentData = filteredData.filter(d => d.data_type === "current");

  return Plot.plot({
    width,
    height: 400,
    grid: true,
    x: {
      type: "time",
      label: "Time →"
    },
    y: {
      label: "↑ PM2.5 (μg/m³)"
    },
    marks: [
      // Base layer - all points
      Plot.dot(filteredData, {
        x: d => new Date(d.ts),
        y: "pm25",
        fill: d => d.aqi_color,
        opacity: d => d.data_type === "forecast" ? 0.5 : 0.8,
        r: 4,
        channels: {
          City: "city",
          PM25: "pm25",
          "AQI Level": "aqi_level",
          "Data Type": "data_type",
          Time: "ts"
        },
        tip: {
          format: {
            Time: d => new Date(d).toLocaleString(),
            PM25: d => `${d} µg/m³`,
            City: true,
            "AQI Level": true,
            "Data Type": true
          }
        }
      }),
      // Highlight layer for current readings
      Plot.dot(currentData, {
        x: d => new Date(d.ts),
        y: "pm25",
        stroke: d => d.aqi_color,
        fill: "none",
        strokeWidth: 2,
        r: 8
      })
    ]
  });
}