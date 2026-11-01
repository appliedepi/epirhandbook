# 45  Interactions avec les répertoires

Dans cette page, nous couvrons les scénarios courants où vous créez, interagissez avec, enregistrez et importez avec des répertoires (dossiers).

## 45.1 Préparation

### Paquet **fs**

Le paquet **fs** est un paquet **tidyverse** qui facilite les interactions avec les répertoires, en améliorant certaines des fonctions **base** de R. Dans les sections ci-dessous, nous utiliserons souvent des fonctions de **fs**.

``` r
pacman::p_load(
  fs, # interactions fichiers/répertoires
  rio, # importation/exportation
  here, # chemins d'accès relatifs aux fichiers
  tidyverse) # gestion et visualisation des données
```

### Imprimer le répertoire comme un arbre de dendrogramme

Utilisez la fonction `dir_tree()` de **fs**.

Fournissez le chemin d’accès au dossier dans `path =`. Utilisez `recurse = FALSE` pour afficher un seul niveau, ou `recurse = TRUE` pour afficher tous les fichiers de tous les sous-niveaux. Ci-dessous, nous utilisons `here()` comme raccourci pour le projet R et spécifions son sous-dossier “data”, qui contient les données d’exemple de ce manuel. Nous le paramétrons pour afficher tous les fichiers contenus dans “data” et ses sous-dossiers.

``` r
fs::dir_tree(path = here("data"), recurse = TRUE)
```

    data
    ├── case_linelists
    │   └── linelist_cleaned.rds
    ├── example
    │   ├── central_hospital.csv
    │   ├── district_weekly_count_data.xlsx
    │   ├── fluh7n9_china_2013.csv
    │   ├── hospital_linelists.xlsx
    │   ├── linelists
    │   │   ├── 20201007linelist.csv
    │   │   ├── case_linelist20201006.csv
    │   │   ├── case_linelist_2020-10-02.csv
    │   │   ├── case_linelist_2020-10-03.csv
    │   │   ├── case_linelist_2020-10-04.csv
    │   │   ├── case_linelist_2020-10-05.csv
    │   │   └── case_linelist_2020-10-08.xlsx
    │   ├── military_hospital.csv
    │   ├── missing.csv
    │   ├── other.csv
    │   ├── port_hospital.csv
    │   └── st_marks_maternity_hospital.csv
    ├── flexdashboard
    │   ├── outbreak_dashboard.Rmd
    │   ├── outbreak_dashboard.html
    │   └── outbreak_dashboard_test.html
    └── malaria_app
        ├── app.R
        ├── data
        │   └── facility_count_data.rds
        ├── funcs
        │   └── plot_epicurve.R
        ├── global.R
        ├── malaria_app.Rproj
        ├── server.R
        └── ui.R

## 45.2 Lister les fichiers d’un répertoire

Pour lister uniquement les noms de fichiers d’un répertoire, vous pouvez utiliser `dir()` à partir de **base** R. Par exemple, cette commande liste les noms des fichiers contenus dans le sous-dossier “linelists” du dossier “example” d’un projet R. Le chemin de fichier relatif est fourni en utilisant `here()`. (dont vous trouverez plus d’informations sur la page [Importer et exporter des données](importing.llms.md) ).

``` r
# noms de fichiers
dir(here("data", "example", "linelists"))
```

    [1] "20201007linelist.csv"          "case_linelist_2020-10-02.csv" 
    [3] "case_linelist_2020-10-03.csv"  "case_linelist_2020-10-04.csv" 
    [5] "case_linelist_2020-10-05.csv"  "case_linelist_2020-10-08.xlsx"
    [7] "case_linelist20201006.csv"    

Pour lister les chemins complets des fichiers du répertoire, vous pouvez utiliser `dir_ls()` de **fs**. Une alternative R **base** est `list.files()`.

