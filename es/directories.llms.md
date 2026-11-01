# 45  Interacciones con directorios

En esta página cubrimos los escenarios comunes en los que se crea, se interactúa, se guarda y se importa con directorios (carpetas).

## 45.1 Preparación

### Paquete **fs**

El paquete **fs** es un paquete **tidyverse** que facilita las interacciones con los directorios, mejorando algunas de las funciones de R **base**. En las secciones siguientes utilizaremos a menudo funciones de **fs**.

``` r
pacman::p_load(
  fs,             # interacciones archivo/directorio
  rio,            # importación/exportación
  here,           # rutas relativas de archivos
  tidyverse)      # gestión y visualización de datos
```

### Imprimir el directorio como un árbol de dendrogramas

Utiliza la función `dir_tree()` de **fs**.

Proporciona la ruta de la carpeta a `path =`. Utiliza `recurse = FALSE` para mostrar un solo nivel, o `recurse = TRUE` para mostrar todos los archivos en todos los subniveles. A continuación utilizamos `here()` como abreviatura del proyecto R y especificamos su subcarpeta “data”, que contiene los datos de ejemplo de este manual. Lo configuramos para que muestre todos los archivos dentro de “data” y sus subcarpetas.

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

## 45.2 Listar los archivos de un directorio

Para listar sólo los nombres de los archivos de un directorio puedes utilizar `dir()` de R **base**. Por ejemplo, este comando lista los nombres de los archivos de la subcarpeta “linelists” de la carpeta “example” en un proyecto R. La ruta relativa de los archivos se proporciona utilizando `here()` (sobre la que puede leer más en la página de [importación y exportación](importing.llms.md)).

``` r
# nombres de archivo
dir(here("data", "example", "linelists"))
```

    [1] "20201007linelist.csv"          "case_linelist_2020-10-02.csv" 
    [3] "case_linelist_2020-10-03.csv"  "case_linelist_2020-10-04.csv" 
    [5] "case_linelist_2020-10-05.csv"  "case_linelist_2020-10-08.xlsx"
    [7] "case_linelist20201006.csv"    

Para listar las rutas completas de los archivos del directorio, puedes utilizar `dir_ls()` de **fs**. Una alternativa de R **base** es `list.files()`.

``` r
# rutas de archivos
dir_ls(here("data", "example", "linelists"))
```

    data/example/linelists/20201007linelist.csv
    data/example/linelists/case_linelist20201006.csv
    data/example/linelists/case_linelist_2020-10-02.csv
    data/example/linelists/case_linelist_2020-10-03.csv
    data/example/linelists/case_linelist_2020-10-04.csv
    data/example/linelists/case_linelist_2020-10-05.csv
    data/example/linelists/case_linelist_2020-10-08.xlsx

Para obtener toda la información de los metadatos de cada archivo en un directorio, (por ejemplo, la ruta, la fecha de modificación, etc.) puedes utilizar `dir_info()` de **fs**.

Esto puede ser especialmente útil si quieres extraer la última hora de modificación del archivo, por ejemplo si quieres importar la versión más reciente de un archivo. Para ver un ejemplo de esto, consulta la página de [importación y exportación](importing.llms.md).

``` r
# información de archivo
dir_info(here("data", "example", "linelists"))
```

Aquí está el dataframe devuelto. Desplázate a la derecha para ver todas las columnas.

## 45.3 Información sobre el archivo

Para extraer información de metadatos sobre un archivo específico, puedes utilizar `file_info()` de **fs** (o `file.info()` de R **base**).

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))
```

Aquí usamos `$` para indexar el resultado y devolver sólo el valor de `modification_time`.

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))$modification_time
```

    [1] "2026-11-01 15:52:15 UTC"

## 45.4 Comprobar si existe

### Objetos R

Puedes utilizar `exists()` de R **base** para comprobar si un objeto R existe *dentro* de R (escribe el nombre del objeto entre comillas).

``` r
exists("linelist")
```

    [1] FALSE

Ten en cuenta que algunos paquetes de R **base** utilizan nombres de objetos genéricos como “data” entre bastidores, que aparecerán como TRUE a menos que se especifique `inherit = FALSE`. Esta es una razón para no nombrar tu conjunto de datos como “data”.

``` r
exists("data")
```

    [1] TRUE

``` r
exists("data", inherit = FALSE)
```

    [1] FALSE

Si estás escribiendo una función, deberías utilizar `missing()` de R **base** para comprobar si un argumento está presente o no, en lugar de `exists()`.

### Directorios

Para comprobar si un directorio existe, escribe la ruta del archivo (y el nombre del archivo) a `is_dir()` de **fs**. Desplázate a la derecha para ver que se imprime `TRUE`.

``` r
is_dir(here("data"))
```

    data 
    TRUE 

Una alternativa de R **base** es `file.exists()`.

