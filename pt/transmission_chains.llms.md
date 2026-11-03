# 37  Cadeias de Transmissão

## 37.1 Visão Geral

A ferramenta primária para manipular, analisar e visualizar dados de cadeias de transmissão e rastreamento de contatos é o pacote **epicontacts**, desenvolvido por membros do RECON. Experimente o gráfico interativo abaixo passando o mouse sobre os nós para ver mais informações, arrastando para movê-los e clicando para destacar os casos subsequentes na cadeia de transmissão.

## 37.2 Preparação

### Carregue os pacotes R

Primeiro carregue os pacotes padrão necessários para importar e manipular os dados. Neste manual, enfatizamos o uso da função `p_load()`, do \*pacman**, que instala os pacotes, caso não estejam instalados, *e* os carrega no R para utilização. Também é possível carregar pacotes instalados utilizando a função `library()`, do R** base\*\*. Para mais informações sobre os pacotes do R, veja a página [Introdução ao R](basics.llms.md).

``` r
pacman::p_load(
   rio,          # File import
   here,         # File locator
   tidyverse,    # Data management + ggplot2 graphics
   remotes       # Package installation from github
)
```

Você vai instalar a versão de desenvolvimento do **epicontacts**, que pode ser instalado diretamente do github utilizando a função `p_install_github()` do pacote **pacman**. Você precisa rodar esse comando abaixo apenas uma vez, e não todas as vezes que usar o pacote (daí em diante, você pode utilizar `p_load()` como de costume).

``` r
pacman::p_install_gh("reconhub/epicontacts@timeline")
```

### Importando os dados

Vamos importar a base de dados de casos da epidemia simulada de Ebola. Se você quiser fazer download dos dados para seguir o passo a passo, veja as instruções na página [Baixando dados do manual](download.llms.md). A base será importada utilizando a função `import()` do pacote **rio**. Veja a página sobre [Importação e exportação](importing.llms.md) para aprender várias formas de importar dados.

``` r
# import the linelist
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

As primeiras 50 linhas da linelist são mostradas abaixo. As colunas de especial interesse são `case_id`, `generation`, `infector`, e `source`.

### Criando um objeto do tipo epicontacts

Depois, precisamos criar um objeto **epicontacts**, que requer dois tipos de dados:

- uma linelist documentando casos onde colunas são variáveis e linhas correspondem a casos únicos
- uma lista de arestas definindo as ligações entre os casos com base em seus IDs únicos (esses podem ser contatos, eventos de transmissão, etc.)

Como já temos uma linelist, precisamos apenas criar a lista de arestas entre os casos, mais especificamente entre seus IDs. Podemos extrair relações de transmição da linelist ao relacionar a coluna `infector` com a coluna `case_id`. Nesse ponto podemos também adicionar “propriedades das arestas”, que seriam quaisquer variáveis que descrevem a relação entre os dois casos, e não os casos em si. Para ilustrar, vamos adicionar uma variável `location` que descreve o local do evento de transmissão, e uma variável de duração, que descreve a duração do contato em dias.

No código abaixo, a função `transmute` do **dplyr** atua de forma semelhante à `mutate`, com a diferença que ela mantém apenas as colunas que especificamos na chamada. A função `drop_na` vai filtrar quaisquer linhas cujas colunas especificadas tenham o valor `NA`; nesse caso, queremos manter apenas as linhas cujo transmissor *(infector)* é conhecido.

``` r
## gera os contatos
set.seed(1)
contacts <- linelist %>%
  transmute(
    infector = infector,
    case_id = case_id,
    location = sample(c("Community", "Nosocomial"), n(), TRUE),
    duration = sample.int(10, n(), TRUE)
  ) %>%
  drop_na(infector)