``` r
# chemins d'accès aux fichiers
dir_ls(here("data", "example", "linelists"))
```

    data/example/linelists/20201007linelist.csv
    data/example/linelists/case_linelist20201006.csv
    data/example/linelists/case_linelist_2020-10-02.csv
    data/example/linelists/case_linelist_2020-10-03.csv
    data/example/linelists/case_linelist_2020-10-04.csv
    data/example/linelists/case_linelist_2020-10-05.csv
    data/example/linelists/case_linelist_2020-10-08.xlsx

Pour obtenir toutes les informations sur les métadonnées de chaque fichier d’un répertoire (par exemple le chemin, la date de modification, etc.), vous pouvez utiliser `dir_info()` de **fs**.

Cela peut être particulièrement utile si vous voulez extraire la date de dernière modification du fichier, par exemple si vous voulez importer la version la plus récente d’un fichier. Pour un exemple de ceci, voir la page [Importer et exporter des données](importing.llms.md).

``` r
# informations sur le fichier
dir_info(here("data", "example", "linelists"))
```

Voici le cadre de données renvoyé. Faites défiler vers la droite pour voir toutes les colonnes.

## 45.3 Informations sur les fichiers

Pour extraire des informations de métadonnées sur un fichier spécifique, vous pouvez utiliser `file_info()`de **fs** (ou `file.info()`de **base** R).

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))
```

Ici, nous utilisons le `$` pour indexer le résultat et retourner uniquement la valeur `modification_time`.

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))$modification_time
```

    [1] "2026-11-01 15:52:14 UTC"

## 45.4 Vérifier s’il existe

### Objets R

Vous pouvez utiliser `exists()` de **base** R pour vérifier si un objet R existe *dans* R (fournir le nom de l’objet entre guillemets).

``` r
exists("linelist")
```

    [1] FALSE

Notez que certains paquets R **base** utilisent des noms d’objets génériques comme “data” en coulisse, qui apparaîtront comme VRAIS à moins que `inherit = FALSE` soit spécifié. C’est une des raisons pour ne pas nommer votre jeu de données “data”.

``` r
exists("data")
```

    [1] TRUE

``` r
exists("data", inherit = FALSE)
```

    [1] FALSE

Si vous écrivez une fonction, vous devriez utiliser `missing()` de **base** R pour vérifier si un argument est présent ou non, au lieu de `exists()`.

### Répertoires

Pour vérifier si un répertoire existe, fournissez le chemin du fichier (et son nom) à `is_dir()` de **fs**. Faites défiler vers la droite pour voir que `TRUE` est imprimé.

``` r
is_dir(here("data"))
```

    data 
    TRUE 

Une alternative est `file.exists()` de **base** R.

### Les fichiers

Pour vérifier si un fichier spécifique existe, utilisez `is_file()` de **fs**. Faites défiler vers la droite pour voir que `TRUE` est imprimé.

``` r
is_file(here("data", "case_linelists", "linelist_cleaned.rds"))
```

    data/case_linelists/linelist_cleaned.rds 
                                        TRUE 

Une alternative **base** R est `file.exists()`.

## 45.5 Créer

### Répertoires

Pour créer un nouveau répertoire (dossier), vous pouvez utiliser `dir_create()` de **fs**. Si le répertoire existe déjà, il ne sera pas écrasé et aucune erreur ne sera retournée.

``` r
dir_create(here("data", "test"))
```

Une alternative est `dir.create()` de **base** R, qui affichera une erreur si le répertoire existe déjà. En revanche, `dir_create()` dans ce scénario sera silencieux.

### Fichiers

Vous pouvez créer un fichier (vide) avec `file_create()` à partir de **fs**. Si le fichier existe déjà, il ne sera pas écrasé ou modifié.

``` r
file_create(here("data", "test.rds"))
```

Une alternative R **base** est `file.create()`. Mais si le fichier existe déjà, cette option le tronquera. Si vous utilisez `file_create()`, le fichier sera laissé inchangé.

### Créer si n’existe pas

