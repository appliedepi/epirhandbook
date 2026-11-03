# 50  Tableau de données

Le manuel se concentre sur les fonctions verbales **dplyr** et l’opérateur pipe **magrittr** `%>%` comme méthode pour nettoyer et regrouper les données, mais le paquet **data.table** offre une méthode alternative que vous pourriez rencontrer dans votre carrière R.

## 50.1 Intro aux tableaux de données

Une table de données est une structure de données bidimensionnelle comme un cadre de données qui permet d’effectuer des opérations de regroupement complexes. La syntaxe data.table est structurée de manière à ce que les opérations puissent être effectuées sur les lignes, les colonnes et les groupes.

La structure est **DT\[i, j, by\]**, séparée par 3 parties : les arguments **i, j** et **by**. L’argument **i** permet de sous-dimensionner les lignes requises, l’argument **j** permet d’opérer sur les colonnes et l’argument **by** permet d’opérer sur les colonnes par groupes.

Cette page abordera les sujets suivants :

- Importation de données et utilisation de `fread()` et `fwrite()`.
- Sélection et filtrage des lignes en utilisant l’argument **i**.
- Utilisation des fonctions d’aide `%like%`, `%chin%`, `%between%`.
- Sélection et calcul sur les colonnes à l’aide de l’argument **j**.
- Calculer par groupes avec l’argument **by**
- Ajouter et mettre à jour des données dans des tableaux de données en utilisant `:=`

## 50.2 Chargement des paquets et importation des données

### Charger des paquets

En utilisant la fonction `p_load()` de **pacman**, nous chargeons (et installons si nécessaire) les paquets nécessaires à cette analyse.

``` r
pacman::p_load(
  data.table, # pour regrouper et nettoyer les données
  tidyverse  # permet d'utiliser la fonction pipe (%>%) dans ce chapitre
  ) 
```

### Importer les données

Cette page va explorer certaines des fonctions principales de **data.table** en utilisant la liste de cas référencée tout au long du manuel.

Nous importons le jeu de données des cas d’une épidémie d’Ebola simulée. Chargez-les directement avec `appliedepidata::get_data(name = "linelist_cleaned_excel")` (voir la page [Télécharger le manuel et les données](download.llms.md) pour plus de détails). A partir de là, nous utilisons `data.table()` pour convertir le cadre de données en un tableau de données.

``` r
linelist <- appliedepidata::get_data(name = "linelist_cleaned_excel") %>% data.table()
```

La fonction `fread()` est utilisée pour importer directement des fichiers délimités réguliers, tels que les fichiers .csv, vers un format de table de données. Cette fonction, et sa contrepartie, `fwrite()`, utilisée pour écrire les tables de données comme des fichiers délimités réguliers, sont des options très rapides et efficaces en termes de calcul pour les grandes bases de données.

Les 20 premières lignes de `linelist` :

Les commandes de base de R, telles que `dim()`, utilisées pour les cadres de données, peuvent également être utilisées pour les tableaux de données.

``` r
dim(linelist) #donne le nombre de lignes et de colonnes du tableau de données
```

    [1] 5888   30

## 50.3 L’argument i: sélection et filtrage des lignes

En rappelant la structure **DT\[i, j, by\]**, nous pouvons filtrer les lignes en utilisant soit des numéros de ligne, soit des expressions logiques. L’argument i est le premier ; par conséquent, la syntaxe **DT\[i\]** ou **DT\[i,\]** peut être utilisée.

Le premier exemple récupère les 5 premières lignes de la table de données, le deuxième exemple sélectionne le sous-ensemble des cas âgés de 18 ans ou plus, et le troisième exemple sélectionne le sous-ensemble des cas âgés de 18 ans ou plus mais non diagnostiqués à l’hôpital central :

``` r
linelist[1:5] #renvoie la 1ère à la 5ème ligne
linelist[age >= 18] #sous-entend les cas égaux ou supérieurs à 18 ans
linelist[age >= 18 & hospital != "Central Hospital"] #subset les cas égaux ou supérieurs à 18 ans mais non diagnostiqués à Central Hospital
```

L’utilisation de .N dans l’argument i représente le nombre total de lignes dans la table de données. Cela peut être utilisé pour effectuer un sous-ensemble sur le nombre de lignes :

``` r
linelist[.N] #renvoie la dernière ligne
linelist[15:.N] #returns the 15th to the last row
```

### Utilisation de fonctions d’aide pour le filtrage

Le tableau de données utilise des fonctions d’aide qui facilitent le sous-ensemble des lignes. La fonction `%like%` est utilisée pour faire correspondre un motif dans une colonne, `%chin%` est utilisée pour faire correspondre un caractère spécifique, et la fonction d’aide `%between%` est utilisée pour faire correspondre des colonnes numériques dans une plage prédéfinie.

Dans les exemples suivants, nous : \* filtrons les lignes où la variable hospital contient “Hospital”. \* filtrons les lignes où le résultat est “Recover” ou “Death”. \* filtrons les lignes dans la tranche d’âge 40-60 ans

