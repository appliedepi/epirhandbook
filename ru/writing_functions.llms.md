# 44  Написание функций

## 44.1 Подготовка

### Загрузка пакетов

Данный фрагмент кода показывает загрузку пакетов, требуемых для анализа. В данном руководстве мы подчеркиваем использование `p_load()` из **pacman**, которая устанавливает пакет, если необходимо, *и* загружает его для использования. Вы можете также загрузить установленные пакеты с помощью `library()` из **базового** R. См. дополнительную информацию о пакетах R на странице [Основы R](basics.llms.md).

### Импорт данных

Мы импортируем набор данных о случаях из имитированной эпидемии Эболы. Если вы хотите скачать данные, чтобы выполнять шаги параллельно, см. инструкции на странице [Скачивание руководства и данных](download.llms.md). Набор данных импортируется с помощью функции `import()` из пакета **rio**. См. страницу [Импорт и экспорт](importing.llms.md), где приводятся разные способы импорта данных.

Мы также используем в последней части этой страницы некоторые данные по гриппу H7N9 2013 года.

## 44.2 Функции

Функции полезны в программировании, так как позволяют сделать код проще для понимания, короче и менее подверженным ошибкам (при условии отсутствия ошибок в самой функции).

Если вы дошли до этого руководства, значит, вы столкнулись с бесконечным количеством функций, поскольку в R каждая операция - это вызов функции, `+, for, if, [, $, { …`. Например `x + y` - это то же самое, что`'+'(x, y)`

R - один из тех языков, которые предлагают наибольшие возможности для работы с функциями и предоставляют пользователю достаточно инструментов для их легкого написания. Мы не должны думать о функциях как о фиксированных на вершине или в конце цепочки программирования, R предлагает возможность использовать их как векторы и даже использовать их внутри других функций, списков…

Существует много очень продвинутых ресурсов по функциональному программированию, и мы приведем здесь лишь краткие практические примеры, которые помогут вам начать знакомство с функциональным программированием. Для более подробного ознакомления с функциональным программированием мы предлагаем вам посетить ссылки на источники.

## 44.3 Зачем использовать функцию?

Прежде чем ответить на этот вопрос, важно отметить, что вы уже получили советы по написанию своих первых функций на языке R на странице [Итерации, циклы и списки](iteration.llms.md) данного руководства. На самом деле, использование “if/else” и циклов часто является ключевой частью многих наших функций, поскольку они позволяют легким образом расширить применение нашего кода, чтобы допускать несколько условий или проводить итерацию кода для повторяющихся задач.

- Я повторяю несколько раз один и тот же блок кода, чтобы применить его к другой переменной или данным?

- Избавление от него существенно сократит общий код и ускорит его выполнение?

- Возможно ли, что написанный мною код используется снова, но с другим значением во многих местах кода?

Если ответ на один из предыдущих вопросов “ДА”, то, скорее всего, необходимо написать функцию

## 44.4 Как R строит функции?

Функции в R имеют три основных компонента:

- `formals()` - это список аргументов, которые контролируют то, как мы можем вызвать функцию

- `body()` - код внутри функции, т.е. внутри фигурных скобок или после круглых скобок, смотря как мы его запишем

и,

- `environment()`, который помогает найти переменные функции и определяет, как функция находит значение.

Как только вы создали свою функцию, вы можете верифицировать каждый из этих компонентов, вызвав соответствующую функцию.

## 44.5 Базовый синтаксис и структура

- Функцию необходимо правильно назвать, чтобы ее работа была понятна сразу после прочтения ее имени. Собственно, так уже сделано в большинстве базовых архитектур R. Такие функции, как `mean()`, `print()`, `summary()` имеют очень понятные имена

- Функции потребуются аргументы, такие как данные, с которыми нужно работать, и другие объекты, которые могут быть статическими значениями, среди прочих опций

- И, наконец, функция выдает результат, исходя из своей основной задачи и переданных ей аргументов. Обычно мы используем встроенные функции, такие как `print()`, `return()`… для создания выходных данных. Выходными данными могут быть логическое значение, число, текст, датафрейм…по сути, любой объект R.

Вот так выглядит состав функции:

``` r
function_name <- function(argument_1, argument_2, argument_3){
  
           function_task
  
           return(output)
}
```

Мы можем создать нашу первую функцию, которую назовем `contain_covid19()`.

``` r
contain_covid19 <- function(barrier_gest, wear_mask, get_vaccine){
  
                            if(barrier_gest == "yes" & wear_mask == "yes" & get_vaccine == "yes" ) 
       
                            return("success")
  
  else("please make sure all are yes, this pandemic has to end!")
}
```

Мы можем затем верифицировать компоненты нашей новой созданной функции.

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

