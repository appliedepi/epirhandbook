# modify the ebola_sim linelist from outbreaks package
######################################################
pacman::p_load(tidyverse, rio, here, incidence, outbreaks, lubridate)

# parts of evd
evd_sim    <- outbreaks::ebola_sim$linelist
evd_sim_tl <- outbreaks::ebola_sim$contacts

# make evd, with contacts transmissions as variables in the linelist
evd <- evd_sim %>% 
     full_join(evd_sim_tl, "case_id")

# plot evd
epicurve_weekly  <- incidence::incidence(evd$date_of_onset, interval = "Monday week", groups = evd$gender)
plot(epicurve_weekly)





# ADD AGE (different means by gender)
#####################################

# Make age for males
ages_m <- round(abs(rnorm(n = nrow(evd %>% filter(gender == "m")), mean = 15, sd = 20)))
hist(ages_m)


# make ages for females
ages_f <- round(abs(rnorm(n = nrow(evd %>% filter(gender == "f")), mean = 5, sd = 15)))
hist(ages_f)

ages_m_in <- ages_m[ages_m < 2]
ages_m_ch <- ages_m[ages_m >= 2 & ages_m <= 5]
ages_m_tn <- ages_m[ages_m > 5 & ages_m < 15]
ages_m_ad <- ages_m[ages_m >= 15]

ages_f_in <- ages_f[ages_f < 2]
ages_f_ch <- ages_f[ages_f >= 2 & ages_f <= 5]
ages_f_tn <- ages_f[ages_f > 5 & ages_f < 15]
ages_f_ad <- ages_f[ages_f >= 15]

ages_m <- c(ages_m_in, ages_m_ch, ages_m_tn, ages_m_ad)
ages_f <- c(ages_f_in, ages_f_ch, ages_f_tn, ages_f_ad)

ages <- c(ages_m, ages_f)

library(faux)

# make weights
wt_m_in <- rnorm_pre(ages_m_in, mu = 15, sd = 3, r = 0.7)
wt_m_ch <- rnorm_pre(ages_m_ch, mu = 40, sd = 10, r = 0.8)
wt_m_tn <- rnorm_pre(ages_m_tn, mu = 55, sd = 10, r = 0.8)
wt_m_ad <- rnorm_pre(ages_m_ad, mu = 70, sd = 10, r = 0.8)

wt_f_in <- rnorm_pre(ages_f_in, mu = 13, sd = 10, r = 0.8)
wt_f_ch <- rnorm_pre(ages_f_ch, mu = 35, sd = 10, r = 0.8)
wt_f_tn <- rnorm_pre(ages_f_tn, mu = 45, sd = 10, r = 0.8)
wt_f_ad <- rnorm_pre(ages_f_ad, mu = 60, sd = 10, r = 0.8)

wt_kg_m <- c(wt_m_in, wt_m_ch, wt_m_tn, wt_m_ad)
plot(ages_m, wt_kg_m)

wt_kg_f <- c(wt_f_in, wt_f_ch, wt_f_tn, wt_f_ad)
plot(ages_f, wt_kg_f)

wt_kg <- c(wt_kg_m, wt_kg_f)
plot(ages, wt_kg)
cor(ages, wt_kg)


# make heights
ht_m_in <- rnorm_pre(ages_m_in, mu = 40, sd = 8, r = 0.7)
ht_m_ch <- rnorm_pre(ages_m_ch, mu = 70, sd = 15, r = 0.8)
ht_m_tn <- rnorm_pre(ages_m_tn, mu = 130, sd = 20, r = 0.8)
ht_m_ad <- rnorm_pre(ages_m_ad, mu = 170, sd = 30, r = 0.8)

ht_f_in <- rnorm_pre(ages_f_in, mu = 30, sd = 10, r = 0.8)
ht_f_ch <- rnorm_pre(ages_f_ch, mu = 60, sd = 15, r = 0.8)
ht_f_tn <- rnorm_pre(ages_f_tn, mu = 110, sd = 20, r = 0.8)
ht_f_ad <- rnorm_pre(ages_f_ad, mu = 150, sd = 30, r = 0.8)

ht_cm_m <- c(ht_m_in, ht_m_ch, ht_m_tn, ht_m_ad)
plot(ages_m, ht_cm_m)

ht_cm_f <- c(ht_f_in, ht_f_ch, ht_f_tn, ht_f_ad)
plot(ages_f, ht_cm_f)

ht_cm   <- c(ht_cm_m, ht_cm_f)
plot(ages, ht_cm)
cor(ages, ht_cm)

demographics <- data.frame(
        evd$gen
)

# add age (split database by gender, add demographics, then re-join)
evd_m <- evd %>% filter(gender == "m")
evd_m <- evd_m[sample(nrow(evd_m)),]
evd_m <- evd_m %>% 
     mutate(age = ages_m,
            wt_kg = wt_kg_m,
            ht_cm = ht_cm_m)

