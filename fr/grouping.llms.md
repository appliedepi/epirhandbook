# 13  Travailler sur des données groupées

[![](../../images/grouping_1500x500.png)](../../images/grouping_1500x500.png)

Ce chapitre explique comment grouper et agréger des données lors une analyse descriptive. Il utilise les fonctions du méta-paquet **tidyverse** pour des fonctions communes et faciles à utiliser.

Grouper les données est une étape essentielle de la gestion et de l’analyse de données. Par exemple, il est souvent nécessaire de créer des résumés statistiques ou des figures “par groupe”. Les fonctions du paquet **dplyr** (qui fait partie de **tidyverse**) permettent de grouper les données et d’effectuer de nombreuses actions “par groupes très facilement.

Ce chapitre aborde les sujets suivants :

- Grouper les données avec la fonction `group_by()`.  
- Dé-grouper des données  
- Résumer les données groupées avec des statistiques (`summarise()`)  
- La différence entre `count()` et `tally()`.  
- Trier les données groupées avec la fonction `arrange()`  
- Filtrer les données groupées avec la fonction `filter()`  
- Créer de nouvelles colonnes avec la fonction `mutate()`  
- Sélectionner les colonnes avec la fonction `select()`  
- La commande **base** R `aggregate()`, qui est une alternative aux fonctions de **dplyr**.

## 13.1 Étapes préliminaires

### Importation des paquets

Ces lignes de code chargent les paquets nécessaires aux analyses. Dans ce guide, nous mettons l’accent sur `p_load()` de **pacman**, qui installe le paquet si nécessaire *puis* l’importe pour l’utiliser. Vous pouvez également charger les paquets installés avec `library()` de **base** R. Voir la page sur [bases de R](basics.llms.md) pour plus d’informations sur les paquets R.

``` r
pacman::p_load(
  rio,       # import des fichiers
  here,      # gestion des chemins d'accès
  tidyverse, # gestion des données + graphiques (inclus dplyr)
  janitor,   # ajout de totaux aux lignes et colonnes
  appliedepidata) # jeux de données d'exemple utilisés dans ce manuel
```

### Import des données

Dans ce chapitre, nous utiliserons un jeu de données fictif pour une épidémie d’Ebola. Chargez-les directement avec `appliedepidata::get_data(name = "linelist_cleaned_rds")` (voir la page [Télécharger le manuel et les données](download.llms.md) pour plus de détails).

``` r
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

Les premières cinquante lignes de la `linelist` :

## 13.2 Grouper des données

La fonction `group_by()` de **dplyr** permet de définir des groupes de lignes à partir des valeurs d’une ou de plusieurs colonnes. Chaque valeur unique (ou combinaison de valeurs unique, dans le cas où plusieurs colonnes sont spécifiées) constitue un groupe. Une fois les données groupées, de nombreuses fonctions utilisées pour le nettoyage ou des analyses descriptives seront appliquées *à chaque groupe*.

Par exemple, le code ci-dessous groupe la `linelist` en fonction des valeurs uniques de la colonne `outcome`. La ou les colonnes selon lesquelles grouper les données sont placées entre parenthèses dans la fonction `group_by()`. La fonction génère un nouveau tableau de données, que nous nommons `ll_by_outcome`.

``` r
ll_by_outcome <- linelist %>% 
  group_by(outcome)