Теперь мы протестируем нашу функцию. Для вызова написанной нами функции необходимо использовать ее так же, как и все функции R, т.е. написать имя функции и добавить необходимые аргументы.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "yes")
```

    [1] "success"

Для надежности мы можем еще раз написать имя каждого аргумента. Но и без их указания код должен работать, поскольку R имеет в памяти расположение каждого аргумента. Поэтому, если значения аргументов расположены в правильном порядке, можно не писать имена аргументов при вызове функций.

``` r
contain_covid19("yes", "yes", "yes")
```

    [1] "success"

Далее посмотрим, что произойдет, если одно из значений `"no"` (нет) или **не** `"yes"` (да).

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "no")
```

    [1] "please make sure all are yes, this pandemic has to end!"

Если мы зададим аргумент, который не распознан, мы получим ошибку:

``` r
contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", get_vaccine = "no")
```

`Error in contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", : could not find function "contain_covid19"`

***ПРИМЕЧАНИЕ:*** Некоторые функции (в большинстве случаев очень короткие и простые) могут не требовать имени и могут использоваться напрямую в строке кода или внутри другой функции для выполнения быстрых задач. Их называют **анонимные функции** .

Например, ниже приведена первая анонимная функция, которая сохраняет только текстовые переменные в наборе данных.

``` r
linelist %>% 
  dplyr::slice_head(n=10) %>%  #эквивалентно функции из базового R "head", возвращает первые n наблюдений набора данных
  select(function(x) is.character(x)) 
```

Затем еще одна функция, которая выбирает каждое второе наблюдение из нашего набора данных (это может быть актуально, когда мы имеем продольные данные с большим количеством записей на пациента, например, после упорядочивания по дате или посещению). В этом случае подходящей функцией вне dplyr будет `function (x) (x%%2 == 0)`, чтобы применить к вектору, содержащему все номера строк.

``` r
linelist %>%   
   slice_head(n=20) %>% 
   tibble::rownames_to_column() %>% # добавляем индексы каждого наблюдения как имена строк, чтобы четко видеть итоговый выбор
   filter(row_number() %%2 == 0)
```

Возможный код в базовом R для той же задачи может выглядеть так:

``` r
linelist_firstobs <- head(linelist, 20)

linelist_firstobs[base::Filter(function(x) (x%%2 == 0), seq(nrow(linelist_firstobs))),]
```

***ВНИМАНИЕ:*** Хотя использование функций действительно может помочь нам в работе с кодом, тем не менее написание некоторых функций или исправление одной из них, если она не была тщательно продумана, написана адекватно и в результате возвращает ошибки, может занять много времени. Поэтому часто рекомендуется сначала написать код на языке R, убедиться, что он выполняет то, что мы задумали, а затем преобразовать его в функцию, состоящую из трех основных компонентов, перечисленных выше.

## 44.6 Примеры

### Выдача таблиц долей для нескольких столбцов

Да, во многих пакетах уже есть хорошие функции, позволяющие очень просто и красиво обобщать информацию. Но мы все же попробуем сделать свои собственные, в рамках наших первых шагов по освоению написания функций.

В этом примере мы хотим показать, как написание простой функции позволяет избежать многократного копирования одного и того же кода.

``` r
proptab_multiple <- function(my_data, var_to_tab){
  
  #печать имен каждой интересующей переменной перед табуляцией
  print(var_to_tab)

  with(my_data,
       rbind( #связать результаты двух следующих функций по строкам
        #табуляция интересующей переменной: дает только числа
          table(my_data[[var_to_tab]], useNA = "no"),
          #расчет долей для каждой интересующей переменной и округление значения до 2 знаков после запятой
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

***СОВЕТ:*** Как было показано выше, очень важно комментировать свои функции так же, как это делается при общем программировании. Следует помнить, что цель функции - сделать код легко читаемым, более коротким и эффективным. Тогда можно понять, что делает функция, просто прочитав ее название, а более подробную информацию можно получить, прочитав комментарии.

Второй вариант - использовать эту функцию внутри другой в цикле, чтобы провести процесс сразу:

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

Более простой способ - использование “apply” из базового R вместо “цикла for”, как выражено ниже:

***СОВЕТ:*** R часто определяется как функциональный язык программирования, и почти каждый раз, когда вы запускаете строку кода, вы используете некоторые встроенные функции. Хорошей привычкой для более комфортного написания функций является частое внутреннее рассмотрение того, как построены основные функции, которые вы используете ежедневно. Вы можете выбрать имя функции и затем использовать горячие клавиши `Ctrl+F2` или `fn+F2` или `Cmd+F2` (в зависимости от вашего компьютера) .

## 44.7 Использование **purrr**: написание функций, которые могут применяться итеративно

### Модификация класса нескольких столбцов в наборе данных

Представим, что нужно поменять множество текстовых переменных в оригинальных данных `linelist` на класс “фактор” для анализа и построения графиков. Вместо того, чтобы повторять один шаг несколько раз, мы можем использовать `lapply()`, чтобы применить это преобразование ко всем нужным переменным в одной строке кода.

***ВНИМАНИЕ:*** `lapply()` выдает список, поэтому может потребовать дополнительной модификации в качестве последнего шага.

Тот же шаг можно сделать с помощью функции `map_if()` из пакета **purrr**

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

### Итеративное создание графиков для разных уровней переменной

Здесь мы построим круговую диаграмму, чтобы посмотреть распределение исходов пациентов в Китае во время вспышки заболевания H7N9 для каждой провинции. Вместо того чтобы повторять код для каждой из них, мы просто применим созданную нами функцию.

``` r
#уточнение опций для использования в highchart
options(highcharter.theme =   highcharter::hc_theme_smpl(tooltip = list(valueDecimals = 2)))


#создаем функцию под названием "chart_outcome_province", которая берет в качестве аргумента набор данных и название провинции, по которой строится график распределения исходов.

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

### Итеративное создание таблиц для разных уровней переменной

Здесь мы создадим три показателя, которые сведем в таблицу, и хотим получить эту таблицу для каждой из провинций. Наши показатели - это задержка между началом заболевания и госпитализацией, процент выздоровления и медианный возраст больных.

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

#соединяем три набора данных с индикаторами

table_indic_all <- indic_1 %>% 
  dplyr::left_join(indic_2, by = "province") %>% 
        left_join(indic_3, by = "province")


#печатаем индикаторы в виде таблицы flextable


print_indic_prov <-  function(table_used, prov){
  
  #сначала немного преобразовываем датафрейм для легкости печати
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

## 44.8 Советы и наилучшие практики для хорошо работающих функций

Функциональное программирование призвано облегчить код и упростить его чтение. Оно не должно приводить к обратному. Приведенные ниже советы помогут вам получить чистый и легко читаемый код.

### Именование и синтаксис

- Избегайте использования символов, которые легко могли бы быть уже заняты другими функциями, уже существующими в вашей среде

- Рекомендуется, чтобы имя функции было коротким и понятным для другого читателя

- Предпочтительно использовать глаголы в качестве имени функции и существительные для имен аргументов.

### Имена столбцов и оценка принципов аккуратности

Если вы хотите знать, как ссылаться на *имена столбцов*, которые заданы в ваш код в виде аргументов, прочитайте это [руководство по программированию tidyverse](https://dplyr.tidyverse.org/articles/programming.html). Среди рассматриваемых тем - *оценка на предмет аккуратности* и использование *embrace* `{ }` “двойных фигурных скобок”

Например, вот краткий шаблон кода со страницы самоучителя, приведенного выше:

``` r
var_summary <- function(data, var) {
  data %>%
    summarise(n = n(), min = min({{ var }}), max = max({{ var }}))
}
mtcars %>% 
  group_by(cyl) %>% 
  var_summary(mpg)
```

### Тестирование и работа с ошибками

Чем сложнее задача функции, тем выше вероятность возникновения ошибок. Поэтому иногда необходимо добавить некоторую верификацию внутри функции, чтобы быстро понять, откуда взялась ошибка, и найти способ ее устранения.

- Более чем рекомендуется ввести проверку на предмет отсутствия одного из аргументов с помощью `missing(argument)`. Эта простая проверка выдаст значение “TRUE” (ИСТИНА) или “FALSE” (ЛОЖЬ).

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

- Используйте `stop()`, чтобы сделать ошибки более обнаружимыми.

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

- Как мы видим, при выполнении большинства встроенных функций в определенных условиях могут появляться сообщения и предупреждения. Мы можем интегрировать их в наши написанные функции с помощью функций `message()` и `warning()`.

- Мы можем обрабатывать ошибки и с помощью функции `safely()`, которая принимает в качестве аргумента одну функцию и выполняет ее безопасным образом. Фактически функция будет выполняться без остановки, если встретит ошибку. `safely()` выдает в качестве выходного результата **список** с двумя объектами: это результат и ошибка, которую она “пропустила”.

Мы можем верифицировать первую, выполнив `mean()` в качестве функции, затем выполняем `safely()`.

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

Как говорилось ранее, подробное комментирование наших кодов является хорошим способом документирования нашей работы.

## 44.9 Ресурсы

[R для науки о данных ссылка](https://r4ds.had.co.nz/functions.html)

[Шпаргалка по продвинутому программированию R](https://www.rstudio.com/wp-content/uploads/2016/02/advancedR.pdf)

[Шпаргалка по пакету purr](https://purrr.tidyverse.org/)

[Видео-выступление Хэдли Викхэма на конференции ACM: радость функционального программирования (как работает map_dbl)](https://youtube.videoken.com/embed/bzUmK0Y07ck)
