---
title: Emissions
---


```js
const climate = await FileAttachment("data/climate_trace_data_pk_100yr_to_2022.csv").csv({
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

Data sourced from [Climate Trace](https://climatetrace.org/data) 2022 emissions data for Pakistan. Climate TRACE provides emissions data covering global emissions from 2015-2022.

_May exclude emissions from sources currently only measured at the country level._

## Emission data table

```js
// Search input
const search = view(Inputs.search(climate, { placeholder: "Search ..." }));
```

```js
// Display table
Inputs.table(search, {
    columns: ["source_name", "source_type", "original_inventory_sector", "gas", "emissions_quantity", "emissions_factor", "capacity", "capacity_units", "activity", "activity_units"]
})
```