```

**Notez que les données elles mêmes n’ont pas été modifiées** après avoir exécuté `group_by()`. Le fait que le dataframe soit “groupé” se verra lorsqu’une autre fonction du paquet **dplyr** tel que `mutate()`, `summarise()`, ou `arrange()` sera appliquée sur le dataframe “groupé”.

Vous pouvez cependant savoir qu’un dataframe est groupé en l’imprimant dans la console. Vous verrez alors qu’il a été transformé en un [objet de classe `tibble`](https://tibble.tidyverse.org/) qui, lorsqu’il est affiché, indique les groupements présents et le nombre de groupes qu’il y a juste au-dessus de la ligne d’en-tête.

``` r
# Faire afficher pour voir le schéma de groupement
ll_by_outcome
```

    # A tibble: 5,888 × 30
    # Groups:   outcome [3]
       case_id generation date_infection date_onset date_hospitalisation
       <chr>        <dbl> <date>         <date>     <date>              
     1 5fe599           4 2014-05-08     2014-05-13 2014-05-15          
     2 8689b7           4 NA             2014-05-13 2014-05-14          
     3 11f8ea           2 NA             2014-05-16 2014-05-18          
     4 b8812a           3 2014-05-04     2014-05-18 2014-05-20          
     5 893f25           3 2014-05-18     2014-05-21 2014-05-22          
     6 be99c8           3 2014-05-03     2014-05-22 2014-05-23          
     7 07e3e8           4 2014-05-22     2014-05-27 2014-05-29          
     8 369449           4 2014-05-28     2014-06-02 2014-06-03          
     9 f393b4           4 NA             2014-06-05 2014-06-06          
    10 1389ca           4 NA             2014-06-05 2014-06-07          
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_outcome <date>, outcome <chr>, gender <chr>,
    #   age <dbl>, age_unit <chr>, age_years <dbl>, age_cat <fct>, age_cat5 <fct>,
    #   hospital <chr>, lon <dbl>, lat <dbl>, infector <chr>, source <chr>,
    #   wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>, chills <chr>,
    #   cough <chr>, aches <chr>, vomit <chr>, temp <dbl>, time_admission <chr>,
    #   bmi <dbl>, days_onset_hosp <dbl>

### Groupes distincts

**Les groupes sont basés sur les combinaisons uniques de valeurs dans les colonnes de groupement**.

Pour afficher les groupes *et le nombre de lignes de chaque groupe*, passez les données groupées à la fonction `tally()`. Pour afficher les groupes présents mais pas le nombre de lignes, passez les données à la fonction `group_keys()`.

Dans l’exemple ci-dessous, il y a **trois** valeurs uniques dans la colonne de groupement `outcome` : “Death”, “Recover”, et “NA”. Vous voyez qu’il y avait `nrow(linelist %>% filter(outcome == "Death"))` morts, `nrow(linelist %>% filter(outcome == "Recover"))` guéris, et `nrow(linelist %>% filter(is.na(outcome)))` individus sans information renseignée.

``` r
linelist %>% 
  group_by(outcome) %>% 
  tally()
```

    # A tibble: 3 × 2
      outcome     n
      <chr>   <int>
    1 Death    2582
    2 Recover  1983
    3 <NA>     1323

Vous pouvez regrouper par plus d’une colonne. Ci-dessous, nous groupons le dataframe par `outcome` et `gender`, puis comptons le nombre de lignes dans chaque groupe. Chaque combinaison unique de `outcome` et `gender` crée un groupe différent, y compris les valeurs manquantes pour chaque colonne.

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally()
```

    # A tibble: 9 × 3
    # Groups:   outcome [3]
      outcome gender     n
      <chr>   <chr>  <int>
    1 Death   f       1227
    2 Death   m       1228
    3 Death   <NA>     127
    4 Recover f        953
    5 Recover m        950
    6 Recover <NA>      80
    7 <NA>    f        627
    8 <NA>    m        625
    9 <NA>    <NA>      71

### Nouvelle colonne

Vous pouvez également grouper selon une colonne crée *directement dans* la fonction `group_by()`. Cela revient à appeler `mutate()` avant le `group_by()`. Cela peut être intéressant pour créer de petites tables descriptives rapidement, mais dans d’autres cas, il sera plus lisible de créer la nouvelle colonne avec la fonction `mutate()` avant de passer le tableau à `group_by()`.

``` r
# grouper les données sur la base d'une colonne crée dans la commande group_by()
linelist %>% 
  group_by(
    age_class = ifelse(age >= 18, "adult", "child")) %>% 
  tally(sort = T)
```

    # A tibble: 3 × 2
      age_class     n
      <chr>     <int>
    1 child      3618
    2 adult      2184
    3 <NA>         86

### Grouper selon plus ou moins de colonnes

Par défaut, si vous exécutez `group_by()` sur des données déjà groupées, les anciens groupes seront supprimés et le ou les nouveaux groupes s’appliqueront. Si vous voulez ajouter de nouveaux groupes à ceux qui existent déjà, incluez l’argument `.add = TRUE`.

``` r
# Grouper par  outcome
by_outcome <- linelist %>% 
  group_by(outcome)

# Ajouter gender aux définition de groupe (grouper par une combinaison
by_outcome_gender <- by_outcome %>% 
  group_by(gender, .add = TRUE)
```

**Conserver tous les groupes**

