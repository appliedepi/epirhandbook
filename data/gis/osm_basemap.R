# Fetch the OpenStreetMap basemap that chapters/gis.qmd shows, once, and save it.
# Source: tile.openstreetmap.org via OpenStreetMap::openmap(), type "osm". Last fetched
# 2026-09-02 with OpenStreetMap 0.4.1 on R 4.6.0. Licence: ODbL, (c) OpenStreetMap
# contributors. The saved object is the package's own S3 class ("OpenStreetMap": a
# list of tiles with hex colour vectors, a bbox and a projection string), so it stays
# readable across package versions as long as autoplot.OpenStreetMap() keeps that shape.
# chapters/gis.qmd shows PNG images made from this file on 2026-09-02. They are
# images/gis_basemap_01_mercator.png to images/gis_basemap_05_density_month.png. The
# chapter does not read the .rds while it renders. Keep this file so that the images
# can be made again. The bounds are those of the whole linelist, so they cover any
# random sample the chapter draws.
# Re-run from the repository root when the basemap needs a refresh:
#   Rscript data/gis/osm_basemap.R
linelist <- rio::import(here::here("data", "case_linelists", "linelist_cleaned.rds"), trust = TRUE)

map <- OpenStreetMap::openmap(
  upperLeft = c(max(linelist$lat, na.rm = TRUE), max(linelist$lon, na.rm = TRUE)),
  lowerRight = c(min(linelist$lat, na.rm = TRUE), min(linelist$lon, na.rm = TRUE)),
  zoom = NULL,
  type = "osm")

saveRDS(map, here::here("data", "gis", "osm_basemap.rds"))
