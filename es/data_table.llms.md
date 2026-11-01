# 50  Data Table

El manual se centra en las funciones “verbales” de **dplyr** y en el operador pipe `%>%` de **magrittr** como método para limpiar y agrupar datos, pero el paquete **data.table** ofrece un método alternativo que puedes encontrar en tu recorrido con R.

## 50.1 Introducción a data.table

Una tabla de datos es una estructura de datos bidimensional como un dataframe que permite realizar operaciones de agrupación complejas. La sintaxis de data.table está estructurada de forma que se puedan realizar operaciones sobre filas, columnas y grupos.

La estructura es **DT\[i, j, by\]**, separada por 3 partes; los argumentos **i**, **j** y **by**. El argumento **i** permite subconjuntar las filas necesarias, el argumento **j** permite operar sobre las columnas y el argumento **by** permite operar sobre las columnas por grupos.

En esta página se tratarán los siguientes temas:

- Importación de datos y uso de `fread()` y `fwrite()`
- Selección y filtrado de filas mediante el argumento **i**
- Uso de las funciones de ayuda `%like%`, `%chin%`, `%between%`
- Selección y cálculo de columnas con el argumento **j**
- Cálculo por grupos utilizando el argumento **by**
- Añadir y actualizar datos a las tablas de datos utilizando `:=`

## 50.2 Cargar paquetes e importar datos

### Cargar paquetes

Utilizando la función `p_load()` de **pacman**, cargamos (e instalamos si es necesario) los paquetes necesarios para este análisis.

``` r
pacman::p_load(
  data.table, # para agrupar y limpiar datos
  tidyverse   # permite el uso de la función pipe (%>%) en este capítulo
  ) 
```

### Importar datos

Esta página explorará algunas de las funciones principales de **data.table** utilizando la lista de casos referenciados a lo largo del manual.

Importamos los datos de casos de una epidemia de ébola simulada. Cárguelo directamente con `appliedepidata::get_data(name = "linelist_cleaned_excel")` (véase la página [Descargando el manual y los datos](download.llms.md) para más detalles). A partir de aquí utilizamos `data.table()` para convertir el dataframe en una data.table.

``` r
linelist <- appliedepidata::get_data(name = "linelist_cleaned_excel") %>% data.table()
```

La función `fread()` se utiliza para importar directamente archivos delimitados regulares, como los archivos .csv, directamente a un formato de tabla de datos. Esta función, y su homóloga, `fwrite()`, utilizada para escribir tablas de datos como archivos delimitados regulares, son opciones muy rápidas y eficientes desde el punto de vista computacional para bases de datos de gran tamaño.

Las primeras 20 filas de `linelist`:

Los comandos de R **base**, como `dim()`, que se utilizan para los dataframes, también pueden utilizarse para las tablas de datos

``` r
dim(linelist) #gives the number of rows and columns in the data table
```

    [1] 5888   30

## 50.3 El argumento i: seleccionar y filtrar filas

Recordando la estructura \*\*DT\*\[i, j, by\]**, podemos filtrar filas utilizando números de fila o expresiones lógicas. El argumento i es el primero; por tanto, se puede utilizar la sintaxis** DT\[i\] **o** DT\[i,\]\*\*.

El primer ejemplo muestra las 5 primeras filas de la tabla de datos, el segundo ejemplo los casos de 18 años o más, y el tercer ejemplo los casos de 18 años o más pero no diagnosticados en el Central Hospital:

``` r
linelist[1:5] # devuelve de la 1ª a la 5ª fila
linelist[age >= 18] # subconjunto de casos iguales o mayores de 18 años
linelist[age >= 18 & hospital != "Central Hospital"] # subconjunto de casos iguales o mayores de 18 años pero no diagnosticados en el Hospital Central
```

El uso de .N en el argumento i representa el número total de filas en la tabla de datos. Esto se puede utilizar para subconjuntar los números de las filas:

``` r
linelist[.N] # devuelve la última fila
linelist[15:.N] # devuelve de la 15ª a la última fila
```

### Uso de funciones de ayuda para el filtrado

Data table utiliza funciones de ayuda que facilitan el subconjunto de filas. La función %like% se utiliza para coincidir con un patrón en una columna, `%chin%` se utiliza para coincidir con un carácter específico, y la función de ayuda `%between%` se utiliza para coincidir con columnas numéricas dentro de un rango preestablecido.

En los siguientes ejemplos: \* filtramos las filas en las que la variable hospital contiene “Hospital” \* filtramos las filas en las que el resultado es “Recover” o “Death” \* filtramos las filas en el rango de edad 40-60

``` r
linelist[hospital %like% "Hospital"] # filtrar filas donde la variable hospital contiene "Hospital"
linelist[outcome %chin% c("Recover", "Death")] # filtra las filas en las que el resultado es "Recuperación" o " Fallecimiento"
linelist[age %between% c(40, 60)] # filtra las filas en el rango de edad 40-60

# %between% debe tomar un vector de longitud 2, mientras que %chin% puede tomar vectores de longitud >= 1
```

## 50.4 El argumento j: seleccionar y calcular en columnas

Utilizando la estructura DT**\[i, j, by\]**, podemos seleccionar columnas utilizando números o nombres. El argumento **j** es el segundo; por lo tanto, se utiliza la sintaxis **DT\[, j\]**. Para facilitar los cálculos sobre el argumento **j**, la columna se envuelve utilizando `list()` o `.()`.

### Selección de columnas

El primer ejemplo recupera la primera, tercera y quinta columnas de la tabla de datos, el segundo ejemplo selecciona todas las columnas excepto las de altura, peso y sexo. El tercer ejemplo utiliza la envoltura `.()` para seleccionar las columnas **case_id** y **outcome**.

