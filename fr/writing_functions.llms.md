# 44  Fonctions d’écriture

## 44.1 Préparation

### Load packages

Ce morceau de code montre le chargement des paquets nécessaires aux analyses. Dans ce manuel, nous mettons l’accent sur `p_load()` de **pacman**, qui installe le paquet si nécessaire *et* le charge pour l’utiliser. Vous pouvez aussi charger les paquets installés avec `library()` de **base** R. Voir la page sur \[R basics\] pour plus d’informations sur les paquets R.

### Importer des données

Nous importons le jeu de données des cas d’une épidémie d’Ebola simulée. Si vous souhaitez télécharger les données pour les suivre pas à pas, consultez les instructions de la page [Télécharger le manuel et les données](download.llms.md). Le jeu de données est importé à l’aide de la fonction `import()` du paquet **rio**. Voir la page [Importer et exporter des données](importing.llms.md) pour les différentes manières d’importer des données.

Nous utiliserons également dans la dernière partie de cette page des données sur la grippe H7N9 de 2013.

## 44.2 Fonctions

Les fonctions sont utiles en programmation car elles permettent de rendre les codes plus faciles à comprendre, plus courts et moins sujets aux erreurs (à condition qu’il n’y ait pas d’erreurs dans la fonction elle-même).

Si vous êtes arrivé jusqu’à ce manuel, cela signifie que vous avez rencontré d’innombrables fonctions, car en R, chaque opération est un appel de fonction. `+, for, if, [, $, { …`. Par exemple, `x + y` est la même chose que `'+'(x, y)`.

R est l’un des langages qui offre le plus de possibilités de travailler avec des fonctions et qui donne suffisamment d’outils à l’utilisateur pour les écrire facilement. Nous ne devrions pas penser aux fonctions comme étant fixées au sommet ou à la fin de la chaîne de programmation, R offre la possibilité de les utiliser comme s’il s’agissait de vecteurs et même de les utiliser à l’intérieur d’autres fonctions, listes…

Il existe de nombreuses ressources très avancées sur la programmation fonctionnelle et nous ne donnerons ici qu’un aperçu pour vous aider à démarrer avec la programmation fonctionnelle avec de courts exemples pratiques. Nous vous encourageons ensuite à visiter les liens sur les références pour en savoir plus.

## 44.3 Pourquoi utiliser une fonction ?

Avant de répondre à cette question, il est important de noter que vous avez déjà eu des conseils pour écrire vos toutes premières fonctions R dans la page sur \[l’itération, les boucles et les listes\] de ce manuel. En fait, l’utilisation de “if/else” et de boucles est souvent au cour de bon nombre de nos fonctions car elles permettent d’élargir l’application de notre code en autorisant des conditions multiples ou d’itérer des codes pour des tâches répétitives.

- Je répète plusieurs fois le même bloc de code pour l’appliquer à une variable ou à des données différentes ?

- Si je m’en débarrasse, cela raccourcira-t-il considérablement mon code global et le rendra-t-il plus rapide ?

- Est-il possible que le code que j’ai écrit soit réutilisé mais avec une valeur différente à plusieurs endroits du code ?

Si la réponse à l’une des questions précédentes est “OUI”, alors vous avez probablement besoin d’écrire une fonction

## 44.4 Comment R construit-il les fonctions ?

Les fonctions dans R ont trois composants principaux :

- le `formals()` qui est la liste d’arguments qui contrôle la façon dont nous pouvons appeler la fonction.

- le `body()` qui est le code à l’intérieur de la fonction, c’est-à-dire entre les accolades ou à la suite de la parenthèse, selon la façon dont on l’écrit.

et,

- l’ `environment()` qui aide à localiser les variables de la fonction et détermine comment la fonction trouve sa valeur.

Une fois que vous avez créé votre fonction, vous pouvez vérifier chacun de ces composants en appelant la fonction associée.

## 44.5 Syntaxe et structure de base

- Une fonction devra être nommée correctement afin que son travail soit facilement compréhensible dès que l’on lit son nom. En fait, c’est déjà le cas avec la majorité de l’architecture R de base. Des fonctions comme `mean()`, `print()`, `summary()` ont des noms qui sont très simples.

