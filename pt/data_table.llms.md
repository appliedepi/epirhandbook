# 50  Data Table

Este livro centra-se nos “verbos” (funções) do pacote **dplyr** e no operador pipe `%>%` do pacote **magrittr** como método para limpar e agrupar dados, mas o pacote **data.table** oferece um método alternativo que você poderá incorporar em seu uso do R.

## 50.1 Introdução ao Data Table

Uma tabela de dados (data table) é uma estrutura de dados bidimensional como um data frame, que permite a realização de operações complexas de agrupamento. A sintaxe data.table é estruturada para que as operações possam ser realizadas em linhas, colunas e grupos.

A estrutura é **DT\[i, j, by\]**, separada por 3 partes; os argumentos **i, j** e **by**. O argumento **i** permite filtrar linhas, o argumento **j** permite operar em colunas e o argumento **by** permite operar em colunas por grupos.

Esta página abordará os seguintes tópicos:

- Importação de dados e uso das funções `fread()` e `fwrite()`
- Filtragem de linhas utilizando o argumento **i**
- Utilização das funções de ajuda `%like%`, `%chin%` e `%between%`
- Seleção e operação com colunas utilizando o argumento **j**
- Operar por grupos utilizando o argumento **by**
- Adição de dados e atualização de data tables (tabelas de dados) utilizando `:=`

## 50.2 Carregar pacotes e importar dados

### Carregar pacotes

Utilizando a função `p_load()` de **pacman**, carregamos (e instalamos, se necessário) os pacotes necessários para esta análise.

``` r
pacman::p_load(
  data.table, # para agrupar e limpar dados
  tidyverse   # permite o uso da função pipe (%>%) neste capítulo
  ) 
```

### Importar dados

Esta página vai explorar algumas das funções centrais do pacote **data.table** recorrendo à mesma linelist de casos utilizada ao longo do manual.

Importamos o conjunto de dados dos casos de uma epidemia simulada de Ébola. Carregue diretamente com `appliedepidata::get_data(name = "linelist_cleaned_excel")` (consulte a página [Baixar manual e dados](download.llms.md) para mais detalhes). Em seguida, utilizamos `data.table()` para converter o quadro de dados em um data table.

``` r
linelist <- appliedepidata::get_data(name = "linelist_cleaned_excel") %>% data.table()
```

A função `fread()` é utilizada para importar arquivos delimitados por caracteres, como arquivos .csv, diretamente para um formato de data table. Esta função, e sua contraparte `fwrite()`, utilizada para escrever data.tables como arquivos delimitados, são opções muito rápidas e computacionalmente eficientes para grandes bancos de dados.

As primeiras 20 linhas da `linelist`:

Comandos do R Base como `dim()` que são utilizados para data frames também podem ser utilizados para data tables (tabelas de dados).

``` r
dim(linelist) #dispõe o número de linhas e colunas na tabela de dados
```

    [1] 5888   30

## 50.3 O argumento i: selecionando e filtrando linhas

Relembrando a estrutura **DT\[i, j, by\]**, podemos filtrar linhas usando números de linha ou expressões lógicas. O argumento i é o primeiro; portanto, a sintaxe **DT\[i\]** ou **DT\[i,\]** pode ser usada.

O primeiro exemplo recupera as primeiras 5 linhas do data table, o segundo exemplo retorna casos com 18 anos ou mais, e o terceiro exemplo gera um subconjunto de casos com 18 anos ou mais, mas não diagnosticados no Hospital Central:

``` r
linelist[1:5] # retorna da 1ª à 5ª fileira
linelist[age >= 18] # subconjunto de casos com 18 anos ou mais
linelist[age >= 18 & hospital != "Central Hospital"] # conjunto de casos com idade igual ou superior a 18 anos, mas não diagnosticados no Hospital Central
```

O uso de .N no argumento i representa o número total de linhas no data table. Isto pode ser usado para criar subconjuntos com base nos números das linhas:

``` r
linelist[.N] # retorna a última linha
linelist[15:.N] # retorna da 15ª à última linha
```

### Funções de ajuda para filtragem

Data tables (tabelas de dados) utilizam funções de auxílio que facilitam a filtragem linhas. A função `%like%` é utilizada para corresponder a um padrão em uma coluna, `%chin%` é utilizada para corresponder a um caractere específico, e a função `%between%` é utilizada para corresponder a colunas numéricas dentro de uma faixa pré-especificada.

Nos exemplos a seguir, nós: \* filtramos linhas em que a variável hospital contém “Hospital” \* filtramos linhas em que o resultado é “Recover” ou “Death” \* filtramos linhas em que a faixa etária (age) é 40-60 anos

``` r
linelist[hospital %like% "Hospital"] # filtrar linhas em que a variável hospital contém "Hospital"
linelist[outcome %chin% c("Recover", "Death")] # filtrar linhas em que o resultado (outcome) é "Recover" ou "Death"
linelist[age %between% c(40, 60)] # filtrar linhas em que a faixa etária (age) é de 40-60 anos

#%between% deve receber um vetor de comprimento 2, enquanto %chin% pode receber vetores de comprimento >= 1
```

## 50.4 O argumento j: seleção e cálculo nas colunas

Usando a estrutura **DT\[i, j, by\]**, podemos selecionar colunas usando números ou nomes. O argumento **j** é o segundo; portanto, a sintaxe **DT\[, j\]** é usada. Para facilitar os cálculos no argumento **j**, a coluna é envolvida utilizando `list()` ou `.()`.

### Seleção de colunas