evd_f <- evd %>% filter(gender == "f")
evd_f <- evd_f[sample(nrow(evd_f)),]
evd_f <- evd_f %>% 
     mutate(age = ages_f,
            wt_kg = wt_kg_f,
            ht_cm = ht_cm_f)

evd <- bind_rows(evd_m, evd_f) %>% 
        arrange(date_of_onset)

# run tests
t.test(data = evd, age ~ gender)
cor(evd$age, evd$ht_cm)
plot(evd$age, evd$ht_cm)

t.test(data = evd, wt_kg ~ gender)
cor(evd$age, evd$wt_kg)
plot(evd$age, evd$wt_kg)

ggplot(data = evd)+
        geom_point(aes(x = age, y = wt_kg, color = gender))+
        facet_wrap(~gender)



# ADD CT VALUE
##############
# add delay
evd <- evd %>%
        # difference in days between onset and hospitalisation
        mutate(onset_to_hosp_days = as.numeric(date_of_hospitalisation - date_of_onset)) %>% 
        mutate(delay_short_long   = ifelse(onset_to_hosp_days <= mean(onset_to_hosp_days, na.rm=T), "short", "long"))

table(evd$delay_short_long)

hist(evd$onset_to_hosp_days, breaks = 30)


# Make CT for short delay
ct_short <- round(abs(rnorm(n = nrow(evd %>% filter(delay_short_long == "short")), mean = 22, sd = 1)))
hist(ct_short)

# make CT for long delay
ct_long <- round(abs(rnorm(n = nrow(evd %>% filter(delay_short_long == "long")), mean = 19, sd = 1)))
hist(ct_long)


# add CT (split database by delay, add ages, then re-join)
evd_ct_short <- evd %>% filter(delay_short_long == "short") %>% 
        mutate(ct_blood = ct_short)

evd_ct_long <- evd %>% filter(delay_short_long == "long") %>% 
        mutate(ct_blood = ct_long)

evd <- bind_rows(evd_ct_short, evd_ct_long)

# run t-test
t.test(data = evd, ct_blood ~ delay_short_long)
ggplot(data = evd,
       mapping = aes(y = ct_blood, x = onset_to_hosp_days))+
        geom_density_2d()+
        ggtitle("D) SCATTER PLOT made using ggplot()")





# add years/months column
#########################
# set default as "years"
evd$age_unit <- "years"

# get random entries to change to months
to_months <- round(rnorm(n=round(nrow(evd)*.005),  mean=nrow(evd)*.5, sd=1000)) # 0.5% of rows
to_months <- to_months[to_months < nrow(evd) & to_months > 0]        # ensure indices are in appropriate range

# get months numbers
months_nums <- sample(c(seq(1:12), 18, 24, 36), size = length(to_months), replace = T)

# replace ages with months numbers
evd$age[to_months]      <- months_nums
evd$age_unit[to_months] <- "months" 

table(evd$age_unit, evd$age)


# GENDER MISSING
################
# random indices to convert to missing:
to_NA_gender <- round(rnorm(n=round(nrow(evd)*.05),  # 5% of entries
                   mean=nrow(evd)*.5,             # mean 1/2 way 
                   sd=1000))
to_NA_gender <- to_NA_gender[to_NA_gender < nrow(evd) & to_NA_gender > 0] # ensure indices are in appropriate range


evd$gender[to_NA_gender] <- NA                       # now replace those indices in foo with NA



# AGE MISSING
#############
# set missing ages as subset of missing gender
to_NA_age <- sample(to_NA_gender, size = round(length(to_NA_gender)*0.3), replace = F)
evd$age[to_NA_age] <- NA

table(is.na(evd$age), is.na(evd$gender))


# ONSET MISSING
###############
# random indices to convert to missing:
to_NA_onset <- round(rnorm(n=round(nrow(evd)*.08),  # 10% of entries
                         mean=nrow(evd)*.4,    # mean **earlier** in the outbreak 
                         sd=1000))
to_NA_onset <- to_NA_sym[to_NA_onset < nrow(evd) & to_NA_onset > 0] # ensure indices are in appropriate range
evd$date_of_onset[to_NA_onset] <- NA



# ADD SYMPTOMS VARIABLES
########################
evd <- evd %>% 
        mutate(fever  = sample(c("yes", "no"), nrow(evd), replace = T, prob = c(0.80, 0.20)),
               chills = sample(c("yes", "no"), nrow(evd), replace = T, prob = c(0.20, 0.80)),
               cough  = sample(c("yes", "no"), nrow(evd), replace = T, prob = c(0.9, 0.15)),
               aches  = sample(c("yes", "no"), nrow(evd), replace = T, prob = c(0.10, 0.90)),
               vomit = sample(c("yes", "no"), nrow(evd), replace = T))

