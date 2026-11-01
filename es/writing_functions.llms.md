# 44  Escribir funciones

## 44.1 Preparación

### Cargar paquetes

Este trozo de código muestra la carga de los paquetes necesarios para los análisis. En este manual destacamos `p_load()` de **pacman**, que instala el paquete si es necesario *y* lo carga para su uso. También puedes cargar los paquetes instalados con `library()` de R **base.** Consulta la página [fundamentos de R](basics.llms.md) para obtener más información sobre los paquetes de R.

### Importar datos

Importamos los datos de casos de una epidemia de ébola simulada. Si deseas descargar los datos para seguirlos paso a paso, consulta las instrucciones en la página \[Descargar libro y datos\]. Los datos se importan mediante la función `import()` del paquete **rio**. Consulta la página sobre [importación y exportación](importing.llms.md) para conocer las distintas formas de importar datos.

También utilizaremos en la última parte de esta página algunos datos sobre la gripe H7N9 de 2013.

## 44.2 Funciones

Las funciones son útiles en la programación, ya que permiten hacer códigos más fáciles de entender, de alguna manera más cortos y menos propensos a errores (dado que no hay errores en la propia función).

Si has llegado hasta este manual, significa que te has encontrado con un sinfín de funciones ya que en R, cada operación es una llamada a una función `+, for, if, [, $, { …`. Por ejemplo, `x + y` es lo mismo que`'+'(x, y)`

R es uno de los lenguajes que más posibilidades ofrece para trabajar con funciones y da suficientes herramientas al usuario para escribirlas fácilmente. No debemos pensar en las funciones como algo fijo en la cima o al final de la cadena de programación, R ofrece la posibilidad de utilizarlas como si fueran vectores e incluso utilizarlas dentro de otras funciones, listas…

Existen muchos recursos muy avanzados sobre programación funcional y aquí sólo daremos una visión para ayudarte a empezar con la programación de funciones con breves ejemplos prácticos. Te animamos a visitar los enlaces de las referencias para leer más sobre el tema.

## 44.3 ¿Por qué utilizar una función?

Antes de responder a esta pregunta, es importante tener en cuenta que ya has tenido consejos para llegar a escribir tus primeras funciones R en la página sobre [Iteración, bucles y listas](iteration.llms.md) de este manual. De hecho, el uso de “if/else” y bucles suele ser una parte fundamental de muchas de nuestras funciones, ya que ayudan fácilmente a ampliar la aplicación de nuestro código permitiendo múltiples condiciones o a iterar códigos para repetir tareas.

- ¿Estoy repitiendo varias veces el mismo bloque de código para aplicarlo a una variable o dato diferente?

- Deshacerse de él, ¿acortará sustancialmente mi código general y hará que se ejecute más rápido?

- ¿Es posible que el código que he escrito se utilice de nuevo pero con un valor diferente en muchos lugares del código?

Si la respuesta a una de las preguntas anteriores es “SÍ”, es probable que tenga que escribir una función.

## 44.4 ¿Cómo construye R las funciones?

Las funciones en R tienen tres componentes principales:

- las `formals()` que es la lista de argumentos que controla cómo podemos llamar a la función

- el `body()` que es el código dentro de la función, es decir, dentro de los paréntesis o después del paréntesis, dependiendo de cómo lo escribamos

y,

- el `environment()` que ayudará a localizar las variables de la función y determina cómo encuentra la función el valor.

Una vez que hayas creado tu función, puedes verificar cada uno de estos componentes llamando a la función asociada.

## 44.5 Sintaxis y estructura básica

- Una función tendrá que ser nombrada adecuadamente para que su trabajo sea fácilmente comprensible tan pronto como leamos su nombre. En realidad, este es el caso de la mayoría de la arquitectura básica de R. Funciones como `mean()`, `print()`, `summary()` tienen nombres muy sencillos

- Una función necesitará argumentos, como los datos sobre los que trabajar y otros objetos que pueden ser valores estáticos entre otras opciones

- Y finalmente una función producirá una salida basada en su tarea principal y en los argumentos que se le han dado. Normalmente utilizaremos las funciones incorporadas como `print()`, `return()`… para producir la salida. La salida puede ser un valor lógico, un número, un carácter, un dataframe… en definitiva cualquier tipo de objeto de R.

Básicamente se trata de la composición de una función:

``` r
function_name <- function(argument_1, argument_2, argument_3){
  
           function_task
  
           return(output)
}
```

Podemos crear nuestra primera función que se llamará `contain_covid19()`.

``` r
contain_covid19 <- function(barrier_gest, wear_mask, get_vaccine){
  
                            if(barrier_gest == "yes" & wear_mask == "yes" & get_vaccine == "yes" ) 
       
                            return("success")
  
  else("please make sure all are yes, this pandemic has to end!")
}
```

A continuación, podemos verificar los componentes de nuestra función recién creada.

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

