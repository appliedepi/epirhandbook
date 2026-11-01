# 21  Tasas estandarizadas

Esta página te mostrará cómo estandarizar un resultado, como las hospitalizaciones o la mortalidad, por características como la edad y el sexo.

Esta página utiliza el paquete **PHEindicatormethods**.

Comenzamos demostrando ampliamente los procesos de preparación/limpieza/unión de datos, ya que esto es común cuando se combinan datos de población de múltiples países, datos de población estándar, defunciones, etc.

## 21.1 Resumen

Hay dos formas principales de estandarizar: la estandarización directa y la indirecta. Supongamos que queremos estandarizar la tasa de mortalidad por edad y sexo para el país A y el país B, y comparar las tasas estandarizadas entre estos países.

- Para la estandarización directa, tendrás que conocer el número de la población de riesgo y el número de defunciones para cada estrato de edad y sexo, para el país A y el país B. Un estrato en nuestro ejemplo podría ser el de las mujeres entre 15-44 años.
- Para la estandarización indirecta, sólo es necesario conocer el número total de defunciones y la estructura por edad y sexo de cada país. Por tanto, esta opción es factible si no se dispone de tasas de mortalidad específicas por edad y sexo o de cifras de población. La estandarización indirecta es, además, preferible en caso de números pequeños por estrato, ya que las estimaciones en la estandarización directa estarían influenciadas por una variación sustancial del muestreo.

## 21.2 Preparación

Para mostrar cómo se realiza la estandarización, utilizaremos recuentos ficticios de la población y de las defunciones del país A y del país B, por edad (en categorías de 5 años) y por sexo (femenino, masculino). Para que los datos estén listos para su uso, realizaremos los siguientes pasos de preparación:

1.  Cargar paquetes
2.  Cargar datos
3.  Unir los datos de población y mortalidad de los dos países
4.  Pivotar largo para que haya una fila por estrato de edad y sexo
5.  Limpiar la población de referencia (población estándar mundial) y unirla a los datos del país

En tu caso, los datos pueden tener un formato diferente. Tal vez esos datos sean por provincia, ciudad u otra zona de captación. Puede que tengas una fila para cada defunció e información sobre la edad y el sexo de cada una (o de una proporción significativa) de estas defunciones. En este caso, consulta las páginas sobre [Agrupar de datos](grouping.llms.md), [Pivotar de datos](pivoting.llms.md) y [Tablas descriptivas](tables_descriptive.llms.md) para crear unos datos con recuentos de eventos y población por estrato de edad y sexo.

También necesitamos una población de referencia, la población estándar. Para los fines de este ejercicio utilizaremos la `world_standard_population_by_sex`. La población estándar mundial se basa en las poblaciones de 46 países y se elaboró en 1960. Hay muchas poblaciones “estándar”; por ejemplo, el sitio web [del NHS de Escocia](https://www.opendata.nhs.scot/dataset/standard-populations) ofrece bastante información sobre la población estándar europea, la población estándar mundial y la población estándar de Escocia.

### Cargar paquetes

Este trozo de código muestra la carga de los paquetes necesarios para los análisis. En este manual destacamos `p_load()` de **pacman**, que instala el paquete si es necesario *y* lo carga para su uso. También puedes cargar los paquetes instalados con `library()` de R **base**. Consulta la página sobre [fundamentos de R](basics.llms.md) para obtener más información sobre los paquetes de R.

``` r
pacman::p_load(
     rio,                 # import/export data
     here,                # localizar archivos
     stringr,             # limpieza de caracteres y cadenas
     PHEindicatormethods, # alternativa para la estandarización de tasas
     tidyverse,           # gestión y visualización de datos
     appliedepidata) # datos de ejemplo utilizados en este manual
```

### Cargar los datos de población

Consulta la página de [descargando el manual y los datos](download.llms.md) para obtener instrucciones sobre cómo descargar todos los datos de ejemplo del manual. Puedes cargar los datos de la página de estandarización directamente en R con las siguientes llamadas a `appliedepidata::get_data()`:

``` r
# importa los datos demográficos del país A directamente de Github
A_demo <- appliedepidata::get_data(name = "country_demographics")

# importa las defunciones del país A directamente de Github
A_deaths <- appliedepidata::get_data(name = "deaths_countryA")

# importa los datos demográficos del país B directamente de Github
B_demo <- appliedepidata::get_data(name = "country_demographics_2")

# importa las defunciones del país B directamente de Github
B_deaths <- appliedepidata::get_data(name = "deaths_countryB")

# importa la población estándar mundial directamente de Github
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

En primer lugar, cargamos los datos demográficos (recuentos de hombres y mujeres por categoría de edad de 5 años) de los dos países que vamos a comparar, “Country A” y “Country B”.

``` r
# País A
A_demo <- appliedepidata::get_data(name = "country_demographics")
```

``` r
# País B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")
```

### Cargar datos de defunciones

Convenientemente, también tenemos los recuentos de las defunciones durante el período de interés, por edad y sexo. Los recuentos de cada país están en un archivo separado, que se muestra a continuación.

Defunciones en Country A

Defunciones en Country B

### Poblaciones y defunciones limpias

Necesitamos unir y transformar estos datos de la siguiente manera:

- Combinar las poblaciones de los países en un solo conjunto de datos y hacer un pivote “largo” para que cada estrato de edad y sexo sea una fila
- Combinar los recuentos de defunciones por país en un solo conjunto de datos y hacer un pivote “largo” para que cada estrato de edad y sexo sea una fila
- Unir las defunciones a las poblaciones

En primer lugar, combinamos los datos de las poblaciones de los países, los pivotamos “largo” y realizamos una pequeña limpieza. Para más detalles, consulta la página sobre [pivotar datos](pivoting.llms.md).

``` r
pop_countries <- A_demo %>%  # comienza con el conjunto de datos del país A
     bind_rows(B_demo) %>%        # une las filas, porque las columnas tienen el mismo nombre
     pivot_longer(                       # pivota a lo largo
          cols = c(m, f),                   # columnas para combinar en una sola
          names_to = "Sex",                 # nombre de la nueva columna que contiene la categoría ("m" o "f") 
          values_to = "Population") %>%     # nombre de la nueva columna que contiene los valores numéricos pivotados
     mutate(Sex = recode(Sex,            # valores recodificados para mayor claridad
          "m" = "Male",
          "f" = "Female"))
```

Los datos de población combinados tienen ahora este aspecto (clica para ver los países A y B):

Y ahora realizamos operaciones similares en los dos conjuntos de datos de defunciones.

``` r
deaths_countries <- A_deaths %>%    # comienza con el conjunto de datos de defunciones del país A
     bind_rows(B_deaths) %>%        # une las filas con el conjunto de datos B, porque las cols tienen el mismo nombre
     pivot_longer(                  # pivota a lo largo
          cols = c(Male, Female),        # columna a transformar en una sola
          names_to = "Sex",              # nombre de la nueva columna que contiene la categoría ("m" o "f")  
          values_to = "Deaths") %>%      # nombre para la nueva columna que contiene los valores numéricos pivotados
     rename(age_cat5 = AgeCat)      # renombra para mayor claridad
```

Los datos de las defunciones tienen ahora este aspecto, y contienen datos de ambos países:

Ahora unimos los datos de defunciones y población basándonos en las columnas comunes `Country`, `age_cat5`, y `Sex`. Esto añade la columna `Deaths`.

``` r
country_data <- pop_countries %>% 
     left_join(deaths_countries, by = c("Country", "age_cat5", "Sex"))
```

Ahora podemos clasificar `Sex`, `age_cat5`, y `Country` como factores y establecer el orden de los niveles utilizando la función `fct_relevel()` del paquete **forcats**, como se describe en la página sobre [Factores](factors.llms.md). Ten en cuenta que la clasificación de los niveles de los factores no cambia visiblemente los datos, pero el comando `arrange()` los ordena por Country, age category, y sex.

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

***PRECAUCIÓN:*** Si tienes pocas defunciones por estrato, considera la posibilidad de utilizar categorías de 10 o 15 años, en lugar de categorías de 5 años para la edad.

### Carga de la población de referencia

Por último, para la estandarización directa, importamos la población de referencia (la “población estándar” mundial por sexo)

``` r
# Población de referencia
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

### Población de referencia limpia

Los valores de la categoría de edad en los dataframes `country_data` y `standard_pop_data` tendrán que estar alineados.

Actualmente, los valores de la columna age_cat5 del dataframe `standard_pop_data` contienen la palabra “years” y “plus”, mientras que los del dataframe `country_data` no. Tendremos que hacer coincidir los valores de la categoría de edad. Usamos `str_replace_all()` del paquete **stringr**, como se describe en la página sobre [Caracteres y cadenas](characters_strings.llms.md), para reemplazar estos patrones sin espacio `""`.

La función `calculate_dsr()` recibe la población estándar mediante su argumento `stdpop =`, así que la columna puede tener cualquier nombre. La renombramos como `"pop"` porque el código siguiente usa `stdpop = pop`.

``` r
# Elimina una cadena específica de los valores de columna
standard_pop_clean <- standard_pop_data %>%
     mutate(
          age_cat5 = str_replace_all(age_cat5, "years", ""),   # elimina "year"
          age_cat5 = str_replace_all(age_cat5, "plus", ""),    # elimina "plus"
          age_cat5 = str_replace_all(age_cat5, " ", "")) %>%   # elimina " " space
     
     rename(pop = WorldStandardPopulation)   # cambia el nombre de la columna por "pop", la columna que se pasa a stdpop = en calculate_dsr()
```

***PRECAUCIÓN:*** Si intentas utilizar `str_replace_all()` para eliminar un *símbolo* de suma, no funcionará porque es un símbolo especial. “Escapa” de los símbolos especiales poniendo dos barras invertidas delante, como en `str_replace_call(columna, "\\+", "")`.

### Crear un conjunto de datos con una población estándar

Por último, el paquete **PHEindicatormethods**, que se detalla [a continuación](#standard_phe), espera que las poblaciones estándar se unan a los recuentos de eventos y poblaciones del país. Por lo tanto, crearemos un conjunto de datos `all_data` con ese fin.

``` r
all_data <- left_join(country_data, standard_pop_clean, by=c("age_cat5", "Sex"))
```

Este conjunto de datos completo tiene el siguiente aspecto:

## 21.3 Paquete **PHEindicatormethods**

Calculamos las tasas estandarizadas con el paquete **PHEindicatormethods**. Este paquete permite calcular las tasas estandarizadas tanto directa como indirectamente. Mostraremos ambos métodos.

En esta sección se utilizará el dataframe `all_data` creado al final de la sección Preparación. Este dataframe incluye las poblaciones de los países, los eventos de defunciones y la población de referencia mundial estándar. Puedes verlo [aquí](#standard_all).

### Tasas estandarizadas directamente

A continuación, primero agrupamos los datos por país y luego los pasamos a la función `calculate_dsr()` para obtener directamente las tasas estandarizadas por país.

Cabe destacar que `calculate_dsr()` necesita la población de referencia (estándar) como una **columna dentro del dataframe específico del país**. Indica el nombre de esa columna en el argumento `stdpop =`. En nuestro ejemplo siguiente, esta columna es `pop`.

Consulta la ayuda de `?calculate_dsr` o los enlaces de la sección Referencias para obtener más información.

``` r
# Calcula las tasas estandarizadas por el método directo por país por edad y sexo
mortality_ds_rate_phe <- all_data %>%
     group_by(Country) %>%
     PHEindicatormethods::calculate_dsr(
          x = Deaths,                 # columna con el número observado de sucesos
          n = Population,             # columna con poblaciones no estándar para cada estrato
          stdpop = pop)               # poblaciones estándar para cada estrato

# Imprimir tabla
knitr::kable(mortality_ds_rate_phe)
```

| Country | total_count | total_pop | value | lowercl | uppercl | confidence | statistic | method |
|:---|---:|---:|---:|---:|---:|:---|:---|:---|
| A | 11344 | 86790567 | 23.56686 | 23.08107 | 24.05944 | 95% | dsr per 100000 | Dobson |
| B | 9955 | 52898281 | 19.32549 | 18.45516 | 20.20882 | 95% | dsr per 100000 | Dobson |

### Tasas estandarizadas indirectamente

Para la estandarización indirecta, se necesita una población de referencia con el número de defunciones y el número de población por estrato. En este ejemplo, calcularemos las tasas del país A *utilizando el país B como población de referencia*, ya que la población de referencia de `standard_pop_clean` no incluye el número de defunciones por estrato.

A continuación, creamos primero la población de referencia del país B. Luego, pasamos los datos de mortalidad y población del país A, los combinamos con la población de referencia y los pasamos a la función `calculate_ISRate()`, para obtener tasas estandarizadas indirectamente. Por supuesto, también se puede hacer a la inversa.

En nuestro ejemplo, la población de referencia se proporciona como un dataframe separado. En este caso, nos aseguraremos que los vectores `x =`, `n =`, `x_ref =` y `n_ref =` estén ordenados por los mismos valores de categoría de normalización (estrato) que los de nuestro dataframe específico del país, ya que los registros se emparejarán por posición.

Consulta la ayuda de `?phr_isr` o los enlaces de la sección Referencias para obtener más información.

``` r
# Crear población de referencia
refpopCountryB <- country_data %>% 
  filter(Country == "B") 

# Calcular las tasas del país A estandarizadas indirectamente por edad y sexo
mortality_is_rate_phe_A <- country_data %>%
     filter(Country == "A") %>%
     PHEindicatormethods::calculate_ISRate(
          x = Deaths,                 # columna con el número observado de sucesos
          n = Population,             # columna con población no estándar para cada estrato
          x_ref = refpopCountryB$Deaths,  # número de defunciones de referencia para cada estrato
          n_ref = refpopCountryB$Population)  # población de referencia para cada estrato

# Imprimir tabla
knitr::kable(mortality_is_rate_phe_A)
```

| observed | expected | ref_rate | value | lowercl | uppercl | confidence | statistic | method |
|---:|---:|---:|---:|---:|---:|:---|:---|:---|
| 11344 | 15847.42 | 18.81914 | 13.47123 | 13.22446 | 13.72145 | 95% | indirectly standardised rate per 100000 | Byars |

## 21.4 Recursos

Si deseas ver otro ejemplo en el que se utilizan **los métodos de PHEindicator**, visita [este sitio web](https://mran.microsoft.com/snapshot/2018-10-22/web/packages/PHEindicatormethods/vignettes/IntroductiontoPHEindicatormethods.html)

Ver el archivo pdf de referencia de [**PHEindicatormethods**](https://cran.r-project.org/web/packages/PHEindicatormethods/PHEindicatormethods.pdf)
