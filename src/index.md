---
theme: [light, dashboard]
title: Paqi dashboard
toc: true
---

# Pakistan AQI Dashboard 🚀

<!-- Load and transform the data -->

```js
const ranks = FileAttachment("data/aqi_ranks.csv").csv({ typed: true });
const aqi = FileAttachment("data/aqi.csv").csv({ typed: true });
const countryData = await FileAttachment("data/countries.csv").csv({
  typed: true,
});
const tokens = await FileAttachment("data/tokens.json").json({ typed: true });
//console.log("Loaded tokens:", tokens);
```

<!-- Load components used in this page -->

```js
import { aqiBarChart } from "./components/ranks.js";
import { aqiLegend } from "./components/aqi_legend.js";
import { stationMap } from "./components/maps.js";
import { createChart } from "./components/chart.js";
import { barChart } from "./components/barplot.js";
```


# Station and City data

```js
function aqiBox() {
  const aqiLevels = [
    { level: "Good", min: 0, max: 50, color: "#97C93D" },
    { level: "Moderate", min: 51, max: 100, color: "#FFCF01" },
    { level: "Unhealthy for Sensitive Groups", min: 101, max: 150, color: "#FF9933" },
    { level: "Unhealthy", min: 151, max: 200, color: "#FF3333" },
    { level: "Very Unhealthy", min: 201, max: 300, color: "#A35DB5" },
    { level: "Hazardous", min: 301, max: Infinity, color: "#8B3F3F" }
  ];

  const getColor = (d) => {
    const level = aqiLevels.find((l) => d <= l.max);
    return level ? level.color : "#8B3F3F";
  };

  return (x) => htl.html`<div style="
    background: ${getColor(x)};
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    text-align: center;
    font-weight: bold;
    display: inline-block;
    min-width: 40px;
    ">${x}</div>`;
}
```


## City and Stations AQI map

<div class="grid">
  <div class="card">
    ${resize((width) => stationMap(aqi, {
      width,
      MAPBOX_ACCESS_TOKEN: tokens.MAPBOX_ACCESS_TOKEN
      }))}
  </div> 
</div> 


<div class="grid grid-cols-2">
  <div class="card">
  Pakistan cities
  ${cityAqiCards(aqi)}
  </div>

  <div class="card">
  
  ```js
// Search input
const search = view(Inputs.search(ranks, { placeholder: "Search cities..." }));
```

```js
// Use in table
Inputs.table(search, {
  format: {
    rank: (d, i) => search[i].rank,
    city: (city, i) => `${search[i].city}, ${search[i].country}`,
    current_aqi: aqiBox()
  },
  columns: ["rank", "city", "current_aqi"],
  header: {
    rank: "Rank",
    city: "Location",
    current_aqi: "AQI"
  },
  width: {
    rank: 35,
    city: 150,
    //AQI: 50
  },
  style: "flex: 1; overflow-y: auto;"
})
```
  </div>
</div>


# Chart

## Bar plot

Displays 2 days of history and current AQI reading at an hourly resolution.

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => barChart(aqi, { width }))}
  </div>
</div>

## Scatter plot

For each city, displays 2 days of historical AQI, the current reading with a circle to highlight it, and a two day forecasted values to the right of that.
The blue lines are individual station readings.

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => createChart(aqi, { width }))}
  </div>
</div>

<!-- A shared color scale for consistency, sorted by the number of launches -->

```js
const color = Plot.scale({
  color: {
    type: "categorical",
    domain: d3
      .groupSort(
        launches,
        (D) => -D.length,
        (d) => d.state
      )
      .filter((d) => d !== "Other"),
    unknown: "var(--theme-foreground-muted)",
  },
});
```

# Appendix

Charts made but probably not needed, leaving for code sample.

## Cities AQI rankings

```js
// city selector slider
const numCities = view(
  Inputs.range([5, 20], {
    label: "Number of cities",
    step: 5,
    value: 10,
  })
);
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => aqiBarChart(ranks, numCities, {width}))}
  </div>
</div>



## Cards

<!-- Cards with big numbers -->

<!-- Cards with AQI data for Pakistani cities -->

```js
function cityAqiCards(data, numCities=6) {
  const aqiLevels = [
    { level: "Good", min: 0, max: 50, color: "#97C93D" },
    { level: "Moderate", min: 51, max: 100, color: "#FFCF01" },
    { level: "Unhealthy for Sensitive Groups", min: 101, max: 150, color: "#FF9933" },
    { level: "Unhealthy", min: 151, max: 200, color: "#FF3333" },
    { level: "Very Unhealthy", min: 201, max: 300, color: "#A35DB5" },
    { level: "Hazardous", min: 301, max: Infinity, color: "#8B3F3F" }
  ];

  const getAqiColor = (aqi) => {
    const level = aqiLevels.find(l => aqi <= l.max);
    return level ? level.color : "#8B3F3F";
  };

  const cityData = data
    .filter((d) => d.data_source === "city" && d.data_type === "current")
    .sort((a, b) => b.aqius - a.aqius)
    .slice(0, numCities); 

  return htl.html`
    <div class="grid grid-cols-3">
      ${cityData.map(
        (city) => htl.html`
        <div class="card" style="
          background-color: ${getAqiColor(city.aqius)};
          color: white;
          padding: 0.7rem;
          border-radius: 8px;
          margin: 0.2rem;
          text-align: center;
        ">
          <h4 style="font-weight: bold; margin-bottom: 0.3rem;">${city.city}</h4>
          <span style="font-size: 1.3rem; font-weight: bold;">${Math.round(city.aqius)}</span>
          <div style="font-size: 0.875rem; margin-top: 0.5rem;">PM2.5: ${Math.round(city.pm25)}</div>
        </div>
      `
      )}
    </div>
  `;
}
```

${cityAqiCards(aqi)}