Ahora vamos a probar nuestra función. Para llamar a nuestra función escrita, la usas como usas todas las funciones de R, es decir, escribiendo el nombre de la función y añadiendo los argumentos necesarios.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "yes")
```

    [1] "success"

Podemos volver a escribir el nombre de cada argumento por precaución. Pero sin especificarlos, el código debería funcionar ya que R tiene en memoria la posición de cada argumento. Así que mientras pongas los valores de los argumentos en el orden correcto, puedes omitir escribir los nombres de los argumentos al llamar a las funciones.

``` r
contain_covid19("yes", "yes", "yes")
```

    [1] "success"

A continuación, veamos qué ocurre si uno de los valores es `"no"` o **no** `"yes"`.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "no")
```

    [1] "please make sure all are yes, this pandemic has to end!"

Si proporcionamos un argumento que no es reconocido, se producirá un error:

``` r
contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", get_vaccine = "no")
```

`Error in contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", : could not find function "contain_covid19"`

***NOTA:*** Algunas funciones (la mayoría de las veces muy cortas y sencillas) pueden no necesitar un nombre y pueden ser utilizadas directamente en una línea de código o dentro de otra función para realizar una tarea rápida. Se llaman **funciones anónimas**.

Por ejemplo, a continuación se muestra una primera función anónima que mantiene sólo las variables de carácter de los datos.

``` r
linelist %>% 
  dplyr::slice_head(n=10) %>%  # equivalente a la función de R base "head" que retorna las n primeras observaciones de un conjunto de datos.
  select(function(x) is.character(x)) 
```

A continuación, otra función que selecciona una de cada dos observaciones de nuestro conjunto de datos (puede ser relevante cuando tenemos datos longitudinales con muchos registros por paciente, por ejemplo, después de haber ordenado por fecha o visita). En este caso, la función adecuada que se escribe fuera de dplyr sería `function (x) (x%%2 == 0)` para aplicarla al vector que contiene todos los números de fila.

``` r
linelist %>%   
   slice_head(n=20) %>% 
   tibble::rownames_to_column() %>% # agrega índices de cada obs como rownames para ver claramente la selección final
   filter(row_number() %%2 == 0)
```

Un posible código en R base para la misma tarea sería:

``` r
linelist_firstobs <- head(linelist, 20)

linelist_firstobs[base::Filter(function(x) (x%%2 == 0), seq(nrow(linelist_firstobs))),]
```

***PRECAUCIÓN:*** Aunque es cierto que el uso de funciones puede ayudarnos con nuestro código, puede llevar mucho tiempo escribir algunas funciones o arreglar una si no ha sido pensada a fondo, escrita adecuadamente y está devolviendo errores como resultado. Por esta razón, a menudo se recomienda escribir primero el código en R, asegurarse de que hace lo que pretendemos, y luego transformarlo en una función con sus tres componentes principales, como se ha indicado anteriormente.

## 44.6 Ejemplos

### Devuelve tablas de proporciones para varias columnas

Sí, ya disponemos de bonitas funciones en muchos paquetes que permiten resumir la información de una manera muy fácil y agradable. Pero aún así intentaremos hacer las nuestras, en nuestros primeros pasos para acostumbrarnos a escribir funciones.

En este ejemplo queremos mostrar cómo la escritura de una función simple te evitaría copiar y pegar el mismo código varias veces.

``` r
proptab_multiple <- function(my_data, var_to_tab){
  
  # imprime el nombre de cada variable de interés antes de realizar la tabulación
  print(var_to_tab)

  with(my_data,
       rbind( # enlaza por filas los resultados de las siguientes dos funciones 
        #tabula la variable de interés: da solo números
          table(my_data[[var_to_tab]], useNA = "no"),
          #calcula la proporción de cada variable de interés y redondear el valor a 2 decimales
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

***CONSEJO:*** Como se ha indicado anteriormente, es muy importante comentar las funciones como se haría en la programación general. Ten en cuenta que el objetivo de una función es hacer un código fácil de leer, más corto y más eficiente. Entonces uno debería ser capaz de entender lo que hace la función con sólo leer su nombre y debería tener más detalles leyendo los comentarios.

Una segunda opción es utilizar esta función en otra a través de un bucle para hacer el proceso a la vez:

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

Una forma más sencilla podría ser utilizar la base R “apply” en lugar de un “bucle for” como se expresa a continuación:

***CONSEJO:*** R se define a menudo como un lenguaje de programación funcional y casi siempre que ejecutas una línea de código estás utilizando algunas funciones incorporadas. Un buen hábito para sentirse más cómodo con la escritura de funciones es echar a menudo un vistazo interno a cómo están construidas las funciones básicas que utiliza a diario. El atajo para hacerlo es seleccionar el nombre de la función y luego clicar en `Ctrl+F2` o `fn+F2` o `Cmd+F2` (dependiendo de tu ordenador).

## 44.7 Uso de **purrr**: escribir funciones que se pueden aplicar de forma iterativa

### Modificar el tipo de múltiples columnas en unos datos

Digamos que muchas variables de carácter en los datos originales de `linelist` necesitan ser cambiadas a “factor” para propósitos de análisis y trazado. En lugar de repetir el paso varias veces, podemos utilizar simplemente `lapply()` para realizar la transformación de todas las variables afectadas en una sola línea de código.

***PRECAUCIÓN:*** `lapply()` devuelve una lista, por lo que su uso puede requerir una modificación adicional como último paso.

El mismo paso puede realizarse utilizando la función `map_if()` del paquete **purrr**

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

### Elaborar de forma iterativa gráficos para diferentes niveles de una variable

Produciremos aquí un gráfico circular para ver la distribución del resultado de los pacientes en China durante el brote de H7N9 para cada provincia. En lugar de repetir el código para cada una de ellas, nos limitaremos a aplicar una función que crearemos.

``` r
# precisar opciones para el uso de highchart
options(highcharter.theme =   highcharter::hc_theme_smpl(tooltip = list(valueDecimals = 2)))


