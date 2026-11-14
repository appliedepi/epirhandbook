# 1  Notas editoriales y técnicas

En esta página describimos la filosofía, el estilo y las decisiones editoriales elegidas para la elaboración de este manual.

## 1.1 R para epidemiología aplicada y salud pública

**Objetivo:** Servir como breve guía de referencia para escribir código en R (en línea y [versión sin conexión](download.llms.md)) con ejemplos detallados que aborden problemas epidemiológicos.

### Cómo utilizar este manual

- Navegue por las páginas del índice o utilice el cuadro de búsqueda
- Clique en los iconos “Copy” para copiar el código  
- Puede seguir paso a paso las lecciones utilizando nuestros [datos de ejemplo](download.llms.md)

**Versión sin conexión**

Consulte las instrucciones en la página de [Descargar el Manual y los datos](download.llms.md).

## 1.2 Enfoque y estilo

El público potencial de este libro es amplio. Seguramente será utilizado tanto por personas muy noveles con R, como por usuarios experimentados buscando los mejores consejos y prácticas. Por lo tanto, este debe ser accesible y conciso a la vez. Por ello, nuestro enfoque fue proporcionar *la información suficiente* para que alguien muy nuevo en R pueda aplicar y seguir el código.

Otros puntos:

- Se trata de un libro de referencia de códigos acompañado de ejemplos relativamente breves, *no* de un libro de texto completo sobre R o ciencia de datos
- Este es un *manual de R* para su uso dentro de la epidemiología aplicada - no un manual sobre los métodos o ciencia de la epidemiología aplicada
- Se trata de un documento vivo: los paquetes de R óptimos para una tarea determinada cambian a menudo, por lo que agradecemos que exista debate sobre cuáles destacar en este manual

### Paquetes de R

**Muchas opciones**

Uno de los aspectos más difíciles de aprender en R es saber qué paquete utilizar para una tarea determinada. Es muy común pelearse con una tarea para luego darse cuenta de que ¡hay un paquete de R que hace todo eso en una línea de código!.

En este manual, tratamos de ofrecerle al menos dos maneras de completar cada tarea: un método probado y comprobado (probablemente en R **base** o **tidyverse**) y un paquete especial de R que está hecho a medida para ese propósito. Queremos que tenga un par de opciones en caso de que no pueda descargar un paquete determinado o de que éste no le funcione.

A la hora de elegir los paquetes a utilizar, hemos dado prioridad a los paquetes y enfoques de R que han sido probados y aprobados por la comunidad, que minimizan el número de paquetes utilizados en una sesión de trabajo típica, que son estables (no cambian con frecuencia) y que realizan la tarea de forma sencilla y limpia.

