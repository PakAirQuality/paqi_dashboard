---
theme: dashboard
title: Beta Graphs in development
toc: true
---

<!-- Load and transform the data -->

```js
import { aqiLegend } from "./components/aqi_legend.js";
const ranks = FileAttachment("data/aqi_ranks.csv").csv({ typed: true });
const aqi = FileAttachment("data/aqi.csv").csv({ typed: true });
const countryData = await FileAttachment("data/countries.csv").csv({
  typed: true,
});
const tokens = await FileAttachment("data/tokens.json").json({ typed: true });
//console.log("Loaded tokens:", tokens);
```


# City Comparisons

Here's a comparison of PM2.5 levels across different cities in Pakistan:

```js
import { cityComparison } from "./components/city.js";
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => cityComparison(aqi, { width }))}
  </div>
</div>


# City Rankings

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

# Simpler City Ranking

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
  }
})
```