Si vous groupez les données sur la base d’une colonne de type “facteur”, il se peut que certains niveaux du facteur ne soient pas présents dans le jeu de données dans son état actuel. Dans ce cas, ces niveaux non représentés seront abandonnés par défaut et n’apparaîtront pas dans les groupes. Pour éviter ce comportement et prendre en compte tous les niveaux du facteur, *y compris lorsqu’ils ne contiennent pas de données*, utilisez l’argument `.drop = FALSE` dans votre commande `group_by()`.

## 13.3 Dégrouper les données

Les dataframes qui ont été groupés le resteront jusqu’à ce qu’ils soient spécifiquement dégroupés grâce à la fonction `ungroup()`. Si vous oubliez de dégrouper, cela peut conduire à des calculs incorrects !

Attention à ne pas oublier de dégrouper les données avant de passer aux étapes qui nécessitent le jeu de données complet et non groupé.

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally() %>% 
  ungroup()
```

On peut également dégrouper seulement certaines colonnes, en passant le nom de la colonne à `ungroup()`.

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally() %>% 
  ungroup(gender) # dégroupe gender, mais garde le groupement par outcome
```

***NOTE:*** Le verbe `count()` dégroupe automatiquement les données après avoir compté les lignes.

## 13.4 Résumer les données par groupe

Voir la section **dplyr** du chapitre sur les [Tableaux descriptifs](tables_descriptive.llms.md) pour une explication détaillée sur comment produire des tableaux récapitulatifs à l’aide de la fonction `summarise()`. Ici, nous décrivons le comportement de `summarise()` lorsque la fonction est appliquée à des données groupées.

La fonction de **dplyr** `summarise()` (ou `summarize()`) prend un dataframe en entrée et le convertit en un *nouveau dataframe* contenant des statistiques de synthèse définies par l’utilisateur. Sur un tableau non groupé, le calcul de synthèse est effectuée sur toutes les lignes. Sur un tableau groupé, le calcul est effectué *pour chaque groupe*.

Plus précisement, la syntaxe de la fonction `summarise()` est du type : “NOM_NOUVELLE_COLONNE = fonction résumé d’une ou plusieurs colonnes des données source”. Dans la fonction statistique, indiquez la colonne à traiter et tout argument pertinent (par exemple, `na.rm = TRUE`). Les fonctions régulièrement utilisées incluent par exemple `mean()`, `min()`, `max()`, `median()`, ou `sd()`, mais on peut également utiliser `sum()` pour compter le nombre de lignes qui répondent à un critère logique (avec l’opérateur `==`).

Vous trouverez ci-dessous un premier où `summarise()` est appliquée *sur des données non groupées* : les statistiques retournées sont produites à partir de l’ensemble des données.

``` r
# statistiques résumées appliquées sur le jeu de données complet
linelist %>% 
  summarise(
    n_cases  = n(),
    mean_age = mean(age_years, na.rm=T),
    max_age  = max(age_years, na.rm=T),
    min_age  = min(age_years, na.rm=T),
    n_males  = sum(gender == "m", na.rm=T))
```

      n_cases mean_age max_age min_age n_males
    1    5888 16.01831      84       0    2803

Maintenant, la même commande est appliquée sur la linelist groupée, ce qui génère les résumés statistique pour chaque groupe. Notez que les colonnes utilisées pour définir les groupes sont gardées dans le tableau agrégé généré par `summarise()`.

``` r
# mais groupé par outcome
linelist %>% 
  group_by(outcome) %>% 
  summarise(
    n_cases  = n(),
    mean_age = mean(age_years, na.rm=T),
    max_age  = max(age_years, na.rm=T),
    min_age  = min(age_years, na.rm=T),
    n_males    = sum(gender == "m", na.rm=T))
```

    # A tibble: 3 × 6
      outcome n_cases mean_age max_age min_age n_males
      <chr>     <int>    <dbl>   <dbl>   <dbl>   <int>
    1 Death      2582     15.9      76       0    1228
    2 Recover    1983     16.1      84       0     950
    3 <NA>       1323     16.2      69       0     625

***Note:*** il est possible d’appeler la fonction en utilisant l’orthographe britannique et américaine : `summarise()` et `summarize()` sont équivalentes.

## 13.5 Comptes et additions