- Une fonction a besoin d’arguments, comme les données sur lesquelles elle travaille et d’autres objets qui peuvent être des valeurs statiques, entre autres options.

- Et enfin, une fonction donnera une sortie basée sur sa tâche principale et les arguments qui lui ont été donnés. Habituellement, nous utilisons les fonctions intégrées telles que `print()`, `return()`… pour produire la sortie. La sortie peut être une valeur logique, un nombre, un caractère, un cadre de données… en bref, tout type d’objet R.

En gros, c’est la composition d’une fonction :

``` r
function_name <- function(argument_1, argument_2, argument_3){
  
           function_task
  
           return(output)
}
```

Nous pouvons créer notre première fonction qui sera appelée \`contain_covid19()\`\`.

``` r
contain_covid19 <- function(barrier_gest, wear_mask, get_vaccine){
  
                            if(barrier_gest == "yes" & wear_mask == "yes" & get_vaccine == "yes" ) 
       
                            return("success")
  
  else("please make sure all are yes, this pandemic has to end!")
}
```

Nous pouvons ensuite vérifier les composants de notre fonction nouvellement créée.

``` r
formals(contain_covid19)
```

    $barrier_gest


    $wear_mask


    $get_vaccine

``` r
body(contain_covid19)
```

    {
        if (barrier_gest == "yes" & wear_mask == "yes" & get_vaccine == 
            "yes") 
            return("success")
        else ("please make sure all are yes, this pandemic has to end!")
    }

``` r
environment(contain_covid19)
```

    <environment: R_GlobalEnv>

Maintenant, nous allons tester notre fonction. Pour appeler notre fonction écrite, vous l’utilisez comme vous utilisez toutes les fonctions R, c’est-à-dire en écrivant le nom de la fonction et en ajoutant les arguments requis.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "yes")
```

    [1] "success"

Par précaution, nous pouvons réécrire le nom de chaque argument. Mais sans les préciser, le code devrait fonctionner puisque R a en mémoire le positionnement de chaque argument. Ainsi, tant que vous mettez les valeurs des arguments dans le bon ordre, vous pouvez éviter d’écrire les noms des arguments lors de l’appel des fonctions.

``` r
contain_covid19("yes", "yes", "yes")
```

    [1] "success"

Voyons ensuite ce qui se passe si l’une des valeurs est `"no"` ou **pas** `"yes"`.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "no")
```

    [1] "please make sure all are yes, this pandemic has to end!"

Si nous fournissons un argument qui n’est pas reconnu, nous obtenons une erreur:

``` r
contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", get_vaccine = "no")
```

\`Erreur dans contain_covid19(barrier_gest = “sometimes”, wear_mask = “yes”, : Impossible de trouver la fonction “contain_covid19”\`\`.

***NOTE:*** Certaines fonctions (la plupart du temps très courtes et simples) peuvent ne pas avoir besoin de nom et peuvent être utilisées directement sur une ligne de code ou à l’intérieur d’une autre fonction pour effectuer une tâche rapide. Elles sont appelées **fonctions anonymes** .

Par exemple ci-dessous est une première fonction anonyme qui ne garde que les variables de caractères le jeu de données.

``` r
linelist %>% 
  dplyr::slice_head(n=10) %>% #équivalent à la fonction "head" de base de R et qui renvoie les n premières observations de l'ensemble de données.
  select(function(x) is.character(x)) 
```

Ensuite, une autre fonction qui sélectionne une observation sur deux de notre ensemble de données (cela peut être utile lorsque nous avons des données longitudinales avec de nombreux enregistrements par patient, par exemple après avoir été classés par date ou par visite). Dans ce cas, la fonction à écrire en dehors de dplyr serait `function (x) (x%%2 == 0)` pour s’appliquer au vecteur contenant tous les numéros de ligne.

``` r
linelist %>%   
   slice_head(n=20) %>% 
   tibble::rownames_to_column() %>% # ajoute les indices de chaque obs comme rownames pour voir clairement la sélection finale
   filter(row_number() %%2 == 0)
