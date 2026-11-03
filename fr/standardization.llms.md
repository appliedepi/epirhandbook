# 21  Taux standardisés

Cette page vous montre comment normaliser un résultat, tel que les hospitalisations ou la mortalité, en fonction de caractéristiques telles que l’âge et le sexe.

Cette page utilise le paquet **PHEindicatormethods**.

Nous commençons par démontrer de manière extensive les processus de préparation/nettoyage/jonction des données, car cela est courant lorsqu’on combine des données de population provenant de plusieurs pays, des données de population standard, des décès, etc.

## 21.1 Vue d’ensemble

Il existe deux manières principales de normaliser : la normalisation directe et la normalisation indirecte. Supposons que nous voulions normaliser le taux de mortalité par âge et par sexe pour le pays A et le pays B, et comparer les taux normalisés entre ces pays.

- Pour une standardisation directe, vous devrez connaître le nombre de personnes à risque et le nombre de décès pour chaque strate d’âge et de sexe, pour le pays A et le pays B. Une strate dans notre exemple pourrait être les femmes âgées de 15 à 44 ans.  
- Pour une standardisation indirecte, il suffit de connaître le nombre total de décès et la structure d’âge et de sexe de chaque pays. Cette option est donc envisageable si les taux de mortalité ou les chiffres de population par âge et par sexe ne sont pas disponibles. La standardisation indirecte est en outre préférable en cas de petits effectifs par strate, car les estimations en standardisation directe seraient influencées par une variation d’échantillonnage importante.

## 21.2 Préparation

Pour montrer comment se fait la standardisation, nous allons utiliser des comptages fictifs de population et de décès du pays A et du pays B, par âge (en catégories de 5 ans) et par sexe (femme, homme). Pour que les ensembles de données soient prêts à être utilisés, nous allons effectuer les étapes de préparation suivantes :

1.  Charger les paquets  
2.  Charger les jeux de données  
3.  Joignez les données de population et de décès des deux pays.
4.  Pivoter plus longtemps pour qu’il y ait une ligne par strate âge-sexe.
5.  Nettoyez la population de référence (population standard mondiale) et joignez-la aux données du pays.

Dans votre scénario, vos données peuvent se présenter sous un format différent. Peut-être vos données sont-elles présentées par province, ville ou autre zone d’attraction. Vous avez peut-être une ligne pour chaque décès et des informations sur l’âge et le sexe pour chacun (ou une proportion importante) de ces décès. Dans ce cas, consultez les pages sur le [Travailler sur des données groupées](grouping.llms.md), [Pivoter les données](pivoting.llms.md), and [Tableaux descriptifs](tables_descriptive.llms.md) pour créer un ensemble de données avec des comptes d’événements et de population par strate âge-sexe.