### Files

Para comprobar si un archivo específico existe, utiliza `is_file()` de **fs**. Desplázate a la derecha para ver que se imprime `TRUE`.

``` r
is_file(here("data", "case_linelists", "linelist_cleaned.rds"))
```

    data/case_linelists/linelist_cleaned.rds 
                                        TRUE 

Una alternativa de R **base** es `file.exists()`.

## 45.5 Crear

### Directorios

Para crear un nuevo directorio (carpeta) puede utilizar `dir_create()` de **fs**. Si el directorio ya existe, no se sobrescribirá y no se devolverá ningún error.

``` r
dir_create(here("data", "test"))
```

Una alternativa es `dir.create()` de R **base**, que mostrará un error si el directorio ya existe. En cambio, `dir_create()` en este escenario será silencioso.

### Archivos

Puedes crear un archivo (vacío) con `file_create()` de **fs**. Si el archivo ya existe, no se sobreescribirá ni se modificará.

``` r
file_create(here("data", "test.rds"))
```

Una alternativa de R **base** es `file.create()`. Pero si el archivo ya existe, esta opción lo truncará. Si se utiliza `file_create()` el archivo se dejará sin cambios

### Crear si no existe

EN CONSTRUCCIÓN

## 45.6 Borrar

### Objetos R

Utiliza `rm()` de R **base** para eliminar un objeto R.

### Directorios

Utiliza `dir_delete()` de **fs**.

### Archivos

Puedes eliminar archivos con `file_delete()` de **fs**.

## 45.7 Ejecución de otros archivos

### `source()`

Para ejecutar un script de R desde otro script de R, puedes utilizar el comando `source()` (de R **base**).

``` r
source(here("scripts", "cleaning_scripts", "clean_testing_data.R"))
```

Esto equivale a ver el script de R anterior y clicar en el botón “Source” en la parte superior derecha del script. Esto ejecutará el script pero lo hará de forma silenciosa (sin salida a la consola de R) a menos que se pretenda específicamente. Consulta la página sobre \[Consola interactiva\] para ver ejemplos de uso de `source()` para interactuar con un usuario a través de la consola de R en modo de pregunta y respuesta.

[![](../../images/source_button.png)](../../images/source_button.png)

### `render()`

`render()` es una variación de `source()` que se utiliza más a menudo para los scripts de R markdown. Tu pescribes `input =` que es el archivo R markdown, y también `output_format =` (normalmente “html_document”, “pdf_document”, “word_document”, ““)

Mira la página sobre [Informes con R Markdown](rmarkdown.llms.md) para más detalles. También consulta la documentación de `render()` [aquí](https://rmarkdown.rstudio.com/docs/reference/render.html) o escribiendo `?render`.

### Ejecutar archivos en un directorio

Puedes crear un bucle *for* y utilizarlo para `source()` cada archivo en un directorio, identificado con `dir()`.

``` r
for(script in dir(here("scripts"), pattern = ".R$")) {   # para cada nombre de script en la carpeta "scripts" del proyecto R (con extensión .R)
  source(here("scripts", script))                        # obtiene el archivo con el nombre correspondiente que existe en la carpeta scripts
}
```

Si sólo quieres ejecutar determinados scripts, puedes identificarlos por su nombre de la siguiente manera:

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

Aquí puedes ver una [comparación](https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html) de las funciones **fs** y R **base**.

### Importar archivos en un directorio

Consulta la página sobre [importación y exportación](importing.llms.md) para importar y exportar archivos individuales.

Consulta también la página de [importación y exportación](importing.llms.md) para conocer los métodos para importar automáticamente el archivo más reciente, basándose en una fecha del nombre del archivo *o* mirando los metadatos del mismo.

Consulta la página sobre [Iteración, bucles y listas](iteration.llms.md) para ver un ejemplo con el paquete **purrr** demostrando:

- Dividir un dataframe y guardarlo como múltiples archivos CSV
- Dividir un dataframe y guardar cada parte como una hoja separada dentro de un libro de Excel
- Importar varios archivos CSV y combinarlos en un dataframe
- Importar un libro de Excel con varias hojas y combinarlas en un dataframe

## 45.8 R **base**

Mira a continuación las funciones `list.files()` y `dir()`, que realizan la misma operación de listar archivos dentro de un directorio especificado. Puedes especificar `ignore.case =` o un patrón específico para buscar.

``` r
list.files(path = here("data"))

list.files(path = here("data", "example"), pattern = "\\.csv$")
# dir(path = here("data", "example"), pattern = "\\.csv$")

list.files(path = here("data", "example"), pattern = "hospital", ignore.case = TRUE)
```

Si un archivo está actualmente “abierto”, se mostrará en su carpeta con una tilde delante, como “~\$hospital_linelists.xlsx”.

## 45.9 Recursos

https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html