```

Agora podemos criar o objeto **epicontacts** utilizando a função `make_epicontacts`. Precisamos especificar qual coluna da linelist aponta para o identificador único dos casos, bem como quais colunas dos contatos apontam para os identificadores únicos dos casos envolvidos em cada relação. Essas relações são direcionadas pois a transmissão vai **do** (*from*) transmissor **para** (*to*) o caso, então precisamos especificar os argumentos `from` e `to` de acordo. Nós também definimos o argumento `directed` *(direcionado)* para `TRUE`, o que vai afetar as operações no futuro.

``` r
## gera o objeto epicontacts
epic <- make_epicontacts(
  linelist = linelist,
  contacts = contacts,
  id = "case_id",
  from = "infector",
  to = "case_id",
  directed = TRUE
)
```

Ao examinarmos objetos do tipo **epicontacts**, podemos ver que a coluna `case_id` na linelist foi renomeada para `id` e as colunas `case_id` e `infector` nos contatos foram renomeadas para `from` e `to`. Isso garante a consistência nas operações de manipulação, visualização e análise subsequentes.

``` r
## visualiza o objeto epicontacts
epic
```


    /// Epidemiological Contacts //

      // class: epicontacts
      // 5,888 cases in linelist; 3,800 contacts; directed 

      // linelist

    # A tibble: 5,888 × 30
       id     generation date_infection date_onset date_hospitalisation date_outcome
       <chr>       <dbl> <date>         <date>     <date>               <date>      
     1 5fe599          4 2014-05-08     2014-05-13 2014-05-15           NA          
     2 8689b7          4 NA             2014-05-13 2014-05-14           2014-05-18  
     3 11f8ea          2 NA             2014-05-16 2014-05-18           2014-05-30  
     4 b8812a          3 2014-05-04     2014-05-18 2014-05-20           NA          
     5 893f25          3 2014-05-18     2014-05-21 2014-05-22           2014-05-29  
     6 be99c8          3 2014-05-03     2014-05-22 2014-05-23           2014-05-24  
     7 07e3e8          4 2014-05-22     2014-05-27 2014-05-29           2014-06-01  
     8 369449          4 2014-05-28     2014-06-02 2014-06-03           2014-06-07  
     9 f393b4          4 NA             2014-06-05 2014-06-06           2014-06-18  
    10 1389ca          4 NA             2014-06-05 2014-06-07           2014-06-09  
    # ℹ 5,878 more rows
    # ℹ 24 more variables: outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>,
    #   age_years <dbl>, age_cat <fct>, age_cat5 <fct>, hospital <chr>, lon <dbl>,
    #   lat <dbl>, infector <chr>, source <chr>, wt_kg <dbl>, ht_cm <dbl>,
    #   ct_blood <dbl>, fever <chr>, chills <chr>, cough <chr>, aches <chr>,
    #   vomit <chr>, temp <dbl>, time_admission <chr>, bmi <dbl>,
    #   days_onset_hosp <dbl>

      // contacts

    # A tibble: 3,800 × 4
       from   to     location   duration
       <chr>  <chr>  <chr>         <int>
     1 f547d6 5fe599 Community         7
     2 f90f5f b8812a Community         5
     3 11f8ea 893f25 Nosocomial        6
     4 aec8ec be99c8 Community         7
     5 893f25 07e3e8 Community         7
     6 133ee7 369449 Community         3
     7 996f3a 2978ac Community         5
     8 133ee7 57a565 Community        10
     9 37a6f6 fc15ef Community         3
    10 9f6884 2eaa9a Community         8
    # ℹ 3,790 more rows

## 37.3 Manipulando

### Subsetting (subconjuntos)

O método `subset()` dos objetos `epicontacts` permitem, entre outras coisas, filtrar as redes baseadas nas propriedades da linelist (“node attributes”) e da base de contatos (“edge attributes”). Esses valores devem ser passados como listas nomeadas ao argumento respectivo. Por exemplo, no código abaixo estamos mantendo apenas os casos masculinos da linelist que possuem data da infecção entre abril e julho de 2014 (datas são especificadas como intervalos), e relações de transmissão que ocorreram no hospital.

``` r
sub_attributes <- subset(
  epic,
  node_attribute = list(
    gender = "m",
    date_infection = as.Date(c("2014-04-01", "2014-07-01"))
  ), 
  edge_attribute = list(location = "Nosocomial")
)
sub_attributes
```


    /// Epidemiological Contacts //

      // class: epicontacts
      // 69 cases in linelist; 1,941 contacts; directed 

      // linelist

    # A tibble: 69 × 30
       id     generation date_infection date_onset date_hospitalisation date_outcome
       <chr>       <dbl> <date>         <date>     <date>               <date>      
     1 5fe599          4 2014-05-08     2014-05-13 2014-05-15           NA          
     2 893f25          3 2014-05-18     2014-05-21 2014-05-22           2014-05-29  
     3 2978ac          4 2014-05-30     2014-06-06 2014-06-08           2014-06-15  
     4 57a565          4 2014-05-28     2014-06-13 2014-06-15           NA          
     5 fc15ef          6 2014-06-14     2014-06-16 2014-06-17           2014-07-09  
     6 99e8fa          7 2014-06-24     2014-06-28 2014-06-29           2014-07-09  
     7 f327be          6 2014-06-14     2014-07-12 2014-07-13           2014-07-14  
     8 90e5fe          5 2014-06-18     2014-07-13 2014-07-14           2014-07-16  
     9 a47529          5 2014-06-13     2014-07-17 2014-07-18           2014-07-26  
    10 da8ecb          5 2014-06-20     2014-07-18 2014-07-20           2014-08-01  
    # ℹ 59 more rows
    # ℹ 24 more variables: outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>,
    #   age_years <dbl>, age_cat <fct>, age_cat5 <fct>, hospital <chr>, lon <dbl>,
    #   lat <dbl>, infector <chr>, source <chr>, wt_kg <dbl>, ht_cm <dbl>,
    #   ct_blood <dbl>, fever <chr>, chills <chr>, cough <chr>, aches <chr>,
    #   vomit <chr>, temp <dbl>, time_admission <chr>, bmi <dbl>,
    #   days_onset_hosp <dbl>

      // contacts

    # A tibble: 1,941 × 4
       from   to     location   duration
       <chr>  <chr>  <chr>         <int>
     1 11f8ea 893f25 Nosocomial        6
     2 a75c7f 7f5a01 Nosocomial        1
     3 a15e13 f327be Nosocomial        7
     4 beb26e 959170 Nosocomial       10
     5 567136 8ebf6e Nosocomial        4
     6 894024 e56412 Nosocomial        2
     7 a2086d a47529 Nosocomial        4
     8 d6584f f5c142 Nosocomial       10
     9 312ecf 3ad520 Nosocomial        1
    10 52ea64 062638 Nosocomial        5
    # ℹ 1,931 more rows

Podemos utilizar a função `thin` para filtrar a linelist para incluir casos encontrados nos contatos definindo o argumento `what = "linelist"`, ou filtrar os contatos para incluir casos enontrados na linelist definindo o argumento `what = "contacts"`. No código abaixo, vamos continuar filtrando o objeto epicontacts para manter apenas as relações de transmissão que envolvam os casos masculinos infectados entre abril e julho que já filtramos acima. Podemos ver que apenas 3 relações de transmissão se encaixam nessa especificação.

``` r
sub_attributes <- thin(sub_attributes, what = "contacts")
nrow(sub_attributes$contacts)
```

    [1] 3

Além de gerar os subconjuntos a partir dos atributos dos nós *(node)* e arestas *(edges)*, as redes podem ser aparadas para incluir apenas componentes que estejam conectados com certos nós. O argumento `cluster_id` recebe um vetor dos IDs dos casos e retorna uma linelist dos indivíduos que estão relacionados, direta ou indiretamente, a esses a IDs. No código abaixo, podemos ver que um total de 13 casos da linelist estão envolvididos nos agrupamentos *(clusters)* contendo `2ae019` e `71577a`.

``` r
sub_id <- subset(epic, cluster_id = c("2ae019","71577a"))
nrow(sub_id$linelist)
```

    [1] 13

O método `subset()` para os objetos `epicontacts` também permite filtrar pelo tamanho do agrupamento utilizando os argumentos `cs`, `cs_min` e `cs_max`. No código abaixo, estamos mantendo apenas os casos relacionados aos agrupamentos com 10 casos ou mais, e podemos ver que 271 casos da linelist estão envolvidos nesses agrupamentos.

``` r
sub_cs <- subset(epic, cs_min = 10)
nrow(sub_cs$linelist)
```

    [1] 271

### Acessando os IDs

A função `get_id()` recupera informações dos IDs dos casos na base de dados, e pode ser parametrizada como:

- **linelist**: IDs nos dados da linelist
- **contacts**: IDs na base de contatos (“from” e “to” combinados)
- **from**: IDs na coluna “from” da base de contatos
- **to** IDs na coluna “to” da base de contatos
- **all**: IDs que aparecem em qualquer coluna e em qualquer base
- **common**: IDs que aparecem tanto na linelist quanto nos contatos

Por exemplo, quais são os primeiros dez IDs na base de contatos?

``` r
contacts_ids <- get_id(epic, "contacts")
head(contacts_ids, n = 10)
```

     [1] "f547d6" "f90f5f" "11f8ea" "aec8ec" "893f25" "133ee7" "996f3a" "37a6f6"
     [9] "9f6884" "4802b1"

Quantos IDs são encontratos tanto na linelist quanto nos contatos?

``` r
length(get_id(epic, "common"))
```

    [1] 4352

## 37.4 Visualização

### Geração de gráficos básicos

Todas as visualizações dos objetos **epicontacts** são tratadas pela função `plot`. Primeiro vamos filtrar o objeto **epicontacts** para incluir apenas os casos com as datas de início em junho de 2014 utilizando a função `subset`, e então, incluir apenas os contatos relacionados a esses casos com a função `thin`.

``` r
## subconjunto (subset) do objeto epicontacts
sub <- epic %>%
  subset(
    node_attribute = list(date_onset = c(as.Date(c("2014-06-30", "2014-06-01"))))
  ) %>%
 thin("contacts")
```

Podemos criar o gráfico básico e interativo de forma muito simples, como mostrado a seguir:

``` r
## cria o gráfico do objeto epicontacts
plot(
  sub,
  width = 700,
  height = 700
)
```

Você pode mover os nós arrastando-os, passar o mouse sobre eles para mais informações ou clicar neles para destacar os casos conectados.

Existem inúmeros argumentos para fazer modificações a esse gráfico. Iremos cobrir os principais aqui, mas confira a documentação via `?vis_epicontacts` (a função chamada ao utilizar `plot` em um objeto **epicontacts**) para ver uma descrição completa dos argumentos da função.

#### Visualizando atributos dos nós

Cor, forma e tamanho dos nós podem ser mapeados a uma dada coluna na linelist utilizando respectivamente os argumentos `node_color`, `node_shape` e `node_size`. Isso é parecido com a sintaxe da função `aes`, que você deve reconhecer, do pacote **ggplot2**.

As cores, formas e tamanhos dos nós podem ser especificados da seguinte forma:

- **Cores:** via argumento `col_pal`, seja pelo fornecimento de uma lista nomeda, para especificação manual da cada cor, como fizemos abaixo, ou pelo fornecimento de uma função de paleta de cor tal como `colorRampPalette(c("black", "red", "orange"))`, que irá fornecer um degradê de cores entre as especificadas.

- **Formas:** passando uma lista nomeada ao argumento `shapes`, especificando uma forma para cada elemento único da coluna da linelist especificado pelo argumento `node_shape`. Veja `codeawesome` para as formas disponíveis.

- **Tamanho:** passando um intervalo de tamanhos dos nós para o argumento `size_range`.

Aqui vemos um exemplo, onde a cor representa o desfecho, forma representa o gênero e tamanho a idade:

``` r
plot(
  sub, 
  node_color = "outcome",
  node_shape = "gender",
  node_size = "age",
  col_pal = c(Death = "firebrick", Recover = "green"),
  shapes = c(f = "female", m = "male"),
  size_range = c(40, 60),
  height = 700,
  width = 700
)
```

#### Visualizando atributos das arestas

Cor, espessura e tipo de linha das arestas podem ser mepeados a uma dada coluna do dataframe de contatos utilizando, respectivamente, os argumentos `edge_color`, `edge_width` e `edge_linetype`. As cores e espessuras, em específico, podem ser passadas como abaixo:

- **Cores:** via argumento `edge_col_pal`, da mesma maneira utilizada para `col_pal`.

- **Espessuras** passando um intervalo de espessura para o argumento `width_range`.

Aqui temos um exemplo:

``` r
plot(
  sub, 
  node_color = "outcome",
  node_shape = "gender",
  node_size = 'age',
  col_pal = c(Death = "firebrick", Recover = "green"),
  shapes = c(f = "female", m = "male"),
  size_range = c(40, 60),
  edge_color = 'location',
  edge_linetype = 'location',
  edge_width = 'duration',
  edge_col_pal = c(Community = "orange", Nosocomial = "purple"),
  width_range = c(1, 3),
  height = 700,
  width = 700
)
```

### Eixo Temporal

Também podemos visualizar a rede ao longo do eixo temporal ao mapear o argumento `x_axis` a alguma coluna na linelist. No exemplo abaixo, o eixo x representa a data de início dos sintomas. Também especificamos o argumento `arrow_size` para nos certificar que as setas não serão muito grandes, e definimos `label = FALSE` para deixar a figura menos congestionada.

``` r
plot(
  sub,
  x_axis = "date_onset",
  node_color = "outcome",
  col_pal = c(Death = "firebrick", Recover = "green"),
  arrow_size = 0.5,
  node_size = 13,
  label = FALSE,
  height = 700,
  width = 700
)
```

Existem inúmeros outros argumentos para especificar como essa rede pode ser visualizada ao longo de um eixo temporal, você pode conferi-los via `?vis_temporal_interactive` (a função que é chamada ao utilizar `plot` em um objeto **epicontacts** com o argumento `x_axis` especificado). Vamos ver algumas formas abaixo.

#### Especificando a forma de uma árvore de transmissão

As árvores de transmissão podem assumir duas formas principais, especificadas utilizando o argumento `network_shape`. A primeira é a forma `branching` como mostrada acima, em que uma aresta reta conecta dois nós. Essa é a representação mais intuitiva, no entanto pode resultar em arestas sobrepostas em uma rede densamente conectada. A segunda forma é um `rectangle`, que produz uma árvore que se parece com uma filogenia. Por exemplo:

``` r
plot(
  sub,
  x_axis = "date_onset",
  network_shape = "rectangle",
  node_color = "outcome",
  col_pal = c(Death = "firebrick", Recover = "green"),
  arrow_size = 0.5,
  node_size = 13,
  label = FALSE,
  height = 700,
  width = 700
)
```

Cada caso pode ser associado a uma posição vertical única ao se modificar o argumento `position_dodge`. A posição dos casos não-conectados (ex: sem nenhum contato reportado) é especificada utilizando o argumento `unlinked_pos`.

``` r
plot(
  sub,
  x_axis = "date_onset",
  network_shape = "rectangle",
  node_color = "outcome",
  col_pal = c(Death = "firebrick", Recover = "green"),
  position_dodge = TRUE,
  unlinked_pos = "bottom",
  arrow_size = 0.5,
  node_size = 13,
  label = FALSE,
  height = 700,
  width = 700
)
```

A posição dos nós pais em relação aos nós filhos pode ser especificada utilizando o argumento `parent_pos`. A opção padrão é posicionar o nó pai no meio, porém ele pode ser posicionado na parte de baixo (`parent_pos = 'bottom'`) ou na parte de cima (`parent_pos = 'top'`).

``` r
plot(
  sub,
  x_axis = "date_onset",
  network_shape = "rectangle",
  node_color = "outcome",
  col_pal = c(Death = "firebrick", Recover = "green"),
  parent_pos = "top",
  arrow_size = 0.5,
  node_size = 13,
  label = FALSE,
  height = 700,
  width = 700
)
```

#### Salvando os gráficos e figuras

Você pode salvar um gráfico como um arquivo html interativo e auto-contido com a função `visSave` do pacote **VisNetwork**:

``` r
plot(
  sub,
  x_axis = "date_onset",
  network_shape = "rectangle",
  node_color = "outcome",
  col_pal = c(Death = "firebrick", Recover = "green"),
  parent_pos = "top",
  arrow_size = 0.5,
  node_size = 13,
  label = FALSE,
  height = 700,
  width = 700
) %>%
  visNetwork::visSave("network.html")
```

Salvar essas saídas de redes como imagens, infelizmente não é tão simples e requer que você salve o arquivo como html e depois tire um screenshot do arquivo utilizando o pacote `webshot`. No código abaixo, estamos convertendo o arquivo html salvo acima em um PNG:

``` r
webshot(url = "network.html", file = "network.png")
```

### Linhas do Tempo

Você também pode incluir linhas do tempo à rede, que são representadas no eixo x de cada caso. Elas pode ser utilizadas para visualizar locais dos casos, por exemplo, ou o tempo até o desfecho. Para gerar uma linha do tempo, precisamos criar um data frame de pelo menos 3 colunas, indicadno o ID do caso, a data de início do “evento” e a data de fim do “evento”. Você também pode adicionar inúmeras outras colunas que depois podem ser mapeadas para as propriedades de nós ou arestas da linha do tempo. No código abaixo,nós geramos uma linha do tempo que vai da data de início dos sintomas até a data do desfecho, e mantemos as variáveis do desfecho e hospital que utilizamos para definir a forma e cor do nó. Note que você pode ter, por caso, mais do que uma linha do dataframe ou evento na linha do tempo, por exemplo, se um caso for transferido entre multiplos hospitais.

``` r
## cria a linha do tempo
timeline <- linelist %>%
  transmute(
    id = case_id,
    start = date_onset,
    end = date_outcome,
    outcome = outcome,
    hospital = hospital
  ) %>%
  filter(id %in% get_id(sub, "common"), !is.na(start), !is.na(end))
```

Depois, passamos o elemento da linha do tempo para o argumento `timeline`. Podemos mapear os atributos da linha do tempo a cores, formas e tamanhos da mesma forma que definimos nas seções anteriores, exceto que temos *dois* nós: os nós de início de fim de cada timeline, que possuem argumentos separados. Por exemplo, `tl_start_node_color` define qual a coluna da linha do tempo está mapeada à cor do nó de início, enquanto `tl_end_node_shape` define qual a coluna da linha do tempo está mapeada à forma do nó final. Também podemos mapear cor, tamanho, tipo de linha e rótulos à *aresta* da linha do tempo via argumentos do tipo `tl_edge_*`.

Confira `?vis_temporal_interactive` (a função chamada ao criar um gráfico de um objeto epicontacts) para documentação detalhada dos argumentos. Cada argumento está anotado no código abaixo:

``` r
## define as formas
shapes <- c(
  f = "female",
  m = "male",
  Death = "user-times",
  Recover = "heartbeat",
  "NA" = "question-circle"
)

## define cores
colours <- c(
  Death = "firebrick",
  Recover = "green",
  "NA" = "grey"
)

## gera o gráfico
plot(
  sub,
  ## mapeia a coordenada x à data de início
  x_axis = "date_onset",
  ## rede na forma retangular
  network_shape = "rectangle",
  ## mapeia a forma dos nós à coluna de gênero
  node_shape = "gender",
  ## não queremos mapear o cor do nó a nenhuma coluna - esse argumento é importante
  ## pois o padrão é mapear ao id do nó, o que vai bagunçar o esquema de cores
  node_color = NULL,
  ## define o tamanho do nó dos casos como 30 (como não é uma característica dos dados, node_size não
  ## é mapeado para nenhum coluna, mas interpretado como o real tamanho do nó)
  node_size = 30,
  ## define a espessura da relação como 4 (como não é uma característica dos dados, edge_width não
  ## é mapeado para nenhum coluna, mas interpretado como a real espessura da aresta)
  edge_width = 4,
  ## passa o objeto da linha do tempo
  timeline = timeline,
  ## mapeia a forma do nó final à coluna de desfecho do objeto da linha do tempo
  tl_end_node_shape = "outcome",
  ## define o tamanho do nó final como 15 (como não é uma característica dos dados, esse
  ## argumento não é mapeado para nenhum coluna, mas interpretado como o real
  ## tamanho do nó)
  tl_end_node_size = 15,
  ## mapeia a cor da aresta da linha do tempo à coluna hospital
  tl_edge_color = "hospital",
  ## define a espessura da aresta da linha do tempo como 2 (como não é uma característica dos dados, esse
  ## argumento não é mapeado para nenhum coluna, mas interpretado como a real
  ## espessura da aresta)
  tl_edge_width = 2,
  ## mapeia os rótulos das arestas à variável hospital
  tl_edge_label = "hospital",
  ## especifica a forma para cada atributo dos nós (definido acima)
  shapes = shapes,
  ## especifica a paleta de cor (definido acima)
  col_pal = colours,
  ## define o tamanho da seta para 0.5
  arrow_size = 0.5,
  ## utiliza as duas colunas na legenda
  legend_ncol = 2,
  ## define o tamanho da fonte
  font_size = 15,
  ## define a o formato da data
  date_labels = c("%d %b %Y"),
  ## não exibe os rótulos de ID abaixo dos nós
  label = FALSE,
  ## especifica a altura
  height = 1000,
  ## especifica a espessura
  width = 1200,
  ## garante que cada nó dos casos tenha um coordenada y única - isso é muito importante
  ## para linhas do tempo, caso contrário você terá linhas do tempo sobrepostas para
  ## casos diferentes
  position_dodge = TRUE
)
```

## 37.5 Análise

### Resumindo

Podemos ter uma visão gerão de algumas propriedades da rede utilizando a função `summary`.

``` r
## resume o objeto epicontacts
summary(epic)
```


    /// Overview //
      // number of unique IDs in linelist: 5888
      // number of unique IDs in contacts: 5511
      // number of unique IDs in both: 4352
      // number of contacts: 3800
      // contacts with both cases in linelist: 56.868 %

    /// Degrees of the network //
      // in-degree summary:
       Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
     0.0000  0.0000  1.0000  0.5392  1.0000  1.0000 

      // out-degree summary:
       Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
     0.0000  0.0000  0.0000  0.5392  1.0000  6.0000 

      // in and out degree summary:
       Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
      0.000   1.000   1.000   1.078   1.000   7.000 

    /// Attributes //
      // attributes in linelist:
     generation date_infection date_onset date_hospitalisation date_outcome outcome gender age age_unit age_years age_cat age_cat5 hospital lon lat infector source wt_kg ht_cm ct_blood fever chills cough aches vomit temp time_admission bmi days_onset_hosp

      // attributes in contacts:
     location duration

Por exemplo, podemos ver que apenas 57% dos contatos possuem ambos os casos na linelist; isso significa que nós não temos dados da linelist sobre um número significativo de casos envolvidos nessas cadeias de transmissão.

### Características por pares

A função `get_pairwise()` permite o processamento de variáveis na linelist de acordo com cada par na base de dados de contatos. Para o seguinte exemplo, a data de início da doença é extraída da linelist para calcular a diferença entre a data de início para cada par. O valor produzido a partir dessa comparação representa o **intervalo serial (si)**

``` r
si <- get_pairwise(epic, "date_onset")   
summary(si)
```

       Min. 1st Qu.  Median    Mean 3rd Qu.    Max.     NAs 
       0.00    5.00    9.00   11.01   15.00   99.00    1820 

``` r
tibble(si = si) %>%
  drop_na(si) %>%
  ggplot(aes(si)) +
  geom_histogram(bins = 30) +
  labs(
    x = "Serial interval",
    y = "Frequency"
  )
```

[![](transmission_chains_files/figure-html/transmission_chains_pairwise-1.png)](transmission_chains_files/figure-html/transmission_chains_pairwise-1.png)

A `get_pairwise()` vai interpretar a classe da coluna sendo utilizada para comparação e vai ajustar o seu método de comparar os valores de acordo. Para números e datas (como **si** do exemplo acima), a função vai subtrair os valores. Quando aplicado a colunas de caracteres ou categóricas, `get_pairwise()` vai colar *(paste)* os valores. Pelo fato da função também permitir processamentos arbitrários (veja o argumento “f”), essas combinações discretas podem ser facilmente tabuladas e analisadas.

``` r
head(get_pairwise(epic, "gender"), n = 10)
```

     [1] "f -> m" NA       "m -> m" NA       "m -> f" "f -> f" NA       "f -> m"
     [9] NA       "m -> f"

``` r
get_pairwise(epic, "gender", f = table)
```

               values.to
    values.from   f   m
              f 464 516
              m 510 468

``` r
fisher.test(get_pairwise(epic, "gender", f = table))
```


        Fisher's Exact Test for Count Data

    data:  get_pairwise(epic, "gender", f = table)
    p-value = 0.03758
    alternative hypothesis: true odds ratio is not equal to 1
    95 percent confidence interval:
     0.6882761 0.9892811
    sample estimates:
    odds ratio 
     0.8252575 

Aqui observamos uma associação significativa entra as relações de transmissão e gênero.

### Identificando agrupamentoss

A função `get_clusters()` pode ser utilizada para identificar componentes conectados em um objeto `epicontacts`. Primeiro, utilizamos para recuperar um `data.frame` contendo a informação dos agrupamentos:

``` r
clust <- get_clusters(epic, output = "data.frame")
table(clust$cluster_size)
```


       1    2    3    4    5    6    7    8    9   10   11   12   13   14 
    1536 1680 1182  784  545  342  308  208  171  100   99   24   26   42 

``` r
ggplot(clust, aes(cluster_size)) +
  geom_bar() +
  labs(
    x = "Cluster size",
    y = "Frequency"
  )
