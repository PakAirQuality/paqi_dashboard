---
theme: [light, dashboard]
title: Paqi dashboard
toc: true
---

# Pakistan AQI Dashboard 🚀

<!-- Load and transform the data -->

```js
const launches = FileAttachment("data/launches.csv").csv({ typed: true });
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

## AQI Rankings

```js
function aqi_sparkbar() {
  const max = d3.max(ranks, (d) => d.current_aqi); // get max AQI value

  return (x) => {
    const aqiLevels = [
      { level: "Good", min: 0, max: 50, color: "#97C93D" },
      { level: "Moderate", min: 51, max: 100, color: "#FFCF01" },
      {
        level: "Unhealthy for Sensitive Groups",
        min: 101,
        max: 150,
        color: "#FF9933",
      },
      { level: "Unhealthy", min: 151, max: 200, color: "#FF3333" },
      { level: "Very Unhealthy", min: 201, max: 300, color: "#A35DB5" },
      { level: "Hazardous", min: 301, max: Infinity, color: "#8B3F3F" },
    ];

    const getColor = (d) => {
      const level = aqiLevels.find((l) => d <= l.max);
      return level ? level.color : "#8B3F3F";
    };

    return htl.html`<div style="
      background: ${getColor(x)};
      color: white;
      width: ${(100 * x) / max}%;
      padding: 4px 8px;
      border-radius: 4px;
      text-align: left;
      font-weight: bold;
      ">${x}</div>`;
  };
}
```

```js
// Search input
const search = view(Inputs.search(ranks, { placeholder: "Search cities..." }));
```

```js
// Display table
Inputs.table(search, {
  format: {
    rank: (d, i) => search[i].rank,
    city: (city, i) => `${search[i].city}, ${search[i].country}`,
    current_aqi: aqi_sparkbar(),
  },
  columns: ["rank", "city", "current_aqi"],
  header: {
    rank: "Rank",
    city: "Location",
    current_aqi: "AQI",
  },
  width: {
    rank: 36,
    city: "auto",
    //current_aqi: 300
  },
})
```

${aqiLegend()}


# Station and City data

## City and Stations AQI map

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => stationMap(aqi, {
      width,
      MAPBOX_ACCESS_TOKEN: tokens.MAPBOX_ACCESS_TOKEN
      }))}
  </div>
</div>


# Chart

## Bar plot

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => barChart(aqi, { width }))}
  </div>
</div>

## Box plot

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


<!-- Plot of launch history -->

```js
function launchTimeline(data, { width } = {}) {
  return Plot.plot({
    title: "Launches over the years",
    width,
    height: 300,
    y: { grid: true, label: "Launches" },
    color: { ...color, legend: true },
    marks: [
      Plot.rectY(
        data,
        Plot.binX(
          { y: "count" },
          { x: "date", fill: "state", interval: "year", tip: true }
        )
      ),
      Plot.ruleY([0]),
    ],
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => launchTimeline(launches, {width}))}
  </div>
</div>

<!-- Plot of launch vehicles -->

```js
function vehicleChart(data, { width }) {
  return Plot.plot({
    title: "Popular launch vehicles",
    width,
    height: 300,
    marginTop: 0,
    marginLeft: 50,
    x: { grid: true, label: "Launches" },
    y: { label: null },
    color: { ...color, legend: true },
    marks: [
      Plot.rectX(
        data,
        Plot.groupY(
          { x: "count" },
          { y: "family", fill: "state", tip: true, sort: { y: "-x" } }
        )
      ),
      Plot.ruleX([0]),
    ],
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => vehicleChart(launches, {width}))}
  </div>
</div>

## Cards 

<!-- Cards with big numbers -->

<!-- Cards with AQI data for Pakistani cities -->

```js
function cityAqiCards(data) {
  const cityData = data
    .filter(d => d.data_source === "city" && d.data_type === "current")
    .sort((a, b) => b.aqius - a.aqius);  // Sort by AQI descending
    
  return htl.html`
    <div class="grid grid-cols-4">
      ${cityData.map(city => htl.html`
        <div class="card">
          <h3>${city.city}</h3>
          <span class="big">${Math.round(city.aqius)}</span>
          <div class="text-sm">PM2.5: ${Math.round(city.pm25)} μg/m³</div>
        </div>
      `)}
    </div>
  `;
}
```
${cityAqiCards(aqi)}




Data: Pakistan A