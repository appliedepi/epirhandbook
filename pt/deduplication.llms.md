# 15  Eliminação de duplicidades

[![](../../images/deduplication.png)](../../images/deduplication.png)

Esta página abrange as seguintes técnicas de eliminação de duplicidades (ou deduplicação):

1.  Identificar e remover duplicidades  
2.  “Fatiar/subdividir” linhas para manter apenas algumas linhas (por exemplo, mín. ou máx.) de cada grupo de linhas  
3.  “Acumular” ou combinar de valores de várias linhas em uma linha

## 15.1 Preparação

### Carregar pacotes

Este pedaço de código mostra o carregamento de pacotes necessários para as análises. Neste manual, enfatizamos `p_load()` de **pacman**, que instala o pacote se necessário *e* o carrega para uso. Você também pode carregar pacotes instalados com `library()` do R **base**. Veja a página em [Introdução ao R](basics.llms.md) para mais informações sobre pacotes R.

``` r
pacman::p_load(
  tidyverse, # deduplicação, agrupamento e funções de fatiamento
  janitor, # função para revisar duplicidades
  stringr) # para pesquisas de strings, pode ser usado em valores "rolling-up"
```

### Importar dados

Para demonstração, usaremos um conjunto de dados de exemplo criado com o código R abaixo.

Os dados são registros de encontros telefônicos COVID-19, incluindo encontros com contatos e casos. As colunas incluem `recordID` (gerado por computador), `personID`, `name`, `date` do encontro, `time` do encontro, o `purpose` do encontro (para entrevistar como um caso ou como um contato ), e `symptoms_ever` (se a pessoa nesse encontro relatou *sempre* ter sintomas).

Aqui está o código para criar o conjunto de dados `obs`:

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

#### Aqui está o data frame

Use as caixas de filtro na parte superior para revisar os encontros de cada pessoa.

Algumas coisas a serem observadas ao revisar os dados:

- Os dois primeiros registros são duplicados 100% completos, incluindo `recordID` duplicado (deve ser uma falha do computador!)  
- As duas segundas linhas são duplicidades, em todas as colunas *exceto para `recordID`*  
- Várias pessoas tiveram vários encontros por telefone, em várias datas e horários, e como contatos e/ou casos  
- Em cada encontro, a pessoa foi perguntada se ela **alguma vez** teve sintomas, e algumas dessas informações estão faltando.

E aqui está um resumo rápido das pessoas e os propósitos de seus encontros, usando `tabyl()` do **janitor**:

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

## 15.2 Remoção de duplicidades

Esta seção descreve como revisar e remover duplicidades em um data frame. Também mostra como lidar com elementos duplicados em um vetor.

### Examinar duplicidades

Para revisar rapidamente as linhas que têm duplicidades, você pode usar `get_dupes()` do pacote **janitor**. *Por padrão*, todas as colunas são consideradas quando as duplicidades são avaliadas - as linhas retornadas pela função são 100% duplicadas considerando os valores em *todas* as colunas.

No data frame `obs`, as duas primeiras linhas são *100% duplicadas* - elas têm o mesmo valor em todas as colunas (incluindo a coluna `recordID`, que *supõe* ser única - deve ser alguma falha do computador ). O data frame retornado inclui automaticamente uma nova coluna `dupe_count` no lado direito, mostrando o número de linhas com essa combinação de valores duplicados.

``` r
# 100% duplicados em todas as colunas
obs %>% 
  janitor::get_dupes()
```

Veja os [dados originais](#dedup_data)

No entanto, se optarmos por ignorar `recordID`, as linhas da 3ª e 4ª linhas também serão duplicadas umas das outras. Ou seja, eles têm os mesmos valores em todas as colunas *exceto* para `recordID`. Você pode especificar colunas específicas a serem ignoradas na função usando um símbolo de menos `-`.

``` r
# Duplica quando a coluna recordID não é considerada
obs %>% 
  janitor::get_dupes(-recordID) # se várias colunas, envolva-as em c()
```

Você também pode especificar positivamente as colunas a serem consideradas. Abaixo, apenas as linhas que possuem os mesmos valores nas colunas `name` e `purpose` são retornadas. Observe como “amrish” agora tem `dupe_count` igual a 3 para refletir seus três encontros de “contato”.

**Role para a esquerda para mais linhas**

``` r
# duplicatas com base nas colunas de nome e propósito SOMENTE
obs %>% 
  janitor::get_dupes(name, purpose)
```

Veja os [dados originais](#dedup_data).

Veja `?get_dupes` para mais detalhes, ou veja esta [referência online](https://cran.r-project.org/web/packages/janitor/vignettes/janitor.html#explore-records-with-duplicated-values%20-para-combinações-específicas-de-variáveis-com-get_dupes)

### Manter apenas linhas únicas

Para manter apenas linhas exclusivas de um data frame, use `distinct()` de **dplyr** (conforme demonstrado na página [Limpeza de dados e funções principais](cleaning.llms.md)). As duplicidades são removidas de forma que apenas a primeira dessas linhas seja mantida. Por padrão, “primeiro” significa o maior `rownumber` (ordem das linhas de cima para baixo). Apenas linhas exclusivas permanecem.

No exemplo abaixo, executamos `distinct()` de forma que a coluna `recordID` seja excluída da consideração - portanto, **duas linhas duplicadas são removidas**. A primeira linha (para “adam”) foi 100% duplicada e foi removida. Além disso, a linha 3 (para “amrish”) era uma duplicata em todas as colunas *exceto* `recordID` (que não está sendo considerada) e, portanto, também foi removida. O conjunto de dados `obs` n agora é `nrow(obs)-2`, não `nrow(obs)` linhas).

*Role para a esquerda para ver todo o data frame*

``` r
# adicionado a uma cadeia de pipes (por exemplo, limpeza de dados)
obs %>% 
  distinct(across(-recordID), # reduz o data frame para apenas linhas únicas (mantém a primeira de todas as duplicidades)
           .keep_all = TRUE) 

# se fora de pipes, inclua os dados como primeiro argumento 
# distinct(obs)
```

***CUIDADO:*** Se estiver usando `distinct()` em dados agrupados, a função será aplicada a cada grupo.

**Remover duplicidades com base em colunas específicas**

Você também pode especificar colunas para serem a base para eliminação de duplicação. Dessa forma, a eliminação de duplicidades se aplica apenas a linhas duplicadas nas colunas especificadas. A menos que você defina `.keep_all = TRUE`, todas as colunas não mencionadas serão descartadas.

No exemplo abaixo, a eliminação de duplicidades se aplica apenas a linhas com valores idênticos para as colunas `name` e `purpose`. Assim, “brian” tem apenas 2 linhas em vez de 3 - seu *primeiro* encontro de “contato” e seu único encontro de “caso”. Para ajustar para que o *último* encontro de brian de cada propósito seja mantido, veja a aba Fatiar dentro de grupos.

*Role para a esquerda para ver todo o data frame*

``` r
# adicionado a uma cadeia de pipes (por exemplo, limpeza de dados)
obs %>% 
  distinct(name, purpose, .keep_all = TRUE) %>% # mantém as linhas únicas por nome e propósito, mantém todas as colunas
  arrange(name)       # organize para facilitar a visualização
```

Veja os [dados originais](#dedup_data).

### Remover duplicidades em um vetor

A função `duplicated()` do R **base** avaliará um vetor (coluna) e retornará um vetor lógico de mesmo comprimento (VERDADEIRO/FALSO). Na primeira vez que um valor aparecer, ele retornará FALSE (não uma duplicata) e, nas próximas vezes em que esse valor aparecer, ele retornará TRUE. Observe como `NA` é tratado da mesma forma que qualquer outro valor.

``` r
x <- c(1, 1, 2, NA, NA, 4, 5, 4, 4, 1, 2)
duplicated(x)
```

     [1] FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE

Para retornar apenas os elementos duplicados, você pode usar colchetes para subconjunto do vetor original:

``` r
x[duplicated(x)]
```

    [1]  1 NA  4  4  1  2

Para retornar apenas os elementos exclusivos, use a função `unique()` do R **base**. Para remover `NA`s da saída, aninhe `na.omit()` dentro de `unique()`.

``` r
unique(x) # alternativamente, use x[!duplicated(x)]
```

    [1]  1  2 NA  4  5

``` r
unique(na.omit(x)) # remove NAs 
```

    [1] 1 2 4 5

### Usando o R **base**

**Para retornar linhas duplicadas**

No R **base**, você também pode ver quais linhas são 100% duplicadas em um data frame `df` com o comando `duplicated(df)` (retorna um vetor lógico das linhas).

Assim, você também pode usar o subconjunto base `[ ]` no data frame para ver as linhas *duplicadas* com `df[duplicated(df),]` (não esqueça a vírgula, significando que você quer ver todas colunas!).

**Para retornar linhas exclusivas**

Veja as notas acima. Para ver as linhas *únicas*, você adiciona o negador lógico `!` na frente da função `duplicated()`:  
`df[!duplicated(df),]`

**Para retornar linhas que são duplicidades em determinadas colunas**

Subsete o `df` que está *dentro dos parênteses `duplicated()`*, então esta função irá operar apenas em certas colunas do `df`.

Para especificar as colunas, forneça os números ou nomes das colunas após uma vírgula (lembre-se, tudo isso está *dentro* da função `duplicated()`).

Certifique-se de manter a vírgula `,` *fora* após a função `duplicated()` também!

Por exemplo, para avaliar apenas as colunas de 2 a 5 para duplicatas: `df[!duplicated(df[, 2:5]),]`  
Para avaliar apenas as colunas `name` e `purpose` para duplicatas: `df[!duplicated(df[, c("name", "purpose)]),]`

## 15.3 Fatiar/Subdividir

Subdividir um data frame, ou “fatiá-lo” (literalmente do inglês *slice*), significa aplicar um filtro nas linhas por número/posição de linha. Isso se torna particularmente útil se você tiver várias linhas por grupo funcional (por exemplo, por “pessoa”) e quiser manter apenas uma ou algumas delas.

A função básica `slice()` aceita números e retorna linhas nessas posições. Se os números fornecidos forem positivos, somente eles serão retornados. Se negativo, essas linhas *não* são retornadas. Os números devem ser todos positivos ou todos negativos.

``` r
obs %>% slice(4) # retorna a 4ª linha
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        3        2 amrish 2020-01-02 14:20         1 contact            No

``` r
obs %>% slice(c(2,4)) # retorna as linhas 2 e 4
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        1        1   adam 2020-01-01 09:00         1 contact          <NA>
    2        3        2 amrish 2020-01-02 14:20         1 contact            No

``` r
#obs %>% slice(c(2:4)) # retorna as linhas 2 a 4
```

Veja os [dados originais](#dedup_data).

Existem várias variações: Estes devem ser fornecidos com uma coluna e um número de linhas para retornar (para `n =`).

- `slice_min()` e `slice_max()` mantêm apenas a(s) linha(s) com o(s) valor(es) mínimo(s) ou máximo(s) da coluna especificada. Isso também funciona para retornar o “min” e o “max” dos fatores ordenados.  
- `slice_head()` e `slice_tail()` - mantém apenas a *primeira* ou *última* linha(s).  
- `slice_sample()` - mantém apenas uma amostra aleatória das linhas.

``` r
obs %>% slice_max(encounter, n = 1) # retorna linhas com o maior número de encontro
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        5        2 amrish 2020-01-05 16:10         3    case           Yes
    2       13        3 mariah 2020-01-06 08:32         3 contact            No
    3       16        5  brian 2020-01-07 07:59         3    case            No

Use argumentos `n =` ou `prop =` para especificar o número ou a proporção de linhas a serem mantidas. Se não estiver usando a função em uma cadeia de pipes, forneça primeiro o argumento de dados (por exemplo, `slice(data, n = 2)`). Veja `?slice` para mais informações.

Outros argumentos:

`.order_by =` usado em `slice_min()` e `slice_max()` esta é uma coluna para ordenar antes de fatiar.  
`with_ties =` TRUE por padrão, significando que os empates são mantidos.  
`.preserve =` FALSE por padrão. Se TRUE, a estrutura de agrupamento é recalculada após o fatiamento.  
`weight_by =` Opcional, coluna numérica para ponderar (número maior com maior probabilidade de ser amostrado). Também `replace =` para se a amostragem é feita com/sem substituição.

***DICA:*** Ao usar `slice_max()` e `slice_min()`, certifique-se de especificar/escrever o `n =` (por exemplo, `n = 2` , não apenas `2`). Caso contrário, você pode receber um erro `Error:`…`is not empty.`

***NOTE:*** Você pode encontrar a função [`top_n()`](https://dplyr.tidyverse.org/reference/top_n.html), que tem foi substituído pelas funções `slice`.

### Subdividão com grupos

As funções `slice_*()` podem ser muito úteis se aplicadas a um data frame agrupado porque a operação de fatia é executada em cada grupo separadamente. Use a **função** `group_by()` em conjunto com `slice()` para agrupar os dados para obter uma fatia de cada grupo.

Isso é útil para a eliminação de duplicação se você tiver várias linhas por pessoa, mas quiser manter apenas uma delas. Você primeiro usa `group_by()` com colunas-chave que são as mesmas por pessoa e, em seguida, usa uma função de fatia em uma coluna que será diferente entre as linhas agrupadas.

No exemplo abaixo, para manter apenas o *último* encontro *por pessoa*, agrupamos as linhas por `name` e então usamos `slice_max()` com `n = 1` na coluna `date`. Estar ciente! Para aplicar uma função como `slice_max()` em datas, a coluna de data deve ser da classe Date.

Por padrão, “empates” (por exemplo, mesma data neste cenário) são mantidos e ainda obteríamos várias linhas para algumas pessoas (por exemplo, adam). Para evitar isso, configuramos `with_ties = FALSE`. Retornamos apenas uma fila por pessoa.

***CAUTION:*** Se estiver usando `arrange()`, especifique `.by_group = TRUE` para organizar os dados em cada grupo.

***DANGER:*** Se `with_ties = FALSE`, a primeira linha de um empate é mantida. Isso pode ser enganoso. Veja como para Mariah, ela tem dois encontros em sua última data (6 de janeiro) e o primeiro (mais antigo) foi mantido. Provavelmente, queremos manter seu encontro posterior naquele dia. Veja como “quebrar” esses empates no próximo exemplo.

``` r
obs %>% 
  group_by(name) %>% # agrupa as linhas por 'name'
  slice_max(date, # mantém linha por grupo com valor máximo de data 
            n = 1, # mantém apenas a linha mais alta
            with_ties = F) # se houver empate (de data), pegue a primeira linha
```

Acima, por exemplo, podemos ver que apenas a linha de Amrish em 5 de janeiro foi mantida, e apenas a linha de Brian em 7 de janeiro foi mantida. Veja os [dados originais](#dedup_data).

**“Desempates”**

Várias instruções de fatia podem ser executadas para “desempate”. Neste caso, se uma pessoa tiver vários encontros em sua última *data*, o encontro com a última *hora* é mantido (`lubridate::hm()` é usado para converter os tempos dos caracteres em uma classe de tempo classificável).  
Observe como agora, a única linha mantida para “Mariah” em 6 de janeiro é o encontro 3 das 08:32, não o encontro 2 às 07:25.

``` r
# Exemplo de várias instruções de fatia para "desempate"
obs %>%
  group_by(name) %>%
  
  # PRIMEIRO - fatia por data mais recente
  slice_max(date, n = 1, with_ties = TRUE) %>% 
  
  # SEGUNDO - se houver empate, selecione a linha com o horário mais recente; empates proibidos
  slice_max(lubridate::hm(time), n = 1, with_ties = FALSE)
```

*No exemplo acima, também seria possível dividir por número de `encounter`, mas mostramos a fatia em `data` e `time` para fins de exemplo.*

***DICA:*** Para usar `slice_max()` ou `slice_min()` em uma coluna “character”, altere-a para uma classe de fator *ordenada*! extensão\>

Veja os [dados originais](#dedup_data).

### Mantenha tudo mas marque-os

Se você quiser manter todos os registros, mas marcar apenas alguns para análise, considere uma abordagem de duas etapas utilizando um recordID/número de encontro exclusivo:

1.  Reduza/faça o recorte do data frame original apenas nas linhas para análise. Salve/retenha este data frame reduzido.  
2.  No data frame original, marque as linhas conforme apropriado com `case_when()`, com base no fato de seu identificador exclusivo de registro (recordID neste exemplo) estar presente no data frame reduzido.

``` r
# 1. Defina o data frame de linhas para manter para análise
obs_keep <- obs %>%
  group_by(name) %>%
  slice_max(encounter, n = 1, with_ties = FALSE) # mantém apenas o último encontro por pessoa


# 2. Marcar data frame original
obs_marked <- obs %>%

  # cria uma nova coluna dup_record
  mutate(dup_record = case_when(
    
    # se o registro estiver no data frame obs_keep
    recordID %in% obs_keep$recordID ~ "For analysis", 
    
    # tudo o mais marcado como "Ignorar" para fins de análise
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

Veja os [dados originais](#dedup_data).

### Calcular a completitude da linha

Crie uma coluna que contenha uma métrica para a completitude da linha (não falta). Isso pode ser útil ao decidir quais linhas priorizar em relação a outras ao remover duplicidade/fatiar.

Neste exemplo, as colunas “chave” sobre as quais você deseja medir a integridade são salvas em um vetor de nomes de coluna.

Então a nova coluna `key_completeness` é criada com `mutate()`. O novo valor em cada linha é definido como uma fração calculada: o número de valores não omissos nessa linha entre as colunas-chave, dividido pelo número de colunas-chave.

Isso envolve a função `rowSums()` do R **base**. Também é usado `.`, que dentro do encadeamento do código (pipe - %\>%) se refere ao data frame naquele ponto do pipe (neste caso, está sendo subconjunto com colchetes `[]`).

\*Role para a direita para ver mais linhas\*\*

``` r
# cria uma coluna "completude da variável chave"
# esta é uma *proporção* das colunas designadas como "key_cols" que não possuem valores omissos

key_cols = c("personID", "name", "symptoms_ever")

obs %>% 
  mutate(key_completeness = rowSums(!is.na(.[,key_cols]))/length(key_cols)) 
```

Veja os [dados originais](#dedup_data).

## 15.4 Valores acumulados

Esta seção descreve:

1.  Como “agregar” valores de várias linhas em apenas uma linha, com algumas variações  
2.  Depois de ter os valores “acumulados”, como substituir/priorizar os valores em cada célula

Esta guia usa o conjunto de dados de exemplo da guia Preparação.

### Valores acumulados em uma linha

O exemplo de código abaixo usa `group_by()` e `summarise()` para agrupar linhas por pessoa e depois colar todos os valores exclusivos nas linhas agrupadas. Assim, você obtém uma linha de resumo por pessoa. Algumas notas:

- Um sufixo é anexado a todas as novas colunas (“\_roll” neste exemplo)  
- Se você quiser mostrar apenas valores exclusivos por célula, envolva o `na.omit()` com `unique()`  
- `na.omit()` remove valores `NA`, mas se isso não for desejado, pode ser removido `paste0(.x)`…

``` r
# Valores "roll-up" em uma linha por grupo (por "personID") 
cases_rolled <- obs %>% 
  
  #cria grupos por nome
  group_by(personID) %>% 
  
  # ordena as linhas dentro de cada grupo (por exemplo, por data)
  arrange(date, .by_group = TRUE) %>% 
  
  # Para cada coluna, cole todos os valores dentro das linhas agrupadas, separados por ";"
  summarise(
    across(everything(), # aplica-se a todas as colunas
           ~paste0(na.omit(.x), collapse = "; "))) # function is defined which combines non-NA values
```

O resultado é uma linha por grupo (`ID`), com entradas organizadas por data e coladas juntas. *Role para a esquerda para ver mais linhas*

Veja os [dados originais](#dedup_data).

**Esta variação mostra apenas valores únicos:**

``` r
# Variação - mostra apenas valores únicos 
cases_rolled <- obs %>% 
  group_by(personID) %>% 
  arrange(date, .by_group = TRUE) %>% 
  summarise(
    across(everything(), # aplica-se a todas as colunas
           ~paste0(unique(na.omit(.x)), collapse = "; "))) # função é definida que combina valores únicos não-NA
```

**Esta variação anexa um sufixo a cada coluna.**  
Neste caso “\_roll” para significar que foi agregado:

``` r
# Variação - sufixo adicionado aos nomes das colunas 
cases_rolled <- obs %>% 
  group_by(personID) %>% 
  arrange(date, .by_group = TRUE) %>% 
  summarise(
    across(everything(),                
           list(roll = ~paste0(na.omit(.x), collapse = "; ")))) # _roll é anexado aos nomes das colunas
```

### Substituir valores/hierarquia

Se você quiser avaliar todos os valores rolados e manter apenas um valor específico (por exemplo, valor “melhor” ou “máximo”), você pode usar `mutate()` nas colunas desejadas, para implementar `case_when()` , que usa `str_detect()` do pacote **stringr** para procurar sequencialmente padrões de string e sobrescrever o conteúdo da célula.

``` r
# CASOS LIMPOS
#############
cases_clean <- cases_rolled %>% 
    
    # clean Yes-No-Unknown vars: replace text with "highest" value present in the string
    mutate(across(c(contains("symptoms_ever")),                     # operates on specified columns (Y/N/U)
             list(mod = ~case_when(                                 # adds suffix "_mod" to new cols; implements case_when()
               
               str_detect(.x, "Yes")       ~ "Yes",                 # if "Yes" is detected, then cell value converts to yes
               str_detect(.x, "No")        ~ "No",                  # then, if "No" is detected, then cell value converts to no
               str_detect(.x, "Unknown")   ~ "Unknown",             # then, if "Unknown" is detected, then cell value converts to Unknown
               TRUE                        ~ as.character(.x)))),   # then, if anything else if it kept as is
      .keep = "unused") # colunas antigas removidas, deixando apenas colunas _mod
```

Agora você pode ver na coluna `symptoms_ever` que se a pessoa ALGUMA VEZ disse “Yes” aos sintomas, então apenas “Yes” é exibido.

Veja os [dados originais](#dedup_data).

## 15.5 Remoção de duplicidades probabilística

Às vezes, você pode querer identificar duplicidades “prováveis” com base na semelhança (por exemplo, string “distance”) em várias colunas, como nome, idade, sexo, data de nascimento etc. Você pode aplicar um algoritmo de correspondência probabilística para identificar duplicidades prováveis.

Consulte a página em [Juntar dados](joining_matching.llms.md) para obter uma explicação sobre este método. A seção sobre Correspondência Probabilística contém um exemplo de aplicação desses algoritmos para comparar um data frame com o *próprio*, realizando assim a desduplicação probabilística.

## 15.6 Recursos

Muitas das informações nesta página são adaptadas destes recursos e vinhetas online:

[datanovia](https://www.datanovia.com/en/lessons/identify-and-remove-duplicate-data-in-r/)

[dplyr tidyverse reference](https://dplyr.tidyverse.org/reference/slice.html)

[vinheta de janitor de cran](https://cran.r-project.org/web/packages/janitor/vignettes/janitor.html#explore-records-with-duplicated-values-for-specific-combinations-of-variables-%20com-get_dupes)