```

[![](transmission_chains_files/figure-html/transmission_chains_cluster-1.png)](transmission_chains_files/figure-html/transmission_chains_cluster-1.png)

Vamos dar uma olhada nos maiores agrupamentos. Para isso, vamos adicionar informações de agrupamentos ao objeto `epicontacts` e depois fazer um subconjunto para manter apenas os maiores agrupamentos:

``` r
epic <- get_clusters(epic)
max_size <- max(epic$linelist$cluster_size)
plot(subset(epic, cs = max_size))
```

### Calculando graus

O grau de um nó corresponde ao seu número de arestas ou conexões com outros nós. `get_degree()` disponibiliza um método fácil para calcular esse valor para redes de `epicontacts`. Um grau alto nesse contexo indica um indivíduo que esteve em contato com vários outros. O argumento `type` indica que nós queremos contar tanto o grau de entrada (in-degree) quanto o de saída (out-degree) e o argumento `only_linelist` indica que queremos calcular apenas o grau para os casos que estejam na linelist.

``` r
deg_both <- get_degree(epic, type = "both", only_linelist = TRUE)
```

Quais os primeiros 10 indivíduos com a maior quantidade de contatos?

``` r
head(sort(deg_both, decreasing = TRUE), 10)
```

    916d0a 858426 6833d7 f093ea 11f8ea 3a4372 38fc71 c8c4d5 a127a7 02d8fd 
         7      6      6      6      5      5      5      5      5      5 

Qual o número médio de contatos?

``` r
mean(deg_both)
```

    [1] 1.078473

## 37.6 Recursos

A [página epicontacts](https://www.repidemicsconsortium.org/epicontacts/index.html) disponibiliza uma visão geral das funções do pacote e inclui algumas outras vignettes mais aprofundadas.

A [páginad do github](http://github.com/reconhub/epicontacts) pode ser utilizada para registrar problemas (issues) e solicitar funcionalidades.
