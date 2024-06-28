# weekly-report

This directory contains all the scripts required to produce the weekly PDF reporting.

## Files

| File Name | Description |
|---|---|
| **main.tf** | Builds infrastructure for cloud migration |
| **main.py** | Creates PDF report embed with Altair visuals |
| **dockerfile**  | Builds docker image |
| **visuals.py** | Fetches data from database and produces Altair visuals |
| **test_visuals.py**  | Test file for visuals.py |

## State Map Visual

An Altair visual was produced to assess the level of risk associated with living in a particular US state.
Red pose a higher risk, whilst yellow a moderate risk.
All greyed out states have no recorded earthquakes.

An example is illustrated below:

![Example State Map Visual](https://github.com/fm1psy/c11-poseidon-earthquake-monitoring/blob/main/diagrams/us_state_map.png)

### Key Files

US State Shapefile: https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html

### Assumptions

To determine the risk score associated with living in a US state susceptible to earthquakes a risk metric was calculated as function of 4 different parameters, with each parameter assigned a _risk weighting_ score dictating their contribution to the final overall score.

| Parameter | Risk Weighting |
|---|---|
| **number of earthquakes** | 0.2 | 
| **average magnitude** | 0.3 |
| **max magnitude** | 0.4 | 
| **average depth** | 0.1 |