```

Un code R de base possible pour la même tâche serait le suivant :

``` r
linelist_firstobs <- head(linelist, 20)

linelist_firstobs[base::Filter(function(x) (x%%2 == 0), seq(nrow(linelist_firstobs))),]
```

***CAUTION:*** S’il est vrai que l’utilisation de fonctions peut nous aider dans notre code, il peut néanmoins être long d’écrire certaines fonctions ou d’en corriger une si elle n’a pas été pensée en profondeur, écrite de manière adéquate et qu’elle renvoie des erreurs en conséquence. C’est pour cette raison qu’il est souvent recommandé d’écrire d’abord le code R, de s’assurer qu’il fait ce que nous voulons qu’il fasse, puis de le transformer en une fonction avec ses trois composants principaux tels que listés ci-dessus.

## 44.6 Exemples

### Retourner les tableaux de proportion pour plusieurs colonnes

Oui, nous avons déjà de belles fonctions dans de nombreux paquets permettant de résumer des informations d’une manière très simple et agréable. Mais nous allons tout de même essayer de créer nos propres fonctions, lors de nos premiers pas dans l’écriture de fonctions.

Dans cet exemple, nous voulons montrer comment l’écriture d’une simple fonction vous évitera de copier-coller le même code plusieurs fois.

``` r
proptab_multiple <- function(my_data, var_to_tab){
  
  #imprimez le nom de chaque variable d'intérêt avant de faire la tabulation
  print(var_to_tab)

  with(my_data,
       rbind( #liez les résultats des deux fonctions suivantes par ligne
        #tabuler la variable d'intérêt: ne donne que des nombres
          table(my_data[[var_to_tab]], useNA = "no"),
          #calculer les proportions pour chaque variable d'intérêt et arrondir la valeur à 2 décimales
         round(prop.table(table(my_data[[var_to_tab]]))*100,2)
         )
       )
}


proptab_multiple(linelist, "gender")
```

    [1] "gender"

               f       m
    [1,] 2807.00 2803.00
    [2,]   50.04   49.96

``` r
proptab_multiple(linelist, "age_cat")
```

    [1] "age_cat"

             0-4     5-9  10-14  15-19   20-29 30-49 50-69 70+
    [1,] 1095.00 1095.00 941.00 743.00 1073.00   754 95.00 6.0
    [2,]   18.87   18.87  16.22  12.81   18.49    13  1.64 0.1

``` r
proptab_multiple(linelist, "outcome")
```

    [1] "outcome"

           Death Recover
    [1,] 2582.00 1983.00
    [2,]   56.56   43.44

***TIP:*** Comme indiqué ci-dessus, il est très important de commenter vos fonctions comme vous le feriez pour la programmation générale. Gardez à l’esprit que le but d’une fonction est de rendre un code facile à lire, plus court et plus efficace. Alors on devrait être capable de comprendre ce que fait la fonction juste en lisant son nom et avoir plus de détails en lisant les commentaires.

Une deuxième option est d’utiliser cette fonction dans une autre via une boucle pour faire le processus en une fois :

``` r
for(var_to_tab in c("gender","age_cat",  "outcome")){
  
  print(proptab_multiple(linelist, var_to_tab))
  
}
```

    [1] "gender"
               f       m
    [1,] 2807.00 2803.00
    [2,]   50.04   49.96
    [1] "age_cat"
             0-4     5-9  10-14  15-19   20-29 30-49 50-69 70+
    [1,] 1095.00 1095.00 941.00 743.00 1073.00   754 95.00 6.0
    [2,]   18.87   18.87  16.22  12.81   18.49    13  1.64 0.1
    [1] "outcome"
           Death Recover
    [1,] 2582.00 1983.00
    [2,]   56.56   43.44

Une manière plus simple serait d’utiliser la fonction “apply” de base R au lieu d’une “boucle for” comme exprimé ci-dessous :

***TIP:*** R est souvent défini comme un langage de programmation fonctionnel et presque chaque fois que vous exécutez une ligne de code, vous utilisez certaines fonctions intégrées. Une bonne habitude pour être plus à l’aise avec l’écriture de fonctions est d’avoir souvent un regard interne sur la façon dont les fonctions de base que vous utilisez quotidiennement sont construites. Le raccourci pour le faire est de sélectionner le nom de la fonction puis de cliquer sur `Ctrl+F2` ou `fn+F2` ou `Cmd+F2` (selon votre ordinateur) .

## 44.7 Utilisation de **purrr** : écrire des fonctions qui peuvent être appliquées de manière itérative.

### Modifier la classe de plusieurs colonnes dans un ensemble de données

Disons que de nombreuses variables de caractère dans les données originales `linelist` doivent être changées en “factor” pour des raisons d’analyse et de traçage. Au lieu de répéter l’étape plusieurs fois, nous pouvons juste utiliser `lapply()` pour faire la transformation de toutes les variables concernées sur une seule ligne de code.

***CAUTION:*** `lapply()` renvoie une liste, donc son utilisation peut nécessiter une modification supplémentaire en dernière étape.

La même étape peut être effectuée en utilisant la fonction `map_if()` du paquet **purrr**.

``` r
linelist_factor2 <- linelist %>%
  purrr::map_if(is.character, as.factor)


