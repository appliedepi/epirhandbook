# 44  Escrevendo funções

## 44.1 Preparação

### Carregar pacotes

Este “chuk” (pedaço) de código mostra o carregamento de pacotes necessários para as análises. Neste manual, enfatizamos `p_load()` de **pacman**, que instala o pacote, se necessário, *e* carrega ele para ser utilizado. Você também pode carregar pacotes instalados com `library()` do R **base**. Veja em [Introdução ao R](basics.llms.md) para mais informações sobre pacotes R.

### Importar dados

Importamos os dados de casos de uma simulação de epidemia de Ebola. Se desejar fazer o download dos dados para seguir passo a passo, veja as instruções na página [Baixar livro e dados](download.llms.md). O conjunto de dados é importado usando a função `import()` do pacote **rio**. Consulte a página [Importar e exportar](importing.llms.md) para várias maneiras de importar dados.

Também usaremos na última parte desta página alguns dados sobre a gripe H7N9 de 2013.

## 44.2 Funções

As funções são úteis na programação, pois permitem tornar os códigos mais fáceis de entender, de alguma forma mais curtos e menos sujeitos a erros (dado que não haja erros na própria função).

Se você chegou até aqui neste manual, significa que encontrou inúmeras funções, uma vez que no R toda operação é uma chamada de função `+, for, if, [, $, { …`. Por exemplo `x + y` é o mesmo que `'+'(x, y)`

R é uma das linguagens que oferece a maior possibilidade de trabalhar com funções e dar ferramentas suficientes para que o usuário as escreva facilmente. Não devemos pensar nas funções como fixas no topo ou no final da cadeia de programação, o R oferece a possibilidade de usá-las como se fossem vetores e até mesmo dentro de outras funções, listas …

Existem muitos recursos muito avançados sobre programação de funções e só daremos aqui uma visão para ajudá-lo a começar com breves exemplos práticos. Em seguida, você é incentivado a visitar os links de referências para ler mais sobre o assunto.

## 44.3 Por que você usaria uma função?

Antes de responder a esta pergunta, é importante observar que você já recebeu dicas para escrever suas primeiras funções R na página [Iteração, loops e listas](iteration.llms.md) deste manual. Na verdade, o uso de “if / else” e loops costuma ser uma parte central de muitas de nossas funções, pois ajudam a ampliar a aplicação do nosso código, permitindo várias condições, ou a iterar códigos para tarefas repetidas.

- Estou repetindo várias vezes o mesmo bloco de código para aplicá-lo a uma variável ou dado diferente?

- Livrar-se dele irá encurtar substancialmente meu código e torná-lo executado mais rápido?

- É possível que o código que escrevi seja usado novamente, mas com um valor diferente em muitos lugares do código?

Se a resposta a uma das perguntas anteriores for “SIM”, provavelmente você precisará escrever uma função

## 44.4 Como o R cria funções?

As funções em R têm três componentes principais:

- `formals()`, que é a lista de argumentos que controla como podemos rodar a função

- `body()`, que é o código dentro da função, ou seja, entre colchetes ou após o parêntese, dependendo de como o escrevemos

e,

- `environment()` que ajudará a localizar as variáveis da função e determina como a função encontra o valor.

Depois de criar sua função, você pode verificar cada um desses componentes chamando a função associada.

## 44.5 Sintaxe e estrutura básicas

- Uma função precisará ser nomeada corretamente para que sua tarefa seja facilmente compreensível assim que lermos seu nome. Na verdade, este já é o caso com a maioria da arquitetura do R base. Funções como `mean()`, `print()`, `summary()` têm nomes que são muito diretos

- Uma função precisará de argumentos, como os dados nos quais trabalhar e outros objetos que podem ser valores estáticos entre outras opções

- E, finalmente, uma função fornecerá uma saída com base em sua tarefa principal e nos argumentos fornecidos. Normalmente usaremos funções embutidas como `print()`, `return()` … para produzir a saída. A saída pode ser um valor lógico, um número, um caractere, um quadro de dados … em suma, qualquer tipo de objeto R.

Basicamente, esta é a composição de uma função:

``` r
function_name <- function(argument_1, argument_2, argument_3){
  
           function_task
  
           return(output)
}
```

Podemos criar nossa primeira função que será chamada `contain_covid19()`.

``` r
contain_covid19 <- function(barrier_gest, wear_mask, get_vaccine){
  
                            if(barrier_gest == "yes" & wear_mask == "yes" & get_vaccine == "yes" ) 
       
                            return("success")
  
  else("please make sure all are yes, this pandemic has to end!")
}
```

Podemos então verificar os componentes de nossa função recém-criada.

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

Agora vamos testar nossa função. Para rodar nossa função escrita, você a usa da mesma forma que usa todas as funções R, ou seja, escrevendo o nome da função e adicionando os argumentos necessários.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "yes")
```

    [1] "success"

Podemos escrever novamente o nome de cada argumento por razões de precaução. Mas o código deve funcionar mesmo sem especificá-los, uma vez que o R tem na memória o posicionamento de cada argumento. Portanto, desde que você coloque os valores dos argumentos na ordem correta, você pode pular a escrita dos nomes dos argumentos ao rodar as funções.

``` r
contain_covid19("yes", "yes", "yes")
```

    [1] "success"

Então, vamos ver o que acontece se um dos valores for `"no"` ou **diferente de** `"yes"`.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "no")
```

    [1] "please make sure all are yes, this pandemic has to end!"

Se fornecermos um argumento que não é reconhecido, obteremos um erro:

``` r
contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", get_vaccine = "no")
```

`Error in conter_covid19(distanciamento_social = "às vezes", usar_mascara = "sim", : could not find function "conter_covid19"`

***NOTA:*** Algumas funções (na maioria das vezes muito curtas e diretas) podem não precisar de um nome e podem ser usadas diretamente em uma linha de código, ou dentro de outra função, para fazer tarefa rápida. Elas são chamadas de **funções anônimas**.

Por exemplo, abaixo está uma primeira função anônima que mantém apenas variáveis de caracteres no conjunto de dados.

``` r
linelist %>% 
  dplyr::slice_head(n=10) %>%  # Equivalente à função "head" do R base, que retorna as primeiras n observações do conjunto de dados
  select(function(x) is.character(x)) 
```

Outra função poderia selecionar uma a cada duas observações do nosso conjunto de dados. Pode ser relevante quando temos dados longitudinais com muitos registros por paciente, por exemplo, após ter solicitado por data ou visita). Nesse caso, a função apropriada para escrever fora do dplyr seria `function (x) (x%%2 == 0)` para aplicar ao vetor contendo todos os números de linha.

``` r
linelist %>%   
   slice_head(n=20) %>% 
   tibble::rownames_to_column() %>% # Adiciona índices de cada registro como rownames para ver claramente a seleção final
   filter(row_number() %%2 == 0)
```

Um possível código do R base para a mesma tarefa seria:

``` r
linelist_firstobs <- head(linelist, 20)

linelist_firstobs[base::Filter(function(x) (x%%2 == 0), seq(nrow(linelist_firstobs))),]
```

***CUIDADO:*** Se por um lado é verdade que o uso de funções pode nos ajudar com nosso código, também pode ser demorado escrever ou mesmo consertá-las se não tiver sido pensada completamente, escrita de forma adequada ou estiver retornando erros como resultado. Por esse motivo, geralmente é recomendado escrever primeiro o código R, certificar-se de que ele faz o que pretendemos fazer e, em seguida, transformá-lo em uma função com seus três componentes principais, conforme listado acima.

## 44.6 Exemplos

### Retorna tabelas de proporção para várias colunas

Sim, já temos funções interessantes em muitos pacotes, permitindo resumir informações de uma forma muito fácil e agradável. Mas ainda vamos tentar fazer o nosso próprio, em nossos primeiros passos para nos acostumarmos a escrever funções.

Neste exemplo, queremos mostrar como escrever uma função simples evitaria que você copiasse e colasse o mesmo código várias vezes.

``` r
proptab_multiple <- function(my_data, var_to_tab){
  
  # Grava o nome de cada variável de interesse antes de fazer a tabulação
  print(var_to_tab)

  with(my_data,
       rbind( # Vincula os resultados das duas funções seguintes por linha
        # Tabula a variável de interesse: fornece apenas números
          table(my_data[[var_to_tab]], useNA = "no"),
          # Calcula as proporções para cada variável de interesse e arredonda o resultado para 2 decimais
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

***DICA:*** Como mostrado acima, é muito importante comentar suas funções como você faria para a programação geral. Lembre-se de que o objetivo de uma função é deixar um código pronto para ser lido, mais curto e mais eficiente. Então, deve-se ser capaz de entender o que a função faz apenas lendo seu nome e encontrar mais detalhes lendo os comentários.

Uma segunda opção é usar a função dentro de outra, por meio de um loop para fazer o processo de uma vez:

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

Uma maneira mais simples poderia ser usar o “apply” do R base em vez de um “for loop”, conforme abaixo:

***DICA:*** R é frequentemente definido como uma linguagem de programação funcional e quase sempre que você executa uma linha de código, está usando algumas funções integradas. Um bom hábito para ficar mais confortável com funções de escrita é frequentemente dar uma olhada interna em como as funções básicas que você usa diariamente são criadas. O atalho para isso é selecionar o nome da função e clicar em`Ctrl+F2` ou `fn+F2` ou `Cmd+F2` (dependendo do seu computador) .

## 44.7 Usando **purrr**: Escrevendo funções que podem ser aplicadas iterativamente

### Modificar a classe de várias colunas em um conjunto de dados

Digamos que muitas variáveis do tipo caractere nos dados originais da `linelist` precisem ser alteradas para “fator” para fins de análise e plotagem. Em vez de repetir a etapa várias vezes, podemos apenas usar `lapply()` para fazer a transformação de todas as variáveis envolvidas em uma única linha de código.

***CUIDADO:*** `lapply()` retorna uma lista, portanto, seu uso pode exigir uma modificação adicional como última etapa.

O mesmo passo pode ser feito usando a função `map_if()` do pacote **purrr**

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

### Produzir gráficos iterativamente para diferentes níveis de uma variável

Vamos produzir um gráfico de pizza para observar a distribuição dos resultados dos pacientes na China durante o surto de H7N9 para cada província. Em vez de repetir o código para cada um deles, apenas aplicaremos uma função que criaremos.

``` r
# Opções precisas para o uso do highchart
options(highcharter.theme =   highcharter::hc_theme_smpl(tooltip = list(valueDecimals = 2)))


# Criar uma função chamada "chart_outcome_province" que leva como argumento o conjunto de dados e o nome da província para a qual plotar a distribuição do resultado.

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

### Produzir tabelas iterativamente para diferentes níveis de uma variável

Aqui criaremos três indicadores para resumir em uma tabela e gostaríamos de produzir esta tabela para cada uma das províncias. Nossos indicadores são o atraso entre o início e a internação, o percentual de recuperação e a idade mediana dos casos.

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

# Junte os três conjuntos de dados de indicadores

table_indic_all <- indic_1 %>% 
  dplyr::left_join(indic_2, by = "province") %>% 
        left_join(indic_3, by = "province")


# Imprima os indicadores em uma flextable


print_indic_prov <-  function(table_used, prov){
  
  # Primeiro, transforme um pouco o quadro de dados para facilitar a visualização
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

## 44.8 Dicas e práticas recomendadas para o bom funcionamento das funções

A programação de funções visa facilitar o código e facilitar sua leitura. Deve produzir o contrário. As dicas abaixo irão ajudá-lo a ter um código limpo e fácil de ler.

### Nomenclatura e sintaxe

- Evite usar caracteres que poderiam facilmente ter sido contemplados em outras funções já existentes em seu ambiente

- Recomenda-se que o nome da função seja curto e fácil de entender

- É preferível usar verbos como o nome da função e substantivos para os nomes dos argumentos.

### Nomes de coluna e avaliação organizada

Se você quiser saber como fazer referência a *nomes de coluna* fornecidos em seu código como argumentos, leia [tidyverse programming guidance](https://dplyr.tidyverse.org/articles/programming.html).Entre os tópicos cobertos estão *avaliação arrumada* (de *tidy evaluation*) e uso de *embrace* `{ }` “Colchetes duplos”

Por exemplo, aqui está um esqueleto rápido de código modelo da página do tutorial mencionado acima:

``` r
var_summary <- function(data, var) {
  data %>%
    summarise(n = n(), min = min({{ var }}), max = max({{ var }}))
}
mtcars %>% 
  group_by(cyl) %>% 
  var_summary(mpg)
```

### Teste e tratamento de erros

Quanto mais complicada a tarefa de uma função, maior a possibilidade de erros. Portanto, às vezes é necessário adicionar alguma verificação na função para ajudar a entender rapidamente de onde vem o erro e encontrar uma maneira de corrigi-lo.

- Pode ser mais do que recomendado introduzir uma verificação sobre a falta de um argumento usando `missing(argumento)`. Esta verificação simples pode retornar um valor “TRUE” (verdadeiro) ou “FALSE” (falso).

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

- Use `stop()` para mais erros detectáveis.

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

- Como vemos quando executamos a maioria das funções integradas, existem mensagens e avisos que podem aparecer em certas condições. Podemos integrá-los na escrita de nossas funções usando as funções `message()` e `warning()`.

- Também podemos lidar com erros usando `safely()`, que pega uma função como um argumento e a executa de maneira segura. Na verdade, a função será executada sem parar se encontrar um erro. `safely()` retorna como resultado uma **list** com dois objetos, que são os resultados e o erro “pulado”.

Podemos verificar executando primeiro a `mean()` como função e, em seguida, executando com `safely()`.

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

Como dito anteriormente, comentar bem nossos códigos já é uma boa forma de termos documentação em nosso trabalho.

## 44.9 Recursos

[link para o livro R para Ciência de Dados](https://r4ds.had.co.nz/functions.html)

[Cheatsheet (cola) em programação avançada em R](https://www.rstudio.com/wp-content/uploads/2016/02/advancedR.pdf)

[Cheatsheet (cola) do Pacote purr](https://purrr.tidyverse.org/)

[Video-ACM palesta por Hadley Wickham: A alegria da programação funcional (como map_dbl funciona)](https://youtube.videoken.com/embed/bzUmK0Y07ck)