Nous avons également besoin d’une population de référence, la population standard. Pour les besoins de cet exercice, nous utiliserons la `world_standard_population_by_sex` (population standard mondiale par sexe). La population standard mondiale est basée sur les populations de 46 pays et a été développée en 1960. Il existe de nombreuses populations “standard” - à titre d’exemple, le site web de [NHS Scotland](https://www.opendata.nhs.scot/dataset/standard-populations) est assez informatif sur la population standard européenne, la population standard mondiale et la population standard écossaise.

### Chargement des paquets

Ce chunk de code montre le chargement des paquets nécessaires aux analyses. Dans ce manuel, nous mettons l’accent sur `p_load()` de **pacman**, qui installe le paquet si nécessaire *et* le charge pour l’utiliser. Vous pouvez également charger les paquets installés avec `library()` de **base** R. Voir la page sur [bases de R](basics.llms.md) pour plus d’informations sur les paquets R.

``` r
pacman::p_load(
     rio, # importer/exporter des données
     here, # localisation des fichiers
     stringr, # nettoyage des caractères et des chaînes de caractères
     PHEindicatormethods, # alternative pour la standardisation des taux
     tidyverse, # gestion et visualisation des données
     appliedepidata) # jeux de données d'exemple utilisés dans ce manuel
```

### Charger les données de la population

Voir la page [Télécharger le manuel et les données](download.llms.md) pour savoir comment télécharger tous les exemples de données du manuel. Vous pouvez charger les données de la page de normalisation directement dans R avec les appels `appliedepidata::get_data()` suivants :

``` r
# données démographiques du pays A
A_demo <- appliedepidata::get_data(name = "country_demographics")

# décès pour le pays A
A_deaths <- appliedepidata::get_data(name = "deaths_countryA")

# données démographiques du pays B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")

# décès pour le pays B
B_deaths <- appliedepidata::get_data(name = "deaths_countryB")

# population de référence (standard mondial)
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

Tout d’abord, nous chargeons les données démographiques (comptage des hommes et des femmes par catégorie d’âge de 5 ans) pour les deux pays que nous allons comparer, le “pays A” et le “pays B”.

``` r
# Pays A
A_demo <- appliedepidata::get_data(name = "country_demographics")
```

``` r
# Pays B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")
```

### Chargement du nombre de morts

De manière pratique, nous disposons également du nombre de décès survenus pendant la période qui nous intéresse, par âge et par sexe. Les chiffres de chaque pays sont dans un fichier séparé, comme indiqué ci-dessous.

Décès dans le pays A

Décès dans le pays B

### Nettoyer les populations et les décès

Nous devons joindre et transformer ces données de la manière suivante :

- Combiner les populations des pays en un seul ensemble de données et faire un pivot “long” pour que chaque strate âge-sexe soit une ligne.  
- Combiner le nombre de décès par pays dans un ensemble de données et faire pivoter “long” pour que chaque strate âge-sexe soit une ligne.  
- Joindre les décès aux populations

Tout d’abord, nous combinons les ensembles de données sur les populations des pays, nous effectuons un pivot plus long et un nettoyage mineur. Voir la page [Pivoter les données](pivoting.llms.md) pour plus de détails.

``` r
pop_countries <- A_demo %>% # Commencez avec l'ensemble de données du pays A
     bind_rows(B_demo) %>% # lier les lignes, car les colonnes portent le même nom
     pivot_longer( # pivot plus long
          cols = c(m, f), # colonnes à combiner en une seule
          names_to = "Sex", # nom de la nouvelle colonne contenant la catégorie ("m" ou "f") 
          values_to = "Population") %>% # nom de la nouvelle colonne contenant les valeurs numériques pivotées
     mutate(Sex = recode(Sex, # re-code les valeurs pour plus de clarté
          "m" = "Male",
          "f" = "Female"))
```

Les données de population combinées ressemblent maintenant à ceci (cliquez pour voir les pays A et B) :

Et maintenant, nous effectuons des opérations similaires sur les deux ensembles de données de décès.

``` r
deaths_countries <- A_deaths %>% # Commencez avec l'ensemble de données des décès du pays A
     bind_rows(B_deaths) %>% # lier les lignes avec l'ensemble de données B, parce que les colonnes sont nommées de manière identique
     pivot_longer( # pivot plus long
          cols = c(Male, Female), # colonne à transformer en une seule
          names_to = "Sex", # nom de la nouvelle colonne contenant la catégorie ("m" ou "f") 
          values_to = "Deaths") %>% # nom pour la nouvelle colonne contenant les valeurs numériques pivotées
     rename(age_cat5 = AgeCat) # renomme pour plus de clarté
```

Les données de décès ressemblent maintenant à ceci, et contiennent les données des deux pays :

Nous joignons maintenant les données de décès et de population sur la base des colonnes communes `Country`, `age_cat5`, et `Sex`. Cela ajoute la colonne `Deaths`.

``` r
country_data <- pop_countries %>% 
     left_join(deaths_countries, by = c("Country", "age_cat5", "Sex"))
```

Nous pouvons maintenant classer `Country`, `age_cat5`, et `Sex` comme facteurs et définir l’ordre des niveaux en utilisant la fonction `fct_relevel()` du paquet **forcats**, comme décrit dans la page sur [Facteurs](factors.llms.md). Notez que le classement des niveaux des facteurs ne change pas visiblement les données, mais la commande `arrange()` les trie par Pays, catégorie d’âge et sexe.

``` r
country_data <- country_data %>% 
  mutate(
    Country = fct_relevel(Country, "A", "B"),
      
    Sex = fct_relevel(Sex, "Male", "Female"),
        
    age_cat5 = fct_relevel(
      age_cat5,
      "0-4", "5-9", "10-14", "15-19",
      "20-24", "25-29",  "30-34", "35-39",
      "40-44", "45-49", "50-54", "55-59",
      "60-64", "65-69", "70-74",
      "75-79", "80-84", "85")) %>% 
          
  arrange(Country, age_cat5, Sex)
```

\*\*\_\_ATTENTION:\_\*\* Si vous avez peu de décès par strate, envisagez d’utiliser des catégories de 10, ou 15 ans, au lieu de catégories de 5 ans pour l’âge.

### Chargement de la population de référence

Enfin, pour la standardisation directe, nous importons la population de référence (la “population standard” mondiale par sexe).

``` r
# Population de référence
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

### Nettoyer la population de référence

Les valeurs des catégories d’âge dans les cadres de données `country_data` et `standard_pop_data` devront être alignées.

Actuellement, les valeurs de la colonne `age_cat5` du cadre de données `standard_pop_data` contiennent le mot “years” et “plus”, alors que celles du cadre de données `country_data` ne le font pas. Nous devrons faire correspondre les valeurs des catégories d’âge. Nous utilisons `str_replace_all()` du paquet **stringr**, comme décrit dans la page [Caractères et chaînes de caractères](characters_strings.llms.md), pour remplacer ces motifs par des `""` sans espace.

La fonction `calculate_dsr()` reçoit la population standard par son argument `stdpop =`, donc la colonne peut avoir n’importe quel nom. Nous la renommons en `"pop"` car le code ci-dessous utilise `stdpop = pop`.

``` r
# Suppression d'une chaîne spécifique des valeurs de la colonne
standard_pop_clean <- standard_pop_data %>%
     mutate(
          age_cat5 = str_replace_all(age_cat5, "years", ""), # supprime "year" (année)
          age_cat5 = str_replace_all(age_cat5, "plus", ""), # supprimez "plus".
          age_cat5 = str_replace_all(age_cat5, " ", "")) %>% # supprime l'espace " ".
     
     rename(pop = WorldStandardPopulation) # change le nom de la colonne en "pop", la colonne donnée à stdpop = dans calculate_dsr()
```

***CAUTION:*** Si vous essayez d’utiliser `str_replace_all()` pour supprimer un *symbole plus*, cela ne fonctionnera pas car c’est un symbole spécial. “Échappez” au spécial en mettant deux barres obliques inverses devant, comme dans `str_replace_call(column, "\\+", "")`.

### Créer un jeu de données avec une population standard

Enfin, le package **PHEindicatormethods**, détaillé [ci-dessous](#standard_phe), attend les populations standards jointes aux événements et aux comptages de population du pays. Nous allons donc créer un jeu de données `all_data` à cet effet.

``` r
all_data <- left_join(country_data, standard_pop_clean, by=c("age_cat5", "Sex"))
```

Cet ensemble de données complet ressemble à ceci :

## 21.3 **PHEindicatormethods** package

Nous calculons les taux standardisés avec le paquet **PHEindicatormethods**. Ce package vous permet de calculer les taux standardisés directement et indirectement. Nous allons montrer les deux.

Cette section utilisera le cadre de données `all_data` créé à la fin de la section Préparation. Ce cadre de données inclut les populations des pays, les événements de décès, et la population de référence standard mondiale. Vous pouvez le visualiser [ici](#standard_all).

### Taux directement standardisés

Ci-dessous, nous regroupons d’abord les données par Pays, puis nous les passons à la fonction `calculate_dsr()` pour obtenir les taux directement standardisés par pays.

A noter - `calculate_dsr()` a besoin de la population de référence (standard) sous forme de **colonne dans le cadre de données spécifique au pays**. Indiquez le nom de cette colonne dans l’argument `stdpop =`. Dans notre exemple ci-dessous, cette colonne est `pop`.

Consultez l’aide de `?calculate_dsr` ou les liens dans la section Références pour plus d’informations.

``` r
# Calculez les taux par pays directement normalisés pour l'âge et le sexe.
mortality_ds_rate_phe <- all_data %>%
     group_by(Country) %>%
     PHEindicatormethods::calculate_dsr(
          x = Deaths, # colonne avec le nombre d'événements observés
          n = Population, # colonne avec les pops non standard pour chaque strate
          stdpop = pop) # populations standard pour chaque strate

# Imprimer le tableau
knitr::kable(mortality_ds_rate_phe)
```

| Country | total_count | total_pop | value | lowercl | uppercl | confidence | statistic | method |
|:---|---:|---:|---:|---:|---:|:---|:---|:---|
| A | 11344 | 86790567 | 23.56686 | 23.08107 | 24.05944 | 95% | dsr per 100000 | Dobson |
| B | 9955 | 52898281 | 19.32549 | 18.45516 | 20.20882 | 95% | dsr per 100000 | Dobson |

### Taux standardisés indirectement

Pour la standardisation indirecte, vous avez besoin d’une population de référence avec le nombre de décès et le nombre de population par strate. Dans cet exemple, nous allons calculer les taux pour le pays A *en utilisant le pays B comme population de référence*, car la population de référence `standard_pop_clean` n’inclut pas le nombre de décès par strate.

Ci-dessous, nous créons d’abord la population de référence du pays B. Ensuite, nous passons les données de mortalité et de population pour le pays A, nous les combinons avec la population de référence, et nous les passons à la fonction `calculate_ISRate()`, pour obtenir des taux indirectement standardisés. Bien sûr, vous pouvez aussi faire l’inverse.

A noter - dans notre exemple ci-dessous, la population de référence est fournie comme un cadre de données séparé. Dans ce cas, nous nous assurons que les vecteurs `x =`, `n =`, `x_ref =` et `n_ref =` sont tous ordonnés par les mêmes valeurs de catégorie de standardisation (strate) que celles de notre cadre de données spécifique au pays, puisque les enregistrements seront appariés par position.

Consultez l’aide de `?phe_isr` ou les liens dans la section Références pour plus d’informations.

``` r
# Créez la population de référence
refpopCountryB <- country_data %>% 
  filter(Country == "B") 

# Calculer les taux pour le pays A indirectement standardisés par âge et sexe
mortality_is_rate_phe_A <- country_data %>%
     filter(Country == "A") %>%
     PHEindicatormethods::calculate_ISRate( #avant c'etait phe_isr()
          x = Deaths, # colonne avec le nombre d'événements observés
          n = Population, # colonne avec les pops non standard pour chaque strate
          x_ref = refpopCountryB$Deaths, # nombre de décès de référence pour chaque strate
          n_ref = refpopCountryB$Population) # population de référence pour chaque strate

# Imprimez le tableau
knitr::kable(mortality_is_rate_phe_A)
```

| observed | expected | ref_rate | value | lowercl | uppercl | confidence | statistic | method |
|---:|---:|---:|---:|---:|---:|:---|:---|:---|
| 11344 | 15847.42 | 18.81914 | 13.47123 | 13.22446 | 13.72145 | 95% | indirectly standardised rate per 100000 | Byars |

## 21.4 Ressources

Pour un autre exemple utilisant **PHEindicatormethods**, veuillez vous rendre sur [ce site Web](https://mran.microsoft.com/snapshot/2018-10-22/web/packages/PHEindicatormethods/vignettes/IntroductiontoPHEindicatormethods.html)

Voir les **PHEindicatormethods** [fichier pdf de référence](https://cran.r-project.org/web/packages/PHEindicatormethods/PHEindicatormethods.pdf)