linelist_factor2 %>%
        glimpse()
```

    List of 30
     $ case_id             : Factor w/ 5888 levels "00031d","00086d",..: 2134 3022 396 4203 3084 4347 179 1241 5594 430 ...
     $ generation          : num [1:5888] 4 4 2 3 3 3 4 4 4 4 ...
     $ date_infection      : Date[1:5888], format: "2014-05-08" NA ...
     $ date_onset          : Date[1:5888], format: "2014-05-13" "2014-05-13" ...
     $ date_hospitalisation: Date[1:5888], format: "2014-05-15" "2014-05-14" ...
     $ date_outcome        : Date[1:5888], format: NA "2014-05-18" ...
     $ outcome             : Factor w/ 2 levels "Death","Recover": NA 2 2 NA 2 2 2 1 2 1 ...
     $ gender              : Factor w/ 2 levels "f","m": 2 1 2 1 2 1 1 1 2 1 ...
     $ age                 : num [1:5888] 2 3 56 18 3 16 16 0 61 27 ...
     $ age_unit            : Factor w/ 2 levels "months","years": 2 2 2 2 2 2 2 2 2 2 ...
     $ age_years           : num [1:5888] 2 3 56 18 3 16 16 0 61 27 ...
     $ age_cat             : Factor w/ 8 levels "0-4","5-9","10-14",..: 1 1 7 4 1 4 4 1 7 5 ...
     $ age_cat5            : Factor w/ 18 levels "0-4","5-9","10-14",..: 1 1 12 4 1 4 4 1 13 6 ...
     $ hospital            : Factor w/ 6 levels "Central Hospital",..: 4 3 6 5 2 5 3 3 3 3 ...
     $ lon                 : num [1:5888] -13.2 -13.2 -13.2 -13.2 -13.2 ...
     $ lat                 : num [1:5888] 8.47 8.45 8.46 8.48 8.46 ...
     $ infector            : Factor w/ 2697 levels "00031d","002e6c",..: 2594 NA NA 2635 180 1799 1407 195 NA NA ...
     $ source              : Factor w/ 2 levels "funeral","other": 2 NA NA 2 2 2 2 2 NA NA ...
     $ wt_kg               : num [1:5888] 27 25 91 41 36 56 47 0 86 69 ...
     $ ht_cm               : num [1:5888] 48 59 238 135 71 116 87 11 226 174 ...
     $ ct_blood            : num [1:5888] 22 22 21 23 23 21 21 22 22 22 ...
     $ fever               : Factor w/ 2 levels "no","yes": 1 NA NA 1 1 1 NA 1 1 1 ...
     $ chills              : Factor w/ 2 levels "no","yes": 1 NA NA 1 1 1 NA 1 1 1 ...
     $ cough               : Factor w/ 2 levels "no","yes": 2 NA NA 1 2 2 NA 2 2 2 ...
     $ aches               : Factor w/ 2 levels "no","yes": 1 NA NA 1 1 1 NA 1 1 1 ...
     $ vomit               : Factor w/ 2 levels "no","yes": 2 NA NA 1 2 2 NA 2 2 1 ...
     $ temp                : num [1:5888] 36.8 36.9 36.9 36.8 36.9 37.6 37.3 37 36.4 35.9 ...
     $ time_admission      : Factor w/ 1072 levels "00:10","00:29",..: NA 308 746 415 514 589 609 297 409 387 ...
     $ bmi                 : num [1:5888] 117.2 71.8 16.1 22.5 71.4 ...
     $ days_onset_hosp     : num [1:5888] 2 1 2 2 1 1 2 1 1 2 ...

### Produire itérativement des graphiques pour différents niveaux d’une variable

Nous allons produire ici un graphique circulaire pour examiner la distribution des résultats des patients en Chine pendant l’épidémie de H7N9 pour chaque province. Au lieu de répéter le code pour chacun d’entre eux, nous allons simplement appliquer une fonction que nous allons créer.

``` r
#Préciser les options pour l'utilisation de highchart
options(highcharter.theme =   highcharter::hc_theme_smpl(tooltip = list(valueDecimals = 2)))