# SYMPTOMS MISSING
# random indices to convert to missing:
to_NA_sym <- round(rnorm(n=round(nrow(evd)*.05),  # 5% of entries
                            mean=nrow(evd)*.2,    # mean **earlier** in the outbreak 
                            sd=1000))
to_NA_sym <- to_NA_sym[to_NA_sym < nrow(evd) & to_NA_sym > 0] # ensure indices are in appropriate range


evd$fever[to_NA_sym] <- NA                       # now replace those indices in foo with NA
evd$chills[to_NA_sym] <- NA                       
evd$cough[to_NA_sym] <- NA                       
evd$aches[to_NA_sym] <- NA                       
evd$vomit[to_NA_sym] <- NA




# add temperature
#################
# Make temp for no fever
temp_normal <- abs(rnorm(n = nrow(evd %>% filter(fever == "no" | is.na(fever))), mean = 37, sd = 0.5))
temp_normal <- temp_normal[temp_normal < 38 & temp_normal > 35]    # ensure appropriate range
temp_normal <- c(temp_normal, rep(NA,    # fill in with NA to get right length
                                  (nrow(evd %>% filter(fever == "no" | is.na(fever))) - length(temp_normal))
                                  )
)
hist(temp_normal)

# make temp for fever
temp_fever <- abs(rnorm(n = nrow(evd %>% filter(fever == "yes")), mean = 39, sd = 0.5))
temp_fever <- temp_fever[temp_fever < 41 & temp_fever > 38]    # ensure appropriate range
temp_fever <- c(temp_fever, rep(NA,    # fill in with NA to get right length
                                  (nrow(evd %>% filter(fever == "yes")) - length(temp_fever))
)
)

hist(temp_fever)


# add temp (split database by delay, add ages, then re-join)
evd_temp_norm <- evd %>% filter(fever == "no" | is.na(fever)) %>% 
        mutate(temp = temp_normal)

evd_temp_fv <- evd %>% filter(fever == "yes") %>% 
        mutate(temp = temp_fever)

evd <- bind_rows(evd_temp_norm, evd_temp_fv)

# run t-test
t.test(data = evd, temp ~ fever)
ggplot(data = evd,
       mapping = aes(y = temp, x = temp))+
        geom_density_2d()+
        ggtitle("D) SCATTER PLOT made using ggplot()")

table(evd$fever)


### Add 3 blank rows to bottom (to be filtered out)
###################################################
evd[nrow(evd)+1,] <- NA
evd[nrow(evd)+1,] <- NA
evd[nrow(evd)+1,] <- NA

### ADD ROWS TO BE FILTERED OUT (from another outbreak years before)
###############################
outbreak2_rownums <- round(rnorm(n=round(nrow(evd)*.10)+1,  # 5% of entries
                                 mean=nrow(evd)*.5,    # mean middle of the outbreak 
                                 sd=1000))

outbreak2_rownums <- outbreak2_rownums[outbreak2_rownums > 0]
hist(outbreak2_rownums)
outbreak2 <- evd[outbreak2_rownums, ] # new outbreak data

hist(outbreak2$date_of_infection, 50)
range(outbreak2$date_of_infection, na.rm=T)

# reduce dates by 2 years
outbreak2 <- outbreak2 %>% mutate(across(contains("date"), lubridate::ymd)) %>%
        mutate(date_of_onset = date_of_onset - lubridate::years(2),
               date_of_hospitalisation = date_of_hospitalisation - lubridate::years(2),
               date_of_infection = date_of_infection - lubridate::years(2),
               date_of_outcome = date_of_outcome - lubridate::years(2),
               
               hospital = rep(c("Hospital A", "Hospital B"), nrow(outbreak2)/2))
outbreak2[1:10,"hospital"] <- "Connaught Hospital"  # add hospital to some

range(outbreak2$date_of_infection, na.rm=T)
table(outbreak2$hospital, useNA = "always")
table(lubridate::year(outbreak2$date_of_onset), useNA = "always")

evd <- rbind(evd, outbreak2) #rbind the second outbreak rows

hist(evd$date_of_onset, 50)
table(evd$hospital, useNA = "always")

### ADD COLUMN TO BE REMOVED
############################
evd$row_num <- seq(1:nrow(evd))
evd <- select(evd, row_num, everything())
# 
# # LOCATION COORDINATES (TO DO)
# ######################
# # coordinates of evd
# range(evd$lon, na.rm=T)
# pacman::p_load("rnaturalearth")
# pacman::p_load("rnaturalearthdata", "rgeos")
# 
# world <- ne_countries(scale = "medium", returnclass = "sf")
# 
# ggplot(data = world) +
#      geom_sf() +
#      geom_point(data = evd, aes(x = lon, y = lat), size = 4, 
#                 shape = 23, fill = "darkred") +
#      coord_sf(xlim = c(-15, -13.0), ylim = c(7, 10), expand = FALSE)
# 


