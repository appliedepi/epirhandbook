# 2  Скачивание руководства и данных

## 2.1 Скачать руководство для работы офлайн

Вы можете скачать этот справочник и читать его без подключения к интернету. Каждый язык — это zip-архив со всем сайтом: каждая глава, каждое изображение и панель навигации.

- Скачайте zip-архив для своего языка и распакуйте его.
- Откройте `index.html` в распакованной папке, чтобы начать чтение.
- Смотрите страницу [Рекомендованные пакеты](packages_suggested.llms.md), чтобы установить нужные пакеты R до потери связи.

**Чтобы скачать справочник:**

[Скачать справочник (zip)](https://github.com/appliedepi/epirhandbook/releases/download/offline/epirhandbook-ru.zip)

Zip-архив пересобирается автоматически, поэтому он всегда соответствует последней версии справочника.

## 2.2 Скачивание данных для параллельной работы

Чтобы выполнять шаги на страницах руководства, вы можете загрузить примеры данных прямо в R с помощью нашего пакета-компаньона **appliedepidata**. Он содержит все наборы данных, используемые в примерах этого руководства.

### Установка пакета

**appliedepidata** отсутствует в CRAN, поэтому установите его из [репозитория Github](https://github.com/appliedepi/appliedepidata) с помощью **pak**:

``` r
# установить последнюю версию пакета appliedepidata
pak::pak("appliedepi/appliedepidata")
```

### Загрузить набор данных напрямую

Используйте `get_data()` с аргументом `name =`, чтобы загрузить набор данных прямо в R — без скачивания, без пути к файлу, без шага `import()`. Функция возвращает набор данных как объект R (таблицу данных, объект `sf`, дерево `phylo` и так далее, в зависимости от набора данных).

``` r
# загрузить очищенный построчный список прямо в R
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

На каждой странице руководства, где используются примеры данных, показан нужный для этой страницы вызов `get_data(name = "...")` — там, где данные используются впервые.

### Сохранить набор данных в файл

Некоторые страницы учат импортировать *файл* (например, книгу Excel или папку с файлами), а не объект R. Для них используйте `save_data()` с аргументами `name =` и `path =`, чтобы записать реальные файлы в выбранную вами папку:

``` r
# записать файл Excel с "сырым" построчным списком в рабочий каталог
appliedepidata::save_data(name = "case_linelists_linelist_raw", path = getwd())
```

Затем вы можете импортировать его с помощью `import()`, как любой файл на вашем компьютере — подробности см. на странице [Импорт и экспорт](importing.llms.md). Обратите внимание, что `save_data()` не распаковывает автоматически наборы данных, которые распространяются в виде архива .zip (например, шейп-файлы из нескольких файлов или папки с файлами); после сохранения используйте `utils::unzip()`.

### Посмотреть доступные данные

- `appliedepidata::search_data()` запускает интерактивное приложение Shiny для фильтрации и поиска всех наборов данных пакета по языку и ключевому слову.
- `appliedepidata::list_data()` возвращает таблицу со всеми названиями наборов данных — для использования в скриптах.

``` r
# интерактивный просмотр наборов данных
appliedepidata::search_data()

# список всех названий наборов данных
appliedepidata::list_data()
```

При желании вы можете просмотреть исходные файлы данных в **[папке “data”](https://github.com/appliedepi/appliedepidata/tree/main/inst/extdata)** репозитория Github пакета **appliedepidata**.

### Справочник наборов данных, по страницам

Ниже указано название, которое нужно передать в `get_data()`/`save_data()` для примеров данных, упомянутых на каждой странице руководства.

#### Построчный список случаев

Это вымышленная вспышка Эболы, расширенная командой, готовившей руководство, из набора данных для практики `ebola_sim` в пакете **outbreaks**.

``` r
# the "raw" linelist - an Excel spreadsheet with messy data
# use this to follow along with the Cleaning data and core functions page
raw_linelist <- appliedepidata::get_data(name = "case_linelists_linelist_raw")

# the "clean" linelist - an R-specific .rds file that preserves column classes
# use this for all other pages of this handbook that use the linelist
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")

# the "clean" linelist, as an Excel file instead
linelist_excel <- appliedepidata::get_data(name = "linelist_cleaned_excel")
```

Часть страницы вычистки использует “словарь вычистки” (.csv файл). Вы можете загрузить его напрямую в R, выполнив следующие команды:

``` r
cleaning_dict <- appliedepidata::get_data(name = "case_linelists_cleaning_dict")
```

#### Работа с датами

Страница [Работа с датами](dates.llms.md) использует число случаев по районам и датам:

``` r
counts <- appliedepidata::get_data(name = "example_district_weekly_count_data")
```

#### Написание функций

Страница [Написание функций](writing_functions.llms.md) использует построчный список вспышки гриппа H7N9 в Китае в 2013 году:

``` r
flu_china <- appliedepidata::get_data(name = "fluH7N9_China_2013")
```

#### Итерации, циклы и списки

Страница [Итерации, циклы и списки](iteration.llms.md) импортирует книгу Excel, в которой один лист на каждую больницу. Сначала сохраните её в файл:

``` r
appliedepidata::save_data(name = "example_hospital_linelists", path = getwd())
```

#### Импорт и экспорт

Страница [Импорт и экспорт](importing.llms.md) импортирует построчный список из файлов Excel. Сначала сохраните их в файлы:

``` r
# "сырой" построчный список
appliedepidata::save_data(name = "linelist_raw", path = getwd())

# очищенный построчный список
appliedepidata::save_data(name = "linelist_cleaned", path = getwd())
```

#### Данные о количестве случаев малярии

Эти данные представляют собой фиктивное количество случаев заболевания малярией по возрастным группам, учреждениям и дням. Файл .rds - это специфический для R тип файла, сохраняющий классы столбцов. Благодаря этому после импорта данных в R вам придется выполнить лишь минимальную вычистку.

``` r
malaria_data <- appliedepidata::get_data(name = "malaria_facility_count_data")
```

#### Данные для шкалы Лайкерта

Это вымышленные данные из опроса Лайкерта, используемые на странице [Демографические пирамиды и шкалы Лайкерта](age_pyramid.llms.md). Вы можете загрузить эти данные напрямую в R, выполнив следующие команды:

``` r
likert_data <- appliedepidata::get_data(name = "likert_data")
```

#### Flexdashboard

Ниже есть ссылки на файлы для страницы [Информационные панели c R Markdown](flexdashboard.llms.md). Это исходные файлы R Markdown/HTML, а не примеры наборов данных, поэтому они не входят в пакет **appliedepidata** - скачайте их напрямую с Github:

- Чтобы скачать R Markdown для информационной панели для вспышки, кликните правой кнопкой на эту [ссылку](https://github.com/appliedepi/epirhandbook/raw/main/data/flexdashboard/outbreak_dashboard.Rmd) (Cmd+клик на Mac) и выберите “Сохранить ссылку как”.  
- Чтобы скачать информационную панель HTML, кликните правой кнопкой на эту [ссылку](https://github.com/appliedepi/epirhandbook/raw/main/data/flexdashboard/outbreak_dashboard_test.html) (Cmd+клик на Mac) и выберите “Сохранить ссылку как”.

#### Отслеживание контактов

Страница [Отслеживание контактов](contact_tracing.llms.md) анализирует пример данных по отслеживанию контактов из [Go.Data](https://github.com/WorldHealthOrganization/godata/tree/master/analytics/r-reporting). Эти данные входят в **appliedepidata**:

``` r
# данные расследования случаев
cases <- appliedepidata::get_data(name = "cases_clean")

# данные регистрации контактов
contacts <- appliedepidata::get_data(name = "contacts_clean")

# данные наблюдения за контактами
followups <- appliedepidata::get_data(name = "followups_clean")

# связи между случаями и контактами
relationships <- appliedepidata::get_data(name = "relationships_clean")
```

***ПРИМЕЧАНИЕ:*** Структурированные данные по отслеживанию контактов из других программ (например, KoBo, DHIS2 Tracker, CommCare) могут выглядеть по-другому. Если вы хотите предложить альтернативные примеры данных или материалы для этой страницы, [свяжитесь с нами](index.llms.md).

***СОВЕТ:*** Если вы используете данные Go.Data и хотите связать это с вашим API, см. страницу Импорта и экспорта [(раздел по API)](importing.llms.md#import_api) и [Сообщество практиков Go.Data](https://community-godata.who.int/).

#### ГИС

Шейп-файлы состоят из нескольких файлов-компонентов, каждый со своим расширением. У одного файла расширение “.shp”, у других может быть “.dbf”, “.prj” и так далее. **appliedepidata** объединяет компоненты каждого шейп-файла в один архив .zip, поэтому используйте `save_data()`, а затем распакуйте:

``` r
# загрузить шейп-файл admin-3 Сьерра-Леоне сразу как объект sf
sle_adm3 <- appliedepidata::get_data(name = "sle_adm3")

# загрузить точки медицинских организаций как объект sf
sle_hf <- appliedepidata::get_data(name = "sle_hf")

# загрузить таблицу населения по ADM3
sle_adm3_pop <- appliedepidata::get_data(name = "sle_admpop_adm3_2020")

# ИЛИ сохранить исходные файлы-компоненты шейп-файла в папку
shp_dir <- "sle_adm3_files"
dir.create(shp_dir)
appliedepidata::save_data(name = "sle_adm3", path = shp_dir)
utils::unzip(file.path(shp_dir, "sle_adm3.zip"), exdir = shp_dir)
```

Страница [Основы ГИС](gis.llms.md) загружает все три набора данных: границы admin-3 `sle_adm3`, точки медицинских организаций `sle_hf` и таблицу населения `sle_admpop_adm3_2020`. Чтобы прочитать шейп-файл по своему пути к файлу, используйте `read_sf()` из пакета **sf**. На той же странице есть ссылки на сайт *Humanitarian Data Exchange*, откуда можно скачать другие шейп-файлы в виде архивов. Точечные данные по учреждениям здравоохранения, например, доступны [здесь](https://data.humdata.org/dataset/hotosm_sle_health_facilities).

#### Филогенетические деревья

См. страницу [Филогенетические деревья](phylogenetic_trees.llms.md). Файл Newick филогенетического дерева, построенного на основе полногеномного секвенирования 299 образцов Shigella sonnei, и соответствующие данные по образцам (преобразованы в текстовый файл). Бельгийские образцы и полученные данные любезно предоставлены Бельгийским центром по изучению сальмонелл и шигелл в рамках проекта, осуществляемого стипендиатом EUPHEM ECDC, и также будут опубликованы в рукописи. Международные данные находятся в открытом доступе в общедоступных базах данных (ncbi) и были опубликованы ранее.

``` r
# the phylogenetic tree, as a "phylo" object (ape package)
tree <- appliedepidata::get_data(name = "Shigella_tree")

# additional information on each sample
sample_data <- appliedepidata::get_data(name = "sample_data_Shigella_tree")

# the subset-tree created later in the page
subtree <- appliedepidata::get_data(name = "Shigella_subtree_2")
```

#### Стандартизация

См. страницу [Стандартизированные коэффициенты](standardization.llms.md). Вы можете загрузить данные напрямую с помощью следующих команд:

``` r
##############
# Страна A
##############
# демография страны A
A_demo <- appliedepidata::get_data(name = "country_demographics")

# смерти в стране A
A_deaths <- appliedepidata::get_data(name = "deaths_countryA")

##############
# Страна B
##############
# демография страны B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")

# смерти в стране B
B_deaths <- appliedepidata::get_data(name = "deaths_countryB")


# Референтная популяция
###############
# стандартное население
# world standard population, by sex
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

#### Временные ряды и обнаружение вспышек

См. страницу [Временные ряды и обнаружение вспышек](time_series.llms.md). Мы используем случаи кампилобактера, зарегистрированные в Германии в 2002-2011, доступные в пакете R **surveillance**. (*примечание* этот набор данных был адаптирован из оригинального в той части, что 3 месяца данных конца 2011 года были удалены в целях демонстрации)

``` r
counts <- appliedepidata::get_data(name = "campylobacter_germany")
```

Мы также используем климатические данные по Германии за 2002-2011 гг. (температура в градусах Цельсия и количество осадков в миллиметрах). Они были загружены из набора данных спутникового реанализа ЕС Copernicus с помощью пакета **ecmwfr**. **appliedepidata** объединяет их в один архив .zip из десяти годовых файлов .nc. `get_data()` читает весь набор сразу как единый объект **stars**; `save_data()` выдаёт исходные файлы .nc, если вы хотите изучить или обработать их самостоятельно.

``` r
# прочитать объединённые климатические данные сразу как объект stars
weather_data <- appliedepidata::get_data(name = "germany_weather")

# ИЛИ сохранить исходные годовые файлы .nc в папку
weather_dir <- "germany_weather_files"
dir.create(weather_dir)
appliedepidata::save_data(name = "germany_weather", path = weather_dir)
utils::unzip(file.path(weather_dir, "germany_weather.zip"), exdir = weather_dir)
```

#### Анализ опросов

Для страницы [Анализ опросов](survey_analysis.llms.md) мы используем выдуманные данные исследования смертности на основе шаблонов опросов MSF OCA. Этот выдуманный набор данных был сгенерирован в рамках [проекта “R4Epis”](https://r4epis.netlify.app/).

``` r
# fictional survey data
survey_data <- appliedepidata::get_data(name = "survey_data")

# fictional survey data dictionary
survey_dict <- appliedepidata::get_data(name = "survey_dict")

# fictional survey population data
population <- appliedepidata::get_data(name = "population")
```

#### Shiny

Страница [Информационные панели с Shiny](shiny_basics.llms.md) демонстрирует создание простого приложения для отображения данных по малярии. Данные приложения входят в состав **appliedepidata**:

``` r
malaria_data <- appliedepidata::get_data(name = "malaria_facility_count_data")
```

Скрипты R этого приложения не являются примерами данных и не входят в **appliedepidata** — скачайте их напрямую с Github:

Вы можете [кликните, чтобы скачать файл app.R, который содержит код и для UI, и для сервера для приложения Shiny.](https://github.com/appliedepi/epirhandbook/raw/main/data/malaria_app/app.R)

Вы можете [кликните, чтобы скачать файл global.R](https://github.com/appliedepi/epirhandbook/raw/main/data/malaria_app/global.R), который должен быть выполнен до открытия приложения, как объясняется на странице.

Вы можете [кликните, чтобы скачать файл plot_epicurve.R](https://github.com/appliedepi/epirhandbook/raw/main/data/malaria_app/funcs/plot_epicurve.R), к которому обращается global.R. Обратите внимание, что его нужно сохранить в папке “funcs”, чтобы работал путь к файлу через here().