EN COURS DE CONSTRUCTION

## 45.6 Supprimer

### Objets R

Utilisez `rm()` de **base** R pour supprimer un objet R.

### Répertoires

Utilisez `dir_delete()` de **fs**.

### Fichiers

Vous pouvez supprimer des fichiers avec `file_delete()` de **fs**.

## 45.7 Exécuter d’autres fichiers

### `source()`

Pour exécuter un script R à partir d’un autre script R, vous pouvez utiliser la commande `source()` (de **base** R).

``` r
source(here("scripts", "cleaning_scripts", "clean_testing_data.R"))
```

Cela revient à afficher le script R ci-dessus et à cliquer sur le bouton “Source” en haut à droite du script. Ceci exécutera le script mais le fera silencieusement (pas de sortie sur la console R) sauf si cela est spécifiquement prévu.

[![](../../images/source_button.png)](../../images/source_button.png)

### `render()`

`render()` est une variation de `source()` le plus souvent utilisée pour les scripts R markdown. Vous fournissez le `input =` qui est le fichier R markdown, et aussi le `output_format =` (typiquement soit “html_document”, “pdf_document”, “word_document”, ““).

Voir la page sur les [Production de rapports avec R Markdown](rmarkdown.llms.md) pour plus de détails. Consultez également la documentation de `render()` [ici](https://rmarkdown.rstudio.com/docs/reference/render.html) ou en entrant `?render`.

### Exécuter des fichiers dans un répertoire

Vous pouvez créer une *boucle for* et l’utiliser pour `source()` chaque fichier d’un répertoire, tel qu’identifié avec `dir()`.

``` r
for(script in dir(here("scripts"), pattern = ".R$")) { # pour chaque nom de script dans le dossier "scripts" du projet R (avec l'extension .R)
  source(here("scripts", script))                        # source le fichier avec le nom correspondant qui existe dans le dossier scripts
}
```

Si vous ne voulez exécuter que certains scripts, vous pouvez les identifier par leur nom comme ceci :

``` r
scripts_to_run <- c(
     "epicurves.R",
     "demographic_tables.R",
     "survival_curves.R"
)

for(script in scripts_to_run) {
  source(here("scripts", script))
}
```

Voici une [comparaison](https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html) des fonctions R **fs** et **base**.

### Importer des fichiers dans un répertoire

Voir la page [Importer et exporter des données](importing.llms.md) pour importer et exporter des fichiers individuels.

Consultez également la page [Importer et exporter des données](importing.llms.md) pour connaître les méthodes permettant d’importer automatiquement le fichier le plus récent, en fonction d’une date figurant dans le nom du fichier *ou* en examinant les métadonnées du fichier.

Voir la page [Itération, boucles et listes](iteration.llms.md) pour un exemple avec le paquet **purrr** démontrant :

- La division d’un cadre de données et son enregistrement dans plusieurs fichiers CSV.  
- Division d’un cadre de données et enregistrement de chaque partie comme une feuille séparée dans un classeur Excel.  
- Importer plusieurs fichiers CSV et les combiner en un seul cadre de données.  
- Importer un classeur Excel avec plusieurs feuilles et les combiner dans un cadre de données.

## 45.8 **base** R

Voir ci-dessous les fonctions `list.files()` et `dir()`, qui effectuent la même opération de listage des fichiers dans un répertoire spécifié. Vous pouvez spécifier `ignore.case =` ou un motif spécifique à rechercher.

``` r
list.files(path = here("data"))

list.files(path = here("data", "example"), pattern = "\\.csv$")
# dir(path = here("data", "example"), pattern = "\\.csv$")

list.files(path = here("data", "example"), pattern = "hospital", ignore.case = TRUE)
```

Si un fichier est actuellement “ouvert”, il s’affiche dans votre dossier avec un tilde devant, comme “~\$hospital_linelists.xlsx”.

## 45.9 Ressources

https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html
