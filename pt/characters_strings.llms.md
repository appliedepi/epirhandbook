# 10  Caracteres e strings

[![](../../images/characters_strings_1500x500.png)](../../images/characters_strings_1500x500.png)

Essa página mostra o uso do pacote **stringr** para avaliar e lidar com cadeias de caracteres (“strings”).

1.  Combinar, ordenar, dividir, organizar - `str_c()`, `str_glue()`, `str_order()`, `str_split()`  

2.  Limpar e padronizar

    - Ajuste o comprimento - `str_pad()`, `str_trunc()`, `str_wrap()`  
    - Alterar maiúsculas e minúsculas - `str_to_upper()`, `str_to_title()`, `str_to_lower()`, `str_to_sentence()`  

3.  Avaliar e extrair por posição - `str_length()`, `str_sub()`, `word()`  

4.  Padrões

    - Detectar e localizar - `str_detect()`, `str_subset()`, `str_match()`, `str_extract()`  
    - Modificar e substituir - `str_sub()`, `str_replace_all()`  

5.  Expressões regulares (“regex”)

Para facilitar a exibição, a maioria dos exemplos são mostrados agindo em um vetor curto do tipo caractere, no entanto, eles podem ser facilmente adaptados a uma coluna dentro de um quadro de dados (*data frame*).