``` r
linelist[ , c(1,3,5)]
linelist[ , -c("gender", "age", "wt_kg", "ht_cm")]
linelist[ , list(case_id, outcome)] #linelist[ , .(case_id, outcome)] works just as well
```

### Cálculo en columnas

Combinando los argumentos **i** y **j** es posible filtrar filas y calcular en sus columnas. El uso de **.N** en el argumento **j** también representa el número total de filas en la tabla de datos y puede ser útil para devolver el número de filas después del filtrado de filas.

En los siguientes ejemplos: \* Contar el número de casos que permanecieron más de 7 días en el hospital \* Calcular la edad media de los casos que murieron en el hospital militar \* Calcular la desviación estándar, la mediana, la edad media de los casos que se recuperaron en el central hospital

``` r
linelist[days_onset_hosp > 7 , .N]
```

    [1] 189

``` r
linelist[hospital %like% "Military" & outcome %chin% "Death", .(mean(age, na.rm = T))] # na.rm = T elimina valores N/A
```

            V1
         <num>
    1: 15.9084

``` r
linelist[hospital == "Central Hospital" & outcome == "Recover", 
                 .(mean_age = mean(age, na.rm = T),
                   median_age = median(age, na.rm = T),
                   sd_age = sd(age, na.rm = T))] # esta sintaxis no utiliza las funciones de ayuda, pero funciona igual de bien
```

       mean_age median_age   sd_age
          <num>      <num>    <num>
    1: 16.85185         14 12.93857

Recuerda que el uso de `.()` en el argumento j facilita el cálculo, devuelve una tabla de datos y permite nombrar las columnas.

## 50.5 El argumento by: cálculo por grupos

El argumento **by** es el tercer argumento de la estructura **DT\[i, j, by\]**. El argumento **by** acepta tanto un vector de caracteres como la sintaxis `list()` o `.()`. El uso de la sintaxis `.()` en el argumento **by** permite renombrar las columnas sobre la marcha.

En los siguientes ejemplos: \* agrupamos el número de casos por hospital \* en los casos de 18 años o más, calculamos la media de altura y peso de los casos según el sexo y si se recuperaron o murieron \* en los ingresos que duraron más de 7 días, contamos el número de casos según el mes en que ingresaron y el hospital en el que lo hicieron

``` r
linelist[, .N, .(hospital)] # número de casos por hospital
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
                             mean_ht = mean(ht_cm, na.rm = T)), .(gender, outcome)] # NAs representan las categorías en las que faltan datos
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

Data.table también permite encadenar expresiones de la siguiente manera:

``` r
linelist[, .N, .(hospital)][order(-N)][1:3] # El 1º selecciona todos los casos por hospital, el 2º ordena los casos en orden descendente, el 3º incluye los 3 hospitales con mayor número de casos.
```

                hospital     N
                  <char> <int>
    1:     Port Hospital  1762
    2:           Missing  1469
    3: Military Hospital   896

En estos ejemplos estamos siguiendo la suposición de que una fila en la tabla de datos es igual a un nuevo caso, y por lo tanto podemos utilizar el **.N** para representar el número de filas en la tabla de datos. Otra función útil para representar el número de casos únicos es `uniqueN()`, que devuelve el número de valores únicos en una entrada dada. Esto se ilustra aquí:

``` r
linelist[, .(uniqueN(gender))] # recuerda que .() en el argumento j devuelve una tabla de datos
```

          V1
       <int>
    1:     3

La respuesta es 3, ya que los valores únicos de la columna de género son m, f y N/A. Compárelo con la función R base `unique()`, que devuelve todos los valores únicos en una entrada dada:

``` r
linelist[, .(unique(gender))]
```

           V1
       <char>
    1:      m
    2:      f
    3:   <NA>

Para hallar el número de casos únicos en un mes determinado escribiríamos lo siguiente:

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

## 50.6 Añadir y actualizar a las tablas de datos

El operador `:=` se utiliza para añadir o actualizar datos en una tabla de datos. La adición de columnas a la tabla de datos puede hacerse de las siguientes maneras:

``` r
linelist[, adult := age >= 18] # añade una columna
linelist[, c("child", "wt_lbs") := .(age < 18, wt_kg*2.204)] # para añadir múltiples columnas se requiere c("") y la sintaxis list() o .()
linelist[, `:=` (bmi_in_range = (bmi > 16 & bmi < 40),
                         no_infector_source_data = is.na(infector) | is.na(source))] # este método utiliza := como operador
linelist[, adult := NULL] # elimina la columna
```

Las agregaciones más complejas están fuera del alcance de este capítulo introductorio, pero la idea es proporcionar una alternativa popular y viable a **dplyr** para agrupar y limpiar datos. El paquete **data.table** es un gran paquete que permite un código ordenado y legible.

## 50.7 Recursos

A continuación, algunos recursos útiles para obtener más información:

- https://cran.r-project.org/web/packages/data.table/vignettes/datatable-intro.html

- https://github.com/Rdatatable/data.table

- https://s3.amazonaws.com/assets.datacamp.com/img/blog/data+table+cheat+sheet.pdf

- https://www.machinelearningplus.com/data-manipulation/datatable-in-r-complete-guide/

- https://www.datacamp.com/community/tutorials/data-table-r-tutorial

Puedes realizar cualquier función de resumen sobre datos agrupados; consulta la hoja de trucos [aquí](https://s3.amazonaws.com/assets.datacamp.com/blog_assets/datatable_Cheat_Sheet_R.pdf) para obtener más información:
