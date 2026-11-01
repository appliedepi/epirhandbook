# 13  Agrupando dados

[![](../../images/grouping_1500x500.png)](../../images/grouping_1500x500.png)

Esta página cobre como agrupar e agregar dados para análise descritiva. Ela faz uso da família de pacotes **tidyverse** que tem funções comuns e fáceis de usar.

O agrupamento de dados é um componente central do gerenciamento e análise de dados. Os dados agrupados estatisticamente resumidos por grupo e que podem ser traçados por grupo em um gráfico. As funções do pacote **dplyr** (parte do **tidyverse**) tornam o agrupamento e as operações subseqüentes bastante fáceis.

Esta página abordará os seguintes tópicos:

- Agrupar dados com a função `group_by()`.  
- Dados desagrupados
- `summarise()`dados agrupados com estatísticas  
- A diferença entre `count()` e `tally()`  
- ’arrange()\`aplicado a dados agrupados  
- `filter()` aplicado aos dados agrupados  
- mutate()\`aplicado a dados agrupados  
- select()`aplicado aos dados agrupados O comando do R **base**`aggregate()\` como alternativa

## 13.1 Preparação

### Carregar pacotes

Este trecho de código mostra o carregamento dos pacotes necessários para as análises. Neste manual, enfatizamos `p_load()` de **pacman**, que instala o pacote se necessário *e* o carrega para utilização. Você também pode carregar os pacotes instalados com `library()` do R **base**. Veja a página em [Introdução ao R](basics.llms.md) para mais informações sobre os pacotes R.

``` r
pacman::p_load(
  rio,       # para importar os dados
  here,      # localizar pacotes
  tidyverse, # limpar, manipular, e visualizar os dados (inlcui dplyr)
  janitor,   # adicionar totais às linhas e colunas 
  appliedepidata) # dados de exemplo utilizados neste manual
```

### Importar datos

Nós importamos os dados de casos de uma epidemia simulada de Ebola. Carregue diretamente com `appliedepidata::get_data(name = "linelist_cleaned_rds")` (consulte a página [Baixar manual e dados](download.llms.md) para mais detalhes).

``` r
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

As primeiras 50 linhas da `linelist`:

## 13.2 Agrupando os dados

A função `group_by()` de **dplyr** agrupa as linhas pelos valores únicos na coluna especificada para ela. Se várias colunas forem especificadas, as linhas são agrupadas pelas combinações únicas de valores através das colunas. Cada valor único (ou combinação de valores) constitui um grupo. Alterações subseqüentes no conjunto de dados ou cálculos podem então ser realizadas dentro do contexto de cada grupo.

Por exemplo, o comando abaixo toma a “linelist” e agrupa as linhas por valores únicos na coluna “outcome”, salvando a saída como uma nova tabela de dados (*dataframe*) chamada “ll_by_outcome”. A(s) coluna(s) de agrupamento são colocadas dentro dos parênteses da função `group_by()`

``` r
ll_by_outcome <- linelist %>% 
  group_by(outcome)
```

**Note que não há nenhuma mudança perceptível no conjunto de dados** após executar `group_by()`, *até* outra função do **dplyr** tal como `mutate()`, `summarise()`, ou `arrange()` ser aplicada no *dataframe* “grouped”.

