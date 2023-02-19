# mountain-tools

This is a tool to colour Scottish mountain slopes in the standard avalanche forecast colours.
It doesn't actively link to any forecasts. It uses the SAIS website to draw a pretty forecast diagram, but only from the data you input!

The elevation dataset used was downlaoded from Copernicus, and is eu_dem_v11_E30N30. It was then trimmed down to the most mountainous areas.
QGIS 3.28.2 was used to process this into avalanche zones, and .model3 files are provided with a few approaches.
sais_categorisation_3.model3 runs the fastest but on the whole of scotland dataset sometimes trips up, in which case manual processing can be done:
- generate elevation polygons in increments of 100m
- generate slope and aspect rasters
- create slope polygons with increments of 25 degrees and discard all but the 25-50 deg zones
- expand these polygons and use them to trim the aspect raster
- create aspect polygons in increments of 45 deg, starting at 22.5 deg
- intersect the aspect and slope polygons
- fix the geometry and remove any areas < 2500m2
- intersect with the elevation polygons
- fix the geometry and remove any areas < 2500m2
- simplify the geometry to the nearest 25m
- convert to the 4326 coordinate system while exporting a .gpkg file