En general, este manual da prioridad a los paquetes y funciones de R de **tidyverse**. Tidyverse es una colección de paquetes de R diseñados para ciencia de datos que comparten la gramática y estructuras de datos subyacentes. Todos los paquetes tidyverse pueden instalarse o cargarse a través del paquete **tidyverse**. Más información en el [sitio web de tidyverse](https://www.tidyverse.org/).

Cuando es aplicable, también ofrecemos opciones de código usando R **base** - los paquetes y funciones que vienen con R en la instalación. Esto se debe a que somos conscientes de que parte de la audiencia de este libro podría no tener una buena conexión a internet para descargar paquetes adicionales.

**Vinculación explícita de las funciones a los paquetes**

Es frustrante cuando en algunos tutoriales de R, se muestra una función (en código), pero no se sabe bien de qué paquete es. En este libro intentamos evitar esta situación.

En el texto explicativo, los nombres de los paquetes se escriben en negrita (por ejemplo, **dplyr**) y las funciones se escriben así: `mutate()`. Nos esforzaremos en dejar claro el paquete del que proviene una función, ya sea haciendo referencia al paquete en el texto o especificando el paquete en el código mediante esta sintaxis: `dplyr::mutate()`. Puede parecer redundante, pero lo hacemos a propósito.

Consulte la página sobre [fundamentos de R](basics.llms.md) para saber más sobre los paquetes y las funciones.

### Código de estilo

En el manual, utilizamos con frecuencia “líneas nuevas”, haciendo que nuestro código parezca “largo”. Lo hacemos por varias razones:

- De esta forma se pueden escribir comentarios explicativos con `#`, los cuales están situados adyacentes a cada línea de código
- En general, el código más largo (en vertical) es más fácil de leer
- Es más fácil de leer en una pantalla estrecha (no es necesario desplazarse lateralmente)
- Con las sangrías, puede ser más fácil saber qué argumentos pertenecen a cada función

Como resultado, el código que *podría* estar escrito:

``` r
linelist %>% 
  group_by(hospital) %>%  # filas agrupadas por hospital
  slice_max(date, n = 1, with_ties = F) # si hay un empate (de fecha), tomar la primera fila
```

…pero se escribe así:

``` r
linelist %>% 
  group_by(hospital) %>% # filas agrupadas por hospital
  slice_max(
    date,                # mantener la fila por grupo con el valor máximo de la fecha 
    n = 1,               # mantener sólo la fila más alta
    with_ties = F)       # si hay un empate (de fecha), tomar la primera fila
```

El código de R generalmente no se ve afectado por nuevas líneas o sangrías. Al escribir el código, si se inicia una nueva línea después de una coma, se aplicarán patrones de sangría automáticos.

También utilizamos muchos espacios (por ejemplo, `n = 1` en lugar de `n=1`) porque es más fácil de leer. ¡Sea amable con la gente que lee su código!

### Nomenclatura

En este manual, generalmente hacemos referencia a “columnas” y “filas” en lugar de “variables” y “observaciones”. Como se explica en este manual sobre [“datos ordenados”](https://tidyr.tidyverse.org/articles/tidy-data.html), la mayoría de los conjuntos de datos estadísticos epidemiológicos se componen estructuralmente de filas, columnas y valores.

*Las variables contienen* los valores que miden el mismo atributo subyacente (como el grupo de edad, el resultado o la fecha de inicio). Las *observaciones contienen* todos los valores medidos en la misma unidad (por ejemplo, una persona, un lugar o una muestra de laboratorio). Por lo tanto, estos aspectos pueden ser más difíciles de definir de forma tangible.

En los conjuntos de datos “ordenados”, cada columna es una variable, cada fila es una observación y cada celda es un único valor. Sin embargo, algunos conjuntos de datos que se encuentran no se ajustan a este molde: unos datos de formato “amplio” puede tener una variable dividida en varias columnas (véase un ejemplo en la página [Pivotar datos](pivoting.llms.md)). Del mismo modo, las observaciones pueden estar divididas en varias filas.

La mayor parte de este manual trata sobre la gestión y la transformación de datos, por lo que las referencias a las estructuras de datos concretas de filas y columnas son más relevantes que las observaciones y las variables más abstractas. Las excepciones se dan sobre todo en las páginas sobre análisis de datos, en las que verá más referencias a las variables y las observaciones.

### Nota

Estos son los tipos de notas que puede encontrar en el manual:

***NOTA:*** Esto es una nota  
***CONSEJO:*** Esto es un consejo.  
***PRECAUCIÓN:*** Esto es una nota de precaución.  
***PELIGRO:*** Esto es un aviso (warning).

## 1.3 Decisiones editoriales

A continuación, hacemos un seguimiento de las decisiones editoriales importantes en torno a la elección de paquetes y funciones. Si no está de acuerdo o quiere ofrecer una nueva herramienta para que la consideremos, únase o inicie una conversación en nuestra [página de Github](https://github.com/appliedepi/epirhandbook_eng).

**Tabla de paquetes, funciones y otras decisiones editoriales**

| Asunto | Considerado | Resultado | Breve explicación |
|----|----|----|----|
| Enfoque general de codificación | **tidyverse**, **data.table**, **base** | **tidyverse**, con una página sobre **data.table**, y menciones de alternativas de R **base** para los lectores sin internet | legibilidad de **tidyverse**, universalidad, más enseñado |
| Carga de paquetes | `library()`,`install.packages()`, `require()`, **pacman** | **pacman** | Acorta y simplifica el código para la mayoría de los casos de instalación/carga de paquetes múltiples |
| Importación y exportación | **rio**, muchos otros paquetes | **rio** | Facilidad para muchos tipos de archivos |
| Agrupación para las estadísticas de síntesis | **dplyr** `group_by()`, **stats** `aggregate()` | **dplyr** `group_by()` | Consecuente con el énfasis en **tidyverse** |
| Pivotar tablas | **tidyr** (funciones de pivote), **reshape2** (melt/cast), **tidyr** (spread/gather) | **tidyr** (funciones de pivote) | **reshape2** se ha retirado, **tidyr** utiliza funciones pivot a partir de la v1.0.0 |
| Limpiar los nombres de las columnas | **linelist**, **janitor** | **janitor** | Se hace hincapié en la consolidación de los paquetes |
| Semanas epidemiológicas. Epiweeks | **lubridate**, **aweek**, **tsibble**, **zoo** | Normalmente **lubridate**, los otros para casos específicos | La flexibilidad, la coherencia y las perspectivas de mantenimiento de los paquetes de lubridate |
| Etiquetas ggplot | `labs()`, `ggtitle()`/`ylab()`/`xlab()` | `labs()` | Todas las etiquetas en un solo lugar, la simplicidad |
| Convertir en factor | `factor()`, **forcats** | **forcats** | Sus diversas funciones también convierten los datos en factor en el mismo comando |
| Curvas epidémicas | **incidence**, **ggplot2**, **EpiCurve** | **incidence2** por rapidez, **ggplot2** para tareas detalladas | fiabilidad |
| Concatenación | `paste()`, `paste0()`, `str_glue()`, `glue()` | `str_glue()` | Sintaxis más sencilla que las funciones de pegado; dentro de **stringr** |

## 1.4 Revisiones importantes

| Fecha        | Cambios mayores                 |
|--------------|---------------------------------|
| 10 Mayo 2021 | Lanzamiento de la versión 1.0.0 |
| 20 Nov 2022  | Lanzamiento de la versión 1.0.1 |

NOVEDADES Con la versión 1.0.1 se han implementado los siguientes cambios:

- Actualización a la versión 4.2 de R
- Limpieza de datos: se cambió {linelist} por {matchmaker}, se eliminó una línea innecesaria del ejemplo de `case_when()`
- Fechas: se cambió `guess_date()` de {linelist} por `parse_date()` de {parsedate}
- Pivotar datos: ligera actualización de `id_cols=` en `pivot_wider()`
- Análisis de encuestas: se cambió `plot_age_pyramid()` por `age_pyramid()`, ligero cambio en el código del gráfico aluvial
- Gráficos de calor: se añadió `ungroup()` al bloque de código de `agg_weeks`
- Gráficos interactivos: se añadió `ungroup()` al bloque de código que crea `agg_weeks` para que `expand()` funcione como se pretende
- Series temporales: se añadió `data.frame()` alrededor de los objetos en todos los comandos `trending::fit()` y `predict()`
- Análisis de combinaciones: se cambió `case_when()` por `ifelse()` y se añadió código opcional con `across()` para preparar los datos
- Cadenas de transmisión: actualización a una versión más reciente de {epicontacts}

## 1.5 Agradecimientos

Este manual ha sido elaborado mediante la colaboración de profesionales de la epidemiología de todo el mundo, basándonos en nuestra experiencia en organismos sanitarios locales, estatales, provinciales y nacionales, la Organización Mundial de la Salud (OMS), Médicos Sin Fronteras (MSF), sistemas hospitalarios e instituciones académicas.

Este manual no es un producto aprobado por ninguna organización específica. Aunque nos esforzamos por ser precisos, no ofrecemos ninguna garantía sobre el contenido de este libro.

### Colaboradores

**Redactor jefe:** [Neale Batra](https://www.linkedin.com/in/neale-batra/)

Equipo central del proyecto: Neale Batra, Alex Spina, [Amrish Baidjoe](https://twitter.com/Ammer_B), Pat Keating, Henry Laurenson-Schafer, Finlay Campbell

**Autores:** [Neale Batra](https://www.linkedin.com/in/neale-batra/), [Alex Spina](https://github.com/aspina7), [Paula Blomquist](https://www.linkedin.com/in/paula-bianca-blomquist-53188186/), [Finlay Campbell](https://github.com/finlaycampbell), [Henry Laurenson-Schafer](https://github.com/henryls1), [Isaac Florence](https://www.Twitter.com/isaacatflorence), [Natalie Fischer](https://www.linkedin.com/in/nataliefischer211/), [Aminata Ndiaye](https://twitter.com/aminata_fadl), [Liza Coyer](https://www.linkedin.com/in/liza-coyer-86022040/), [Jonathan Polonsky](https://twitter.com/jonny_polonsky), [Yurie Izawa](https://ch.linkedin.com/in/yurie-izawa-a1590319), [Chris Bailey](https://twitter.com/cbailey_58?lang=en), [Daniel Molling](https://www.linkedin.com/in/daniel-molling-4005716a/), [Isha Berry](https://twitter.com/ishaberry2), [Emma Buajitti](https://twitter.com/buajitti), [Mathilde Mousset](https://mathildemousset.wordpress.com/research/), [Sara Hollis](https://www.linkedin.com/in/saramhollis/), Wen Lin

**Revisores:** Pat Keating, Annick Lenglet, Margot Charette, Danielly Xavier, Esther Kukielka, Michelle Sloan, Aybüke Koyuncu, Rachel Burke, Kate Kelsey, [Berhe Etsay](https://www.linkedin.com/in/berhe-etsay-5752b1154/), John Rossow, Mackenzie Zendt, James Wright, Laura Haskins, [Flavio Finger](https://ffinger.github.io), Tim Taylor, [Jae Hyoung Tim Lee](https://www.linkedin.com/in/jaehyoungtlee/), [Brianna Bradley](https://www.linkedin.com/in/brianna-bradley-bb8658155), [Wayne Enanoria](https://www.linkedin.com/in/wenanoria), Manual Albela Miranda, [Molly Mantus](https://www.linkedin.com/in/molly-mantus-174550150/), Pattama Ulrich, Joseph Timothy, Adam Vaughan, Olivia Varsaneux, Lionel Monteiro, Joao Muianga

Equipo de traducción al español: Juan Carlos Fernández-Merino, Juan Francisco Monteagudo, Ximena Tolosa, Luis Hernando Aguilar Ramirez, Ignacio Castro Aguirre, Esther Kukielka, Cristina Torró, Ana Fernández-Ayuso. Se ha trabajado con el traductor online DeepL, ajustando manualmente los términos médicos epidemiológicos, estadísticos e informáticos específicos. Del mismo modo se han revisado todas las páginas para corregir defectos de estilo así como aplicar los acuerdos editoriales definidos por el equipo de traducción al español.

**Illustraciones:** Calder Fong

### Financiación y apoyo

Este libro ha sido principalmente un esfuerzo voluntario que ha requerido miles de horas de trabajo.  
El manual recibió apoyo financiaciero de [TEPHINET](https://www.tephinet.org/), la red mundial de Programas de Formación en Epidemiología de Campo (FETP) a través de una subvención para el desarrollo de capacidades de emergencia COVID-19.

La Red de Antiguos Alumnos de ([EAN](https://epietalumni.net/)) proporcionó apoyo administrativo, con un agradecimiento especial a Annika Wendland. EPIET es el Programa Europeo de Formación en Epidemiología de Intervención.

Un agradecimiento especial a Médicos Sin Fronteras (MSF) Centro Operativo de Ámsterdam (OCA) por su apoyo durante la elaboración de este manual.

*Esta publicación fue respaldada por el Acuerdo de Cooperación número NU2GGH001873, financiado por los Centros para el Control y la Prevención de Enfermedades a través de TEPHINET, un programa de The Task Force for Global Health. Su contenido es responsabilidad exclusiva de los autores y no representa necesariamente las opiniones oficiales de los Centros para el Control y la Prevención de Enfermedades, el Departamento de Salud y Servicios Humanos, The Task Force for Global Health, Inc. o TEPHINET.*

### Inspiración

Hay multitud de tutoriales y viñetas que aportaron conocimientos para el desarrollo del contenido del manual y se acreditan en sus respectivas páginas.

De manera más general, las siguientes fuentes han servido de inspiración para este manual:

[El proyecto “R4Epis”](https://r4epis.netlify.app/) (una colaboración entre MSF y RECON)

[R Epidemics Consortium (RECON)](https://www.repidemicsconsortium.org/)

[El libro R for Data Science (R4DS)](https://r4ds.had.co.nz/), en español en este enlace

[bookdown: Creación de libros y documentos técnicos con R Markdown](https://bookdown.org/yihui/bookdown/)

[Netlify](https://www.netlify.com) alberga este sitio web

## 1.6 Condiciones de uso y contribución

### Licencia

[![Creative Commons License](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/4.0/)  
Esta obra está bajo una [Licencia Internacional Creative Commons Attribution-NonCommercial-ShareAlike 4.0](http://creativecommons.org/licenses/by-nc-sa/4.0/).

Los cursos académicos y los programas de formación en epidemiología pueden utilizar este manual con sus estudiantes - por favor díganos. Si tiene preguntas sobre el uso que se le va a dar, envíe un correo electrónico a contact@appliedepi.org.

### Cita sugerida

Batra, Neale, et al. Manual de R para Epidemiología. 2021. [![DOI](https://zenodo.org/badge/231610102.svg)](https://zenodo.org/badge/231610102.svg)  

### Contribución

Si quiere hacer una contribución de contenido, por favor, póngase en contacto con nosotros primero a través de Github o por correo electrónico. Estamos implementando un calendario de actualizaciones y estamos creando una guía para colaboradores.

Tenga en cuenta que el proyecto epiRhandbook se publica con un [Código de Conducta del Colaborador](https://contributor-covenant.org/version/2/0/CODE_OF_CONDUCT.html) . Al contribuir a este proyecto, se compromete a respetar sus términos.

## 1.7 Información de la sesión (R, paquetes)

A continuación se presentan las versiones de R y de todos los paquetes de R de la imagen de Docker que contiene todos los paquetes que utiliza este Manual.

``` r
sessioninfo::session_info(pkgs = "installed", include_base = TRUE)
```

    ─ Session info ───────────────────────────────────────────────────────────────
     setting  value
     version  R version 4.6.0 (2026-04-24)
     os       Ubuntu 26.04 LTS
     system   x86_64, linux-gnu
     ui       X11
     language en_US:en
     collate  en_US.UTF-8
     ctype    en_US.UTF-8
     tz       Etc/UTC
     date     2026-11-14
     pandoc   3.7.0.2 @ /usr/bin/ (via rmarkdown)
     quarto   1.9.38 @ /usr/local/bin/quarto

    ─ Packages ───────────────────────────────────────────────────────────────────
     package              * version    date (UTC) lib source
     abind                  1.4-8      2024-09-12 [1] RSPM
     adagio                 0.9.2      2023-10-26 [1] RSPM
     anytime                0.3.13     2026-04-14 [1] RSPM
     ape                    5.8-1      2024-12-16 [1] RSPM
     aplot                  0.3.0      2026-06-23 [1] RSPM
     appliedepidata         0.0.0.9013 2026-11-02 [1] Github (appliedepi/appliedepidata@77036b1)
     apyramid               0.1.3      2023-02-14 [1] RSPM
     arm                    1.15-3     2026-04-15 [1] RSPM
     askpass                1.2.1      2024-10-04 [1] RSPM
     assertthat             0.2.1      2019-03-21 [1] RSPM
     aweek                  1.0.3      2022-10-06 [1] RSPM
     backports              1.5.1      2026-04-03 [1] RSPM
     base                 * 4.6.0      2026-04-24 [1] local
     base64enc              0.1-6      2026-02-02 [1] RSPM
     bayestestR             0.18.1     2026-05-24 [1] RSPM
     bigD                   0.3.1      2025-04-03 [1] RSPM
     binom                  1.1-1.1    2022-05-02 [1] RSPM
     BiocManager            1.30.27    2025-11-14 [1] RSPM
     bit                    4.6.0      2025-03-06 [1] RSPM
     bit64                  4.8.2      2026-05-19 [1] RSPM
     bitops                 1.0-9      2024-10-03 [1] RSPM
     blob                   1.3.0      2026-01-14 [1] RSPM
     boot                   1.3-32     2025-08-29 [1] CRAN (R 4.6.0)
     broom                  1.0.13     2026-05-14 [1] RSPM
     broom.helpers          1.22.0     2025-09-17 [1] RSPM
     bslib                  0.11.0     2026-05-16 [1] RSPM
     ca                     0.71.1     2020-01-24 [1] RSPM
     cachem                 1.1.0      2024-05-16 [1] RSPM
     callr                  3.8.0      2026-06-05 [1] RSPM
     car                    3.1-5      2026-02-03 [1] RSPM
     carData                3.0-6      2026-01-30 [1] RSPM
     cards                  0.8.0      2026-05-28 [1] RSPM
     cardx                  0.3.3      2026-05-29 [1] RSPM
     cellranger             1.1.0      2016-07-27 [1] RSPM
     CFtime                 1.7.3      2026-04-02 [1] RSPM
     checkmate              2.3.4      2026-02-03 [1] RSPM
     ciTools                0.6.1      2020-10-25 [1] RSPM
     class                  7.3-23     2025-01-01 [1] CRAN (R 4.6.0)
     classInt               0.4-11     2025-01-08 [1] RSPM
     cli                    3.6.6      2026-04-09 [1] RSPM
     clipr                  0.8.1      2026-05-25 [1] RSPM
     clock                  0.7.4      2026-01-13 [1] RSPM
     cluster                2.1.8.2    2026-02-05 [1] CRAN (R 4.6.0)
     cmprsk                 2.2-12     2024-05-19 [1] RSPM
     coarseDataTools        0.7.2      2025-04-11 [1] RSPM
     coda                   0.19-4.1   2024-01-31 [1] RSPM
     codetools              0.2-20     2024-03-31 [1] CRAN (R 4.6.0)
     colorspace             2.1-2      2025-09-22 [1] RSPM
     colourpicker           1.3.0      2023-08-21 [1] RSPM
     cols4all               0.10       2025-10-27 [1] RSPM
     commonmark             2.0.0      2025-07-07 [1] RSPM
     compiler               4.6.0      2026-04-24 [1] local
     conflicted             1.2.0      2023-02-01 [1] RSPM
     correlation            0.8.8      2025-07-08 [1] RSPM
     corrplot               0.95       2024-10-14 [1] RSPM
     corrr                  0.4.5      2025-08-18 [1] RSPM
     cowplot                1.2.0      2025-07-07 [1] RSPM
     crayon                 1.5.3      2024-06-20 [1] RSPM
     crosstalk              1.2.2      2025-08-26 [1] RSPM
     curl                   7.1.0      2026-04-22 [1] RSPM
     data.table             1.18.4     2026-05-06 [1] RSPM
     data.tree              1.2.0      2025-08-25 [1] RSPM
     datasets             * 4.6.0      2026-04-24 [1] local
     datawizard             1.3.1      2026-04-26 [1] RSPM
     DBI                    1.3.0      2026-02-25 [1] RSPM
     dbplyr                 2.6.0      2026-06-17 [1] RSPM
     deldir                 2.0-4      2024-02-28 [1] RSPM
     DEoptimR               1.2-0      2026-06-07 [1] RSPM
     Deriv                  4.2.0      2025-06-20 [1] RSPM
     desc                   1.4.3      2023-12-10 [1] RSPM
     diagram                1.6.5      2020-09-30 [1] RSPM
     DiagrammeR             1.0.12     2026-04-27 [1] RSPM
     dichromat              2.0-0.1    2022-05-02 [1] RSPM
     digest                 0.6.39     2025-11-19 [1] RSPM
     distcrete              1.0.3      2017-11-23 [1] RSPM
     distributional         0.8.1      2026-06-27 [1] RSPM
     doBy                   4.7.1      2025-12-02 [1] RSPM
     doParallel             1.0.17     2022-02-07 [1] RSPM
     dplyr                  1.2.1      2026-04-03 [1] RSPM
     DT                     0.34.0     2025-09-02 [1] RSPM
     dtplyr                 1.3.3      2026-02-11 [1] RSPM
     e1071                  1.7-17     2025-12-18 [1] RSPM
     easystats              0.7.6      2026-05-24 [1] RSPM
     ecmwfr                 2.0.3      2025-02-10 [1] RSPM
     effectsize             1.0.2      2026-03-11 [1] RSPM
     Epi                    2.65       2026-04-15 [1] RSPM
     epicontacts            1.2.0      2026-11-02 [1] Github (reconhub/epicontacts@e68f228)
     epidict                0.3.0      2026-11-02 [1] Github (R4EPI/epidict@af29299)
     EpiEstim               2.2-5      2025-06-27 [1] RSPM
     epikit                 0.2.0      2025-11-05 [1] RSPM
     EpiNow2                1.9.0      2026-06-16 [1] RSPM
     epitabulate            0.1.0      2026-11-02 [1] Github (R4EPI/epitabulate@6f5539d)
     epitrix                0.4.1      2025-07-25 [1] RSPM
     etm                    1.1.2      2025-04-12 [1] RSPM
     evaluate               1.0.5      2025-08-27 [1] RSPM
     evd                    2.3-7.1    2024-09-21 [1] RSPM
     exactRankTests         0.8-37     2026-05-04 [1] RSPM
     fabletools             0.8.0      2026-06-28 [1] RSPM
     fansi                  1.0.7      2025-11-19 [1] RSPM
     farver                 2.1.2      2024-05-13 [1] RSPM
     fastLink               0.6.1      2023-11-17 [1] RSPM
     fastmap                1.2.0      2024-05-15 [1] RSPM
     fastymd                0.1.5      2026-02-27 [1] RSPM
     feasts                 0.5.0      2026-02-09 [1] RSPM
     ff                     4.5.2      2025-01-13 [1] RSPM
     filelock               1.0.3      2023-12-11 [1] RSPM
     fitdistrplus           1.2-6      2026-01-24 [1] RSPM
     flexdashboard          0.6.3      2026-01-28 [1] RSPM
     flextable              0.9.12     2026-06-02 [1] RSPM
     fontawesome            0.5.3      2024-11-16 [1] RSPM
     fontBitstreamVera      0.1.1      2017-02-01 [1] RSPM
     fontLiberation         0.1.0      2016-10-15 [1] RSPM
     fontquiver             0.2.1      2017-02-01 [1] RSPM
     forcats                1.0.1      2025-09-25 [1] RSPM
     foreach                1.5.2      2022-02-02 [1] RSPM
     forecast               9.0.2      2026-03-18 [1] RSPM
     foreign                0.8-91     2026-01-29 [1] CRAN (R 4.6.0)
     formatR                1.14       2023-01-17 [1] RSPM
     formattable            0.2.1      2021-01-07 [1] RSPM
     Formula                1.2-5      2023-02-24 [1] RSPM
     fracdiff               1.5-4      2026-04-28 [1] RSPM
     fs                     2.1.0      2026-04-18 [1] RSPM
     furrr                  0.4.0      2026-03-31 [1] RSPM
     futile.logger          1.4.9      2025-12-29 [1] RSPM
     futile.options         1.0.1      2018-04-20 [1] RSPM
     future                 1.70.0     2026-03-14 [1] RSPM
     future.apply           1.20.2     2026-02-20 [1] RSPM
     gargle                 1.6.1      2026-01-29 [1] RSPM
     gclus                  1.3.3      2025-03-28 [1] RSPM
     gdtools                0.5.1      2026-05-25 [1] RSPM
     generics               0.1.4      2025-05-09 [1] RSPM
     geojsonsf              2.0.5      2025-11-26 [1] RSPM
     getPass                0.2-4      2023-12-10 [1] RSPM
     ggdist                 3.3.3      2025-04-23 [1] RSPM
     ggExtra                0.11.0     2025-09-01 [1] RSPM
     ggforce                0.5.0      2025-06-18 [1] RSPM
     ggfun                  0.2.0      2025-07-15 [1] RSPM
     gghighlight            0.5.0      2025-06-14 [1] RSPM
     ggiraph                0.9.6      2026-02-21 [1] RSPM
     ggnewscale             0.5.2      2025-06-20 [1] RSPM
     ggplot2                4.0.3      2026-04-22 [1] RSPM
     ggplotify              0.1.3      2025-09-20 [1] RSPM
     ggpubr                 0.6.3      2026-02-24 [1] RSPM
     ggrepel                0.9.8      2026-03-17 [1] RSPM
     ggsci                  5.1.0      2026-06-26 [1] RSPM
     ggsignif               0.6.4      2022-10-13 [1] RSPM
     ggtext                 0.1.2      2022-09-16 [1] RSPM
     ggtime                 0.2.0      2026-02-09 [1] RSPM
     ggtree                 4.2.1      2026-10-29 [1] Bioconduc~
     ggupset                0.4.1      2025-02-11 [1] RSPM
     glmnet                 5.0        2026-05-04 [1] RSPM
     globals                0.19.1     2026-03-13 [1] RSPM
     glue                   1.8.1      2026-04-17 [1] RSPM
     googledrive            2.1.2      2025-09-10 [1] RSPM
     googlesheets4          1.1.2.9000 2026-11-02 [1] Github (tidyverse/googlesheets4@55cd9fd)
     gower                  1.0.2      2024-12-17 [1] RSPM
     graphics             * 4.6.0      2026-04-24 [1] local
     grates                 1.8.0      2026-03-25 [1] RSPM
     grDevices            * 4.6.0      2026-04-24 [1] local
     grid                   4.6.0      2026-04-24 [1] local
     gridExtra              2.3.1      2026-06-25 [1] RSPM
     gridGraphics           0.5-1      2020-12-13 [1] RSPM
     gridtext               0.1.6      2026-02-19 [1] RSPM
     gt                     1.3.0      2026-01-22 [1] RSPM
     gtable                 0.3.6      2024-10-25 [1] RSPM
     gtools                 3.9.5      2023-11-20 [1] RSPM
     gtsummary              2.5.1      2026-05-30 [1] RSPM
     hardhat                1.4.3      2026-04-04 [1] RSPM
     haven                  2.5.5      2025-05-30 [1] RSPM
     here                   1.0.2      2025-09-15 [1] RSPM
     highcharter            0.9.5      2026-04-22 [1] RSPM
     highr                  0.12       2026-03-06 [1] RSPM
     hms                    1.1.4      2025-10-17 [1] RSPM
     htmltools              0.5.9      2025-12-04 [1] RSPM
     htmlwidgets            1.6.4      2023-12-06 [1] RSPM
     httpuv                 1.6.17     2026-03-18 [1] RSPM
     httr                   1.4.8      2026-02-13 [1] RSPM
     httr2                  1.2.3      2026-06-23 [1] RSPM
     i2extras               0.2.1.9000 2026-11-02 [1] Github (reconverse/i2extras@10fea67)
     ids                    1.0.1      2017-05-31 [1] RSPM
     igraph                 2.3.3      2026-06-26 [1] RSPM
     imputeTS               3.4        2025-08-25 [1] RSPM
     incidence              1.7.6      2025-06-19 [1] RSPM
     incidence2             2.6.4      2026-03-02 [1] RSPM
     inline                 0.3.21     2025-01-09 [1] RSPM
     insight                1.5.2      2026-06-28 [1] RSPM
     ipred                  0.9-15     2024-07-18 [1] RSPM
     isoband                0.3.0      2025-12-07 [1] RSPM
     iterators              1.0.14     2022-02-05 [1] RSPM
     janitor                2.2.1      2024-12-22 [1] RSPM
     jomo                   2.7-6      2023-04-15 [1] RSPM
     jpeg                   0.1-11     2025-03-21 [1] RSPM
     jquerylib              0.1.4      2021-04-26 [1] RSPM
     jsonlite               2.0.0      2025-03-27 [1] RSPM
     juicyjuice             0.1.0      2022-11-10 [1] RSPM
     kableExtra             1.4.0      2024-01-24 [1] RSPM
     KernSmooth             2.23-26    2025-01-01 [1] CRAN (R 4.6.0)
     keyring                1.4.1      2025-06-15 [1] RSPM
     knitr                  1.51       2025-12-20 [1] RSPM
     labeling               0.4.3      2023-08-29 [1] RSPM
     labelled               2.16.0     2025-10-22 [1] RSPM
     lambda.r               1.2.4      2019-09-18 [1] RSPM
     later                  1.4.8      2026-03-05 [1] RSPM
     lattice                0.22-9     2026-02-09 [1] CRAN (R 4.6.0)
     lava                   1.9.2      2026-06-30 [1] RSPM
     lazyeval               0.2.3      2026-04-04 [1] RSPM
     leafem                 0.2.5      2025-08-28 [1] RSPM
     leafgl                 0.2.4      2026-04-15 [1] RSPM
     leaflegend             1.2.8      2026-05-16 [1] RSPM
     leaflet                2.2.3      2025-09-04 [1] RSPM
     leaflet.providers      3.0.0      2026-03-18 [1] RSPM
     leafsync               0.1.0      2019-03-05 [1] RSPM
     lifecycle              1.0.5      2026-01-08 [1] RSPM
     listenv                1.0.0      2026-06-22 [1] RSPM
     litedown               0.9        2025-12-18 [1] RSPM
     lme4                   2.0-1      2026-03-05 [1] RSPM
     lmtest                 0.9-40     2022-03-21 [1] RSPM
     logger                 0.4.2      2026-05-10 [1] RSPM
     loo                    2.10.0     2026-06-26 [1] RSPM
     lpSolve                5.6.23     2024-12-14 [1] RSPM
     lubridate              1.9.5      2026-02-04 [1] RSPM
     lwgeom                 0.2-16     2026-05-03 [1] RSPM
     magrittr               2.0.5      2026-04-04 [1] RSPM
     maptiles               0.11.0     2025-12-12 [1] RSPM
     markdown               2.0        2025-03-23 [1] RSPM
     MASS                   7.3-65     2025-02-28 [1] CRAN (R 4.6.0)
     matchmaker             0.1.1      2020-02-21 [1] RSPM
     Matrix                 1.7-5      2026-03-21 [1] CRAN (R 4.6.0)
     MatrixModels           0.5-4      2025-03-26 [1] RSPM
     matrixStats            1.5.0      2025-01-07 [1] RSPM
     maxstat                0.7-26     2025-05-02 [1] RSPM
     mcmc                   0.9-8      2023-11-16 [1] RSPM
     MCMCpack               1.7-1      2024-08-27 [1] RSPM
     memoise                2.0.1      2021-11-26 [1] RSPM
     methods              * 4.6.0      2026-04-24 [1] local
     mgcv                   1.9-4      2025-11-07 [1] CRAN (R 4.6.0)
     mice                   3.19.0     2025-12-10 [1] RSPM
     microbenchmark         1.5.0      2024-09-04 [1] RSPM
     mime                   0.13       2025-03-17 [1] RSPM
     miniUI                 0.1.2      2025-04-17 [1] RSPM
     minqa                  1.2.8      2024-08-17 [1] RSPM
     mitml                  0.4-5      2023-03-08 [1] RSPM
     mitools                2.4        2019-04-26 [1] RSPM
     modelbased             0.16.0     2026-06-30 [1] RSPM
     modelr                 0.1.11     2023-03-22 [1] RSPM
     munsell                0.5.1      2024-04-01 [1] RSPM
     mvtnorm                1.4-1      2026-06-06 [1] RSPM
     naniar                 1.1.0      2024-03-05 [1] RSPM
     ncmeta                 0.4.0      2024-03-25 [1] RSPM
     networkD3              0.4.1      2025-04-14 [1] RSPM
     nlme                   3.1-169    2026-03-27 [1] CRAN (R 4.6.0)
     nloptr                 2.2.1      2025-03-17 [1] RSPM
     nnet                   7.3-20     2025-01-01 [1] CRAN (R 4.6.0)
     norm                   1.0-11.1   2023-06-18 [1] RSPM
     numDeriv               2016.8-1.1 2019-06-06 [1] RSPM
     officer                0.7.5      2026-05-15 [1] RSPM
     openssl                2.4.2      2026-06-09 [1] RSPM
     OpenStreetMap          0.4.1      2025-09-29 [1] RSPM
     ordinal                2025.12-29 2026-01-10 [1] RSPM
     otel                   0.2.0      2025-08-29 [1] RSPM
     pacman                 0.5.1      2019-03-11 [1] RSPM
     padr                   0.6.3      2024-11-21 [1] RSPM
     pak                    0.10.0     2026-06-07 [1] RSPM (R 4.6.0)
     pan                    2.0        2026-06-30 [1] RSPM
     parallel               4.6.0      2026-04-24 [1] local
     parallelly             1.48.0     2026-06-29 [1] RSPM
     parameters             0.29.2     2026-06-28 [1] RSPM
     parsedate              1.3.2      2024-12-09 [1] RSPM
     patchwork              1.3.2      2025-08-25 [1] RSPM
     pbkrtest               0.5.5      2025-07-18 [1] RSPM
     pcaPP                  2.0-5      2024-08-19 [1] RSPM
     performance            0.17.1     2026-06-30 [1] RSPM
     PerformanceAnalytics   2.1.0      2026-04-11 [1] RSPM
     permute                0.9-10     2026-02-06 [1] RSPM
     PHEindicatormethods    2.1.1      2025-11-18 [1] RSPM
     pillar                 1.11.1     2025-09-17 [1] RSPM
     pkgbuild               1.4.8      2025-05-26 [1] RSPM
     pkgconfig              2.0.3      2019-09-22 [1] RSPM
     plotly                 4.12.0     2026-01-24 [1] RSPM
     plotrix                3.8-14     2026-02-13 [1] RSPM
     plyr                   1.8.9      2023-10-02 [1] RSPM
     png                    0.1-9      2026-03-15 [1] RSPM
     polyclip               1.10-7     2024-07-23 [1] RSPM
     polyCub                0.9.4      2026-04-24 [1] RSPM
     polynom                1.4-1      2022-04-11 [1] RSPM
     posterior              1.7.0      2026-04-01 [1] RSPM
     primarycensored        1.5.1      2026-06-15 [1] RSPM
     processx               3.9.0      2026-04-22 [1] RSPM
     prodlim                2026.03.11 2026-03-11 [1] RSPM
     progressr              0.19.0     2026-03-31 [1] RSPM
     projections            0.6.1      2024-12-06 [1] RSPM
     promises               1.5.0      2025-11-01 [1] RSPM
     proxy                  0.4-29     2025-12-29 [1] RSPM
     ps                     1.9.3      2026-04-20 [1] RSPM
     purrr                  1.2.2      2026-04-10 [1] RSPM
     pyinit                 1.1.5      2026-01-08 [1] RSPM
     qap                    0.1-2      2022-06-27 [1] RSPM
     quadprog               1.5-8      2019-11-20 [1] RSPM
     quantmod               0.4.29     2026-06-28 [1] RSPM
     quantreg               6.1        2025-03-10 [1] RSPM
     QuickJSR               1.10.0     2026-05-17 [1] RSPM
     R.methodsS3            1.8.2      2022-06-13 [1] RSPM
     R.oo                   1.27.1     2025-05-02 [1] RSPM
     R.utils                2.13.0     2025-02-24 [1] RSPM
     R6                     2.6.1      2025-02-15 [1] RSPM
     ragg                   1.5.2      2026-03-23 [1] RSPM
     rappdirs               0.3.4      2026-01-17 [1] RSPM
     raster                 3.6-32     2025-03-28 [1] RSPM
     rbibutils              2.4.1      2026-01-21 [1] RSPM
     RColorBrewer           1.1-3      2022-04-03 [1] RSPM
     Rcpp                   1.1.1-1.1  2026-04-24 [1] RSPM
     RcppParallel           5.1.11-2   2026-03-05 [1] RSPM
     RcppRoll               0.3.2      2026-03-28 [1] RSPM
     Rdpack                 2.6.6      2026-02-08 [1] RSPM
     reactable              0.4.5      2025-12-01 [1] RSPM
     reactR                 0.6.1      2024-09-14 [1] RSPM
     readr                  2.2.0      2026-02-19 [1] RSPM
     readxl                 1.5.0      2026-05-16 [1] RSPM
     recipes                1.3.3      2026-05-30 [1] RSPM
     RecordLinkage          0.4-12.6   2026-01-25 [1] RSPM
     reformulas             0.4.4      2026-02-02 [1] RSPM
     registry               0.5-1      2019-03-05 [1] RSPM
     rematch                2.0.0      2023-08-30 [1] RSPM
     rematch2               2.1.2      2020-05-01 [1] RSPM
     remotes                2.5.0      2024-03-17 [1] RSPM
     report                 0.6.4      2026-05-04 [1] RSPM
     repr                   1.1.7      2024-03-22 [1] RSPM
     reprex                 2.1.1      2024-07-06 [1] RSPM
     reshape2               1.4.5      2025-11-12 [1] RSPM
     rio                    1.3.0      2026-04-02 [1] RSPM
     rJava                  1.0-18     2026-04-08 [1] RSPM
     rjson                  0.2.23     2024-09-16 [1] RSPM
     rlang                  1.2.0      2026-04-06 [1] RSPM
     rlist                  0.4.6.2    2021-09-03 [1] RSPM
     rmarkdown              2.31       2026-03-26 [1] RSPM
     RNetCDF                2.11-1     2025-04-30 [1] RSPM
     RobStatTM              1.0.11     2024-10-17 [1] RSPM
     robustbase             0.99-7     2026-02-05 [1] RSPM
     rpart                  4.1.27     2026-03-27 [1] CRAN (R 4.6.0)
     rprojroot              2.1.1      2025-08-26 [1] RSPM
     rrcov                  1.7-7      2025-04-21 [1] RSPM
     rsample                1.3.2      2026-01-30 [1] RSPM
     RSQLite                3.53.3     2026-06-30 [1] RSPM
     rstan                  2.32.7     2025-03-10 [1] RSPM
     rstantools             2.6.0      2026-01-10 [1] RSPM
     rstatix                0.7.3      2025-10-18 [1] RSPM
     rstudioapi             0.19.0     2026-06-11 [1] RSPM
     runner                 0.4.6      2026-01-31 [1] RSPM
     rvest                  1.0.5      2025-08-29 [1] RSPM
     s2                     1.1.11     2026-06-01 [1] RSPM
     S7                     0.2.2      2026-04-22 [1] RSPM
     sass                   0.4.10     2025-04-11 [1] RSPM
     scales                 1.4.0      2025-04-24 [1] RSPM
     see                    0.14.1     2026-06-29 [1] RSPM
     selectr                0.6-0      2026-06-23 [1] RSPM
     SemiCompRisks          3.4        2021-02-03 [1] RSPM
     seriation              1.5.8      2025-08-20 [1] RSPM
     servr                  0.33       2026-06-16 [1] RSPM
     sessioninfo            1.2.4      2026-06-04 [1] RSPM
     sf                     1.1-1      2026-05-06 [1] RSPM
     shape                  1.4.6.1    2024-02-23 [1] RSPM
     shiny                  1.14.0     2026-06-21 [1] RSPM
     shinyjs                2.1.1      2026-01-15 [1] RSPM
     sitrep                 0.4.1      2026-11-02 [1] Github (R4EPI/sitrep@72c205f)
     skimr                  2.2.2      2026-01-10 [1] RSPM
     slider                 0.3.3      2025-11-14 [1] RSPM
     snakecase              0.11.1     2023-08-27 [1] RSPM
     sodium                 1.4.0      2024-12-16 [1] RSPM
     sourcetools            0.1.7-2    2026-03-28 [1] RSPM
     sp                     2.2-1      2026-02-13 [1] RSPM
     spacesXYZ              1.6-0      2025-06-06 [1] RSPM
     SparseM                1.84-2     2024-07-17 [1] RSPM
     sparsevctrs            0.3.6      2026-01-27 [1] RSPM
     spatial                7.3-18     2025-01-01 [1] CRAN (R 4.6.0)
     spatstat.data          3.1-9      2025-10-18 [1] RSPM
     spatstat.geom          3.8-1      2026-05-23 [1] RSPM
     spatstat.univar        3.2-0      2026-05-18 [1] RSPM
     spatstat.utils         3.2-3      2026-05-10 [1] RSPM
     spData                 2.3.5      2026-05-04 [1] RSPM
     spdep                  1.4-2      2026-02-13 [1] RSPM
     splines                4.6.0      2026-04-24 [1] local
     SQUAREM                2026.1     2026-03-12 [1] RSPM
     srvyr                  1.3.1      2026-02-02 [1] RSPM
     StanHeaders            2.32.10    2024-07-15 [1] RSPM
     stars                  0.7-2      2026-04-03 [1] RSPM
     stats                * 4.6.0      2026-04-24 [1] local
     stats4                 4.6.0      2026-04-24 [1] local
     stinepack              1.5        2024-03-07 [1] RSPM
     stringdist             0.9.17     2026-01-16 [1] RSPM
     stringi                1.8.7      2025-03-27 [1] RSPM
     stringr                1.6.0      2025-11-04 [1] RSPM
     surveillance           1.25.0     2025-06-25 [1] RSPM
     survey                 4.5        2026-02-24 [1] RSPM
     survival               3.8-6      2026-01-16 [1] CRAN (R 4.6.0)
     survminer              0.5.2      2026-02-25 [1] RSPM
     svglite                2.2.2      2025-10-21 [1] RSPM
     sys                    3.4.3      2024-10-04 [1] RSPM
     systemfonts            1.3.2      2026-03-05 [1] RSPM
     tcltk                  4.6.0      2026-04-24 [1] local
     tensorA                0.36.2.1   2023-12-13 [1] RSPM
     terra                  1.9-34     2026-06-19 [1] RSPM
     textshaping            1.0.5      2026-03-06 [1] RSPM
     threejs                0.3.4      2025-04-21 [1] RSPM
     tibble                 3.3.1      2026-01-11 [1] RSPM
     tidyquant              1.0.12     2026-03-16 [1] RSPM
     tidyr                  1.3.2      2025-12-19 [1] RSPM
     tidyselect             1.2.1      2024-03-11 [1] RSPM
     tidytree               0.4.7      2026-01-08 [1] RSPM
     tidyverse              2.0.0      2023-02-22 [1] RSPM
     timechange             0.4.0      2026-01-29 [1] RSPM
     timeDate               4052.112   2026-01-28 [1] RSPM
     timetk                 2.9.1      2025-08-29 [1] RSPM
     tinytex                0.60       2026-06-16 [1] RSPM
     tmap                   4.4-1      2026-06-26 [1] RSPM
     tmaptools              3.3        2025-07-24 [1] RSPM
     tools                  4.6.0      2026-04-24 [1] local
     treeio                 1.36.1     2026-04-30 [1] Bioconduc~
     trending               0.1.0      2023-04-03 [1] RSPM
     truncnorm              1.0-9      2023-03-20 [1] RSPM
     tseries                0.10-61    2026-03-26 [1] RSPM
     tsfeatures             1.1.1      2023-08-28 [1] RSPM
     tsibble                1.2.0      2026-02-09 [1] RSPM
     TSP                    1.2.7      2026-03-23 [1] RSPM
     TTR                    0.24.4     2023-11-28 [1] RSPM
     tweenr                 2.0.3      2024-02-26 [1] RSPM
     tzdb                   0.5.0      2025-03-15 [1] RSPM
     ucminf                 1.2.3      2026-04-02 [1] RSPM
     units                  1.0-1      2026-03-11 [1] RSPM
     UpSetR                 1.4.1      2026-05-25 [1] RSPM
     urca                   1.3-4      2024-05-27 [1] RSPM
     utf8                   1.2.6      2025-06-08 [1] RSPM
     utils                * 4.6.0      2026-04-24 [1] local
     uuid                   1.2-2      2026-01-23 [1] RSPM
     V8                     8.2.0      2026-04-21 [1] RSPM
     vctrs                  0.7.3      2026-04-11 [1] RSPM
     vegan                  2.7-5      2026-05-25 [1] RSPM
     viridis                0.6.5      2024-01-29 [1] RSPM
     viridisLite            0.4.3      2026-02-04 [1] RSPM
     visdat                 0.6.0      2023-02-02 [1] RSPM
     visNetwork             2.1.4      2025-09-04 [1] RSPM
     vistime                1.3.0      2026-03-28 [1] RSPM
     vroom                  1.7.1      2026-03-31 [1] RSPM
     warp                   0.2.3      2026-01-13 [1] RSPM
     webshot                0.5.5      2023-06-26 [1] RSPM
     withr                  3.0.3      2026-06-19 [1] RSPM
     wk                     0.9.5      2025-12-18 [1] RSPM
     writexl                1.5.4      2025-04-15 [1] RSPM
     xfun                   0.59       2026-06-19 [1] RSPM
     XML                    3.99-0.23  2026-03-20 [1] RSPM
     xml2                   1.6.0      2026-06-22 [1] RSPM
     xtable                 1.8-8      2026-02-22 [1] RSPM
     xts                    0.14.2     2026-02-28 [1] RSPM
     yaml                   2.3.12     2025-12-10 [1] RSPM
     yardstick              1.4.0      2026-04-07 [1] RSPM
     ympes                  1.9.0      2025-04-14 [1] RSPM
     yulab.utils            0.2.4      2026-02-02 [1] RSPM
     yyjsonr                0.1.22     2026-04-05 [1] RSPM
     zip                    3.0.0      2026-06-10 [1] RSPM
     zoo                    1.8-15     2025-12-15 [1] RSPM

     [1] /opt/R/4.6.0/lib/R/library
     * ── Packages attached to the search path.

    ──────────────────────────────────────────────────────────────────────────────
