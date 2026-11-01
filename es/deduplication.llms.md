# 15  De-duplicación

[![](../../images/deduplication.png)](../../images/deduplication.png)

Esta página cubre las siguientes técnicas de De-duplicación:

1.  Identificación y eliminación de filas duplicadas
2.  “Recortar” filas para mantener sólo determinadas filas (por ejemplo, mínimas o máximas) de cada grupo de filas
3.  “Reunir” o combinar valores de varias filas en una sola fila

## 15.1 Preparación

### Cargar paquetes

Este trozo de código muestra la carga de los paquetes necesarios para el análisis. En este manual destacamos `p_load()` de **pacman**, que instala el paquete si es necesario *y* lo carga para su uso. También puedes cargar los paquetes instalados con `library()` de R **base** Consulta la página sobre [fundamentos de R](basics.llms.md) para obtener más información sobre los paquetes de R.

``` r
pacman::p_load(
  tidyverse,   # funciones de de-duplicación, agrupación y troceado
  janitor,     # función para revisar duplicados
  stringr)      # para búsquedas de cadenas, se puede utilizar en valores "móviles"
```

### Importar datos

Para la demostración, utilizaremos unos datos de ejemplo que se crea con el código R que aparece a continuación.

Los datos son registros de encuentros telefónicos COVID-19, incluyendo encuentros con contactos y con casos. Las columnas incluyen `recordID` (generado por ordenador), `personID`, `name`, `date` del encuentro, `time` del encuentro, `purpose` del encuentro (para entrevistar como caso o como contacto), y `symptoms_ever` (si la persona en ese encuentro declaró haber tenido síntomas *alguna vez*).

Este es el código para crear el set de datos `obs`:

``` r
obs <- data.frame(
  recordID  = c(1,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18),
  personID  = c(1,1,2,2,3,2,4,5,6,7,2,1,3,3,4,5,5,7,8),
  name      = c("adam", "adam", "amrish", "amrish", "mariah", "amrish", "nikhil", "brian", "smita", "raquel", "amrish",
                "adam", "mariah", "mariah", "nikhil", "brian", "brian", "raquel", "natalie"),
  date      = c("1/1/2020", "1/1/2020", "2/1/2020", "2/1/2020", "5/1/2020", "5/1/2020", "5/1/2020", "5/1/2020", "5/1/2020","5/1/2020", "2/1/2020",
                "5/1/2020", "6/1/2020", "6/1/2020", "6/1/2020", "6/1/2020", "7/1/2020", "7/1/2020", "7/1/2020"),
  time      = c("09:00", "09:00", "14:20", "14:20", "12:00", "16:10", "13:01", "15:20", "14:20", "12:30", "10:24",
                "09:40", "07:25", "08:32", "15:36", "15:31", "07:59", "11:13", "17:12"),
  encounter = c(1,1,1,1,1,3,1,1,1,1,2,
                2,2,3,2,2,3,2,1),
  purpose   = c("contact", "contact", "contact", "contact", "case", "case", "contact", "contact", "contact", "contact", "contact",
                "case", "contact", "contact", "contact", "contact", "case", "contact", "case"),
  symptoms_ever = c(NA, NA, "No", "No", "No", "Yes", "Yes", "No", "Yes", NA, "Yes",
                    "No", "No", "No", "Yes", "Yes", "No","No", "No")) %>% 
  mutate(date = as.Date(date, format = "%d/%m/%Y"))
```

#### Este es el dataframe

Utiliza los cuadros de filtro de la parte superior para revisar los encuentros de cada persona.

Hay que tener en cuenta algunas cosas al revisar los datos:

- Los dos primeros registros están 100% duplicados, incluido el `recordID` de registro duplicado (¡debe ser un fallo informático!)
- Las dos segundas filas están duplicadas, en todas las columnas *excepto en `recordID`*
- Varias personas tuvieron múltiples encuentros telefónicos, en diversas fechas y horas, y como contactos y/o casos
- En cada encuentro se preguntaba a la persona si había tenido **alguna vez** síntomas, y parte de esta información falta.