Les fonctions `count()` et `tally()` fournissent des fonctionnalités similaires mais légèrement différentes. Pour plus de détails sur la distinction entre les deux, voir [ici](https://dplyr.tidyverse.org/reference/tally.html).

### `tally()`

`tally()` est un raccourci pour `summarise(n = n())`, et *ne groupe pas* les données d’elle même. Ainsi, pour obtenir des totaux groupés, il faut d’abord exécuter la commande `group_by()` avant la commande `tally()`. On peut ajouter `sort = TRUE` pour voir les plus grands groupes en premier.

Exemple sans grouper les données :

``` r
linelist %>% 
  tally()
```

         n
    1 5888

En groupant les données avant d’applique la fonction `tally()` :

``` r
linelist %>% 
  group_by(outcome) %>% 
  tally(sort = TRUE)
```

    # A tibble: 3 × 2
      outcome     n
      <chr>   <int>
    1 Death    2582
    2 Recover  1983
    3 <NA>     1323

### `count()`

En revanche, la fonction `count()` effectue les actions suivantes :

1.  applique `group_by()` sur la ou les colonnes spécifiées  
2.  applique `summarise()` et retourne la colonne `n` avec le nombre de lignes par groupe  
3.  puis applique la fonction `ungroup()`.

``` r
linelist %>% 
  count(outcome)
```

      outcome    n
    1   Death 2582
    2 Recover 1983
    3    <NA> 1323

Tout comme avec `group_by()` il est possible de créer une nouvelle colonne directement dans la commande `count()` :

``` r
linelist %>% 
  count(age_class = ifelse(age >= 18, "adult", "child"), sort = T)
```

      age_class    n
    1     child 3618
    2     adult 2184
    3      <NA>   86

`count()` peut être utilisée plusieurs fois à la suite pour résumer des données de manière plus en plus compacte. Par exemple, pour résumer le nombre d’hôpitaux présents pour chaque sexe, exécutez ce qui suit. Notez que le nom de la dernière colonne est changé de la valeur par défaut “n” pour plus de clarté (avec `name =`).

``` r
linelist %>% 
  # compte le nombre de lignes pour chaque combinaison gender x hospital
  count(gender, hospital) %>% 
  # en utilisant le jeu de données agrégées, compte le nombre d’hôpitaux pour chaque genre.
  count(gender, name = "hospitals per gender" ) 
```

      gender hospitals per gender
    1      f                    6
    2      m                    6
    3   <NA>                    6

### Ajouter des colonnes contenant les décomptes

Contrairement à `count()` et `summarise()`, vous pouvez utiliser la fonction `add_count()` pour *ajouter une nouvelle colonne* `n` avec le nombre de lignes par groupe *tout en conservant toutes les autres colonnes* du dataframe. Cela signifie que le nombre de lignes total d’un groupe est ajouté pour chaque ligne du groupe dans une nouvelle colonne `n`.

Dans l’exemple suivant, nous ajoutons cette colonne et ré-arrangeons ensuite les colonnes pour une lecture plus aisée du tableau. Pour un autre exemple, voir la section plus bas sur comment [filtrer sur la taille du groupe](#group_filter_grp_size).

``` r
linelist %>% 
  as_tibble() %>%  # conversion en tibble pour un meilleur affichage
  add_count(hospital) %>%  # ajoute la colonne n avec les totaux par hôpitaux
  select(hospital, n, everything()) # trie les colonnes
```

    # A tibble: 5,888 × 31
       hospital                       n case_id generation date_infection date_onset
       <chr>                      <int> <chr>        <dbl> <date>         <date>    
     1 Other                        885 5fe599           4 2014-05-08     2014-05-13
     2 Missing                     1469 8689b7           4 NA             2014-05-13
     3 St. Mark's Maternity Hosp…   422 11f8ea           2 NA             2014-05-16
     4 Port Hospital               1762 b8812a           3 2014-05-04     2014-05-18
     5 Military Hospital            896 893f25           3 2014-05-18     2014-05-21
     6 Port Hospital               1762 be99c8           3 2014-05-03     2014-05-22
     7 Missing                     1469 07e3e8           4 2014-05-22     2014-05-27
     8 Missing                     1469 369449           4 2014-05-28     2014-06-02
     9 Missing                     1469 f393b4           4 NA             2014-06-05
    10 Missing                     1469 1389ca           4 NA             2014-06-05
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_hospitalisation <date>, date_outcome <date>,
    #   outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>, age_years <dbl>,
    #   age_cat <fct>, age_cat5 <fct>, lon <dbl>, lat <dbl>, infector <chr>,
    #   source <chr>, wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>,
    #   chills <chr>, cough <chr>, aches <chr>, vomit <chr>, temp <dbl>,
    #   time_admission <chr>, bmi <dbl>, days_onset_hosp <dbl>

### Ajouter les totaux

Pour facilement ajouter les totaux par lignes ou colonnes d’un tableau après avoir utilisé `tally()` ou `count()`, consultez la section **janitor** de la page [sur les tables descriptives](tables_descriptive.llms.md#tbl_janitor). Ce paquet offre des fonctions telles que `adorn_totals()` et `adorn_percentages()` pour ajouter des totaux et pourcentages. Par exemple :

``` r
linelist %>%                                  # case linelist
  tabyl(age_cat, gender) %>%                  # décomptes croisés de deux colonnes
  adorn_totals(where = "row") %>%             # ajoute ligne de totaux
  adorn_percentages(denominator = "col") %>%  # ajoute proportions (dénominateur colonne)
  adorn_pct_formatting() %>%                  # formate en %
  adorn_ns(position = "front") %>%            # formate en : "N (%)"
  adorn_title(                                # ajuste les titres
    row_name = "Age Category",
    col_name = "Gender")
```

                          Gender                            
     Age Category              f              m          NA_
              0-4   640  (22.8%)   416  (14.8%)  39  (14.0%)
              5-9   641  (22.8%)   412  (14.7%)  42  (15.1%)
            10-14   518  (18.5%)   383  (13.7%)  40  (14.4%)
            15-19   359  (12.8%)   364  (13.0%)  20   (7.2%)
            20-29   468  (16.7%)   575  (20.5%)  30  (10.8%)
            30-49   179   (6.4%)   557  (19.9%)  18   (6.5%)
            50-69     2   (0.1%)    91   (3.2%)   2   (0.7%)
              70+     0   (0.0%)     5   (0.2%)   1   (0.4%)
             <NA>     0   (0.0%)     0   (0.0%)  86  (30.9%)
            Total 2,807 (100.0%) 2,803 (100.0%) 278 (100.0%)

Pour ajouter des lignes de totaux plus complexes qui impliquent des statistiques récapitulatives autres que des *sommes*, voir [cette section de la page Tables descriptives](tables_descriptive.llms.md#tbl_dplyr_totals).

## 13.6 Grouper par date

Pour grouper des données par date, il faut avoir, ou créer une colonne contenant l’unité de temps qui vous intéresse (par exemple : “jour”, “semaine épidémiologique”, “mois”, etc). Vous pouvez créer cette colonne en utilisant `floor_date()` du paquet **lubridate**, tel qu’expliqué dans la section sur les [Semaines épidémiologiques](dates.llms.md#dates_epi_wks) du chapitre sur les [dates](dates.llms.md). Cette colonne peut être simplement passée à `group_by()` ou `count()` de **dplyr** pour grouper les lignes par les valeurs uniques de date ou obtenir le nombre de lignes par date.

Un besoin spécifique à la gestion et l’analyse de données par date consiste à compléter les dates de la séquence qui ne sont pas présentes dans les données. Pour cela, on peut utiliser `complete()` du paquet **tidyr** pour que la série de dates agrégées comprenne *toutes les unités de dates possibles* dans la plage. Sans cette étape, une semaine où aucun cas n’a été signalé n’apparaîtrait pas dans les données…

La fonction `complete()`, *redéfinit* la colonne contenant les dates comme une *séquence* de dates (en passant `seq.Date()` du minimum au maximum comme argument). Par défaut, les valeurs du nombre de cas (et autres colonnes) dans les nouvelles lignes “développées” contient des “NA”, mais l’on peut modifier ce comportement. Par exemple, on peut mettre le nombre de cas à 0 en utilisant l’argument `fill =` de `complete()`, qui prend en entrée une liste nommée (si votre colonne de nombre de cas est nommée `n`, fournissez `fill = list(n = 0)`. Voir `?complete` pour plus de détails et la page [Manipuler les dates](dates.llms.md) pour un exemple.

### Grouper par jours (linelist)

Voici un exemple où l’on va grouper le nombre de cas de la linelist par jour, *sans utiliser* la fonction `complete()`. Note : les premières lignes ignorent les dates sans cas.

``` r
daily_counts <- linelist %>% 
  drop_na(date_onset) %>%        # Exclut les cas où date_onset est vide
  count(date_onset)              # Compte le nombre de lignes par date
```

Maintenant, le même exemple en utilisant la commande `complete()` pour s’assurer que tous les jours dans la fourchette temporelle seront représentés dans les données.

``` r
daily_counts <- linelist %>% 
  drop_na(date_onset) %>%     # Exclut les cas où date_onset est vide
  count(date_onset) %>%       # Compte le nombre de lignes par jour
  complete(                   # Ajoute les jours manquants (sans cas)
    date_onset = seq.Date(    # redéfinit la colonne comme une séquence de dates
      from = min(date_onset, na.rm=T), 
      to = max(date_onset, na.rm=T),
      by = "day"),
    fill = list(n = 0))                   # set new filled-in rows to display 0 in column n (not NA as default) 
```

### Grouper par semaines (linelist)

Le même principe peut être appliqué au groupement par semaine. Dans cet exemple, on va d’abord créer une nouvelle colonne contenant la semaine à l’aide de la fonction `floor_date()` du package **lubridate** (avec `unit = "week"`). Ensuite, on utilise la fonction `count()` pour obtenir le nombre de cas hebdomadaires. On termine enfin avec un `complete()` pour compléter toutes les semaines dans le jeu de données agrégées, même il n’y a pas eu de cas cette semaine là.

``` r
# Make dataset of weekly case counts
weekly_counts <- linelist %>% 
  drop_na(date_onset) %>%        # Exclut les cas où date_onset est vide
  mutate(week = lubridate::floor_date(date_onset, unit = "week")) %>%  # new column of week of onset
  count(week) %>%                # Compte le nombre de lignes par semaine
  complete(                      # Ajoute les semaines non représentées (sans cas)
    week = seq.Date(             # redéfinit la colonne comme une séquence de dates
      from = min(week, na.rm=T), 
      to = max(week, na.rm=T),
      by = "week"),
    fill = list(n = 0))          # remplit les nouvelles dates ajoutées de 0 (aurait été des NA par 
```

Voici les 50 premières lignes du jeu de données créé :

### Grouper par mois (linelist)

Pour agréger les cas par mois, nous utiliserons à nouveau `floor_date()`, avec l’argument `unit = "months"`. Cette commande arrondit chaque date au 1er de son mois. La sortie sera donc de la classe Date. Notez que dans l’étape `complete()`, nous utilisons également `by = "months"`.

``` r
# Make dataset of monthly case counts
monthly_counts <- linelist %>% 
  drop_na(date_onset) %>% 
  mutate(month = lubridate::floor_date(date_onset, unit = "months")) %>%  # new column, 1st of month of onset
  count(month) %>%             # Compte le nombre de cas par mois
  complete(
    month = seq.Date(
      min(month, na.rm=T),     # Ajoute les mois non représentées (sans cas)
      max(month, na.rm=T),
      by="month"),
    fill = list(n = 0))
```

### Comptes journaliers en semaines (données agrégées)

Pour agréger les nombres de cas quotidiens (données déjà agrégées par jour, donc) en nombre de cas hebdomadaires, utilisez `floor_date()` de la même manière que dans les exemples précédents. Cependant, il faut ensuite utiliser les fonctions `group_by()` et `summarize()` au lieu de `count()` car il faut *faire la somme des nombres de cas quotidiens* au lieu de simplement compter le nombre de lignes par semaine.

#### Comptes journaliers en mois (données agrégées)

Pour agréger les nombres de cas journaliers par mois, utilisez `floor_date()` de la même manière que dans les exemples précédents (avec `unit = "month"`). Cependant, il faut ensuite utiliser les fonctions `group_by()` et `summarize()` au lieu de `count()` car il faut additionner le nombre de cas quotidiens au lieu de simplement compter le nombre de lignes par mois.

## 13.7 Trier les données groupées

La fonction `arrange()` de **dplyr** qui permet d’ordonner les lignes d’un dataframe se comporte de la même manière lorsque les données sont groupées, *sauf* si vous définissez l’argument `.by_group = TRUE`. Dans ce cas, les lignes sont d’abord ordonnées par les colonnes de regroupement, puis par toutes les autres colonnes que vous spécifiez à `arrange()`.

## 13.8 Filtrer les données groupées

### `filter()`

Lorsque l’on utilise la fonction `filter` en conjonction avec des fonctions qui évaluent le dataframe (`max()`, `min()` ou `mean()` par exemple), la commande est désormais appliquée à chaque groupe indépendamment. Par exemple, pour filtrer et conserver les lignes où les patients ont un âge supérieur à l’âge médian, le filtre s’appliquera désormais à l’intérieur de chaque groupe, pour pour conserver les lignes où l’age des patients est supérieur à l’âge médian *du groupe*.

### `slice()`

La fonction **dplyr** `slice()`, qui [filtre les lignes en fonction de leur position dans les données](https://dplyr.tidyverse.org/reference/slice.html), peut également être appliquée par groupe. N’oubliez pas de trier les données au sein de chaque groupe pour obtenir la “tranche” souhaitée.

Par exemple, pour extraire uniquement les 5 dernières admissions de chaque hôpital :

1.  Groupez les données de la linelist par la colonne `hospital`.  
2.  Triez les enregistrements du plus récent au plus ancien grâce à la colonne `date_hospitalisation` *dans chaque groupe d’hôpitaux*.  
3.  Tranchez pour récupérer les 5 premières lignes de chaque hôpital

``` r
linelist %>%
  group_by(hospital) %>%
  arrange(hospital, date_hospitalisation) %>%
  slice_head(n = 5) %>% 
  arrange(hospital) %>%                            # (pour l'affichage)
  select(case_id, hospital, date_hospitalisation)  # (pour l'affichage)
```

    # A tibble: 30 × 3
    # Groups:   hospital [6]
       case_id hospital          date_hospitalisation
       <chr>   <chr>             <date>              
     1 20b688  Central Hospital  2014-05-06          
     2 d58402  Central Hospital  2014-05-10          
     3 b8f2fd  Central Hospital  2014-05-13          
     4 acf422  Central Hospital  2014-05-28          
     5 275cc7  Central Hospital  2014-05-28          
     6 d1fafd  Military Hospital 2014-04-17          
     7 974bc1  Military Hospital 2014-05-13          
     8 6a9004  Military Hospital 2014-05-13          
     9 09e386  Military Hospital 2014-05-14          
    10 865581  Military Hospital 2014-05-15          
    # ℹ 20 more rows

`slice_head()` : sélectionne les n premières lignes (“par le haut”)  
`slice_tail()` : sélectionne les n dernières lignes (“par le bas”)  
`slice_sample()` : sélectionne n lignes aléatoirement  
`slice_min()` : sélectionne les n lignes avec les plus petites valeurs dans une colonne donnée (argument `order_by =`). Utiliser `with_ties = TRUE` pour garder les ex-æquo  
`slice_max()` : sélectionne les n lignes avec les plus grandes valeurs dans une colonne donnée (argument `order_by =`). Utiliser `with_ties = TRUE` pour garder les ex-æquo

Voir le chapitre sur la [dé-duplication](deduplication.llms.md) pour plus d’exemples et de détails sur la fonction `slice()`.

### Filtrer sur la taille des groupes

La fonction `add_count()` ajoute une colonne `n` aux données originales, ajoutant ainsi, pour chaque ligne, le nombre de lignes du groupe auquel cette ligne appartient.

Dans l’exemple ci-dessous, `add_count()` est appliqué à la colonne `hospital`, de sorte que les valeurs de la nouvelle colonne `n` reflètent le nombre de lignes dans le groupe hospitalier de cette ligne. Bien sûr, cela veut dire que la valeur de la colonne “n” est répétée pour chaque ligne du groupe.

Dans l’exemple ci-dessous, le nom de la colonne `n` pourrait être modifié en utilisant `name =` dans `add_count()`.

``` r
linelist %>% 
  as_tibble() %>% 
  add_count(hospital) %>%          # ajoute le nombre de patients admis dans cette hôpital, pour chaque groupe
  select(hospital, n, everything()) # Pour un meilleur affichage
```

    # A tibble: 5,888 × 31
       hospital                       n case_id generation date_infection date_onset
       <chr>                      <int> <chr>        <dbl> <date>         <date>    
     1 Other                        885 5fe599           4 2014-05-08     2014-05-13
     2 Missing                     1469 8689b7           4 NA             2014-05-13
     3 St. Mark's Maternity Hosp…   422 11f8ea           2 NA             2014-05-16
     4 Port Hospital               1762 b8812a           3 2014-05-04     2014-05-18
     5 Military Hospital            896 893f25           3 2014-05-18     2014-05-21
     6 Port Hospital               1762 be99c8           3 2014-05-03     2014-05-22
     7 Missing                     1469 07e3e8           4 2014-05-22     2014-05-27
     8 Missing                     1469 369449           4 2014-05-28     2014-06-02
     9 Missing                     1469 f393b4           4 NA             2014-06-05
    10 Missing                     1469 1389ca           4 NA             2014-06-05
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_hospitalisation <date>, date_outcome <date>,
    #   outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>, age_years <dbl>,
    #   age_cat <fct>, age_cat5 <fct>, lon <dbl>, lat <dbl>, infector <chr>,
    #   source <chr>, wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>,
    #   chills <chr>, cough <chr>, aches <chr>, vomit <chr>, temp <dbl>,
    #   time_admission <chr>, bmi <dbl>, days_onset_hosp <dbl>

Il est alors facile de filtrer les lignes de cas qui ont été hospitalisés dans un “petit” hôpital. Par exemple un hôpital qui a admis moins de 500 patients :

``` r
linelist %>% 
  add_count(hospital) %>% 
  filter(n < 500)
```

## 13.9 `mutate()`

Pour conserver toutes les colonnes et lignes (sans les résumer) et *ajouter une nouvelle colonne contenant des statistiques de groupe*, utilisez `mutate()` après `group_by()` au lieu de `summarise()`.

Ceci est utile si vous voulez les statistiques de groupe dans le jeu de données original *avec toutes les autres colonnes présentes* - par exemple pour les calculs qui comparent une ligne à son groupe.

Par exemple, le code ci-dessous calcule la différence entre le délai d’admission d’une ligne et le délai d’admission médian pour son hôpital. Les étapes sont les suivantes :

1.  Groupez les données par hôpital  
2.  Utilisez la colonne `days_onset_hosp` (délai à l’hospitalisation) pour créer une nouvelle colonne contenant le délai moyen de l’hôpital pour chaque patient de cet hôpital  
3.  Calculez la différence entre les deux colonnes

``` r
linelist %>% 
  # grouper les données par hôpital
  group_by(hospital) %>% 
  
  # Ajoute de nouvelles colonnes (conserve toutes lies lignes)
  mutate(
    # Délai moyen d'admission pour chaque hôpital (arrondi à la 1re décimale)
    group_delay_admit = round(mean(days_onset_hosp, na.rm=T), 1),
    
    # Différence entre le délai de chaque patient et le délai moyen de son hôpital
    diff_to_group     = round(days_onset_hosp - group_delay_admit, 1)) %>%
  
  # Sélectionne colonnes (pour l'affichage)
  select(case_id, hospital, days_onset_hosp, group_delay_admit, diff_to_group)
```

    # A tibble: 5,888 × 5
    # Groups:   hospital [6]
       case_id hospital              days_onset_hosp group_delay_admit diff_to_group
       <chr>   <chr>                           <dbl>             <dbl>         <dbl>
     1 5fe599  Other                               2               2             0  
     2 8689b7  Missing                             1               2.1          -1.1
     3 11f8ea  St. Mark's Maternity…               2               2.1          -0.1
     4 b8812a  Port Hospital                       2               2.1          -0.1
     5 893f25  Military Hospital                   1               2.1          -1.1
     6 be99c8  Port Hospital                       1               2.1          -1.1
     7 07e3e8  Missing                             2               2.1          -0.1
     8 369449  Missing                             1               2.1          -1.1
     9 f393b4  Missing                             1               2.1          -1.1
    10 1389ca  Missing                             2               2.1          -0.1
    # ℹ 5,878 more rows

## 13.10 `select()` sur les données groupées

La fonction `select()` fonctionne sur les données groupées, à ce détail près que les colonnes utilisées pour les groupes sont toujours inclues, même si elles n’ont pas été mentionnées dans les colonnes à conserver. Pour se débarrasser de ces colonnes, il faut utiliser `ungroup()` avant le `select()`.

## 13.11 Resources

Pour plus d’information, voici quelques ressources utiles :

Vous pouvez utiliser n’importe quelle fonction agrégeant sur des données groupées ; Voir l’antisèche sur [la transformation des données avec Rstudio](https://github.com/rstudio/cheatsheets/blob/master/data-transformation.pdf)

La page de The Data Carpentry sur [**dplyr**](https://datacarpentry.org/R-genomics/04-dplyr.html)

La page de référence de l’aide du **tidyverse** sur [group_by()](https://dplyr.tidyverse.org/reference/group_by.html) et [grouping](https://dplyr.tidyverse.org/articles/grouping.html)

Cette page sur la [manipulation des données](https://itsalocke.com/files/DataManipulationinR.pdf)

[Résummer les données avec des conditions avec dplyr](https://stackoverflow.com/questions/23528862/summarize-with-conditions-in-dplyr)