#créer une fonction appelée "chart_outcome_province" qui prend comme argument l'ensemble de données et le nom de la province pour laquelle on veut tracer la distribution du résultat.

chart_outcome_province <- function(data_used, prov){
  
  tab_prov <- data_used %>% 
    filter(province == prov,
           !is.na(outcome))%>% 
    group_by(outcome) %>% 
    count() %>%
    adorn_totals(where = "row") %>% 
    adorn_percentages(denominator = "col", )%>%
    mutate(
        perc_outcome= round(n*100,2))
  
  
  tab_prov %>%
    filter(outcome != "Total") %>% 
  highcharter::hchart(
    "pie", hcaes(x = outcome, y = perc_outcome),
    name = paste0("Distibution of the outcome in:", prov)
    )
  
}

chart_outcome_province(flu_china, "Shanghai")
```

``` r
chart_outcome_province(flu_china,"Zhejiang")
```

``` r
chart_outcome_province(flu_china,"Jiangsu")
```

### Produire itérativement des tableaux pour différents niveaux d’une variable

Ici, nous allons créer trois indicateurs à résumer dans un tableau et nous voudrions produire ce tableau pour chacune des provinces. Nos indicateurs sont le délai entre l’apparition et l’hospitalisation, le pourcentage de guérison et l’âge médian des cas.

``` r
indic_1 <- flu_china %>% 
  group_by(province) %>% 
  mutate(
    date_hosp= strptime(date_of_hospitalisation, format = "%m/%d/%Y"),
    date_ons= strptime(date_of_onset, format = "%m/%d/%Y"), 
    delay_onset_hosp= as.numeric(date_hosp - date_ons)/86400,
    mean_delay_onset_hosp = round(mean(delay_onset_hosp, na.rm=TRUE ), 0)) %>%
  select(province, mean_delay_onset_hosp)  %>% 
  distinct()
     

indic_2 <-  flu_china %>% 
            filter(!is.na(outcome)) %>% 
            group_by(province, outcome) %>% 
            count() %>%
            pivot_wider(names_from = outcome, values_from = n) %>% 
    adorn_totals(where = "col") %>% 
    mutate(
        perc_recovery= round((Recover/Total)*100,2))%>% 
  select(province, perc_recovery)
    
    
    
indic_3 <-  flu_china %>% 
            group_by(province) %>% 
            mutate(
                    median_age_cases = median(as.numeric(na_if(age, "?")), na.rm = TRUE)
            ) %>% 
  select(province, median_age_cases)  %>% 
  distinct()

#Joindre les trois ensembles de données d'indicateurs

table_indic_all <- indic_1 %>% 
  dplyr::left_join(indic_2, by = "province") %>% 
        left_join(indic_3, by = "province")


#Imprimez les indicateurs dans un tableau mobile