Y aquí hay un resumen rápido de las personas y los propósitos de sus encuentros, usando `tabyl()` de **janitor**:

``` r
obs %>% 
  tabyl(name, purpose)
```

        name case contact
        adam    1       2
      amrish    1       3
       brian    1       2
      mariah    1       2
     natalie    1       0
      nikhil    0       2
      raquel    0       2
       smita    0       1

## 15.2 De-duplicación

Esta sección describe cómo revisar y eliminar filas duplicadas en un dataframe. También muestra cómo manejar los elementos duplicados en un vector.

### Examinar las filas duplicadas

Para revisar rápidamente las filas que tienen duplicados, puedes utilizar `get_dupes()` del paquete **janitor**. Por *defecto*, se revisan todas las columnas cuando se evalúan los duplicados - las filas devueltas por la función están 100% duplicadas considerando los valores de *todas* las columnas.

En el dataframe `obs`, las dos primeras filas están *100% duplicadas* - tienen el mismo valor en cada columna (incluyendo la columna recordID, que se *supone* que es única - debe ser algún fallo informático). El dataframe devuelto incluye automáticamente una nueva columna `dupe_count` en el lado derecho, que muestra el número de filas con esa combinación de valores duplicados.

``` r
# 100% de duplicados en todas las columnas
obs %>% 
  janitor::get_dupes()
```