Esse [manual das funções do stringr](https://cran.r-project.org/web/packages/stringr/vignettes/stringr.html) forneceu grande parte da inspiração para esta página.

## 10.1 Preparação

### Carregue os pacotes

Instale ou carregue o **stringr** e outros pacotes **tidyverse**.

``` r
# instalar/carregar pacotes
pacman::p_load(
  stringr,    # muitas funções para lidar com strings
  tidyverse,  # para manipulação opicional de dados
  tools,      # alternativa para converter para maiúsculas
  appliedepidata) # dados de exemplo utilizados neste manual
```

### Importar os dados

Nesta página, faremos referência ocasional à `linelist`, uma lista de casos de uma simulação de epidemia de Ebola. Carregue diretamente com `appliedepidata::get_data(name = "linelist_cleaned_rds")` (consulte a página [Baixar manual e dados](download.llms.md) para mais detalhes).

``` r
# Exemplo de importação 
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

As primeiras 50 linhas da lista estão exibidas abaixo.

## 10.2 Unir, dividir e organizar

Essa seção aborda:

- O uso das funções `str_c()`, `str_glue()`, e `unite()` para combinar strings (caracteres ou descrições)  
- O uso da função `str_order()` para organizar strings  
- O uso das funções `str_split()` e `separate()` para dividir strings

### Combinar strings

Para combinar ou concatenar múltiplos strings em um único string, sugerimos usar `str_c` do **stringr**. Se você tiver distintos valores de caracteres para combinar, basta fornecê-los como argumentos exclusivos, separados por vírgulas.

``` r
str_c("String1", "String2", "String3")
```

    [1] "String1String2String3"

O argumento `sep =` insere um valor de caractere entre cada um dos argumentos fornecidos (por exemplo, inserir uma vírgula, espaço ou nova linha `"\n"`)

``` r
str_c("String1", "String2", "String3", sep = ", ")
```

    [1] "String1, String2, String3"

O argumento `collapse =` é relevante se você estiver inserindo múltiplos *vetores* como argumentos para a função `str_c()`. Ele é usado para separar os elementos do que seria um vetor de *saída*, de forma que o vetor de saída tenha apenas um longo elemento de caractere.

O exemplo abaixo mostra a combinação de dois vetores em um (nomes e sobrenomes). Outro exemplo semelhante pode ser sobre jurisdições e suas contagens de casos. Neste exemplo:

- O valor `sep =` aparece entre cada nome e sobrenome  
- O valor `collapse =` aparece entre cada pessoa

``` r
first_names <- c("abdul", "fahruk", "janice") 
last_names  <- c("hussein", "akinleye", "okeke")

# sep é exibido entre as respectivas strings de entrada, enquanto collapse é exibido entre os elementos produzidos
str_c(first_names, last_names, sep = " ", collapse = ";  ")
```

    [1] "abdul hussein;  fahruk akinleye;  janice okeke"

Nota: Dependendo do contexto de exibição desejado, ao imprimir/exibir uma string combinada com novas linhas, você pode precisar inserir a frase inteira em `cat()` para que as novas linhas sejam impressas/exibidas corretamente:

``` r
# Para que as novas linhas sejam impressas corretamente, a frase pode precisar estar inserida na função cat()
cat(str_c(first_names, last_names, sep = " ", collapse = ";\n"))
```

    abdul hussein;
    fahruk akinleye;
    janice okeke

### Strings dinâmicas

Use `str_glue()` para inserir um código R dinâmico em um string. Esta é uma função muito útil para criar legendas dinâmicas de gráficos, conforme demonstrado abaixo.

- Todo o conteúdo fica entre aspas duplas `str_glue("")`  
- Qualquer código dinâmico ou referências aos valores predefinidos são colocados entre chaves `{}` com aspas duplas. Pode haver muitas chaves no mesmo comando `str_glue()`.  
- Para exibir aspas como caracter ’’, use aspas *simples* entre aspas duplas (por exemplo, ao fornecer o formato de data - veja o exemplo abaixo)  
- Dica: você pode usar `\n` para forçar uma nova linha  
- Dica: você usa `format()` para ajustar a exibição da data e usa `Sys.Date()` para exibir a data atual

Um simples exemplo da gráfico com legenda dinâmica:

``` r
str_glue("Data include {nrow(linelist)} cases and are current to {format(Sys.Date(), '%d %b %Y')}.")
```

    Data include 5888 cases and are current to 01 Nov 2026.

Um formato alternativo é usar espaços reservados dentro dos colchetes e definir o código em argumentos separados no final da função `str_glue()`, conforme abaixo. Isso pode melhorar a legibilidade do código se o texto for longo.

``` r
str_glue("Linelist as of {current_date}.\nLast case hospitalized on {last_hospital}.\n{n_missing_onset} cases are missing date of onset and not shown",
         current_date = format(Sys.Date(), '%d %b %Y'),
         last_hospital = format(as.Date(max(linelist$date_hospitalisation, na.rm=T)), '%d %b %Y'),
         n_missing_onset = nrow(linelist %>% filter(is.na(date_onset)))
         )
```

    Linelist as of 01 Nov 2026.
    Last case hospitalized on 30 Apr 2015.
    256 cases are missing date of onset and not shown

**Extraindo de uma tabela de dados**

Às vezes, é útil extrair dados de um data frame e colá-los juntos na sequência. Abaixo está um exemplo de data frame. Vamos usá-lo para fazer uma declaração resumida sobre as jurisdições e as contagens de casos novos e totais.

``` r
# fazer um data frame de casos
case_table <- data.frame(
  zone        = c("Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5"),
  new_cases   = c(3, 0, 7, 0, 15),
  total_cases = c(40, 4, 25, 10, 103)
  )
```

Use `str_glue_data()`, que é feito especialmente para obter dados de linhas do data frame:

``` r
case_table %>% 
  str_glue_data("{zone}: {new_cases} ({total_cases} total cases)")
```

    Zone 1: 3 (40 total cases)
    Zone 2: 0 (4 total cases)
    Zone 3: 7 (25 total cases)
    Zone 4: 0 (10 total cases)
    Zone 5: 15 (103 total cases)

**Combine strings em linhas**

Se você estiver tentando “acumular” valores em uma coluna de um data frame, por exemplo, combinar valores de várias linhas em apenas uma linha, colando-os juntos com um separador, consulte a seção da página [Eliminação de duplicidades](deduplication.llms.md) em [“acumulando” valores](deduplication.llms.md#str_rollup).

**Data frame para uma linha**

Você pode fazer a frase aparecer em uma linha usando `str_c()` (especificando o data frame e os nomes das colunas) e fornecendo os argumentos `sep =` e `collapse =`.

``` r
str_c(case_table$zone, case_table$new_cases, sep = " = ", collapse = ";  ")
```

    [1] "Zone 1 = 3;  Zone 2 = 0;  Zone 3 = 7;  Zone 4 = 0;  Zone 5 = 15"

Você poderia adicionar o texto “Novos Casos:” ao início da instrução envolvendo a função com `str_c()` (se “Novos Casos:” estivesse dentro do `str_c()` original, ele apareceria várias vezes).

``` r
str_c("New Cases: ", str_c(case_table$zone, case_table$new_cases, sep = " = ", collapse = ";  "))
```

    [1] "New Cases: Zone 1 = 3;  Zone 2 = 0;  Zone 3 = 7;  Zone 4 = 0;  Zone 5 = 15"

### Unir colunas

Dentro de uma tabela de dados, reunir valores de caracteres de várias colunas pode ser obtido com `unite()` do pacote **tidyr**. Isso é o oposto de `separate()`.

Forneça o nome da nova coluna unida. Em seguida, forneça os nomes das colunas que deseja unir.

- Por padrão, o separador usado na coluna unida é o underline `_`, mas isso pode ser alterado com o argumento `sep =`.  
- `remove =` rremove as colunas de entrada da tabela de dados (TRUE por padrão)  
- `na.rm =` remove os valores ausentes durante a união (FALSE por padrão)

Abaixo, definimos uma mini-tabela de dados para demonstrar:

``` r
df <- data.frame(
  case_ID = c(1:6),
  symptoms  = c("jaundice, fever, chills",     # paciente 1
                "chills, aches, pains",        # paciente 2 
                "fever",                       # paciente 3
                "vomiting, diarrhoea",         # paciente 4
                "bleeding from gums, fever",   # paciente 5
                "rapid pulse, headache"),      # paciente 6
  outcome = c("Recover", "Death", "Death", "Recover", "Recover", "Recover"))
```

``` r
df_split <- separate(df, symptoms, into = c("sym_1", "sym_2", "sym_3"), extra = "merge", fill = "right")
```

Aqui está o exemplo da tabela de dados:

Abaixo, unimos as três colunas de sintomas:

``` r
df_split %>% 
  unite(
    col = "all_symptoms",         # nome da nova coluna unida
    c("sym_1", "sym_2", "sym_3"), # colunas para unir
    sep = ", ",                   # separador para usar na coluna unida
    remove = TRUE,                # se TRUE (verdadeiro), remove colunas de entrada da tabela de dados
    na.rm = TRUE                  # se TRUE, os valores ausentes são removidos antes da união
  )
```

      case_ID                all_symptoms outcome
    1       1     jaundice, fever, chills Recover
    2       2        chills, aches, pains   Death
    3       3                       fever   Death
    4       4         vomiting, diarrhoea Recover
    5       5 bleeding, from, gums, fever Recover
    6       6      rapid, pulse, headache Recover

### Dividir

Para dividir um objeto de texto (string) com base em um padrão, use `str_split()`. Ele avalia o(s) string(s) e retorna uma `list` de vetores de caracteres que consistem nos valores recém-divididos.

O exemplo simples abaixo avalia uma string e a divide em três. Por padrão, ele retorna um objeto da `list` de classes com um elemento (um vetor de caracteres) para cada string fornecida inicialmente. Se `simplify = TRUE`, ele retorna uma matriz de caracteres.

Neste exemplo, uma string é fornecida e a função retorna uma lista com um elemento - um vetor de caracteres com três valores.

``` r
str_split(string = "jaundice, fever, chills",
          pattern = ",")
```

    [[1]]
    [1] "jaundice" " fever"   " chills" 

Se o resultado de saída for salvo, você poderá acessar o enésimo valor de divisão com a sintaxe de colchetes. Para acessar um valor específico, você pode usar uma sintaxe como esta: `the_returned_object[[1]][2]`, que acessaria o segundo valor da primeira string avaliada (“febre”). Consulte a página [Introdução ao R](basics.llms.md) para obter mais detalhes sobre como acessar os elementos.

``` r
pt1_symptoms <- str_split("jaundice, fever, chills", ",")

pt1_symptoms[[1]][2]  # extrai o segundo valor do primeiro (e único) elemento da lista
```

    [1] " fever"

Se múltiplos strings forem fornecidas por `str_split()`, haverá mais de um elemento na lista retornada.

``` r
symptoms <- c("jaundice, fever, chills",     # paciente 1
              "chills, aches, pains",        # paciente 2 
              "fever",                       # paciente 3
              "vomiting, diarrhoea",         # paciente 4
              "bleeding from gums, fever",   # paciente 5
              "rapid pulse, headache")       # paciente 6

str_split(symptoms, ",")                     # dividir os sintomas de cada paciente
```

    [[1]]
    [1] "jaundice" " fever"   " chills" 

    [[2]]
    [1] "chills" " aches" " pains"

    [[3]]
    [1] "fever"

    [[4]]
    [1] "vomiting"   " diarrhoea"

    [[5]]
    [1] "bleeding from gums" " fever"            

    [[6]]
    [1] "rapid pulse" " headache"  

Para retornar uma “matriz de caracteres”, que pode ser útil ao criar colunas de tabela de dados, defina o argumento `simplify = TRUE` como mostrado abaixo:

``` r
str_split(symptoms, ",", simplify = TRUE)
```

         [,1]                 [,2]         [,3]     
    [1,] "jaundice"           " fever"     " chills"
    [2,] "chills"             " aches"     " pains" 
    [3,] "fever"              ""           ""       
    [4,] "vomiting"           " diarrhoea" ""       
    [5,] "bleeding from gums" " fever"     ""       
    [6,] "rapid pulse"        " headache"  ""       

Você também pode ajustar o número de divisões a serem criadas com o argumento `n =`. Por exemplo, isso restringe o número de divisões a 2. Quaisquer outras vírgulas permanecem dentro dos segundos valores.

``` r
str_split(symptoms, ",", simplify = TRUE, n = 2)
```

         [,1]                 [,2]            
    [1,] "jaundice"           " fever, chills"
    [2,] "chills"             " aches, pains" 
    [3,] "fever"              ""              
    [4,] "vomiting"           " diarrhoea"    
    [5,] "bleeding from gums" " fever"        
    [6,] "rapid pulse"        " headache"     

*Oservação - as mesmas saídas podem ser obtidas com `str_split_fixed()`, em que você não fornece o argumento `simplify`, mas deve designar o número de colunas (`n`).*

``` r
str_split_fixed(symptoms, ",", n = 2)
```

### Dividir colunas

Se você está tentando dividir a coluna da tabela de dados, é melhor usar a função `separate()` do **dplyr**. É usado para dividir uma coluna de caracteres em outras colunas.

Digamos que temos uma simples tabela de dados `df` (definida e unida na [seção Unir](#str_unite)) contendo uma coluna `case_ID`, uma coluna de caractere com muitos sintomas e uma coluna de resultado. Nosso objetivo é separar a coluna de `symptoms` em várias colunas - cada uma contendo um sintoma.

Assumindo que os dados sejam divididos por meio do `separate()`, primeiro forneça a coluna a ser separada. Em seguida, forneça `into =` como um vetor `c( )` contendo os *novos* nomes das colunas, conforme mostrado abaixo.

- `sep =` o separador, pode ser um caractere ou um número (interpretado como a posição do caractere para dividir)

- `remove =` TRUE por padrão, remove a coluna de entrada

- `convert =` FALSE por padrão, fará com que a string “NA” se torne `NA`

- `extra =` isso controla o que acontece se houver mais valores criados pela separação do que novas colunas nomeadas.

- `extra = "warn"` significa que você verá um aviso, mas os valores em excesso serão descartados (**o padrão**)

- `extra = "drop"` significa que os valores em excesso serão descartados sem aviso

- \*\*`extra = "merge"` somente será dividido para o número de novas colunas listadas em `into` - \*esta configuração preservará todos os seus dados\*\*

Um exemplo com `extra = "merge"` está abaixo - nenhum dado é perdido. Duas novas colunas são definidas, mas quaisquer terceiros sintomas são combinados na segunda coluna nova:

``` r
# terceiros sintomas combinados na segunda nova coluna
df %>% 
  separate(symptoms, into = c("sym_1", "sym_2"), sep=",", extra = "merge", fill = "right")
```

      case_ID              sym_1          sym_2 outcome
    1       1           jaundice  fever, chills Recover
    2       2             chills   aches, pains   Death
    3       3              fever           <NA>   Death
    4       4           vomiting      diarrhoea Recover
    5       5 bleeding from gums          fever Recover
    6       6        rapid pulse       headache Recover

Quando `extra = "drop"` é usado abaixo, os terceiros sintomas são perdidos:

``` r
# terceiros sintomas são perdidos
df %>% 
  separate(symptoms, into = c("sym_1", "sym_2"), sep=",", extra = "drop", fill = "right")
```

      case_ID              sym_1      sym_2 outcome
    1       1           jaundice      fever Recover
    2       2             chills      aches   Death
    3       3              fever       <NA>   Death
    4       4           vomiting  diarrhoea Recover
    5       5 bleeding from gums      fever Recover
    6       6        rapid pulse   headache Recover

**CUIDADO:** Se você não fornecer valores suficientes `into` para as novas colunas, seus dados podem ser truncados.

### Organizar em ordem alfabética

Várias strings podem ser classificadas em ordem alfabética. `str_order()` retorna a ordem, enquanto `str_sort()` retorna as strings nessa ordem.

``` r
# strings
health_zones <- c("Alba", "Takota", "Delta")

# retornar a ordem alfabética
str_order(health_zones)
```

    [1] 1 3 2

``` r
# retornar as strings em ordem alfabética
str_sort(health_zones)
```

    [1] "Alba"   "Delta"  "Takota"

Para usar um alfabeto diferente, adicione o argumento `locale =`. Veja a lista completa de localidades digitando `stringi::stri_locale_list()` no R console.

### Funções do R base

É comum ver as funções do R **base** `paste()` e `paste0()`, que concatenam vetores após converter todas as partes em caracteres. Eles agem de forma semelhante a `str_c()` , mas a sintaxe é indiscutivelmente mais complicada - entre parênteses cada parte é separada por uma vírgula. As partes são textos de caracteres (entre aspas) ou objetos de código predefinidos (sem aspas). Por exemplo:

``` r
n_beds <- 10
n_masks <- 20

paste0("Regional hospital needs ", n_beds, " beds and ", n_masks, " masks.")
```

    [1] "Regional hospital needs 10 beds and 20 masks."

Os argumentos `sep =` e `collapse =` podem ser especificados. `paste()` é simplesmente `paste0()` com um `sep = " "` padrão (um espaço).

## 10.3 Limpe e padronize

### Mudar maiúsculas e minúsculas

Frequentemente, é necessário alterar a capitalização / maiúsculas de um valor de string, por exemplo, nomes de jursidições. Use `str_to_upper()`, `str_to_lower()`, e `str_to_title()`, de **stringr**, como mostrado abaixo:

``` r
str_to_upper("California")
```

    [1] "CALIFORNIA"

``` r
str_to_lower("California")
```

    [1] "california"

Usando R **base**, o acima também pode ser obtido com `toupper()`, `tolower()`.

**Capitalização de título**

Transformar o string para que cada palavra inicie com maiúscula pode ser conseguido com `str_to_title()`:

``` r
str_to_title("go to the US state of california ")
```

    [1] "Go To The Us State Of California "

Use `toTitleCase()` do pacote **tools** para obter uma capitalização mais sutil (palavras em inglês como “to”, “the” e “of” não são capitalizadas).

``` r
tools::toTitleCase("This is the US state of california")
```

    [1] "This is the US State of California"

Você também pode usar `str_to_sentence()`, que coloca em maiúscula apenas a primeira letra do string.

``` r
str_to_sentence("the patient must be transported")
```

    [1] "The patient must be transported"

### Comprimento do código

Use `str_pad()` para adicionar caracteres a uma string, com um comprimento mínimo. Por padrão, espaços são adicionados, mas você também pode preencher com outros caracteres usando o argumento `pad =`.

``` r
# Códigos ICD de comprimento diferente
ICD_codes <- c("R10.13",
               "R10.819",
               "R17")

# Códigos ICD preenchidos com 7 caracteres no lado direito
str_pad(ICD_codes, 7, "right")
```

    [1] "R10.13 " "R10.819" "R17    "

``` r
# Pad com pontos em vez de espaços
str_pad(ICD_codes, 7, "right", pad = ".")
```

    [1] "R10.13." "R10.819" "R17...."

Por exemplo, para preencher números com zeros à esquerda (como para horas ou minutos), você pode preencher o número com o comprimento mínimo de 2 com `pad = "0"`.

``` r
# Adicione zeros à esquerda de dois dígitos (por exemplo, para tempos minutos / horas)
str_pad("4", 2, pad = "0") 
```

    [1] "04"

``` r
# exemplo usando uma coluna numérica chamada "horas"
# hours <- str_pad(hours, 2, pad = "0")
```

### Truncar

`str_trunc()` define um comprimento máximo para cada string. Se uma string exceder esse comprimento, ela será truncada (encurtada) e uma reticência (…) será incluída para indicar que a string era anteriormente mais longa. Observe que as reticências *são* counted contadas no comprimento. Os caracteres de reticências podem ser alterados com o argumento `ellipsis =`. O argumento opcional `side =` especifica onde as reticências aparecerão dentro da string truncada (“esquerda”, “direita” ou “centro”).

``` r
original <- "Symptom onset on 4/3/2020 with vomiting"
str_trunc(original, 10, "center")
```

    [1] "Symp...ing"

### Padronizar comprimento

Use `str_trunc()` para definir um comprimento máximo, e então use `str_pad()` para expandir as strings muito curtas para aquele comprimento truncado. No exemplo abaixo, 6 é definido como o comprimento máximo (um valor é truncado) e, em seguida, um valor muito curto é preenchido para atingir o comprimento de 6.

``` r
# Códigos ICD de comprimento diferente
ICD_codes   <- c("R10.13",
                 "R10.819",
                 "R17")

# truncar com comprimento máximo de 6
ICD_codes_2 <- str_trunc(ICD_codes, 6)
ICD_codes_2
```

    [1] "R10.13" "R10..." "R17"   

``` r
# expandir para comprimento mínimo de 6
ICD_codes_3 <- str_pad(ICD_codes_2, 6, "right")
ICD_codes_3
```

    [1] "R10.13" "R10..." "R17   "

### Remova os espaços em branco à esquerda / à direita

Use `str_trim()` para remover espaços, `\n` para novas linhas ou tabulações (`\t`) nos lados de uma entrada de string. Adicione `"right"` `"left"`, ou `"both"` ao comando para especificar qual lado cortar (por exemplo, `str_trim(x, "right")`.

``` r
# Números ID com espaços em excesso à direita
IDs <- c("provA_1852  ", # dois espaços excedentes
         "provA_2345",   # zero espaço excedente
         "provA_9460 ")  # um espaço excedente

# IDs cortados para remover espaços em excesso apenas no lado direito
str_trim(IDs)
```

    [1] "provA_1852" "provA_2345" "provA_9460"

### Remova os espaços em branco repetidos dentro do texto

Use `str_squish()` para remover espaços repetidos que aparecem dentro de uma string. Por exemplo, para converter espaços duplos em espaços simples. Ele também remove espaços, novas linhas ou tabulações do lado de fora da string como `str_trim()`.

``` r
# o original contém espaços em excesso dentro da string
str_squish("  Pt requires   IV saline\n") 
```

    [1] "Pt requires IV saline"

Digite `?str_trim`, `?str_pad` em seu console R para ver mais detalhes.

### Quebrar em parágrafos

Use `str_wrap()` para quebrar um texto longo e não estruturado em um parágrafo estruturado com comprimento de linha fixo. Fornece o comprimento de caractere ideal para cada linha e aplica um algoritmo para inserir novas linhas (`\n`) dentro do parágrafo, conforme mostrado no exemplo abaixo.

``` r
pt_course <- "Symptom onset 1/4/2020 vomiting chills fever. Pt saw traditional healer in home village on 2/4/2020. On 5/4/2020 pt symptoms worsened and was admitted to Lumta clinic. Sample was taken and pt was transported to regional hospital on 6/4/2020. Pt died at regional hospital on 7/4/2020."

str_wrap(pt_course, 40)
```

    [1] "Symptom onset 1/4/2020 vomiting chills\nfever. Pt saw traditional healer in\nhome village on 2/4/2020. On 5/4/2020\npt symptoms worsened and was admitted\nto Lumta clinic. Sample was taken and pt\nwas transported to regional hospital on\n6/4/2020. Pt died at regional hospital\non 7/4/2020."

A função **base** `cat()` pode ser envolvida no comando acima para mostrar o resultado, exibindo as novas linhas adicionadas.

``` r
cat(str_wrap(pt_course, 40))
```

    Symptom onset 1/4/2020 vomiting chills
    fever. Pt saw traditional healer in
    home village on 2/4/2020. On 5/4/2020
    pt symptoms worsened and was admitted
    to Lumta clinic. Sample was taken and pt
    was transported to regional hospital on
    6/4/2020. Pt died at regional hospital
    on 7/4/2020.

## 10.4 Manipular por posição

### Extrair pela posição dos caracteres

Use `str_sub()` para retornar apenas uma parte de uma string. A função tem três argumentos principais:

1.  o(s) vetor(es) de caracteres
2.  posição inicial
3.  posição final

Algumas notas sobre os números de posição:

- Se um número de posição for positivo, a posição é contada a partir da extremidade esquerda da string.
- Se um número de posição for negativo, ele é contado a partir da extremidade direita da string.
- Os números das posições são inclusivos.
- As posições que se estendem além da string serão truncadas (removidas).

Abaixo estão alguns exemplos aplicados à string “pneumonia”:

``` r
# começar e terminar em terceiro da esquerda (3ª letra da esquerda)
str_sub("pneumonia", 3, 3)
```

    [1] "e"

``` r
# 0 não está presente
str_sub("pneumonia", 0, 0)
```

    [1] ""

``` r
# 6º da esquerda, para o 1º da direita
str_sub("pneumonia", 6, -1)
```

    [1] "onia"

``` r
# 5º da direita, para o 2º da direita
str_sub("pneumonia", -5, -2)
```

    [1] "moni"

``` r
# 4º da esquerda para uma posição fora da string
str_sub("pneumonia", 4, 15)
```

    [1] "umonia"

### Extrair por posição de palavra

Para extrair a enésima ‘palavra’, use `word()`, também do pacote **stringr**. Forneça as strings (descriçoes), a posição da primeira palavra a extrair e a posição da última palavra a extrair.

Por padrão, o separador entre ‘palavras’ é considerado um espaço, a menos que indicado de outra forma com `sep =` (por exemplo, `sep = "_"` quando as palavras são separadas por underlines).

``` r
# strings para avaliar
chief_complaints <- c("I just got out of the hospital 2 days ago, but still can barely breathe.",
                      "My stomach hurts",
                      "Severe ear pain")

# extraia a 1ª a 3ª palavras de cada string (descrição)
word(chief_complaints, start = 1, end = 3, sep = " ")
```

    [1] "I just got"       "My stomach hurts" "Severe ear pain" 

### Substituir pela posição do caractere

`str_sub()` emparelhado com o operador de atribuição (`<-`) pode ser usado para modificar uma parte de uma string:

``` r
word <- "pneumonia"

# converter o terceiro e o quarto caracteres em X 
str_sub(word, 3, 4) <- "XX"

# exibe
word
```

    [1] "pnXXmonia"

Um exemplo aplicado a várias strings (por exemplo, uma coluna). Observe a expansão do comprimento de “HIV”.

``` r
words <- c("pneumonia", "tubercolosis", "HIV")

# converter o terceiro e o quarto caracteres em X 
str_sub(words, 3, 4) <- "XX"

words
```

    [1] "pnXXmonia"    "tuXXrcolosis" "HIXX"        

### Avalie o comprimento

``` r
str_length("abc")
```

    [1] 3

Alternativamente, use `nchar()` do R **base**

## 10.5 Padrões

Muitas funções **stringr** trabalham para detectar, localizar, extrair, combinar, substituir e dividir com base em um *padrão* especificado.

### Detectar um padrão

Use `str_detect()` como abaixo para detectar a presença / ausência de um padrão dentro de uma string. Primeiro forneça a string ou vetor a ser pesquisado (`string =`) e, em seguida, o padrão a ser procurado (`pattern =`). Observe que, por padrão, a pesquisa *diferencia maiúsculas de minúsculas*!

``` r
str_detect(string = "primary school teacher", pattern = "teach")
```

    [1] TRUE

O argumento `negate =` pode ser incluído e definido como `TRUE` se você quiser saber se o padrão NÃO está presente.

``` r
str_detect(string = "primary school teacher", pattern = "teach", negate = TRUE)
```

    [1] FALSE

Para ignorar maiúsculas e minúsculas, envolva o padrão em `regex()`, e *em* `regex()` adicione o argumento `ignore_case = TRUE` (ou `T` como abreviação).

``` r
str_detect(string = "Teacher", pattern = regex("teach", ignore_case = T))
```

    [1] TRUE

Quando `str_detect()` é aplicado a um vetor de caracteres ou uma coluna da tabela de dados, ele retornará TRUE ou FALSE para cada um dos valores.

``` r
# um vetor / coluna de ocupações
occupations <- c("field laborer",
                 "university professor",
                 "primary school teacher & tutor",
                 "tutor",
                 "nurse at regional hospital",
                 "lineworker at Amberdeen Fish Factory",
                 "physican",
                 "cardiologist",
                 "office worker",
                 "food service")

# Detecta a presença do padrão "prof" em cada string - a saída é um vetor TRUE / FALSE
str_detect(occupations, "teach")
```

     [1] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE

Se você precisar contar os `TRUE`s, simplesmente some os resultados por meio da função `sum()`. Essa função conta o número de `TRUE`.

``` r
sum(str_detect(occupations, "teach"))
```

    [1] 1

Para pesquisar incluindo vários termos, inclua-os separados por barras OR (`|`) dentro do argumento `pattern =`, conforme mostrado abaixo:

``` r
sum(str_detect(string = occupations, pattern = "teach|professor|tutor"))
```

    [1] 3

Se precisar construir uma longa lista de termos de pesquisa, você pode combiná-los usando `str_c()` e `sep = |`, em seguida defina que este é um objeto de caractere e referencie o vetor posteriormente de forma mais sucinta. O exemplo abaixo inclui possíveis termos de pesquisa de ocupação para provedores médicos de linha de frente.

``` r
# termos de busca
occupation_med_frontline <- str_c("medical", "medicine", "hcw", "healthcare", "home care", "home health",
                                "surgeon", "doctor", "doc", "physician", "surgery", "peds", "pediatrician",
                               "intensivist", "cardiologist", "coroner", "nurse", "nursing", "rn", "lpn",
                               "cna", "pa", "physician assistant", "mental health",
                               "emergency department technician", "resp therapist", "respiratory",
                                "phlebotomist", "pharmacy", "pharmacist", "hospital", "snf", "rehabilitation",
                               "rehab", "activity", "elderly", "subacute", "sub acute",
                                "clinic", "post acute", "therapist", "extended care",
                                "dental", "dential", "dentist", sep = "|")

occupation_med_frontline
```

    [1] "medical|medicine|hcw|healthcare|home care|home health|surgeon|doctor|doc|physician|surgery|peds|pediatrician|intensivist|cardiologist|coroner|nurse|nursing|rn|lpn|cna|pa|physician assistant|mental health|emergency department technician|resp therapist|respiratory|phlebotomist|pharmacy|pharmacist|hospital|snf|rehabilitation|rehab|activity|elderly|subacute|sub acute|clinic|post acute|therapist|extended care|dental|dential|dentist"

Este comando retorna o número de ocupações que contêm qualquer um dos termos de pesquisa para provedores médicos de linha de frente (`occupation_med_frontline`):

``` r
sum(str_detect(string = occupations, pattern = occupation_med_frontline))
```

    [1] 2

**Funções de pesquisa de string do R base**

A função **base** `grepl()` funciona de forma similar à função `str_detect()`, no sentido de que procura por correspondências com um padrão e retorna um vetor lógico. A sintaxe básica é `grepl(pattern, strings_to_search, ignore.case = FALSE, ...)`. Uma vantagem é que o argumento `ignore.case` é mais fácil de escrever (não há necessidade de envolver a função `regex()`).

Da mesma forma, as funções de **base** `sub()` e `gsub()` agem de forma semelhante a `str_replace()`. Sua sintaxe básica é: `gsub(pattern, replacement, strings_to_search, ignore.case = FALSE)`. `sub()` substituirá a primeira instância do padrão, enquanto `gsub()` substituirá todas as instâncias do padrão.

#### Converta vírgulas em pontos

Aqui está um exemplo de uso de `gsub()` para converter vírgulas em pontos em um vetor de números. Isso pode ser útil se seus dados vierem de outras partes do mundo que não os Estados Unidos ou a Grã-Bretanha.

O `gsub()` interno que atua primeiro em `lengths` convertendo quaisquer pontos em nenhum espaço ““. O caractere de ponto final”.” deve ser “escapado” com duas barras para realmente significar um ponto, porque “.” em regex significa “qualquer caractere”. Em seguida, o resultado (apenas com vírgulas) é passado para o `gsub()` , no qual as vírgulas são substituídas por pontos.

``` r
lengths <- c("2.454,56", "1,2", "6.096,5")

as.numeric(gsub(pattern = ",",                # encontra vírgulas   
                replacement = ".",            # substitui por pontos
                x = gsub("\\.", "", lengths)  # vetor com outros pontos removidos (deve-se "escapar" os pontos)
                )
           )                                  # converter resultado em numérico
```

### Substituir tudo

Use `str_replace_all()` omo uma ferramenta de “localizar e substituir”. Primeiro, forneça as strings a serem avaliadas para `string =`, depois o padrão a ser substituído por `pattern =` e, a seguir, o valor de substituição para `replacement =`. O exemplo abaixo substitui todas as ocorrências de “morto” por “óbito”. Observe que isso É sensível a maiúsculas e minúsculas.

``` r
outcome <- c("Karl: dead",
            "Samantha: dead",
            "Marco: not dead")

str_replace_all(string = outcome, pattern = "dead", replacement = "deceased")
```

    [1] "Karl: deceased"      "Samantha: deceased"  "Marco: not deceased"

Notas:

- Para substituir um padrão por `NA`, use `str_replace_na()`.  
- A função `str_replace()` substitui apenas a primeira instância do padrão em cada string avaliada.

### Detectar dentro da lógica

**Dentro de `case_when()`**

`str_detect()` é frequentemente usado em `case_when()` (de **dplyr**). Digamos que `occupations` é uma coluna na lista. A função `mutate()` abaixo cria uma nova coluna chamada `is_educator` usando lógica condicional via `case_when()`. Veja a página sobre limpeza de dados para aprender mais sobre `case_when()`.

``` r
df <- df %>% 
  mutate(is_educator = case_when(
    # pesquisa de termo dentro da ocupação, sem distinção entre maiúsculas e minúsculas
    str_detect(occupations,
               regex("teach|prof|tutor|university",
                     ignore_case = TRUE))              ~ "Educator",
    # todos os outros
    TRUE                                               ~ "Not an educator"))
```

Como um lembrete, pode ser importante adicionar critérios de exclusão à lógica condicional (`negate = F`):

``` r
df <- df %>% 
  # valor na nova coluna is_educator é baseado na lógica condicional
  mutate(is_educator = case_when(
    
    # a coluna de ocupação deve atender a 2 critérios para ser atribuído "Educador":
    # deve ter um termo de pesquisa E NÃO qualquer termo de exclusão
    
    # Deve conter um termo de pesquisa
    str_detect(occupations,
               regex("teach|prof|tutor|university", ignore_case = T)) &              
    
    # E NÃO deve ter um termo de exclusão
    str_detect(occupations,
               regex("admin", ignore_case = T),
               negate = TRUE)                       ~ "Educator",
    
    # Todas as linhas que não atendem aos critérios acima
    TRUE                                            ~ "Not an educator"))
```

### Localize a posição do padrão

Para localizar a *primeira* posição de um padrão, use `str_locate()`. Ele produz uma posição inicial e final.

``` r
str_locate("I wish", "sh")
```

         start end
    [1,]     5   6

Como outras funções `str`, há uma versão “\_all” (`str_locate_all()`) que retornará as posições de *todas* as instâncias do padrão dentro de cada string. Isso resulta em uma `list`.

``` r
phrases <- c("I wish", "I hope", "he hopes", "He hopes")

str_locate(phrases, "h" )     # posição da *primeira* instância do padrão
```

         start end
    [1,]     6   6
    [2,]     3   3
    [3,]     1   1
    [4,]     4   4

``` r
str_locate_all(phrases, "h" ) # posição de *cada* instância do padrão
```

    [[1]]
         start end
    [1,]     6   6

    [[2]]
         start end
    [1,]     3   3

    [[3]]
         start end
    [1,]     1   1
    [2,]     4   4

    [[4]]
         start end
    [1,]     4   4

### Extraia uma combinação

`str_extract_all()` retorna os próprios padrões de correspondência, o que é mais útil quando você oferece vários padrões por meio de condições “OU”. Por exemplo, procurando no vetor string de ocupações (consulte a aba anterior) “educador”, “prof” ou “tutor”.

`str_extract_all()` retorna uma `list` que contém todas as correspondências para cada string avaliada. Veja abaixo como a ocupação 3 tem duas correspondências de padrão dentro dela.

``` r
str_extract_all(occupations, "teach|prof|tutor")
```

    [[1]]
    character(0)

    [[2]]
    [1] "prof"

    [[3]]
    [1] "teach" "tutor"

    [[4]]
    [1] "tutor"

    [[5]]
    character(0)

    [[6]]
    character(0)

    [[7]]
    character(0)

    [[8]]
    character(0)

    [[9]]
    character(0)

    [[10]]
    character(0)

`str_extract()` extrai apenas *a primeira combinação* (match) em cada string avaliada, produzindo um vetor de caracteres com um elemento para cada string avaliada. Retorna `NA` onde não há uma combinação. Os `NA`s pode ser removido envolvendo o vetor retornado com `na.exclude()`. Observe como o segundo dos acertos da ocupação 3 não é mostrado.

``` r
str_extract(occupations, "teach|prof|tutor")
```

     [1] NA      "prof"  "teach" "tutor" NA      NA      NA      NA      NA     
    [10] NA     

### Subconjunto e contagem

As funções alinhadas incluem `str_subset()` e `str_count()`.

`str_subset()` retorna os valores reais que continham o padrão:

``` r
str_subset(occupations, "teach|prof|tutor")
```

    [1] "university professor"           "primary school teacher & tutor"
    [3] "tutor"                         

`str_count()` retorna um vetor de números: o **número de vezes** que um termo de pesquisa aparece em cada valor avaliado.

``` r
str_count(occupations, regex("teach|prof|tutor", ignore_case = TRUE))
```

     [1] 0 1 2 1 0 0 0 0 0 0

### Grupos Regex

UNDER CONSTRUCTION

## 10.6 Caracteres especiais

**Barra invertida `\` como escape**

A barra invertida `\` é usada para “escapar” do significado do próximo caractere. Desta forma, uma barra invertida pode ser usada para exibir uma aspa dentro de outras aspas (`\"`) - a aspa do meio não “quebrará” as aspas circundantes.

Observação - portanto, se você deseja *exibir* uma barra invertida, deve-se escapar de seu significado com outra barra invertida. Portanto, você deve escrever duas barras invertidas `\\` para mostrar uma.

**Caracteres especiais**

| Caracteres especiais | Representa                          |
|----------------------|-------------------------------------|
| `"\\"`               | barra invertida                     |
| `"\n"`               | uma nova linha                      |
| `"\""`               | aspas duplas *entre* aspas duplas   |
| `'\''`               | aspas simples *entre* aspas simples |
| `"\`“\`              | acento grave                        |
| `"\r"`               | retorno de carro                    |
| `"\t"`               | tabulação                           |
| `"\v"`               | tabulação vertical                  |
| `"\b"`               | backspace                           |

Execute `?"'"` no console R para exibir uma lista completa desses caracteres especiais (ela aparecerá no painel Ajuda do RStudio).

## 10.7 Regular expressões (regex)

## 10.8 Regex e caracteres especiais

Expressões regulares, ou “regex”, é uma linguagem concisa para descrever padrões em strings. Se você não estiver familiarizado com ela, uma expressão regular pode parecer uma linguagem alienígena. Aqui tentamos desmistificar um pouco essa linguagem.

*Grande parte desta seção foi adaptada [desse tutorial](https://towardsdatascience.com/a-gentle-introduction-to-regular-expressions-with-r-df5e897ca432) e [desta página de referência](https://evoldyn.gitlab.io/evomics-2018/ref-sheets/R_strings.pdf)*. Nós adaptamos seletivamente aqui sabendo que este manual pode ser visto por pessoas sem acesso à Internet para ver os outros tutoriais.

Uma expressão regular é frequentemente aplicada para extrair padrões específicos de texto “não estruturado” - por exemplo, notas médicas, queixas principais, histórico do paciente ou outras colunas de texto livre em uma tabela de dados.

Existem quatro ferramentas básicas que podem ser usadas para criar uma expressão regular básica:

1.  Conjuntos de caracteres
2.  Meta caracteres
3.  Quantificadores
4.  Grupos

**Conjunto de caracteres**

Os conjuntos de caracteres são uma forma de expressar as opções de listagem para uma correspondência de caracteres, entre colchetes. Portanto, qualquer correspondência será acionada se qualquer um dos caracteres entre colchetes for encontrado na string. Por exemplo, para procurar vogais, pode-se usar este conjunto de caracteres: “\[aeiou\]”. Alguns outros conjuntos de caracteres comuns são:

| Conjunto de caracteres | Correspondências para                   |
|------------------------|-----------------------------------------|
| `"[A-Z]"`              | qualquer letra maiúscula isolada        |
| `"[a-z]"`              | qualquer letra minúscula isolada        |
| `"[0-9]"`              | qualquer dígito                         |
| `[:alnum:]`            | qualquer caractere alfanumérico         |
| `[:digit:]`            | qualquer dígito numérico                |
| `[:alpha:]`            | qualquer letra (maiúscula ou minúscula) |
| `[:upper:]`            | qualquer letra maiúscula                |
| `[:lower:]`            | qualquer letra minúscula                |

Os conjuntos de caracteres podem ser combinados dentro de um colchete (sem espaços!), como `"[A-Za-z]"` (qualquer letra maiúscula ou minúscula), ou outro exemplo `"[t-z0-5]"` (t minúsculo até z OU número de 0 a 5).

**Metacaracteres**

Metacaracteres são abreviações para conjuntos de caracteres. Alguns dos mais importantes estão listados abaixo:

| Meta character | Representa                                              |
|----------------|---------------------------------------------------------|
| `"\\s"`        | um espaço simples                                       |
| `"\\w"`        | qualquer caractere alfanumérico único (A-Z, a-z ou 0-9) |
| `"\\d"`        | qualquer dígito numérico único (0-9)                    |

**Quantificadores**

Normalmente, você não deseja pesquisar uma correspondência em apenas um caractere. Os quantificadores permitem que você designe o comprimento das letras/números para permitir a correspondência.

Quantificadores são números escritos entre chaves `{ }` *após* o caractere que estão quantificando, por exemplo,

- `"A{2}"` retornará instâncias de **duas** letras A maiúsculas.  
- `"A{2,4}"` retornará instâncias **entre duas e quatro** letras A maiúsculas (*não coloque espaços!*).  
- `"A{2,}"` retornará as correspondências de **duas ou mais** letras A maiúsculas.  
- `"A+"` retornará instâncias de **uma ou mais** letras A maiúsculas (grupo estendido até que um caractere diferente seja encontrado).  
- Preceda com um `*` asterisco para retornar **zero ou mais** correspondências (útil se você não tiver certeza de que o padrão está presente)

Usando o símbolo mais `+` como quantificador, a correspondência ocorrerá até que um caractere diferente seja encontrado. Por exemplo, esta expressão retornará *todas* as palavras (caracteres alfabéticos: `"[A-Za-z]+"`

``` r
# teste string para quantificadores
test <- "A-AA-AAA-AAAA"
```

Quando um quantificador de {2} é usado, apenas pares de A’s consecutivos são retornados. Dois pares são identificados dentro `AAAA`.

``` r
str_extract_all(test, "A{2}")
```

    [[1]]
    [1] "AA" "AA" "AA" "AA"

Quando um quantificador de {2,4} é usado, grupos de A’s consecutivos com comprimento de dois a quatro são retornados.

``` r
str_extract_all(test, "A{2,4}")
```

    [[1]]
    [1] "AA"   "AAA"  "AAAA"

Com o quantificador `+`, grupos de **um ou mais** são retornados:

``` r
str_extract_all(test, "A+")
```

    [[1]]
    [1] "A"    "AA"   "AAA"  "AAAA"

**Posição relativa**

Esses requisitos expressam o que precede ou segue um padrão. Por exemplo, para extrair frases, “dois números seguidos de um ponto” (`""`). (?\<=\\)\s(?=\[A-Z\])

``` r
str_extract_all(test, "")
```

    [[1]]
     [1] "A" "-" "A" "A" "-" "A" "A" "A" "-" "A" "A" "A" "A"

| Declaração de posição | Corresponde a                          |
|-----------------------|----------------------------------------|
| `"(?<=b)a"`           | “a” que **é precedido** por um “b”     |
| `"(?<!b)a"`           | “a” que **NÃO é precedido** por um “b” |
| `"a(?=b)"`            | “a” que **é seguido** por um “b”       |
| `"a(?!b)"`            | “a” que **NÃO é seguido** por um “b”   |

**Grupos**

Capturar grupos em sua expressão regular é uma maneira de ter um resultado mais organizado na extração.

**Exemplos de Regex**

Abaixo está um texto livre para os exemplos. Tentaremos extrair informações úteis dele usando um termo de pesquisa de expressão regular.

``` r
pt_note <- "Patient arrived at Broward Hospital emergency ward at 18:00 on 6/12/2005. Patient presented with radiating abdominal pain from LR quadrant. Patient skin was pale, cool, and clammy. Patient temperature was 99.8 degrees farinheit. Patient pulse rate was 100 bpm and thready. Respiratory rate was 29 per minute."
```

Esta expressão corresponde a todas as palavras (qualquer caractere até atingir um objeto não caractere, como um espaço):

``` r
str_extract_all(pt_note, "[A-Za-z]+")
```

    [[1]]
     [1] "Patient"     "arrived"     "at"          "Broward"     "Hospital"   
     [6] "emergency"   "ward"        "at"          "on"          "Patient"    
    [11] "presented"   "with"        "radiating"   "abdominal"   "pain"       
    [16] "from"        "LR"          "quadrant"    "Patient"     "skin"       
    [21] "was"         "pale"        "cool"        "and"         "clammy"     
    [26] "Patient"     "temperature" "was"         "degrees"     "farinheit"  
    [31] "Patient"     "pulse"       "rate"        "was"         "bpm"        
    [36] "and"         "thready"     "Respiratory" "rate"        "was"        
    [41] "per"         "minute"     

A expressão `"[0-9]{1,2}"` corresponde a números consecutivos com 1 ou 2 dígitos de comprimento. Também pode ser escrito `"\\d{1,2}"`, ou `"[:digit:]{1,2}"`.

``` r
str_extract_all(pt_note, "[0-9]{1,2}")
```

    [[1]]
     [1] "18" "00" "6"  "12" "20" "05" "99" "8"  "10" "0"  "29"

Você pode ver uma lista útil de expressões regex e dicas na página 2 [deste cheatsheet](https://evoldyn.gitlab.io/evomics-2018/ref-sheets/R_strings.pdf)

Também veja o [tutorial](https://towardsdatascience.com/a-gentle-introduction-to-regular-expressions-with-r-df5e897ca432).

## 10.9 Recursos

Uma planilha de referencia para as funções de **stringr** pode ser encontrada [aqui](https://evoldyn.gitlab.io/evomics-2018/ref-sheets/R_strings.pdf)

Uma vinheta sobre **stringr** pode ser encontrada [aqui](https://cran.r-project.org/web/packages/stringr/vignettes/stringr.html)