# Crear una función llamada "chart_outcome_province" que tome como argumento el conjunto de datos y el nombre de la provincia para la cual plotear la distribución del resultado.

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

### Producir iterativamente tablas para diferentes niveles de una variable

Aquí crearemos tres indicadores para resumirlos en una tabla y nos gustaría elaborar esta tabla para cada una de las provincias. Nuestros indicadores son el retraso entre el inicio y la hospitalización, el porcentaje de recuperación y la mediana de edad de los casos.

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

# unir los indicadores de los tres conjuntos de datos

table_indic_all <- indic_1 %>% 
  dplyr::left_join(indic_2, by = "province") %>% 
        left_join(indic_3, by = "province")


# imprimir los indicadores en una flextable


print_indic_prov <-  function(table_used, prov){
  
  # primero transforma un poco el dataframe para facilitar la impresión
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

## 44.8 Consejos y buens prácticas para el buen funcionamiento de las funciones

La programación funcional está pensada para aliviar el código y facilitar su lectura. Podría producir lo contrario. Los siguientes consejos le ayudarán a tener un código limpio y fácil de leer.

### Nombres y sintaxis

- Evitar el uso de caracteres que podrían haber sido fácilmente tomados por otras funciones ya existentes en su entorno

- Se recomienda que el nombre de la función sea corto y sencillo de entender para otro lector

- Es preferible utilizar verbos como nombre de la función y sustantivos para los nombres de los argumentos.

### Nombres de columnas y evaluación ordenada

Si quiere saber cómo referenciar *nombres de columnas* que se proporcionan a su código como argumentos, lea esta [guía de programación de tidyverse](https://dplyr.tidyverse.org/articles/programming.html). Entre los temas tratados están la *evaluación ordenada* y el uso del *abrazo* con `{ }` “llaves dobles”

Por ejemplo, aquí hay un esqueleto rápido de código de plantilla del tutorial de la página mencionada anteriormente:

``` r
var_summary <- function(data, var) {
  data %>%
    summarise(n = n(), min = min({{ var }}), max = max({{ var }}))
}
mtcars %>% 
  group_by(cyl) %>% 
  var_summary(mpg)
```

### Pruebas y tratamiento de errores

Cuanto más complicada sea la tarea de una función, mayor será la posibilidad de errores. Por lo tanto, a veces es necesario añadir alguna verificación dentro de la función para ayudar a entender rápidamente de dónde proviene el error y encontrar una manera de solucionarlo.

- Puede ser más que recomendable introducir una comprobación sobre la ausencia de un argumento utilizando `missing(argumento)`. Esta simple comprobación puede devolver el valor “TRUE” o “FALSE”.

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

- Utiliza `stop()` para errores más detectables.

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

- Como vemos cuando ejecutamos la mayoría de las funciones incorporadas, hay mensajes y advertencias que pueden aparecer en ciertas condiciones. Podemos integrarlos en nuestras funciones escritas utilizando las funciones `message()` y `warning()`.

- También podemos manejar los errores usando `safely()` que toma una función como argumento y la ejecuta de forma segura. De hecho, la función se ejecutará sin detenerse si encuentra un error. `safely()` devuelve como salida una **lista** con dos objetos que son los resultados y el error que se ha “saltado”.

Podemos verificarlo ejecutando primero la `mean()` como función, y luego ejecutarla con `safely()`.

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

Como se ha dicho anteriormente, comentar bien nuestros códigos ya es una buena forma de tener documentación en nuestro trabajo.

## 44.9 Recursos

[Funciones en R for Data Science en español](https://es.r4ds.hadley.nz/funciones.html)

[Cheatsheet advanzado de programación de R](https://www.rstudio.com/wp-content/uploads/2016/02/advancedR.pdf)

[Cheatsheet del paquete purr](https://purrr.tidyverse.org/)

[Vídeo-ACM charla de Hadley Wickham: La alegría de la programación funcional (cómo funciona map_dbl)](https://youtube.videoken.com/embed/bzUmK0Y07ck)