print_indic_prov <-  function(table_used, prov){
  
  #d'abord transformer un peu le dataframe pour faciliter l'impression.
  indic_prov <- table_used %>%
    filter(province==prov) %>%
    pivot_longer(names_to = "Indicateurs", cols = 2:4) %>% 
   mutate( indic_label = factor(Indicateurs,
   levels= c("mean_delay_onset_hosp","perc_recovery","median_age_cases"),
   labels=c("Mean delay onset-hosp","Percentage of recovery", "Median age of the cases"))
   ) %>% 
    ungroup(province) %>% 
    select(indic_label, value)
  

    tab_print <- flextable(indic_prov)  %>%
    theme_vanilla() %>% 
    flextable::fontsize(part = "body", size = 10) 
    
    
     tab_print <- tab_print %>% 
                  autofit()   %>%
                  set_header_labels( 
                indic_label= "Indicateurs", value= "Estimation") %>%
    flextable::bg( bg = "darkblue", part = "header") %>%
    flextable::bold(part = "header") %>%
    flextable::color(color = "white", part = "header") %>% 
    add_header_lines(values = paste0("Indicateurs pour la province de: ", prov)) %>% 
bold(part = "header")
 
 tab_print <- colformat_double(tab_print,
   digits = 2,
   na_str = "-")

tab_print 
    
}




print_indic_prov(table_indic_all, "Shanghai")
```

| Indicateurs pour la province de: Shanghai |            |
|-------------------------------------------|------------|
| Indicateurs                               | Estimation |
| Mean delay onset-hosp                     | 4.00       |
| Percentage of recovery                    | 46.67      |
| Median age of the cases                   | 67.00      |

``` r
print_indic_prov(table_indic_all, "Jiangsu")
```

| Indicateurs pour la province de: Jiangsu |            |
|------------------------------------------|------------|
| Indicateurs                              | Estimation |
| Mean delay onset-hosp                    | 6.00       |
| Percentage of recovery                   | 71.43      |
| Median age of the cases                  | 55.00      |

## 44.8 Conseils et meilleures pratiques pour des fonctions bien rodées

La programmation fonctionnelle a pour but d’alléger le code et d’en faciliter la lecture. Elle devrait produire le contraire. Les conseils ci-dessous vous aideront à avoir un code propre et facile à lire.

### Nommage et syntaxe

- Evitez d’utiliser des caractères qui auraient pu être facilement pris par d’autres fonctions déjà existantes dans votre environnement.

- Il est recommandé que le nom de la fonction soit court et facile à comprendre pour un autre lecteur.

- Il est préférable d’utiliser des verbes pour le nom de la fonction et des noms pour les noms des arguments.

### Noms de colonnes et évaluation ordonnée

Si vous voulez savoir comment référencer les *noms de colonnes* qui sont fournis à votre code en tant qu’arguments, lisez ce [guide de programmation tidyverse](https://dplyr.tidyverse.org/articles/programming.html). Parmi les sujets abordés figurent *l’évaluation tidée* et l’utilisation de l’accolade double `{ }`.

Par exemple, voici un squelette de code rapide tiré du tutoriel de la page mentionnée juste au-dessus :

``` r
var_summary <- function(data, var) {
  data %>%
    summarise(n = n(), min = min({{ var }}), max = max({{ var }}))
}
mtcars %>% 
  group_by(cyl) %>% 
  var_summary(mpg)
```

### Test et gestion des erreurs

Plus la tâche d’une fonction est compliquée, plus la possibilité d’erreurs est élevée. Il est donc parfois nécessaire d’ajouter une vérification dans la fonction pour aider à comprendre rapidement d’où vient l’erreur et trouver un moyen de la corriger.

- Il peut être plus que recommandé d’introduire une vérification de l’absence d’un argument en utilisant `missing(argument)`. Cette simple vérification peut retourner la valeur “TRUE” ou “FALSE”.

``` r
contain_covid19_missing <- function(barrier_gest, wear_mask, get_vaccine){
  
  if (missing(barrier_gest)) (print("please provide arg1"))
  if (missing(wear_mask)) print("please provide arg2")
  if (missing(get_vaccine)) print("please provide arg3")


  if (!barrier_gest == "yes" | wear_mask =="yes" | get_vaccine == "yes" ) 
       
       return ("you can do better")
  
  else("please make sure all are yes, this pandemic has to end!")
}