``` r
linelist[hospital %like% "Hospital"] #filtre les lignes où la variable hospital contient "Hospital"
linelist[outcome %chin% c("Recover", "Death")] #filtre les lignes où l'issue est "Recover" ou "Death".
linelist[age %between% c(40, 60)] #filtre les lignes dans la tranche d'âge 40-60

#%between% doit prendre un vecteur de longueur 2, tandis que %chin% peut prendre des vecteurs de longueur >= 1
```

## 50.4 L’argument j: sélection et calcul sur les colonnes

En utilisant la structure **DT\[i, j, by\]**, nous pouvons sélectionner des colonnes en utilisant des nombres ou des noms. L’argument **j** est le second ; on utilise donc la syntaxe **DT\[, j\]**. Pour faciliter les calculs sur l’argument **j**, la colonne est enveloppée en utilisant soit `list()` soit `.()`.

### Sélection de colonnes

Le premier exemple récupère les première, troisième et cinquième colonnes de la table de données, le deuxième exemple sélectionne toutes les colonnes à l’exception des colonnes taille, poids et sexe. Le troisième exemple utilise la terminaison `.()` pour sélectionner les colonnes **identification du cas** et **résultat**.

``` r
linelist[ , c(1,3,5)]
linelist[ , -c("gender", "age", "wt_kg", "ht_cm")]
linelist[ , list(case_id, outcome)] #linelist[ , .(case_id, outcome)] fonctionne tout aussi bien
```

### Calcul sur les colonnes

En combinant les arguments **i** et **j**, il est possible de filtrer les lignes et de calculer sur les colonnes. L’utilisation de **.N** dans l’argument **j** représente également le nombre total de lignes dans le tableau de données et peut être utile pour retourner le nombre de lignes après le filtrage des lignes.

Dans les exemples suivants, nous : \* Comptons le nombre de cas qui sont restés plus de 7 jours à l’hôpital. \* Calculer l’âge moyen des cas qui sont décédés à l’hôpital militaire. \* Calculer l’écart-type, la médiane et l’âge moyen des cas qui se sont rétablis à l’hôpital central.

``` r
linelist[days_onset_hosp > 7 , .N]
```

    [1] 189

``` r
linelist[hospital %like% "Military" & outcome %chin% "Death", .(mean(age, na.rm = T))] #na.rm = T supprime les valeurs N/A
```

            V1
         <num>
    1: 15.9084

``` r
linelist[hospital == "Central Hospital" & outcome == "Recover", 
                 .(mean_age = mean(age, na.rm = T),
                   median_age = median(age, na.rm = T),
                   sd_age = sd(age, na.rm = T))] #cette syntaxe n'utilise pas les fonctions d'aide mais fonctionne tout aussi bien
```

       mean_age median_age   sd_age
          <num>      <num>    <num>
    1: 16.85185         14 12.93857

N’oubliez pas que l’utilisation de la terminaison .() dans l’argument j facilite le calcul, renvoie un tableau de données et permet de nommer les colonnes.

## 50.5 L’argument by : calcul par groupes

L’argument **by** est le troisième argument de la structure **DT\[i, j, by\]**. L’argument **by** accepte à la fois un vecteur de caractères et la syntaxe `list()` ou `.()`. L’utilisation de la syntaxe `.()` dans l’argument **by** permet de renommer les colonnes à la volée.

Dans les exemples suivants, nous :  
\* regroupons le nombre de cas par hôpital \* dans les cas de 18 ans ou plus, calculer la taille et le poids moyens des cas selon le sexe et selon qu’ils sont guéris ou décédés \* dans les admissions qui ont duré plus de 7 jours, compter le nombre de cas selon le mois d’admission et l’hôpital où ils ont été admis.

``` r
linelist[, .N, .(hospital)] #le nombre de cas par hôpital
```

                                   hospital     N
                                     <char> <int>
    1:                                Other   885
    2:                              Missing  1469
    3: St. Mark's Maternity Hospital (SMMH)   422
    4:                        Port Hospital  1762
    5:                    Military Hospital   896
    6:                     Central Hospital   454

``` r
linelist[age > 18, .(mean_wt = mean(wt_kg, na.rm = T),
                             mean_ht = mean(ht_cm, na.rm = T)), .(gender, outcome)] #NAs représentent les catégories pour lesquelles les données sont manquantes
```

       gender outcome  mean_wt  mean_ht
       <char>  <char>    <num>    <num>
    1:      m Recover 71.90227 178.1977
    2:      f   Death 63.27273 159.9448
    3:      m   Death 71.61770 175.4726
    4:      f    <NA> 64.49375 162.7875
    5:      m    <NA> 72.65505 176.9686
    6:      f Recover 62.86498 159.2996
    7:   <NA> Recover 67.21429 175.2143
    8:   <NA>   Death 69.16667 170.7917
    9:   <NA>    <NA> 70.25000 175.5000

