# Makes the two example maps in the GIS chapter gallery: a dot density map and a
# proportional symbols map. Both use the same 1000 sampled Ebola cases and the
# Western Area admin level 3 areas, the data the chapter itself uses.
# Re-run with: Rscript data/gis/make_gis_examples.R
# Output folder: the GIS_EXAMPLES_OUT environment variable, or images/ when unset.

library(dplyr)
library(ggplot2)
library(sf)

out <- Sys.getenv("GIS_EXAMPLES_OUT", here::here("images"))
dir.create(out, recursive = TRUE, showWarnings = FALSE)

d <- appliedepidata::get_data(name = "sle_adm3") %>%
  janitor::clean_names() %>%
  filter(admin2name %in% c("Western Area Urban", "Western Area Rural"))

d1 <- appliedepidata::get_data(name = "linelist_cleaned_rds")
set.seed(1)
d1 <- d1[sample(nrow(d1), 1000), ]
d1 <- st_as_sf(d1, coords = c("lon", "lat"), crs = 4326)

d2 <- d1 %>%
  st_join(d, join = st_intersects) %>%
  st_drop_geometry() %>%
  filter(!is.na(admin3pcod)) %>%
  count(admin3pcod, name = "cases")

# all 12 areas keep a row, so an area with no sampled case scores 0 rather than dropping out
# centroids taken in UTM zone 28N, a projected CRS that covers Sierra Leone, then sent back to WGS84
pd <- d %>%
  left_join(d2, by = "admin3pcod") %>%
  mutate(cases = tidyr::replace_na(cases, 0)) %>%
  st_transform(32628) %>%
  st_centroid() %>%
  st_transform(4326)
stopifnot(nrow(pd) == 12)

# window on the Freetown peninsula; it holds all 1000 sampled cases
xlim <- c(-13.30, -13.16)
ylim <- c(8.415, 8.502)

thm <- theme_minimal(base_size = 14) +
  theme(
    axis.line = element_line(colour = "black", linewidth = 0.6),
    axis.ticks = element_line(colour = "black", linewidth = 0.6),
    axis.ticks.length = unit(3.5, "pt"),
    axis.text = element_text(colour = "black"),
    axis.title = element_text(colour = "black"),
    legend.position = "bottom"
  )

q <- ggplot() +
  geom_sf(data = d, fill = "#f7f7f7", colour = "grey40", linewidth = 0.35) +
  geom_sf(data = d1, aes(colour = "Case"), size = 1.2, alpha = 0.45) +
  scale_colour_manual(name = NULL, values = c("Case" = "#08519c")) +
  coord_sf(xlim = xlim, ylim = ylim, expand = FALSE) +
  thm +
  labs(
    title = "Dot density map",
    caption = stringr::str_wrap(
      "1000 cases sampled from the Ebola linelist, drawn over the Western Area admin level 3 areas.",
      95
    )
  )
ggsave(
  file.path(out, "gis_dot_density.png"),
  q,
  width = 10,
  height = 7,
  dpi = 115
)

q <- ggplot() +
  geom_sf(data = d, fill = "#f7f7f7", colour = "grey40", linewidth = 0.35) +
  geom_sf(data = pd, aes(size = cases), colour = "#cb181d", alpha = 0.55) +
  scale_size_area(name = "Cases", max_size = 26, breaks = c(25, 100, 200)) +
  coord_sf(xlim = xlim, ylim = ylim, expand = FALSE) +
  thm +
  labs(
    title = "Proportional symbols map",
    caption = stringr::str_wrap(
      sprintf(
        "Circle area is proportional to the case count. %d of the 1000 sampled cases fall inside the Western Area admin level 3 areas. %d of the %d areas have no sampled case and no circle.",
        sum(pd$cases),
        sum(pd$cases == 0),
        nrow(pd)
      ),
      95
    )
  )
ggsave(
  file.path(out, "gis_proportional_symbols.png"),
  q,
  width = 10,
  height = 7,
  dpi = 115
)
