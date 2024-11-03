import * as Plot from "npm:@observablehq/plot";
import * as Inputs from "npm:@observablehq/inputs";
import * as d3 from "npm:d3";
import { aqiLevels } from "./aqi_levels.js";

const METRICS = {
  "PM2.5": "pm25",
  "AQI US": "aqius",
  "AQI CN": "aqicn"
};

// Helper function to get AQI color based on AQIUS value

function getAqiColor(aqius) {
const level = aqiLevels.find(l => aqius >= l.min && aqius <= l.max);
return level ? level.color : "#8B3F3F";
}


export function createChart(data, {width = 640} = {}) {
  const container = document.createElement("div");
  container.style.display = "flex";
  container.style.flexDirection = "column";
  container.style.gap = "1rem";
  
  // Title
  const title = document.createElement("h3");
  title.textContent = "City Data";
  title.style.margin = "0";
  title.style.textAlign = "left";
  
  // Controls container
  const controls = document.createElement("div");
  controls.style.display = "flex";
  controls.style.gap = "1rem";
  controls.style.alignItems = "center";

  // Create selectors
  const citySelect = Inputs.select([...new Set(data.map(d => d.city))].sort(), {
    value: "Karachi",
    label: "Select City"
  });

  const metricSelect = Inputs.select(Object.keys(METRICS), {
    value: "PM2.5",
    label: "Select Metric"
  });

  // create the plot function
function createPlot(selectedCity, selectedMetric) {
  const metric = METRICS[selectedMetric];
  const today = new Date();
  const twoDaysFromNow = new Date(today);
  twoDaysFromNow.setDate(today.getDate() + 2);

  // First filter by city and timeframe
  const filteredData = data
    .filter(d => d.city === selectedCity)
    .filter(d =>
      d.data_type !== "forecast" ||
      (d.data_type === "forecast" && new Date(d.ts) <= twoDaysFromNow)
    );

  // Separate city and station data
  const cityData = filteredData.filter(d => d.data_source === "city");
  const stationData = filteredData.filter(d => d.data_source === "station");
  const currentData = cityData.filter(d => d.data_type === "current");

  // Get unique station names for the legend
  const stationNames = [...new Set(stationData.map(d => d.station_name))];

  return Plot.plot({
    width,
    height: 400,
    grid: true,
    x: {
      type: "time",
      label: "Time →"
    },
    y: {
      label: `↑ ${selectedMetric}`,
      domain: [0, d3.max(filteredData, d => d[metric])]
    },
    marks: [
      // Station data - lines (grouped by station)
      ...stationNames.map(station => Plot.line(
        stationData.filter(d => d.station_name === station),
        {
          x: d => new Date(d.ts),
          y: metric,
          stroke: "steelblue",
          opacity: 0.3,
          strokeWidth: 1
        }
      )),

      // Station data - points
      Plot.dot(stationData, {
        x: d => new Date(d.ts),
        y: metric,
        fill: "steelblue",
        opacity: 0.3,
        r: 3,
        tip: true,
        channels: {
          Station: "station_name",
          PM25: "pm25",
          AQIUS: "aqius",
          Time: "ts"
        },
        tip: {
          format: {
            Time: d => new Date(d).toLocaleString(),
            PM25: d => `${d} µg/m³`,
            AQIUS: true,
            Station: true
          }
        }
      }),

      // City data - line
      Plot.line(cityData, {
        x: d => new Date(d.ts),
        y: metric,
        stroke: "black",
        opacity: 0.6
      }),

      // City data - points
      Plot.dot(cityData, {
        x: d => new Date(d.ts),
        y: metric,
        fill: d => getAqiColor(d.aqius),
        opacity: d => d.data_type === "forecast" ? 0.5 : 0.8,
        r: 4,
        tip: true,
        channels: {
          City: "city",
          PM25: "pm25",
          AQIUS: "aqius",
          Time: "ts"
        },
        tip: {
          format: {
            Time: d => new Date(d).toLocaleString(),
            PM25: d => `${d} µg/m³`,
            AQIUS: true,
            City: true
          }
        }
      }),

      // Highlight current city readings
      Plot.dot(currentData, {
        x: d => new Date(d.ts),
        y: metric,
        stroke: d => getAqiColor(d.aqius),
        fill: "none",
        strokeWidth: 2,
        r: 8
      })
    ],
    
    style: {
      backgroundColor: "white",
      color: "black",
      fontFamily: "system-ui"
    }
  });
}

// end createplot


  // Initial chart
  let chart = createPlot(citySelect.value, metricSelect.value);

  // Update chart when selections change
  function updateChart() {
    const newChart = createPlot(citySelect.value, metricSelect.value);
    chart.replaceWith(newChart);
    chart = newChart;
  }

  citySelect.addEventListener("change", updateChart);
  metricSelect.addEventListener("change", updateChart);

  // Assemble the component
  container.appendChild(title);
  controls.appendChild(citySelect);
  controls.appendChild(metricSelect);
  container.appendChild(controls);
  container.appendChild(chart);

  return container;
}
