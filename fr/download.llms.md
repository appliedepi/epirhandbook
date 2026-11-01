# 2  Télécharger le manuel et les données

## 2.1 Télécharger le manuel hors-ligne

Vous pouvez télécharger ce manuel et le lire sans connexion Internet. Chaque langue est un fichier zip qui contient tout le site : chaque chapitre, chaque image et la barre de navigation.

- Téléchargez le fichier zip de votre langue, puis décompressez-le.
- Ouvrez `index.html` dans le dossier décompressé pour commencer la lecture.
- Consultez la page [Paquets conseillés](packages_suggested.llms.md) pour installer les paquets R dont vous avez besoin avant de perdre votre connexion.

**Pour télécharger le manuel :**

[Télécharger le manuel (zip)](https://github.com/appliedepi/epirhandbook/releases/download/offline/epirhandbook-fr.zip)

Le fichier zip est reconstruit automatiquement : il suit donc toujours la dernière version du manuel.

## 2.2 Télécharger les données

Pour reproduire les exemples du manuel, vous pouvez charger les données d’exemple directement dans R avec notre paquet R compagnon, **appliedepidata**. Il contient tous les jeux de données utilisés dans les exemples de ce manuel.

### Installer le paquet

**appliedepidata** n’est pas sur le CRAN ; installez-le depuis son [dépôt Github](https://github.com/appliedepi/appliedepidata) avec **pak** :

``` r
# installer la dernière version du paquet appliedepidata
pak::pak("appliedepi/appliedepidata")
```

### Charger un jeu de données directement

Utilisez `get_data()` avec le `name =` du jeu de données pour le charger directement dans R — sans téléchargement, sans chemin de fichier, sans étape `import()`. La fonction renvoie le jeu de données sous forme d’objet R (un tableau de données, un objet `sf`, un arbre `phylo`, etc., selon le jeu de données).

``` r
# charger la linelist nettoyée directement dans R
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

Chaque page de ce manuel qui utilise des données d’exemple indique l’appel `get_data(name = "...")` nécessaire pour cette page, à l’endroit où les données sont utilisées pour la première fois.

### Enregistrer un jeu de données dans un fichier

Certaines pages vous apprennent à importer un *fichier* (par exemple un classeur Excel, ou un dossier de fichiers) plutôt qu’un objet R. Pour celles-ci, utilisez `save_data()` avec `name =` et `path =` pour écrire le ou les fichiers réels dans un dossier de votre choix :

``` r
# écrire le fichier Excel de la linelist brute dans votre répertoire de travail
appliedepidata::save_data(name = "case_linelists_linelist_raw", path = getwd())
```

Vous pouvez ensuite l’importer avec `import()` comme n’importe quel fichier de votre ordinateur — voir la page [Importer et exporter des données](importing.llms.md) pour plus de détails. Notez que `save_data()` ne décompresse pas automatiquement les jeux de données distribués sous forme d’archive .zip (par exemple les shapefiles composés de plusieurs fichiers, ou les dossiers de fichiers) ; utilisez ensuite `utils::unzip()` sur le .zip enregistré.

### Parcourir les données disponibles

- `appliedepidata::search_data()` lance une application Shiny interactive pour filtrer et rechercher tous les jeux de données du paquet par langue et par mot-clé.
- `appliedepidata::list_data()` renvoie un tableau de données listant tous les noms de jeux de données, pour une utilisation dans vos scripts.

``` r
# parcourir les jeux de données de façon interactive
appliedepidata::search_data()

# lister tous les noms de jeux de données
appliedepidata::list_data()
```

Si vous le souhaitez, vous pouvez consulter les fichiers de données bruts dans le **[dossier “data”](https://github.com/appliedepi/appliedepidata/tree/main/inst/extdata)** du dépôt Github du paquet **appliedepidata**.

### Référence des jeux de données, par page

Vous trouverez ci-dessous le nom à utiliser avec `get_data()`/`save_data()` pour les données d’exemple citées sur chaque page de ce manuel.

#### Liste de cas (linelist)

Il s’agit d’une linelist pour une épidémie d’Ebola fictive, développée par notre équipe à partir du jeu de données d’exemple `ebola_sim` du paquet **outbreaks**.

La liste de cas “brute” est une feuille de calcul Excel contenant des données désordonnées. Utilisez-la pour suivre la page [Nettoyer les données et fonctions essentielles](cleaning.llms.md).

``` r
# the "raw" linelist - an Excel spreadsheet with messy data
# use this to follow along with the Cleaning data and core functions page
raw_linelist <- appliedepidata::get_data(name = "case_linelists_linelist_raw")

# the "clean" linelist - an R-specific .rds file that preserves column classes
# use this for all other pages of this handbook that use the linelist
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")

# the "clean" linelist, as an Excel file instead
linelist_excel <- appliedepidata::get_data(name = "linelist_cleaned_excel")
```

Une partie de la page sur le nettoyage des données utilise un “dictionnaire de nettoyage” (fichier .csv). Vous pouvez le charger directement dans R en exécutant les commandes suivantes :

``` r
cleaning_dict <- appliedepidata::get_data(name = "case_linelists_cleaning_dict")
```

#### Manipuler les dates

La page [Manipuler les dates](dates.llms.md) utilise des nombres de cas par district et par date :

``` r
counts <- appliedepidata::get_data(name = "example_district_weekly_count_data")
```

#### Fonctions d’écriture

La page [Fonctions d’écriture](writing_functions.llms.md) utilise une liste de cas de l’épidémie de grippe H7N9 de 2013 en Chine :

``` r
flu_china <- appliedepidata::get_data(name = "fluH7N9_China_2013")
```

#### Itération, boucles et listes

La page [Itération, boucles et listes](iteration.llms.md) importe un classeur Excel avec une feuille par hôpital. Enregistrez-le d’abord dans un fichier :

``` r
appliedepidata::save_data(name = "example_hospital_linelists", path = getwd())
```

#### Importer et exporter des données

La page [Importer et exporter des données](importing.llms.md) importe la liste de cas depuis des fichiers Excel. Enregistrez-les d’abord dans des fichiers :

``` r
# la liste de cas brute
appliedepidata::save_data(name = "linelist_raw", path = getwd())

# la liste de cas nettoyée
appliedepidata::save_data(name = "linelist_cleaned", path = getwd())
```

#### Cas de paludisme

Ces données sont des comptages fictifs de cas de paludisme par groupe d’âge, établissement et jour. Un fichier .rds est un type de fichier spécifique à R qui préserve les classes de colonnes. Cela garantit que vous n’aurez qu’un nettoyage minimal à faire après avoir importé les données dans R.

``` r
malaria_data <- appliedepidata::get_data(name = "malaria_facility_count_data")
```

#### Données sur l’échelle de Likert

Il s’agit de données fictives issues d’une enquête de type Likert, utilisées dans la page [Pyramides démographiques et échelles de Likert](age_pyramid.llms.md). Vous pouvez charger ces données directement dans R en exécutant les commandes suivantes :

``` r
likert_data <- appliedepidata::get_data(name = "likert_data")
```

#### Flexdashboard

Vous trouverez ci-dessous des liens vers les fichiers associés à la page [Tableaux de bord avec R Markdown](flexdashboard.llms.md). Il s’agit de fichiers sources R Markdown/HTML, et non de jeux de données d’exemple ; ils ne font donc pas partie du paquet **appliedepidata** - téléchargez-les directement depuis Github :

- Pour télécharger le fichier RMarkdown (.Rmd) du tableau de bord sur les épidémies, faites un clic droit sur ce [lien](https://github.com/appliedepi/epirhandbook/raw/main/data/flexdashboard/outbreak_dashboard.Rmd) (Cmd+clic pour Mac) et sélectionnez “Enregistrer le lien sous”.  
- Pour télécharger le tableau de bord HTML, cliquez avec le bouton droit de la souris sur ce [lien](https://github.com/appliedepi/epirhandbook/raw/main/data/flexdashboard/outbreak_dashboard_test.html). (Cmd + clic pour Mac) et sélectionnez “Enregistrer le lien sous”.

#### Recherche des contacts

La page [Recherche des contacts](contact_tracing.llms.md) analyse des exemples de données de recherche des contacts provenant de [Go.Data](https://github.com/WorldHealthOrganization/godata/tree/master/analytics/r-reporting). Ces données font partie de **appliedepidata** :

``` r
# données d'investigation des cas
cases <- appliedepidata::get_data(name = "cases_clean")

# données d'enregistrement des contacts
contacts <- appliedepidata::get_data(name = "contacts_clean")

# données de suivi des contacts
followups <- appliedepidata::get_data(name = "followups_clean")

# liens entre les cas et les contacts
relationships <- appliedepidata::get_data(name = "relationships_clean")
```

***NOTE:*** Les données structurées de recherche des contacts provenant d’autres logiciels (par exemple KoBo, DHIS2 Tracker, CommCare) peuvent être organisées différemment. Si vous souhaitez contribuer à l’élaboration d’un échantillon de données ou d’un contenu alternatif pour cette page, veuillez [nous contacter](index.llms.md).

***TIP:*** Si vous déployez Go.Data et souhaitez vous connecter à l’API de votre instance, consultez la page Importation et exportation, [(section API)](importing.llms.md#import_api) et la [Communauté de pratique Go.Data](https://community-godata.who.int/).

#### SIG

Les shapefiles comportent de nombreux sous-fichiers, chacun avec une extension différente. Un fichier porte l’extension “.shp”, mais d’autres peuvent porter “.dbf”, “.prj”, etc. **appliedepidata** regroupe les sous-fichiers de chaque shapefile dans une seule archive .zip ; utilisez donc `save_data()` puis décompressez :

``` r
# charger le shapefile admin-3 de la Sierra Leone directement comme objet sf
sle_adm3 <- appliedepidata::get_data(name = "sle_adm3")

# charger les points des établissements de santé comme objet sf
sle_hf <- appliedepidata::get_data(name = "sle_hf")

# charger la table de population ADM3
sle_adm3_pop <- appliedepidata::get_data(name = "sle_admpop_adm3_2020")

# OU enregistrer les sous-fichiers bruts du shapefile dans un dossier
shp_dir <- "sle_adm3_files"
dir.create(shp_dir)
appliedepidata::save_data(name = "sle_adm3", path = shp_dir)
utils::unzip(file.path(shp_dir, "sle_adm3.zip"), exdir = shp_dir)
```

La page [Notions de base sur les SIG](gis.llms.md) charge les trois jeux de données : les limites admin-3 `sle_adm3`, les points des établissements de santé `sle_hf` et la table de population `sle_admpop_adm3_2020`. Pour lire un shapefile depuis votre propre chemin de fichier, utilisez `read_sf()` du paquet **sf**. Cette page renvoie également au site *Humanitarian Data Exchange*, où vous pouvez télécharger d’autres shapefiles sous forme d’archives zippées. Les points des établissements de santé, par exemple, sont [ici](https://data.humdata.org/dataset/hotosm_sle_health_facilities).

#### Arbres phylogénétiques

Voir la page sur les [arbres phylogénétiques](phylogenetic_trees.llms.md). Fichier Newick de l’arbre phylogénétique construit à partir du séquençage du génome entier de 299 échantillons de Shigella sonnei, et données d’échantillons correspondantes (converties en fichier texte). Les échantillons belges et les données résultantes sont aimablement fournis par le CNR belge pour Salmonella et Shigella dans le cadre d’un projet mené par un boursier EUPHEM de l’ECDC, et seront également publiés dans un manuscrit. Les données internationales sont disponibles sur des bases de données publiques (ncbi) et ont déjà été publiées.

``` r
# l'arbre phylogénétique, sous forme d'objet "phylo" (paquet ape)
tree <- appliedepidata::get_data(name = "Shigella_tree")

# informations supplémentaires sur chaque échantillon
sample_data <- appliedepidata::get_data(name = "sample_data_Shigella_tree")

# le sous-arbre créé plus loin dans la page
subtree <- appliedepidata::get_data(name = "Shigella_subtree_2")
```

#### Standardisation

Pour la page sur la [standardisation des données](standardization.llms.md), vous pouvez charger les données directement avec les commandes suivantes :

``` r
##############
# Pays A
##############
# démographie du pays
A_demo <- appliedepidata::get_data(name = "country_demographics")

# décès du pays
A_deaths <- appliedepidata::get_data(name = "deaths_countryA")

##############
# Pays B
##############
# démographie du pays
B_demo <- appliedepidata::get_data(name = "country_demographics_2")

# décès du pays
B_deaths <- appliedepidata::get_data(name = "deaths_countryB")


# Population de référence
###############
# population de référence
# world standard population, by sex
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

#### Séries temporelles et détection des épidémies

Voir la page sur [les séries temporelles et la détection des épidémies](time_series.llms.md). Nous utilisons les cas de campylobacter rapportés en Allemagne de 2002 à 2011, tels que disponibles dans le paquet R **surveillance**. (*note* cet ensemble de données a été adapté de l’original, en ce sens que 3 mois de données ont été supprimés à partir de la fin de 2011 à des fins de démonstration).

``` r
counts <- appliedepidata::get_data(name = "campylobacter_germany")
```

Nous utilisons également les données climatiques de l’Allemagne entre 2002 et 2011 (température en degrés Celsius et précipitations en millimètres). Ces données ont été téléchargées à partir d’un jeu de données dérivé des données produites par le satellite Copernicus (UE) à l’aide du paquet **ecmwfr**. **appliedepidata** les regroupe en une seule archive .zip contenant dix fichiers .nc annuels. `get_data()` lit l’ensemble du lot directement sous forme d’objet **stars** combiné ; `save_data()` vous donne les fichiers .nc bruts si vous souhaitez les inspecter ou les traiter vous-même.

``` r
# lire les données climatiques combinées directement comme objet stars
weather_data <- appliedepidata::get_data(name = "germany_weather")

# OU enregistrer les fichiers .nc annuels bruts dans un dossier
weather_dir <- "germany_weather_files"
dir.create(weather_dir)
appliedepidata::save_data(name = "germany_weather", path = weather_dir)
utils::unzip(file.path(weather_dir, "germany_weather.zip"), exdir = weather_dir)
```

#### Analyse d’enquêtes

Pour la page [analyse d’enquête](survey_analysis.llms.md), nous utilisons des données d’enquêtes de mortalité fictives basées sur les modèles d’enquête MSF OCA. Ces données fictives ont été générées dans le cadre du projet [“R4Epis”](https://r4epis.netlify.app/).

``` r
# fictional survey data
survey_data <- appliedepidata::get_data(name = "survey_data")

# fictional survey data dictionary
survey_dict <- appliedepidata::get_data(name = "survey_dict")

# fictional survey population data
population <- appliedepidata::get_data(name = "population")
```

#### Shiny

La page sur les [tableaux de bord avec Shiny](shiny_basics.llms.md) illustre la construction d’une application simple pour afficher les données sur le paludisme. Les données de l’application font partie de **appliedepidata** :

``` r
malaria_data <- appliedepidata::get_data(name = "malaria_facility_count_data")
```

Les scripts R de l’application ne sont pas des données d’exemple ; ils ne font donc pas partie de **appliedepidata** — téléchargez-les directement depuis Github :

Vous pouvez [cliquer ici pour télécharger le fichier app.R qui contient à la fois le code de l’interface utilisateur et du serveur pour l’application Shiny.](https://github.com/appliedepi/epirhandbook/raw/main/data/malaria_app/app.R).

Vous pouvez [cliquer ici pour télécharger le fichier global.R](https://github.com/appliedepi/epirhandbook/raw/main/data/malaria_app/global.R) qui doit être exécuté avant l’ouverture de l’app, comme expliqué dans la page.

Vous pouvez [cliquer ici pour télécharger le fichier plot_epicurve.R](https://github.com/appliedepi/epirhandbook/raw/main/data/malaria_app/funcs/plot_epicurve.R) dont l’exécution est lancée par le script global.R. Notez que vous devrez peut-être le stocker dans un dossier “funcs” pour que les chemins de fichier here() fonctionnent correctement.