# make column names messy
evd <- evd %>% 
     rename(`infection date` = date_of_infection,
            `date onset` = date_of_onset,
            `hosp date` = date_of_hospitalisation)


# CLASSES
##########
evd$`date onset` <- as.character(evd$`date onset`)
#evd$`date onset`[1] <- "15th April 2014"
class(evd$`date onset`)

evd$age <- as.character(evd$age)


### ADD data dictionary row !!!
### CANCEL - this is done only as a demonstration in the cleaning page now (dec 29 2020 NB)
# evd <- evd %>% 
#         mutate(across(everything(), as.character)) %>% 
#         add_row(.before = 1,
#                 row_num = "000",
#                 case_id = "case identification number assigned by MOH",
#                 generation = "transmission chain generation number",
#                 `infection date` = "estimated date of infection, mm/dd/yyyy",
#                 `date onset` = "date of symptom onset, YYYY-MM-DD",
#                 `hosp date` = "date of initial hospitalization, mm/dd/yyyy",
#                 date_of_outcome = "date of outcome status determination",
#                 outcome = "either 'Death' or 'Recovered' or 'Unknown'",
#                 gender = "either 'm' or 'f' or 'unknown'",
#                 hospital = "Name of hospital of first admission",
#                 lon = "longitude of residence, approx",
#                 lat = "latitude of residence, approx",
#                 infector = "case_id of infector",
#                 source = "context of known transmission event",
#                 age = "age number",
#                 age_unit = "age unit, either 'years' or 'months' or 'days'",
#                 fever = "presence of fever on admission, either 'yes' or 'no'",
#                 chills = "presence of chills on admission, either 'yes' or 'no'",
#                 cough = "presence of cough on admission, either 'yes' or 'no'",
#                 aches = "presence of aches on admission, either 'yes' or 'no'",
#                 vomit = "presence of vomiting on admission, either 'yes' or 'no'"
#                 )

### CHANGE HOSPITAL NAMES ###
evd <- evd %>% 
        mutate(hospital = recode(hospital,
                # OLD = NEW
                "Connaught Hopital" = "Port Hopital",
                "Connaught Hospital" = "Port Hospital",
                "Rokupa Hopital"    = "Central Hopital",
                "Rokupa Hospital"   = "Central Hospital",
                "other"             = "Other",
                "Princess Christian Maternity Hopital (PCMH)" = "St. Marks Maternity Hopital (SMMH)",
                "Princess Christian Maternity Hospital (PCMH)" = "St. Mark's Maternity Hospital (SMMH)"))

### ADD COLUMN: TIME OF ADMISSION
 # Hours:
evd <- evd %>% 
        mutate(hours = round(rnorm(n=nrow(evd), mean=13, sd=4)),   # avg 1pm
               hours = ifelse(hours>24 | hours < 0, NA, hours),   
               hours = str_pad(hours, 2, pad = "0"),             # pad with leading zeros
               minutes = round(rnorm(n=nrow(evd), mean=30, sd=20)),
               minutes = ifelse(minutes>60 | minutes <0, NA, minutes),
               minutes = str_pad(minutes, 2, pad = "0"),
               
               time_admission = str_c(hours, minutes, sep = ":")
               ) %>% 
        select(-hours, -minutes)



### ADD DUPLICATE ROWS
######################
duplicate_rownums <- round(rnorm(n=round(nrow(evd)*.02),  # 2% of entries
                                 mean=nrow(evd)*.5,    # mean middle of the outbreak 
                                 sd=1000))
hist(duplicate_rownums)
dups <- evd[duplicate_rownums, ] %>% 
        mutate(case_id = " ")
        
        
evd <- rbind(evd, dups) #rbind the same rows

### Add merged column header cells !!!
# DO THIS IN EXCEL AFTER EXPORTING. Add two extra columns and merge the column names. They will be removed in the cleaning page. 
# "Merged header" and then underneath two columns each saying "this is under a merged header"



# round weight and height and temp values
evd <- evd %>% 
        mutate(wt_kg = round(wt_kg),
               ht_cm = round(ht_cm),
               temp  = round(temp,1))


# remove other columns
evd <- select(evd, case_id:age, age_unit, everything()) %>% 
        select(-onset_to_hosp_days, -delay_short_long)
head(evd, 10)

# checks
##########

table(Hospital  = evd$hospital,                     # hospital name
      YearOnset = lubridate::year(evd$`date onset`),  # year of date_onset
      useNA     = "always")                              # show missing values


# export
rio::export(evd, here::here("data", "linelist_raw.xlsx"))


#################################################################################
#################################################################################
#################################################################################


#### Make alerts linelist  


