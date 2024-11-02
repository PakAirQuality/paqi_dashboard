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
    const filteredData = data
      .filter(d => d.city === selectedCity)
      .filter(d => d.data_source === "city")
      .map(d => ({
        ...d,
        ts: new Date(d.ts).toLocaleDateString() // Convert timestamps to date strings
      }));

    return Plot.plot({
      width,
      height: 400,
      marginLeft: 60,

      y: {
        grid: true,
        label: `↑ ${metric}`,
        domain: [0, d3.max(filteredData, d => d[metric])],
      },
      
      marks: [
        Plot.boxY(filteredData, {
          x: "ts",
          y: metric,
          stroke: "black",
          tip: false
        })
      ]
    });
  }





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
