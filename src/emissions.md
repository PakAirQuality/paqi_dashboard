---
title: Emissions
---

```js
const climate = await FileAttachment(
  "data/climate_trace_data_pk_100yr_to_2022.csv"
).csv({
  typed: true,
});
const tokens = await FileAttachment("data/tokens.json").json({ typed: true });
//console.log("Loaded tokens:", tokens);
```

```js
import { climateMap } from "./components/climate_map.js";
```

# Greenhouse emissions - 2022

Pakistan CO2 emissions plotted on a map.

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => climateMap(climate, {
      width,
      MAPBOX_ACCESS_TOKEN: tokens.MAPBOX_ACCESS_TOKEN
    }))}
  </div>
</div>

## Important Notes About This Data

### Current Status:

* 📅 Data shown is for 2022 only
* ⚠️ Dataset is currently incomplete and being updated (may exclude emissions from some sources)
* 🔄 Emissions categorization is in progress

### Upcoming Improvements:

* Expanding data coverage
* Adding detailed emissions categories (gas, cement, oil, etc.)
* Implementing better visualization of emission types
* Regular updates with latest available data

Data Disclaimer: This is a beta version of our emissions map. We're continuously working to improve data accuracy and completeness.

## Emission data table

```js
// Search input
const search = view(Inputs.search(climate, { placeholder: "Search ..." }));
```

```js
// Display table
Inputs.table(search, {
  columns: [
    "source_name",
    "source_type",
    "original_inventory_sector",
    "gas",
    "emissions_quantity",
    "emissions_factor",
    "capacity",
    "capacity_units",
    "activity",
    "activity_units",
  ],
});
```