O primeiro exemplo recupera a primeira, terceira e quinta colunas do data table, o segundo exemplo seleciona todas as colunas, exceto as colunas gender, age, wt_kg e ht_cm. O terceiro exemplo utiliza o envelope `.()` para selecionar as colunas **case_id** e **outcome**.

``` r
linelist[ , c(1,3,5)]
linelist[ , -c("gender", "age", "wt_kg", "ht_cm")]
linelist[ , list(case_id, outcome)] #linelist[ , .(case_id, outcome)] funciona tão bem quanto
```

### Cálculo nas colunas

Combinando os argumentos **i** e **j** é possível filtrar linhas e calcular colunas. Usar **.N** no argumento **j** também representa o número total de linhas no data table e pode ser útil para retornar o número de linhas após a filtragem.

Nos exemplos a seguir, nós: \* contamos o número de casos que permaneceram mais de 7 dias no hospital \* calculamos a idade média dos casos que vieram a óbito no hospital militar \* calculamos o desvio padrão, mediana, e média da idade dos casos que se recuperaram no hospital central

``` r
linelist[days_onset_hosp > 7 , .N]
```

    [1] 189

``` r
linelist[hospital %like% "Military" & outcome %chin% "Death", .(mean(age, na.rm = T))] #na.rm = T remove valores N/A
```

            V1
         <num>
    1: 15.9084

``` r
linelist[hospital == "Central Hospital" & outcome == "Recover", 
                 .(mean_age = mean(age, na.rm = T),
                   median_age = median(age, na.rm = T),
                   sd_age = sd(age, na.rm = T))] # esta sintaxe não utiliza as funções de ajuda, mas funciona tão bem quanto
```

       mean_age median_age   sd_age
          <num>      <num>    <num>
    1: 16.85185         14 12.93857

Lembre-se que usar o envelope .() no argumento j facilita o cálculo, retorna um data table e permite a nomeação de colunas.

## 50.5 The by argument: computing by groups

O argumento **by** é o terceiro argumento na estrutura **DT\[i, j, by\]**. Ele aceita tanto um vetor de caracteres quanto a sintaxe `list()` ou `.()`. A utilização da sintaxe `.()` no argumento **by** permite renomear a coluna imediatamente.

Nos exemplos a seguir, nós: \* agrupamos o número de casos por hospital \* calculamos a altura média e o peso dos casos com 18 anos ou mais, de acordo com o sexo e desfecho (se eles se recuperaram ou vieram a óbito) \* contamos o número de casos com tempo de internação \> 7 dias, de acordo com o mês e o hospital em que foram admitidos

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
                             mean_ht = mean(ht_cm, na.rm = T)), .(gender, outcome)] #NAs representam as categorias em que os dados estão faltando
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

Data.table também permite expressões em serquência:

``` r
linelist[, .N, .(hospital)][order(-N)][1:3] #1º seleciona todos os casos por hospital, 2º ordena os casos em ordem decrescente, 3º seleciona um subconjunto dos 3 hospitais com o maior número de casos
```

                hospital     N
                  <char> <int>
    1:     Port Hospital  1762
    2:           Missing  1469
    3: Military Hospital   896

Nestes exemplos, estamos seguindo a suposição de que uma linha no data table é igual a um novo caso, e assim podemos usar o **.N** para representar o número de linhas no data table. Outra função útil para representar o número de casos únicos é `uniqueN()`, que retorna o número de valores únicos em uma determinada entrada. Como ilustrado aqui:

``` r
linelist[, .(uniqueN(gender))] # lembre que o envelope .() no argumento j retorna um data table
```

          V1
       <int>
    1:     3

A resposta é 3, pois os valores únicos na coluna de gênero são m, f e N/A. Compare com a função `unique()` do R Base, que retorna todos os valores únicos em uma determinada entrada:

``` r
linelist[, .(unique(gender))]
```

           V1
       <char>
    1:      m
    2:      f
    3:   <NA>

Para encontrar o número de casos únicos em um determinado mês, escrevemos o seguinte:

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

## 50.6 Adicionar e atualizar data tables (tabelas de dados)

O operador `:=` é utilizado para adicionar ou atualizar dados em um data table. A adição de colunas pode ser feita das seguintes maneiras:

``` r
linelist[, adult := age >= 18] # adiciona uma coluna
linelist[, c("child", "wt_lbs") := .(age < 18, wt_kg*2.204)] #para adicionar múltiplas colunas é necessário usar as sintaxes c(""), list() ou .() syntax
linelist[, `:=` (bmi_in_range = (bmi > 16 & bmi < 40),
                         no_infector_source_data = is.na(infector) | is.na(source))] #Este método utiliza `:=` como um operador funcional 
linelist[, adult := NULL] # deleta a coluna
```

Outras agregações complexas estão além do objetivo deste capítulo introdutório, mas a ideia é fornecer uma alternativa popular e viável ao **dplyr** para agrupamento e limpeza de dados. O pacote **data.table** é um grande pacote que permite um código limpo e legível.

## 50.7 Recursos

Aqui estão alguns recursos úteis para maiores informações: \* https://cran.r-project.org/web/packages/data.table/vignettes/datatable-intro.html \* https://github.com/Rdatatable/data.table \* https://s3.amazonaws.com/assets.datacamp.com/img/blog/data+table+cheat+sheet.pdf \* https://www.machinelearningplus.com/data-manipulation/datatable-in-r-complete-guide/ \* https://www.datacamp.com/community/tutorials/data-table-r-tutorial

Você pode realizar qualquer função de resumo sobre dados agrupados; veja a Cheat Sheet para mais informações: https://s3.amazonaws.com/assets.datacamp.com/blog_assets/datatable_Cheat_Sheet_R.pdf