Você pode, no entanto, “ver” os agrupamentos imprimindo o quadro de dados. Ao imprimir um quadro de dados agrupados, você verá que ele foi transformado em um objeto de classe \[`tibble` (https://tibble.tidyverse.org/) que, quando impresso, mostra quais agrupamentos foram aplicados e quantos grupos existem - escritos logo acima da linha do cabeçalho.

``` r
# visualizar quais grupos estão ativvos
ll_by_outcome
```

    # A tibble: 5,888 × 30
    # Groups:   outcome [3]
       case_id generation date_infection date_onset date_hospitalisation
       <chr>        <dbl> <date>         <date>     <date>              
     1 5fe599           4 2014-05-08     2014-05-13 2014-05-15          
     2 8689b7           4 NA             2014-05-13 2014-05-14          
     3 11f8ea           2 NA             2014-05-16 2014-05-18          
     4 b8812a           3 2014-05-04     2014-05-18 2014-05-20          
     5 893f25           3 2014-05-18     2014-05-21 2014-05-22          
     6 be99c8           3 2014-05-03     2014-05-22 2014-05-23          
     7 07e3e8           4 2014-05-22     2014-05-27 2014-05-29          
     8 369449           4 2014-05-28     2014-06-02 2014-06-03          
     9 f393b4           4 NA             2014-06-05 2014-06-06          
    10 1389ca           4 NA             2014-06-05 2014-06-07          
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_outcome <date>, outcome <chr>, gender <chr>,
    #   age <dbl>, age_unit <chr>, age_years <dbl>, age_cat <fct>, age_cat5 <fct>,
    #   hospital <chr>, lon <dbl>, lat <dbl>, infector <chr>, source <chr>,
    #   wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>, chills <chr>,
    #   cough <chr>, aches <chr>, vomit <chr>, temp <dbl>, time_admission <chr>,
    #   bmi <dbl>, days_onset_hosp <dbl>

### Grupos únicos

**Os grupos criados refletem cada combinação única de valores através das colunas de agrupamento.**

Para ver os grupos *e o número de linhas em cada grupo*, passe os dados agrupados para `tally()`. Para ver apenas os grupos únicos sem conta, você pode passar para `group_keys()`.

Veja abaixo que existem **três** valores únicos na coluna de agrupamento `outcome` (desfecho, em português): “Death” (óbito), “Recover” (Recuperado), e `NA`. Veja que existem `nrow(linelist %>% filter(outcome == "Death"))` óbitos, `nrow(linelist %>% filter(outcome == "Recover"))` recuperações, e `nrow(linelist %>% filter(is.na(outcome)))` sem nenhum resultado registrado.

``` r
linelist %>% 
  group_by(outcome) %>% 
  tally()
```

    # A tibble: 3 × 2
      outcome     n
      <chr>   <int>
    1 Death    2582
    2 Recover  1983
    3 <NA>     1323

Você pode agrupar por mais de uma coluna. Abaixo, o *dataframe* é agrupado por ‘outcome’ e ‘gender’, e depois contada. Observe como cada combinação única de “outcome” e “gender” é registrada como seu próprio grupo - incluindo valores ausentes para cada coluna.

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally()
```

    # A tibble: 9 × 3
    # Groups:   outcome [3]
      outcome gender     n
      <chr>   <chr>  <int>
    1 Death   f       1227
    2 Death   m       1228
    3 Death   <NA>     127
    4 Recover f        953
    5 Recover m        950
    6 Recover <NA>      80
    7 <NA>    f        627
    8 <NA>    m        625
    9 <NA>    <NA>      71

### Novas colunas

Você também pode criar uma nova coluna de agrupamento *dentro* da função `group_by()`. Isto equivale a chamar a função`mutate()` antes da instrução `group_by()`. Para uma tabulação rápida, este estilo pode ser útil, mas para maior clareza em seu código, considere criar esta coluna em seu próprio passo `mutate()` e depois encadear (usando o “pipe” %\>%) com o `group_by()`.

``` r
# agrupar dados baseado em uma coluna biária criada dentro do próprio comando group_by  
linelist %>% 
  group_by(
    age_class = ifelse(age >= 18, "adult", "child")) %>% 
  tally(sort = T)
```

    # A tibble: 3 × 2
      age_class     n
      <chr>     <int>
    1 child      3618
    2 adult      2184
    3 <NA>         86

### Adicionar/Eliminar colunas de agrupamento

Por padrão, se você executar `group_by()` em dados que já estão agrupados, os grupos antigos serão removidos e o(s) novo(s) grupo(s) será(ão) aplicado(s). Se você quiser adicionar novos grupos aos já existentes, inclua o argumento \`.add = TRUE’.

``` r
# Agrupado por 'outcome' (desfecho)
by_outcome <- linelist %>% 
  group_by(outcome)

# Adicionar um agrupamento por 'gender' (sexo) 
by_outcome_gender <- by_outcome %>% 
  group_by(gender, .add = TRUE)
```

**Manter todos os grupos**

Se você agrupar em uma coluna do tipo fator, pode haver níveis do fator que não estão presentes atualmente nos dados. Se você agrupar nesta coluna, por padrão esses níveis não presentes são descartados e não incluídos como grupos. Para alterar isso para que todos os níveis apareçam como grupos (mesmo que não estejam presentes nos dados), defina `.drop = FALSE` em seu comando `group_by()`.

## 13.3 Desagrupar

Os dados que foram agrupados permanecerão agrupados até que especificamente não sejam agrupados através do `ungroup()`. Se você se esquecer de desagradar, isso pode levar a cálculos incorretos! Abaixo está um exemplo de remoção de todos os agrupamentos:

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally() %>% 
  ungroup()
```

Você também pode remover o agrupamento apenas para colunas específicas, colocando o nome da coluna dentro de `ungroup()`.

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally() %>% 
  ungroup(gender) # remove o agrupamento por `gender` (sexo), mantendo o agrupamento por `outcome` (desfecho) 
```

***NOTA:*** O verbo `count()` desagrupa os dados automaticamente após a contagem.

## 13.4 Resumir os dados (Summarise)

Consulte a seção **dplyr** da página [Tabelas descritivas](tables_descriptive.llms.md) para obter uma descrição detalhada de como produzir tabelas resumidas com `summarise()`. Aqui abordamos brevemente como seu comportamento muda quando aplicado a dados agrupados.

A função **dplyr** `summarise()` (ou `summarize()`) pega um dataframe e o converte em um *novo* dataframe resumido, com colunas contendo as estatísticas resumidas que você definiu. Em dataframe não agrupados, as estatísticas resumidas serão calculadas a partir de todas as linhas. A aplicação de `summarise()` aos dados agrupados produz estas estatísticas resumidas *para cada grupo*.

A sintaxe de `summarise()` é tal que você fornece o(s) nome(s) da(s) **nova(s)** coluna(s) resumo, um sinal de igual, e então uma função estatística a ser aplicada aos dados, como mostrado abaixo. Por exemplo, `min()`, `max()`, `median()`, ou `sd()`. Dentro da função estatística, liste a coluna a ser operada e qualquer argumento relevante (por exemplo, `na.rm = TRUE`). Você pode utilizar `sum()` para contar o número de linhas que satisfazem um critério lógico (com duplo igual a \`==\`\`).

Abaixo está um exemplo de `summarise()` aplicado *em dados não-agrupados*. As estatísticas resultantes são produzidas a partir de todo o conjunto de dados.

``` r
# estatísticas resumo na linelist desagrupada 
linelist %>% 
  summarise(
    n_cases  = n(),
    mean_age = mean(age_years, na.rm=T),
    max_age  = max(age_years, na.rm=T),
    min_age  = min(age_years, na.rm=T),
    n_males  = sum(gender == "m", na.rm=T))
```

      n_cases mean_age max_age min_age n_males
    1    5888 16.01831      84       0    2803

Em contraste, abaixo está a mesma declaração `summarise()` aplicada aos dados agrupados. As estatísticas são calculadas para cada grupo de “outcome” (desfecho). Observe como as colunas de agrupamento serão transportadas para o dataframe.

``` r
# statísticas resumo na linelist agrupada 
linelist %>% 
  group_by(outcome) %>% 
  summarise(
    n_cases  = n(),
    mean_age = mean(age_years, na.rm=T),
    max_age  = max(age_years, na.rm=T),
    min_age  = min(age_years, na.rm=T),
    n_males    = sum(gender == "m", na.rm=T))
```

    # A tibble: 3 × 6
      outcome n_cases mean_age max_age min_age n_males
      <chr>     <int>    <dbl>   <dbl>   <dbl>   <int>
    1 Death      2582     15.9      76       0    1228
    2 Recover    1983     16.1      84       0     950
    3 <NA>       1323     16.2      69       0     625

***DICA:*** A função `summarise` funciona com a ortografia britânica e americana - `summarise()` e `summarize()` chamam a mesma função.

## 13.5 Contagens

As funções `count()` e `tally()` tem funcionalidade semelhante mas são diferentes. Leia mais sobre a distinção entre `tally()` e `count()` [here](https://dplyr.tidyverse.org/reference/tally.html)

### `tally()`

`tally()` é um atalho para `summarise(n = n())`, e *não* agrupa os dados. Assim, para ter `tallys` (contagens) agrupadas, esta função deve ser precedida de um comando `group_by()`. Você pode adicionar `sort = TRUE` para ver os grupos maiores primeiro.

``` r
linelist %>% 
  tally()
```

         n
    1 5888

``` r
linelist %>% 
  group_by(outcome) %>% 
  tally(sort = TRUE)
```

    # A tibble: 3 × 2
      outcome     n
      <chr>   <int>
    1 Death    2582
    2 Recover  1983
    3 <NA>     1323

### `count()`

Por outro lado, `count()` faz o seguinte:

1.  aplica `group_by()` nas colunas especificadas  
2.  aplica `summarise()` e retorna a coluna `n` com o número de linhas por grupo
3.  aplica `ungroup()`

``` r
linelist %>% 
  count(outcome)
```

      outcome    n
    1   Death 2582
    2 Recover 1983
    3    <NA> 1323

Assim como em `group_by()` você pode adicionar uma nova coluna dentro do comando `count()`:

``` r
linelist %>% 
  count(age_class = ifelse(age >= 18, "adult", "child"), sort = T)
```

      age_class    n
    1     child 3618
    2     adult 2184
    3      <NA>   86

O comando`count()` pode ser chamado várias vezes, com a funcionalidade “rolling-up” (rolando para cima). Por exemplo, para resumir o número de hospitais presentes para cada sexo, execute o seguinte. Nota, o nome da coluna final é alterado do padrão “n” para maior clareza (com `name =`).

``` r
linelist %>% 
  # produz contagens para grupos únicos de  "outcome-gender" groups
  count(gender, hospital) %>% 
  # junta lingas por `gender` (3) e conta a quantidade de hospitais por gênero (6)
  count(gender, name = "hospitals per gender" ) 
```

      gender hospitals per gender
    1      f                    6
    2      m                    6
    3   <NA>                    6

### Adicionar contagens

Em contraste com `count()` e `summarise()`, você pode utilizar `add_count()` para *adicionar* uma nova coluna `n` com a contagem de linhas por grupo *enquanto mantém todas as outras colunas do dataframe*.

Isto significa que o número de contagem de um grupo, na nova coluna `n`, será impresso em cada linha do grupo. Para fins de demonstração, adicionamos esta coluna e depois reorganizamos as colunas para facilitar a visualização. Veja a seção abaixo em [filtro no tamanho do grupo](#group_filter_grp_size) para outro exemplo.

``` r
linelist %>% 
  as_tibble() %>%                   # converte para "tibble" para melhro vizualização
  add_count(hospital) %>%           # adiciona coluna n com as contages por hospital 
  select(hospital, n, everything()) # re-organiza para o propósito desta demostração
```

    # A tibble: 5,888 × 31
       hospital                       n case_id generation date_infection date_onset
       <chr>                      <int> <chr>        <dbl> <date>         <date>    
     1 Other                        885 5fe599           4 2014-05-08     2014-05-13
     2 Missing                     1469 8689b7           4 NA             2014-05-13
     3 St. Mark's Maternity Hosp…   422 11f8ea           2 NA             2014-05-16
     4 Port Hospital               1762 b8812a           3 2014-05-04     2014-05-18
     5 Military Hospital            896 893f25           3 2014-05-18     2014-05-21
     6 Port Hospital               1762 be99c8           3 2014-05-03     2014-05-22
     7 Missing                     1469 07e3e8           4 2014-05-22     2014-05-27
     8 Missing                     1469 369449           4 2014-05-28     2014-06-02
     9 Missing                     1469 f393b4           4 NA             2014-06-05
    10 Missing                     1469 1389ca           4 NA             2014-06-05
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_hospitalisation <date>, date_outcome <date>,
    #   outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>, age_years <dbl>,
    #   age_cat <fct>, age_cat5 <fct>, lon <dbl>, lat <dbl>, infector <chr>,
    #   source <chr>, wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>,
    #   chills <chr>, cough <chr>, aches <chr>, vomit <chr>, temp <dbl>,
    #   time_admission <chr>, bmi <dbl>, days_onset_hosp <dbl>

### Adicionar totais

Para adicionar facilmente uma linhas ou colunas com os *total* ou colunas após utilizar `tally()` ou `count()`, veja a seção **janitor** da página [Tabelas descritivas](tables_descriptive.llms.md#tbl_janitor). Este pacote oferece funções como `adorn_totals()` e `adorn_percentages()` para adicionar totais e converter para mostrar porcentagens. Abaixo está um breve exemplo:

``` r
linelist %>%                                  # caso linelist
  tabyl(age_cat, gender) %>%                  # tabela cruzada para duas colinas
  adorn_totals(where = "row") %>%             # adiciona uma linha de totais
  adorn_percentages(denominator = "col") %>%  # converte para proporções com a coluna `denominator`
  adorn_pct_formatting() %>%                  # converte proporções para porcentagens
  adorn_ns(position = "front") %>%            # mostrar como: "count (percent)"
  adorn_title(                                # ajustar título
    row_name = "Age Category",
    col_name = "Gender")
```

                          Gender                            
     Age Category              f              m          NA_
              0-4   640  (22.8%)   416  (14.8%)  39  (14.0%)
              5-9   641  (22.8%)   412  (14.7%)  42  (15.1%)
            10-14   518  (18.5%)   383  (13.7%)  40  (14.4%)
            15-19   359  (12.8%)   364  (13.0%)  20   (7.2%)
            20-29   468  (16.7%)   575  (20.5%)  30  (10.8%)
            30-49   179   (6.4%)   557  (19.9%)  18   (6.5%)
            50-69     2   (0.1%)    91   (3.2%)   2   (0.7%)
              70+     0   (0.0%)     5   (0.2%)   1   (0.4%)
             <NA>     0   (0.0%)     0   (0.0%)  86  (30.9%)
            Total 2,807 (100.0%) 2,803 (100.0%) 278 (100.0%)

Para adicionar linhas de totais mais complexas que envolvam estatísticas resumidas diferentes de *somas*, ver [esta seção da página Tabelas Descritivas](tables_descriptive.llms.md#tbl_dplyr_totals).

## 13.6 Agrupoando por data

Ao agrupar os dados por data, você deve ter (ou criar) uma coluna para a unidade de data de interesse - por exemplo “dia”, “epiweek”, “mês”, etc. Você pode fazer esta coluna utilizando `floor_date()` from **lubridate**, como explicado na seção [Semanas Epidemiológicas](dates.llms.md#dates_epi_wks) da página [Trabalhando com datas](dates.llms.md). Uma vez que você tenha esta coluna, você pode utilizar `count()` from **dplyr**\* para agrupar as linhas por esses valores de data únicos e obter contagens agregadas.

Uma etapa adicional comum para situações de datas, é “preencher” quaisquer datas na seqüência que não estejam presentes nos dados. Utilize `complete()` do **tidyr**\* para que a série de datas agregadas seja *completa* incluindo *todas as unidades de data possíveis* dentro do intervalo. Sem esta etapa, uma semana sem casos reportados pode não aparecer em seus dados!

Dentro de `complete()` você *define* sua coluna de datas como uma *seqüência* de datas `seq.Date()` do mínimo para o máximo - assim, as datas são expandidas. Por padrão, os valores de contagem de casos em qualquer nova linha “expandida” serão `NA`. Você pode defini-los como 0 utilizando o `fill =` argumento de `complete()`, que espera uma lista nomeada (se sua coluna de contagem for chamada `n`, forneça `fill = list(n = 0)`. Veja \`?complete’ para detalhes e a página [Trabalhando com datas](dates.llms.md#dates_epi_wks) para um exemplo.

### Os casos da Linelist em dias

Aqui está um exemplo de agrupamento de casos em dias *sem* utilizar a função `complete()`. Observe que as primeiras linhas saltam as datas sem casos.

``` r
daily_counts <- linelist %>% 
  drop_na(date_onset) %>%        # remove casos que faltam date_onset
  count(date_onset)              # conta o número de linhas poro data única 
```

Abaixo nós adicionamos o comando `complete()` para assegurar que todos os dias estão representados.

``` r
daily_counts <- linelist %>% 
  drop_na(date_onset) %>%                 # remove casos em que faltam date_onset
  count(date_onset) %>%                   # conta o número de linhas poro data única
  complete(                               # assegura que todos os dias aparecem 
    date_onset = seq.Date(                # re-define a coluna data como uma sequencia diária
      from = min(date_onset, na.rm=T), 
      to = max(date_onset, na.rm=T),
      by = "day"),
    fill = list(n = 0))                   # configura as linhas adicionadas para apresentar 0 e na coluna n  (não NAcomo no padrão) 
```

### Casos Linelist em semanas

O mesmo princípio pode ser aplicado durante semanas. Primeiro cria-se uma nova coluna que é a semana do caso utilizando `floor_date()` com `unit = "week"`. Em seguida, utilize `count()` como acima para obter contagens semanais de casos. Termine com `complete()` para garantir que todas as semanas sejam representadas, mesmo que não contenham casos.

``` r
# Mostrar dados por contagens semanais
weekly_counts <- linelist %>% 
  drop_na(date_onset) %>%                 # remove casos em que está faltando date_onset
  mutate(week = lubridate::floor_date(date_onset, unit = "week")) %>%  # nova coluna com a data 
  count(week) %>%                         #  agrupa dados por semana e conta 
  complete(                               # assegura que todos as semanas aparencem 
    week = seq.Date(                      # redefine a coluna data como uma sequência completa
      from = min(week, na.rm=T), 
      to = max(week, na.rm=T),
      by = "week"),
    fill = list(n = 0))                   # configura as linhas adicionadas para apresentar 0 e na coluna n  (não NAcomo no padrão) 
```

Aqui estão as 50 primeiras linhas do dataframe resultante:

### Casos da Linelist em meses

Para agregar os casos em meses, novamente utilize `floor_date()` do pacote **lubridate**, mas com o argumento `unit = "months"`. Isto arredonda cada data até o dia 1 de seu mês. A saída será classe Data. Observe que no passo `complete()` também utilizamos `by = "months"`.

``` r
# Mostrar dados para contagens mensais
monthly_counts <- linelist %>% 
  drop_na(date_onset) %>% 
  mutate(month = lubridate::floor_date(date_onset, unit = "months")) %>%  # nova colua com o 1 mês do `onset` 
  count(month) %>%                          # conta casos por mês
  complete(
    month = seq.Date(
      min(month, na.rm=T),     # inclui todos os meses mesmo os sem casos reportados 
      max(month, na.rm=T),
      by="month"),
    fill = list(n = 0))
```

### Contagens diárias em semanas

Para agregar as contagens diárias em contagens semanais, utilize `floor_date()` como acima. Entretanto, utilize `group_by()` e `summarize()` em vez de `count()` porque você precisa `sum()` contar casos diários em vez de apenas contar o número de filas por semana.

#### Contagens diárias em meses

Para agregar as contagens diárias em contagens de meses, utilize `floor_date()` com `unit = "month"` (mês) como acima. Entretanto, utilize `group_by()` e `summarize()` em vez de `count()` porque você precisa `sum()` contar casos diários em vez de apenas contar o número de filas por mês.

## 13.7 Organizando dados agrupados

Utilizando o verbo `arrange()`do **dplyr** para ordenar as linhas em um quadro de dados se comporta da mesma forma quando os dados são agrupados, *a menos que* você defina o argumento `.by_group =TRUE`. Neste caso, as linhas são ordenadas primeiro pelas colunas de agrupamento e depois por quaisquer outras colunas que você especificar para `arrange()`.

## 13.8 Filtrando dados agrupados

### `filter()`

Quando aplicadas em conjunto com funções que avaliam o dataframe (como `max()`, `min()`, `mean()`), estas funções serão agora aplicadas aos grupos. Por exemplo, se você quiser filtrar e manter linhas onde os pacientes estão acima da mediana de idade, isto agora será aplicado por grupo - filtrando para manter linhas acima da mediana de idade do *grupo*.

### Linhas de corte por grupo

A função `slice()` (literalmente: fatiar) do pacote **dplyr** , que [filtra linhas com base em sua posição](https://dplyr.tidyverse.org/reference/slice.html) nos dados, também pode ser aplicada por grupo. Lembre-se de levar em conta a ordenação dos dados dentro de cada grupo para obter a “fatia” desejada.

Por exemplo, para recuperar apenas as últimas 5 admissões de cada hospital:

1.  Agrupar a lineliste por coluna “hospital”.  
2.  Organizar os registros da mais recente à mais antiga `date_hospitalisation` (data de hospitalização) *em cada grupo hospitalar*.  
3.  Divide para recuperar as 5 primeiras fileiras de cada hospital

``` r
linelist %>%
  group_by(hospital) %>%
  arrange(hospital, date_hospitalisation) %>%
  slice_head(n = 5) %>% 
  arrange(hospital) %>%                            # para visualizar
  select(case_id, hospital, date_hospitalisation)  # para visualizar
```

    # A tibble: 30 × 3
    # Groups:   hospital [6]
       case_id hospital          date_hospitalisation
       <chr>   <chr>             <date>              
     1 20b688  Central Hospital  2014-05-06          
     2 d58402  Central Hospital  2014-05-10          
     3 b8f2fd  Central Hospital  2014-05-13          
     4 acf422  Central Hospital  2014-05-28          
     5 275cc7  Central Hospital  2014-05-28          
     6 d1fafd  Military Hospital 2014-04-17          
     7 974bc1  Military Hospital 2014-05-13          
     8 6a9004  Military Hospital 2014-05-13          
     9 09e386  Military Hospital 2014-05-14          
    10 865581  Military Hospital 2014-05-15          
    # ℹ 20 more rows

`slice_head()` - selecciona n linhas do topo  
`slice_tail()` - selecciona n linhas do final `slice_sample()` - seleciona aleatoriamente n linhas `slice_min()` - seleciona n linhas com os valores mais altos da coluna `order_by =`, use `with_ties = TRUE` para manter os vínculos `slice_max()` - seleciona os menores valores da coluna `order_by =` column, , use `with_ties = TRUE` para manter os vínculos

Veja a página [Eliminando duplicidades](deduplication.llms.md) para meis exemplos e detalhes de `slice()`.

### Filtrar por tamanho do grupo

A função `add_count()` adiciona uma coluna `n` aos dados originais dando o número de linhas no grupo daquela linha.

Mostrado abaixo, `add_count()` é aplicado à coluna `hospital`, assim os valores na nova coluna `n` refletem o número de linhas no grupo hospitalar. Observe como os valores na coluna `n` são repetidos. No exemplo abaixo, o nome da coluna `n` poderia ser alterado utilizando `name =` dentro de `add_count()`. Para fins de demonstração, reorganizamos as colunas com `select()`.

``` r
linelist %>% 
  as_tibble() %>% 
  add_count(hospital) %>%          # adiciona "número de linhas adimitidas no mesmo hospital que o dessa linha" 
  select(hospital, n, everything())
```

    # A tibble: 5,888 × 31
       hospital                       n case_id generation date_infection date_onset
       <chr>                      <int> <chr>        <dbl> <date>         <date>    
     1 Other                        885 5fe599           4 2014-05-08     2014-05-13
     2 Missing                     1469 8689b7           4 NA             2014-05-13
     3 St. Mark's Maternity Hosp…   422 11f8ea           2 NA             2014-05-16
     4 Port Hospital               1762 b8812a           3 2014-05-04     2014-05-18
     5 Military Hospital            896 893f25           3 2014-05-18     2014-05-21
     6 Port Hospital               1762 be99c8           3 2014-05-03     2014-05-22
     7 Missing                     1469 07e3e8           4 2014-05-22     2014-05-27
     8 Missing                     1469 369449           4 2014-05-28     2014-06-02
     9 Missing                     1469 f393b4           4 NA             2014-06-05
    10 Missing                     1469 1389ca           4 NA             2014-06-05
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_hospitalisation <date>, date_outcome <date>,
    #   outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>, age_years <dbl>,
    #   age_cat <fct>, age_cat5 <fct>, lon <dbl>, lat <dbl>, infector <chr>,
    #   source <chr>, wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>,
    #   chills <chr>, cough <chr>, aches <chr>, vomit <chr>, temp <dbl>,
    #   time_admission <chr>, bmi <dbl>, days_onset_hosp <dbl>

Torna-se então fácil filtrar para linhas de casos que foram hospitalizados em um hospital “pequeno”, digamos, um hospital que admitiu menos de 500 pacientes:

``` r
linelist %>% 
  add_count(hospital) %>% 
  filter(n < 500)
```

## 13.9 Criando novas variáveis (mutate) em dados agrupados

Para manter todas as colunas e linhas (não resumir) e *adicionar uma nova coluna contendo estatísticas de grupo*, utilizar `mutate()` após `group_by()` em vez de `summarise()`.

Isto é útil se você quiser estatísticas de grupo no conjunto de dados original \* com todas as outras colunas presentes\* - por exemplo, para cálculos que comparam uma linha com seu grupo.

Por exemplo, este código abaixo calcula a diferença entre o atraso de para a admissão de uma observação e o atraso mediano para seu hospital. As etapas são:

1.  Agrupar os dados por hospital  
2.  Utilize a coluna `days_onset_hosp` (atraso à hospitalização) para criar uma nova coluna contendo o atraso médio no hospital para *aquela linha*.  
3.  Calcular a diferença entre as duas colunas

Nós usamos a função `select()` para selecionar apenas certas colunas a serem exibidas, para fins de demonstração.

``` r
linelist %>% 
  # agrupando dados por hospital (sem mudanças na linelist ainda)
  group_by(hospital) %>% 
  
  # novas colunas
  mutate(
    # quantidades de dias média para admissão por hospital (arredondado para 1 decimal)
    group_delay_admit = round(mean(days_onset_hosp, na.rm=T), 1),
    
    # diferença entre o atraso daquela observação e o atraso medio do hospital (arredondado para 1 decimal)
    diff_to_group     = round(days_onset_hosp - group_delay_admit, 1)) %>%
  
  # seleciona alguma linhas apenas - para fim de demostração/visualização  
  select(case_id, hospital, days_onset_hosp, group_delay_admit, diff_to_group)
```

    # A tibble: 5,888 × 5
    # Groups:   hospital [6]
       case_id hospital              days_onset_hosp group_delay_admit diff_to_group
       <chr>   <chr>                           <dbl>             <dbl>         <dbl>
     1 5fe599  Other                               2               2             0  
     2 8689b7  Missing                             1               2.1          -1.1
     3 11f8ea  St. Mark's Maternity…               2               2.1          -0.1
     4 b8812a  Port Hospital                       2               2.1          -0.1
     5 893f25  Military Hospital                   1               2.1          -1.1
     6 be99c8  Port Hospital                       1               2.1          -1.1
     7 07e3e8  Missing                             2               2.1          -0.1
     8 369449  Missing                             1               2.1          -1.1
     9 f393b4  Missing                             1               2.1          -1.1
    10 1389ca  Missing                             2               2.1          -0.1
    # ℹ 5,878 more rows

## 13.10 Selecionar em dados agrupados

O verbo `select()` funciona em dados agrupados, mas as colunas de agrupamento são sempre incluídas (mesmo se não mecionadas explicitamente em `select()`). Se você não quiser essas colunas, precisa usarprimeiro a função `ungroup()` para desagrupá-los.

## 13.11 Recursos

Aqui estão alguns recursos úteis para mais informações.

Você pode aplicar funções de resumo em dados agrupados; ver a [“cheat sheet” (cola) de transformação de dados do RStudio.](https://github.com/rstudio/cheatsheets/blob/master/data-transformation.pdf)

A página do Data Carpentry [**dplyr**](https://datacarpentry.org/R-genomics/04-dplyr.html)  
As páginas de referência do **tidyverse** em [group_by()](https://dplyr.tidyverse.org/reference/group_by.html) and [grouping](https://dplyr.tidyverse.org/articles/grouping.html)

Esta página em [Manipulação de dados](https://itsalocke.com/files/DataManipulationinR.pdf)

[Resumindo com condicionamento no dplyr](https://stackoverflow.com/questions/23528862/summarize-with-conditions-in-dplyr)