``` r
linelist[days_onset_hosp > 7, .N, .(month = month(date_hospitalisation), hospital)]
```

        month                             hospital     N
        <num>                               <char> <int>
     1:     5                    Military Hospital     3
     2:     6                        Port Hospital     4
     3:     7                        Port Hospital     8
     4:     8 St. Mark's Maternity Hospital (SMMH)     5
     5:     8                    Military Hospital     9
     6:     8                                Other    10
     7:     8                        Port Hospital    10
     8:     9                        Port Hospital    28
     9:     9                              Missing    27
    10:     9                     Central Hospital    10
    11:     9 St. Mark's Maternity Hospital (SMMH)     6
    12:    10                              Missing     2
    13:    10                    Military Hospital     3
    14:     3                        Port Hospital     1
    15:     4                    Military Hospital     1
    16:     5                                Other     2
    17:     5                     Central Hospital     1
    18:     5                              Missing     1
    19:     6                              Missing     7
    20:     6 St. Mark's Maternity Hospital (SMMH)     2
    21:     6                    Military Hospital     1
    22:     7                    Military Hospital     3
    23:     7                                Other     1
    24:     7                              Missing     2
    25:     7 St. Mark's Maternity Hospital (SMMH)     1
    26:     8                     Central Hospital     2
    27:     8                              Missing     6
    28:     9                                Other     9
    29:     9                    Military Hospital    11
    30:    10                        Port Hospital     3
    31:    10                                Other     4
    32:    10 St. Mark's Maternity Hospital (SMMH)     1
    33:    10                     Central Hospital     1
    34:    11                              Missing     2
    35:    11                        Port Hospital     1
    36:    12                        Port Hospital     1
        month                             hospital     N
        <num>                               <char> <int>

Data.table permet également d’enchaîner les expressions comme suit :

``` r
linelist[, .N, .(hospital)][order(-N)][1:3] #La première sélectionne tous les cas par hôpital, la deuxième ordonne les cas par ordre décroissant, la troisième sous-ensemble les 3 hôpitaux ayant le plus grand nombre de cas.
```

                hospital     N
                  <char> <int>
    1:     Port Hospital  1762
    2:           Missing  1469
    3: Military Hospital   896

Dans ces exemples, nous partons du principe qu’une ligne du tableau de données correspond à un nouveau cas, et nous pouvons donc utiliser la fonction **.N** pour représenter le nombre de lignes du tableau de données. Une autre fonction utile pour représenter le nombre de cas uniques est `uniqueN()`, qui retourne le nombre de valeurs uniques dans une entrée donnée. Ceci est illustré ici :

``` r
linelist[, .(uniqueN(gender))] #souvenez-vous que .() dans l'argument j renvoie un tableau de données
```

          V1
       <int>
    1:     3

La réponse est 3, car les valeurs uniques de la colonne sexe sont m, f et N/A. Comparez avec la fonction R de base `unique()`, qui renvoie toutes les valeurs uniques dans une entrée donnée :

``` r
linelist[, .(unique(gender))]
```

           V1
       <char>
    1:      m
    2:      f
    3:   <NA>

Pour trouver le nombre de cas uniques dans un mois donné, nous écririons ce qui suit :

``` r
linelist[, .(uniqueN(case_id)), .(month = month(date_hospitalisation))]
```

        month    V1
        <num> <int>
     1:     5    62
     2:     6   100
     3:     7   198
     4:     8   509
     5:     9  1170
     6:    10  1228
     7:    11   813
     8:    12   576
     9:     1   434
    10:     2   310
    11:     3   290
    12:     4   198

## 50.6 Ajout et mise à jour des tables de données

L’opérateur `:=` est utilisé pour ajouter ou mettre à jour des données dans une table de données. L’ajout de colonnes à votre table de données peut se faire de la manière suivante :

``` r
linelist[, adult := age >= 18] #ajoute une colonne
linelist[, c("child", "wt_lbs") := .(age < 18, wt_kg*2.204)] #pour ajouter plusieurs colonnes, il faut utiliser la syntaxe c("") et list() ou .()
linelist[, `:=` (bmi_in_range = (bmi > 16 & bmi < 40),
                         no_infector_source_data = is.na(infector) | is.na(source))] #Cette méthode utilise := comme un opérateur fonctionnel `:=`.
linelist[, adult := NULL] #supprime la colonne
```

Des agrégations plus complexes dépassent le cadre de ce chapitre d’introduction, mais l’idée est de fournir une alternative populaire et viable à **dplyr** pour regrouper et nettoyer les données. Le package **data.table** est un excellent package qui permet d’obtenir un code soigné et lisible.

## 50.7 Ressources

Voici quelques ressources utiles pour plus d’informations : \* https://cran.r-project.org/web/packages/data.table/vignettes/datatable-intro.html \* https://github.com/Rdatatable/data.table \* https://s3.amazonaws.com/assets.datacamp.com/img/blog/data+table+cheat+sheet.pdf \* https://www.machinelearningplus.com/data-manipulation/datatable-in-r-complete-guide/ \* https://www.datacamp.com/community/tutorials/data-table-r-tutorial

Vous pouvez exécuter n’importe quelle fonction de synthèse sur des données groupées ; voir la Cheat Sheet ici pour plus d’informations : https://s3.amazonaws.com/assets.datacamp.com/blog_assets/datatable_Cheat_Sheet_R.pdf