contain_covid19_missing(get_vaccine = "yes")
```

    [1] "please provide arg1"
    [1] "please provide arg2"

    Error in `contain_covid19_missing()`:
    ! argument "barrier_gest" is missing, with no default

- Utilisez `stop()` pour les erreurs plus faciles à détecter.

``` r
contain_covid19_stop <- function(barrier_gest, wear_mask, get_vaccine){
  
  if(!is.character(barrier_gest)) (stop("arg1 should be a character, please enter the value with `yes`, `no` or `sometimes"))
  
  if (barrier_gest == "yes" & wear_mask =="yes" & get_vaccine == "yes" ) 
       
       return ("success")
  
  else("please make sure all are yes, this pandemic has to end!")
}


contain_covid19_stop(barrier_gest=1, wear_mask="yes", get_vaccine = "no")
```

    Error in `contain_covid19_stop()`:
    ! arg1 should be a character, please enter the value with `yes`, `no` or `sometimes

- Comme nous le voyons lorsque nous exécutons la plupart des fonctions intégrées, des messages et des avertissements peuvent apparaître dans certaines conditions. Nous pouvons les intégrer dans nos fonctions écrites en utilisant les fonctions `message()` et `warning()`.

- Nous pouvons également gérer les erreurs en utilisant la fonction `safely()` qui prend une fonction en argument et l’exécute de manière sûre. En fait, la fonction s’exécutera sans s’arrêter si elle rencontre une erreur. `safely()` retourne en sortie une **liste** avec deux objets qui sont les résultats et l’erreur qu’elle a “sautée”.

Nous pouvons vérifier en exécutant d’abord la fonction `mean()`, puis en l’exécutant avec `safely()`.

``` r
linelist %>% 
  select(where(is.numeric)) %>% 
  map(mean)
```

    $generation
    [1] 16.56165

    $age
    [1] NA

    $age_years
    [1] NA

    $lon
    [1] -13.23381

    $lat
    [1] 8.469638

    $wt_kg
    [1] 52.64487

    $ht_cm
    [1] 124.9633

    $ct_blood
    [1] 21.20686

    $temp
    [1] NA

    $bmi
    [1] 46.89023

    $days_onset_hosp
    [1] NA

``` r
safe_mean <- safely(mean)
linelist %>% 
  select(where(is.numeric)) %>% 
  map(safe_mean)
```

    $generation
    $generation$result
    [1] 16.56165

    $generation$error
    NULL


    $age
    $age$result
    [1] NA

    $age$error
    NULL


    $age_years
    $age_years$result
    [1] NA

    $age_years$error
    NULL


    $lon
    $lon$result
    [1] -13.23381

    $lon$error
    NULL


    $lat
    $lat$result
    [1] 8.469638

    $lat$error
    NULL


    $wt_kg
    $wt_kg$result
    [1] 52.64487

    $wt_kg$error
    NULL


    $ht_cm
    $ht_cm$result
    [1] 124.9633

    $ht_cm$error
    NULL


    $ct_blood
    $ct_blood$result
    [1] 21.20686

    $ct_blood$error
    NULL


    $temp
    $temp$result
    [1] NA

    $temp$error
    NULL


    $bmi
    $bmi$result
    [1] 46.89023

    $bmi$error
    NULL


    $days_onset_hosp
    $days_onset_hosp$result
    [1] NA

    $days_onset_hosp$error
    NULL

Comme dit précédemment, bien commenter nos codes est déjà un bon moyen d’avoir de la documentation dans notre travail.

## 44.9 Ressources

[Lien vers R pour la science des données](https://r4ds.had.co.nz/functions.html)

[Cheatsheet advance R programming](https://www.rstudio.com/wp-content/uploads/2016/02/advancedR.pdf)

[Cheatsheet purr Package](https://purrr.tidyverse.org/)

[Video-ACM talk by Hadley Wickham : Les joies de la programmation fonctionnelle (comment fonctionne map_dbl)](https://youtube.videoken.com/embed/bzUmK0Y07ck)