Ver los [datos originales](#dedup_data)

Sin embargo, si decidimos ignorar `recordID`, las filas 3 y 4 también están duplicadas entre sí. Es decir, tienen los mismos valores en todas las columnas *excepto* en recordID. Puedes especificar las columnas que se van a ignorar en la función mediante el símbolo `-` menos.

``` r
# Duplicados cuando no se tiene en cuenta la columna recordID
obs %>% 
  janitor::get_dupes(-recordID)        # si hay varias columnas, envolverlas en c()
```

También puedes especificar positivamente las columnas a considerar. A continuación, sólo se devuelven las filas que tienen los mismos valores en las columnas `name` y `purpose`. Observa cómo “amrish” tiene ahora `dupe_count` igual a 3 para reflejar sus tres encuentros de “contacto”.

\*Desplázate a la izquierda para ver más filas\*\*

``` r
# duplicados basados SOLO en las columnas name y purpose
obs %>% 
  janitor::get_dupes(name, purpose)
```

Ver los [datos originales](#dedup_data).

Para más detalles, consulta `?get_dupes` o esta [referencia en línea](https://cran.r-project.org/web/packages/janitor/vignettes/janitor.html#explore-records-with-duplicated-values-for-specific-combinations-of-variables-with-get_dupes)

### Mantener sólo filas únicas

Para mantener sólo las filas únicas de un dataframe, utiliza `distinct()` de **dplyr** (como se muestra en la página [Limpieza de datos y funciones básicas](cleaning.llms.md)). Las filas duplicadas se eliminan de forma que sólo se conserva la primera de dichas filas. Por defecto, “primero” significa el `rownumber` más alto (orden de filas de arriba a abajo). Sólo se mantienen las filas únicas.

En el ejemplo siguiente, ejecutamos `distinct()` de forma que la columna `recordID` se excluye de la consideración - así **se eliminan dos filas duplicadas**. La primera fila (para “adam”) estaba 100% duplicada y ha sido eliminada. También la fila 3 (para “amrish”) estaba duplicada en todas las columnas *excepto* en `recordID` (que no se tiene en cuenta), por lo que también se ha eliminado. El set de datos `obs` tiene ahora `nrow(obs)-2` filas, no `nrow(obs)`).

*Desplázate a la izquierda para ver el dataframe completo*

``` r
# añadido a una cadena de pipes (ej: limpieza de datos)
obs %>% 
  distinct(across(-recordID), # reduce el data frame a sólo filas únicas (mantiene la primera de cualquier duplicado)
           .keep_all = TRUE) 

# si fuera de pipes, incluir los datos como primer argumento 
# distinct(obs)
```

***PRECAUCIÓN:*** Si se utiliza `distinct()` en datos agrupados, la función se aplicará a cada grupo.

**De-duplicar en base a columnas específicas**

También puedes especificar las columnas que serán la base de la De-duplicación. De esta manera, la De-duplicación sólo se aplica a las filas que están duplicadas dentro de las columnas especificadas. A menos que establece `.keep_all = TRUE`, todas las columnas no mencionadas se eliminarán.

En el ejemplo siguiente, la De-duplicación sólo se aplica a las filas que tienen valores idénticos para las columnas `name` y `purpose`. Por lo tanto, “brian” sólo tiene 2 filas en lugar de 3: su *primer* encuentro como “contacto” y su único encuentro como “caso”. Para ajustar que se mantenga el *último encuentro de brian* de cada propósito, Mira el apartado Cortar dentro de los grupos.

*Desplázate a la izquierda para ver el dataframe completo*

``` r
# añadido a una cadena de pipes (ej: limpieza de datos)
obs %>% 
  distinct(name, purpose, .keep_all = TRUE) %>%  # mantiene filas únicas por nombre y propósito, conserva todas las columnas
  arrange(name)                                  # organiza para facilitar la visualización
```

Ver los [datos originales](#dedup_data).

### De-duplicar elementos en un vector

La función `duplicated()` de R **base** evaluará un vector (columna) y devolverá un vector lógico de la misma longitud (TRUE/FALSE). La primera vez que aparezca un valor, devolverá FALSE (no es un duplicado), y las siguientes veces que aparezca ese valor devolverá TRUE. Nótese que `NA` se trata igual que cualquier otro valor.

``` r
x <- c(1, 1, 2, NA, NA, 4, 5, 4, 4, 1, 2)
duplicated(x)
```

     [1] FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE

Para devolver sólo los elementos duplicados, se pueden utilizar corchetes para subconjuntar el vector original:

``` r
x[duplicated(x)]
```

    [1]  1 NA  4  4  1  2

Para devolver sólo los elementos únicos, utiliza `unique()` de R **base**. Para eliminar los `NA` de la salida, anida `na.omit()` dentro de `unique()`.

``` r
unique(x)           # alternativamente, usa x[!duplicated(x)]
```

    [1]  1  2 NA  4  5

``` r
unique(na.omit(x))  # elimina NAs 
```

    [1] 1 2 4 5

### Utilizando R **base**

**Para devolver las filas duplicadas**

En R **base**, también se puede ver qué filas están 100% duplicadas en un dataframe `df` con el comando `duplicated(df)` (devuelve un vector lógico de las filas).

Así, también puedes utilizar el subconjunto base `[ ]` en el dataframe para ver las filas *duplicadas* con `df[duplicated(df),]` (¡no olvides la coma, que significa que quieres ver todas las columnas!)

**Para devolver filas únicas**

Ver las notas anteriores. Para ver las filas *únicas* se añade el negador lógico `!` delante de la función duplicated(): `df[!duplicated(df),]`

**Para devolver las filas que son duplicados de sólo ciertas columnas**

Subconjunta el `df` que está *dentro de los paréntesis de `duplicated()`*, para que esta función opere sólo en ciertas columnas del df. Para especificar las columnas, proporciona los números o nombres de las columnas después de una coma (recuerda que todo esto está *dentro* de la función `duplicated()`).

¡Asegúrate también de mantener la coma `,` *fuera*, después de la función `duplicated()`!

Por ejemplo, para evaluar sólo las columnas 2 a 5 en busca de duplicados: `df[!duplicated(df[, 2:5]),]` Para evaluar sólo las columnas `name` y `purpose` en busca de duplicados: `df[!duplicated(df[, c("name", "purpose)]),]`

## 15.3 Recortar

Para “recortar” un dataframe con un filtro de filas por su número de fila/posición. Esto resulta especialmente útil si tiene varias filas por grupo funcional (por ejemplo, por “persona”) y sólo quieres conservar una o algunas de ellas.

La función básica `slice()` acepta números y devuelve filas en esas posiciones. Si los números proporcionados son positivos, sólo se devuelven éstos. Si son negativos, *no se devuelven esas filas*. Los números deben ser todos positivos o todos negativos.

``` r
obs %>% slice(4)  # devuelve la 4ª fila
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        3        2 amrish 2020-01-02 14:20         1 contact            No

``` r
obs %>% slice(c(2,4))  #  devuelve las filas 2 y 4
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        1        1   adam 2020-01-01 09:00         1 contact          <NA>
    2        3        2 amrish 2020-01-02 14:20         1 contact            No

``` r
#obs %>% slice(c(2:4))  # devuelve las filas 2 a 4
```

Ver los [datos originales](#dedup_data).

Existen diversas variantes: Se les debe proporcionar una columna y un número de filas a devolver (a `n =`).

- `slice_min()` y `slice_max()` mantienen sólo la(s) fila(s) con el valor(es) mínimo o máximo de la columna especificada. Esto también funciona para devolver el “min” y el “max” de los factores ordenados.
- `slice_head()` y `slice_tail()` - mantienen sólo la *primera* o la *última* fila.
- `slice_sample()` - mantener sólo una muestra aleatoria de las filas.

``` r
obs %>% slice_max(encounter, n = 1)  # devuelve las filas con el mayor número de encuentros
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        5        2 amrish 2020-01-05 16:10         3    case           Yes
    2       13        3 mariah 2020-01-06 08:32         3 contact            No
    3       16        5  brian 2020-01-07 07:59         3    case            No

Utiliza los argumentos `n =` o `prop =` para especificar el número o la proporción de filas que deben conservarse. Si no se utiliza la función en una cadena de tuberías, proporciona primero el argumento datos (por ejemplo, `slice(datos, n = 2)`). Para más información, consulta con `?slice`.

Otros argumentos:

`.order_by =` utilizado en `slice_min()` y `slice_max()` esta es una columna para ordenar por antes de recortarlas. `with_ties =` TRUE por defecto, lo que significa que se mantienen los empates. `.preserve =` FALSE por defecto. Si es TRUE, la estructura de agrupación se recalcula después del recorte. `weight_by =` Opcional, columna numérica para ponderar por (un número mayor tiene más probabilidades de ser muestreado). También `replace =` para saber si el muestreo se realiza con/sin reemplazo.

***CONSEJO:*** Al utilizar `slice_max()` y `slice_min()`, asegúrate de especificar/escribir el `n =` (por ejemplo, `n = 2`, no simplemente 2). De lo contrario, puedes obtener un error `Error:` …`is not empty.`.

***NOTA:*** Es posible que encuentres la función [`top_n()`](https://dplyr.tidyverse.org/reference/top_n.html), que ha sido sustituida por las funciones `slice`.

### Recortar con grupos

Las funciones `slice_*()` pueden ser muy útiles si se aplican a un dataframe agrupado porque la operación de recorte se realiza en cada grupo por separado. Utiliza la **función** `group_by()` junto con `slice()` para agrupar los datos y tomar un corte de cada grupo.

Esto es útil para la De-duplicación si tienes varias filas por persona pero sólo quieres mantener una de ellas. Primero se utiliza `group_by()` con columnas clave que son las mismas por persona, y luego se utiliza una función slice en una columna que será diferente entre las filas agrupadas.

En el ejemplo siguiente, para mantener sólo el *último* encuentro *por persona*, agrupamos las filas por nombre y luego utilizamos `slice_max()` con `n = 1` en la columna de `date`. Ten en cuenta que Para aplicar una función como \`slice_max() en las fechas, la columna de fecha debe ser de tipo Date.

Por defecto, los “empates” (por ejemplo, la misma fecha en este escenario) se mantienen, y todavía obtendríamos múltiples filas para algunas personas (por ejemplo, adam). Para evitar esto, establecemos `with_ties = FALSE`. Sólo obtendremos una fila por persona.

***PRECACUCIÓN:*** Si utilizas `arrange()`, especifica .`by_group = TRUE` para que los datos se ordenen dentro de cada grupo.

***PELIGRO:*** Si `with_ties = FALSE`, se mantiene la primera fila de un empate. Esto puede ser engañoso. Mira cómo para Mariah, ella tiene dos encuentros en su última fecha (6 de enero) y el primero (el más temprano) se mantuvo. Es probable que queramos mantener tu último encuentro en ese día. Mira cómo “romper” estos vínculos en el siguiente ejemplo.

``` r
obs %>% 
  group_by(name) %>%       # agrupar las filas por 'name'
  slice_max(date,          # mantener fila por grupo con valor máximo de fecha 
            n = 1,         # mantener sólo la fila más alta 
            with_ties = F) # si hay un empate (de fecha), tomar la primera fila
```

Arriba, por ejemplo, podemos ver que sólo se conservó la fila de Amrish del 5 de enero, y sólo se conservó la fila de Brian del 7 de enero. Ver los [datos originales](#dedup_data).

**Romper los “empates”**

Se pueden ejecutar múltiples sentencias de recorte para “romper empates”. En este caso, si una persona tiene varios encuentros en tu última *fecha*, se mantiene el encuentro con la última *hora* (se utiliza `lubridate::hm()` para convertir los caracteres de tiempo en tipo tiempo, ordenable). Observa ahora cómo, la única fila que se mantiene para “Mariah” el 6 de enero es el encuentro 3 de las 08:32, no el encuentro 2 de las 07:25.

``` r
# Ejemplo de múltiples sentencias de corte para "romper empates"
obs %>%
  group_by(name) %>%
  
  # PRIMERO - cortar por la fecha más reciente
  slice_max(date, n = 1, with_ties = TRUE) %>% 
  
  # SEGUNDO - si hay empate, seleccionar la fila con la hora más tardía; prohibidos los empates
  slice_max(lubridate::hm(time), n = 1, with_ties = FALSE)
```

*En el ejemplo anterior, también habría sido posible realizar un recorte por número de encuentro, pero mostramos el corte por fecha y hora a modo de ejemplo.*

***CONSEJO:*** Para utilizar `slice_max()` o `slice_min()` en una columna “carácter”, ¡mútala a un tipo de factor *ordenado*!

Ver los [datos originales](#dedup_data).

### Mantener todos pero marcados

Si deseas conservar todos los registros pero marcar sólo algunos para tu análisis, considera un enfoque de dos pasos utilizando un número de registro/encuentro único:

1.  Reduce/recorta el dataframe original a sólo las filas para el análisis. Guarda/conserva este dataframe reducido.
2.  En el dataframe original, marca las filas según corresponda con `case_when()`, basándose en si tu identificador único de registro (recordID en este ejemplo) está presente en el dataframe reducido.

``` r
# 1. Definir data frame de filas a mantener para el análisis
obs_keep <- obs %>%
  group_by(name) %>%
  slice_max(encounter, n = 1, with_ties = FALSE) # Conservar sólo el último encuentro por persona


# 2.  Marcar el data frame original
obs_marked <- obs %>%

   # crear nueva columna dup_record
  mutate(dup_record = case_when(
    
    # si el registro está en el data frame obs_keep
    recordID %in% obs_keep$recordID ~ "For analysis", 
    
    # todos los demás marcados como " Ignore " para fines de análisis
    TRUE                            ~ "Ignore"))

# imprimir
obs_marked
```

       recordID personID    name       date  time encounter purpose symptoms_ever
    1         1        1    adam 2020-01-01 09:00         1 contact          <NA>
    2         1        1    adam 2020-01-01 09:00         1 contact          <NA>
    3         2        2  amrish 2020-01-02 14:20         1 contact            No
    4         3        2  amrish 2020-01-02 14:20         1 contact            No
    5         4        3  mariah 2020-01-05 12:00         1    case            No
    6         5        2  amrish 2020-01-05 16:10         3    case           Yes
    7         6        4  nikhil 2020-01-05 13:01         1 contact           Yes
    8         7        5   brian 2020-01-05 15:20         1 contact            No
    9         8        6   smita 2020-01-05 14:20         1 contact           Yes
    10        9        7  raquel 2020-01-05 12:30         1 contact          <NA>
    11       10        2  amrish 2020-01-02 10:24         2 contact           Yes
    12       11        1    adam 2020-01-05 09:40         2    case            No
    13       12        3  mariah 2020-01-06 07:25         2 contact            No
    14       13        3  mariah 2020-01-06 08:32         3 contact            No
    15       14        4  nikhil 2020-01-06 15:36         2 contact           Yes
    16       15        5   brian 2020-01-06 15:31         2 contact           Yes
    17       16        5   brian 2020-01-07 07:59         3    case            No
    18       17        7  raquel 2020-01-07 11:13         2 contact            No
    19       18        8 natalie 2020-01-07 17:12         1    case            No
         dup_record
    1        Ignore
    2        Ignore
    3        Ignore
    4        Ignore
    5        Ignore
    6  For analysis
    7        Ignore
    8        Ignore
    9  For analysis
    10       Ignore
    11       Ignore
    12 For analysis
    13       Ignore
    14 For analysis
    15 For analysis
    16       Ignore
    17 For analysis
    18 For analysis
    19 For analysis

Ver los [datos originales](#dedup_data).

### Calcular la exhaustividad de las filas

Crea una columna que contenga una métrica para la exhaustividad/completitud de la fila (que no tenga valores faltantes). Esto podría ser útil a la hora de decidir qué filas se priorizan sobre otras al de-duplicar/repartir.

En este ejemplo, las columnas “clave” sobre las que se quiere medir la integridad se guardan en un vector de nombres de columnas.

A continuación se crea la nueva columna `key_completeness` con `mutate()`. El nuevo valor de cada fila se define como una fracción calculada: el número de valores no ausentes en esa fila entre las columnas clave, dividido por el número de columnas clave.

Esto implica la función `rowSums()` de R **base**. También se utiliza `.` , que dentro del piping se refiere al dataframe en ese punto (en este caso, se está subconjuntando con corchetes `[]`).

\*Desplázate a la derecha para ver más filas\*\*.

``` r
# crear una columna "key variable" de exhaustividad
# esta es una *proporción* de las columnas designadas como "key_cols" que tienen valores no ausentes

key_cols = c("personID", "name", "symptoms_ever")

obs %>% 
  mutate(key_completeness = rowSums(!is.na(.[,key_cols]))/length(key_cols)) 
```

Ver los [datos originales](#dedup_data).

## 15.4 Combinación de valores

Esta sección describe:

1.  Cómo “combinar” valores de varias filas en una sola fila, con algunas variaciones
2.  Una vez que se hayan “combinado” los valores, cómo sobrescribir/priorizar los valores en cada celda

Esta sección utiliza los datos de ejemplo de la sección Preparación.

### Combinar los valores en una fila

El código de ejemplo que se muestra a continuación utiliza `group_by()` y `summarise()` para agrupar las filas por persona, y luego pega todos los valores únicos dentro de las filas agrupadas. Así, se obtiene una fila de resumen por persona. Algunas notas:

- Se añade un sufijo a todas las nuevas columnas (“\_roll” en este ejemplo)
- Si quieres mostrar sólo los valores únicos por celda, entonces envuelve el `na.omit()` con `unique()`
- `na.omit()` elimina los valores `NA`, pero si no se desea se puede eliminar con `paste0(.x)`…

``` r
# valores "móviles" en una fila por grupo (por "personID") 
cases_rolled <- obs %>% 
  
  # crear grupos por nombre
  group_by(personID) %>% 
  
    # ordenar las filas dentro de cada grupo (por ejemplo, por fecha)
  arrange(date, .by_group = TRUE) %>% 
  
    # Para cada columna, pegar todos los valores dentro de las filas agrupadas, separados por ";"
  summarise(
    across(everything(),                           # aplicar a todas las columnas
           ~paste0(na.omit(.x), collapse = "; "))) # se define la función que combina los valores que no son valores NA
```

El resultado es una fila por grupo (`ID`), con entradas ordenadas por fecha y pegadas. *Desplázate a la izquierda para ver más filas*

Ver los [datos originales](#dedup_data).

**Esta variación sólo muestra valores únicos:**

``` r
# Variación - muestra sólo valores únicos
cases_rolled <- obs %>% 
  group_by(personID) %>% 
  arrange(date, .by_group = TRUE) %>% 
  summarise(
    across(everything(),                                   # aplicar a todas las columnas
           ~paste0(unique(na.omit(.x)), collapse = "; "))) # se define la función que combina los valores que no son valores NA
```

**Esta variación añade un sufijo a cada columna.** En este caso, “\_roll” para indicar que se ha combinado (roll):

``` r
# Variación - sufijo añadido a los nombres de columna 
cases_rolled <- obs %>% 
  group_by(personID) %>% 
  arrange(date, .by_group = TRUE) %>% 
  summarise(
    across(everything(),                
           list(roll = ~paste0(na.omit(.x), collapse = "; ")))) # _roll se añade a los nombres de columna
```

### Sobrescribir valores/jerarquía

Si luego quieres evaluar todos los valores combinados, y mantener sólo un valor específico (por ejemplo, el “mejor” o el “máximo” valor), puedes utilizar `mutate()` a través de las columnas deseadas, para implementar `case_when()`, que utiliza `str_detect()` del paquete **stringr** para buscar secuencialmente patrones de cadena y sobrescribir el contenido de la celda.

``` r
# LIMPIAR CASOS
###############
cases_clean <- cases_rolled %>% 
    
    # limpia las vars Yes-No-Unknown: sustituye el texto por el valor "más alto" presente en la cadena
    mutate(across(c(contains("symptoms_ever")),                     # opera en las columnas especificadas (Y/N/U)
             list(mod = ~case_when(                                 # añade el sufijo "_mod" a las nuevas cols; implementa case_when()
               
               str_detect(.x, "Yes")       ~ "Yes",                 # si se detecta " Yes ", entonces el valor de la celda se convierte en yes
               str_detect(.x, "No")        ~ "No",                  # entonces, si se detecta "No", el valor de la celda se convierte en no
               str_detect(.x, "Unknown")   ~ "Unknown",             # entonces, si se detecta " Unknown ", el valor de la celda se convierte en Unknown
               TRUE                        ~ as.character(.x)))),   # entonces, si cualquier otra cosa si mantiene tal cual
      .keep = "unused")                                             # las columnas antiguas se eliminan, dejando sólo las columnas _mod
```

Ahora puedes ver en la columna `symptoms_ever` que si la persona ALGUNA vez dijo “Yes” a los síntomas, entonces sólo se muestra “Yes”.

Ver los [datos originales](#dedup_data).

## 15.5 De-duplicación probabilística

A veces, puedes querer identificar duplicados “probables” basándote en la similitud (por ejemplo, la “distancia” de la cadena) en varias columnas como el nombre, la edad, el sexo, la fecha de nacimiento, etc. Puedes aplicar un algoritmo de coincidencia probabilística para identificar duplicados probables.

Consulta la página sobre la [unión de datos](joining_matching.llms.md) para obtener una explicación sobre este método. La sección sobre Coincidencia probabilística contiene un ejemplo de aplicación de estos algoritmos para comparar un dataframe *consigo mismo*, realizando así una De-duplicación probabilística.

## 15.6 Recursos

Gran parte de la información de esta página está adaptada de estos recursos y viñetas en línea:

[datanovia](https://www.datanovia.com/en/lessons/identify-and-remove-duplicate-data-in-r/)

[Referencia de dplyr tidyverse](https://dplyr.tidyverse.org/reference/slice.html)

[Viñeta janitor de CRAN](https://cran.r-project.org/web/packages/janitor/vignettes/janitor.html#explore-records-with-duplicated-values-for-specific-combinations-of-variables-with-get_dupes)
