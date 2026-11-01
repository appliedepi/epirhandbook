# 21  Normalização de taxas

Esta página irá descrever como normalizar os dados, como hospitalizações ou mortalidade, com características como idade e sexo.

Esta página utiliza o pacote **PHEindicatormethods**.

Nós iniciaremos enfatizando os processos de preparação/limpeza/união dos dados, por serem atividades comuns ao combinar dados populacionais de diferentes países, dados populacionais padrões, óbitos, etc.

## 21.1 Visão geral

Existem duas principais formas de normalizar: normalização direta e indireta. Digamos que gostaríamos de normalizar as taxas de mortalidade por idade e sexo, nos países A e B, e, então, comparar as taxas entre esses países.

- Para realizar a normalização direta, você precisa saber o número da população sob-risco, e o número de mortes para cada faixa etária por sexo, tanto para o país A, quanto para o B. Uma faixa etária em nosso exemplo poderia ser mulheres entre 15-44 anos.
- Para realizar a normalizaçaõ de forma indireta, você apenas precisa saber o número total de mortes, e a composição da população por sexo e idade em cada país. Logo, está opção é viável quando as taxas de mortalidade específicas por idade e sexo, ou números da população, não estão disponíveis. A normalização indireta também é preferida nos casos de pequenas quantidades por estrato, uma vez que estimativas com a normalização direta seriam influenciadas pela variação amostral.

## 21.2 Preparação

Para mostrar como a normalização é feita, nós iremos utilizar dados ficcionais com a quantidade populacional e quantidade de mortes dos países A e B, por idade (em categorias de 5 anos) e sexo (mulheres, homens). Para criar conjuntos de dados prontos para uso, nós iremos executar as seguintes etapas de preparação:

1.  Carregar os pacotes
2.  Carregar os conjuntos dos dados
3.  Unir os dados populacionais e de óbitos dos dois países
4.  Transformar para o formato longo, de forma que haja apenas uma linha por estrato idade-sexo
5.  Limpar a população de referência (população mundial padrão) e uni-la aos dados dos países

No seu cenário, os dados podem estar em um formato diferente. Talvez seus dados sejam por províncias, cidades, ou outros tipos de área. Talvez você tenha uma linha para cada óbito, e informações (ou uma proporção significante) sobre idade e sexo para cada um desses óbitos. Neste caso, veja as páginas sobre [Agrupando dados](grouping.llms.md), [Pivoteando os dados](pivoting.llms.md), e [Tabelas descritivas](tables_descriptive.llms.md) para criar um conjunto de dados com quantidades de eventos e população por estrato idade-sexo.

Nós também precisamos de uma população de referência, a população padrão. Para os propósitos deste exercício, nós iremos utilizar o `world_standard_population_by_sex`. A “população padrão mundial” é baseada nas populações de 46 países e foi criada em 1960. Existem muitas populações “padrão” - por exemplo, o site do [NHS Scotland](https://www.opendata.nhs.scot/dataset/standard-populations) possui muitas informações sobre a População Padrão Européia, População Padrão Mundial, e População Padrão Escocesa.

### Carregue os pacotes R

O código abaixo realiza o carregamento dos pacotes necessários para a análise dos dados. Neste manual, enfatizamos o uso da função `p_load()`, do **pacman**, que instala os pacotes, caso não estejam instalados, *e* os carrega no R para utilização. Também é possível carregar pacotes instalados utilizando a função `library()`, do R **base**. Para mais informações sobre os pacotes do R, veja a página [Introdução ao R](basics.llms.md).

``` r
pacman::p_load(
     rio,                 # importar/exportar dados
     here,                # localizar arquivos
     stringr,             # limpar caracteres e strings
     PHEindicatormethods, # alternativa para padronização das taxas
     tidyverse,           # gerenciamento e visualização dos dados
     appliedepidata) # dados de exemplo utilizados neste manual
```

### Carregue os dados populacionais

Veja a página [Download do manual e dados](download.llms.md) para instruções sobre como baixar todos os dados de exemplos utilizados neste manual. Você pode carregar os dados da página de Padronização diretamente no R com as chamadas `appliedepidata::get_data()` abaixo:

``` r
# importe dados demográficos do país A
A_demo <- appliedepidata::get_data(name = "country_demographics")

# importe dados de óbitos do país A
A_deaths <- appliedepidata::get_data(name = "deaths_countryA")

# importe dados demográficos do país B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")

# importe dados de óbitos do país B
B_deaths <- appliedepidata::get_data(name = "deaths_countryB")

# importe dados demográficos da População padrão mundial
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

Primeiro, nós carregamos os dados demográficos (contanges de homens e mulheres por categorias de 5 em 5 anos) para os países que iremos comparar, “País A” e “País B”.

``` r
# País A
A_demo <- appliedepidata::get_data(name = "country_demographics")
```

``` r
# País B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")
```

### Carregue a quantidade de óbitos

Convenientemente, a quantidade de óbitos, por idade e sexo durante o período de interesse, também está disponível. Cada contagem por país está em arquivos separados, como mostrado abaixo.

Óbitos no país A

Óbitos no país B

### Limpe os dados populacionais e de óbitos

Nós precisamos unir e transformar estes dados da seguinte maneira:

- Combine as populações dos países em um conjunto de dados e o transforme para o formato “longo”, de forma que cada estrato idade-sexo esteja em uma linha
- Combine a quantidade de óbitos dos países em um conjunto de dados e o transforme para o formato “longo”, de forma que cada estrato idade-sexo esteja em uma linha
- Una os óbitos com as populações

Primeiro, nós iremos unir os dados de população por país, transformar para o formato longo, e realizar uma limpeza mínima dos dados. Veja a página sobre [Pivoteando os dados](pivoting.llms.md) para mais detalhes.

``` r
pop_countries <- A_demo %>%  # inicie com os dados do país A
     bind_rows(B_demo) %>%        # una as linhas, uma vez que as colunas têm o mesmo nome
     pivot_longer(                       # transforme (pivot) para o formato longo
          cols = c(m, f),                   # colunas para combinar em uma
          names_to = "Sex",                 # nome para a nova coluna contendo a categoria ("m" ou "f") 
          values_to = "Population") %>%     # nome para a nova coluna contendo os valores numéricos transformados (pivoted)
     mutate(Sex = recode(Sex,            # re-codifique os valores para clareza
          "m" = "Male",
          "f" = "Female"))
```

Agora, os dados populacionais combinados estão assim (clique para ver os países A e B)

E, agora, nós iremos realizar operações similares nos dois bancos de óbitos.

``` r
deaths_countries <- A_deaths %>%    # inicie com os dados de óbitos do país A
     bind_rows(B_deaths) %>%        # una as linhas com os dados do país B, uma vez que o nome das colunas é igual
     pivot_longer(                  # transforme para formato longo
          cols = c(Male, Female),        # colunas para transformar em uma
          names_to = "Sex",              # nome da nova coluna contendo a categoria ("m" ou "f") 
          values_to = "Deaths") %>%      # nome da nova coluna contendo os valores numéricos transformados
     rename(age_cat5 = AgeCat)      # renomeie para mais clareza
```

Agora, os dados de óbitos estão da seguinte forma, e contêm dados de ambos países:

Agora, nós uniremos os dados populacionais e de óbitos, baseado nas colunas em comum `Country`, `age_cat5`, e `Sex`. O processo também adiciona a coluna `Deaths`.

``` r
country_data <- pop_countries %>% 
     left_join(deaths_countries, by = c("Country", "age_cat5", "Sex"))
```

Então, podemos classificar `Sex`, `age_cat5`, e `Country` como factors, e ajustar a ordem dos níveis com a função `fct_relevel()` do pacote **forcats**, como descrito na página [Fatores](factors.llms.md). Nota, visivelmente, classificar os níveis dos factors não altera os dados, mas o comando `arrange()` ordena os dados por país (Country), categoria de idade (age), e sexo (sex).

``` r
country_data <- country_data %>% 
  mutate(
    Country = fct_relevel(Country, "A", "B"),
      
    Sex = fct_relevel(Sex, "Male", "Female"),
        
    age_cat5 = fct_relevel(
      age_cat5,
      "0-4", "5-9", "10-14", "15-19",
      "20-24", "25-29",  "30-34", "35-39",
      "40-44", "45-49", "50-54", "55-59",
      "60-64", "65-69", "70-74",
      "75-79", "80-84", "85")) %>% 
          
  arrange(Country, age_cat5, Sex)
```

***CUIDADO:*** Se você possuir poucos óbitos por estrato, considere utilizar categorias com intervalos de 10 ou 15 anos, em vez de 5 anos.

### Carregue os dados populacionais de referência

Por último, para realizar a padronização direta, nós iremos importar a população de referência (“população mundial de referência” por sexo)

``` r
# População de referência
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

### Limpe os dados da população de referência

Os valores por categorias de idade nos conjuntos de dados `country_data` e `standard_pop_data` precisam ser alinhados.

No momento, os valores da coluna `age_cat5`, do conjunto `standard_pop_data`, contém as palavras “years” e “plus”, enquanto os dados em `country_data` não possuem essas palavras. Nós precisamos garantir que os valores da categoria “age” coincidam. Para tanto, utilizaremos a função `str_replace_all()`, do pacote **stringr**, como descrito na página sobre [Caracteres e strings](characters_strings.llms.md), para substituir estes padrões para “sem espaço” `""`.

A função `calculate_dsr()` recebe a população de referência pelo argumento `stdpop =`, então a coluna pode ter qualquer nome. Nós a renomeamos para `"pop"` porque o código abaixo usa `stdpop = pop`.

``` r
# Remova palavras específicas da coluna valores ("values")
standard_pop_clean <- standard_pop_data %>%
     mutate(
          age_cat5 = str_replace_all(age_cat5, "years", ""),   # remova "year"
          age_cat5 = str_replace_all(age_cat5, "plus", ""),    # remova "plus"
          age_cat5 = str_replace_all(age_cat5, " ", "")) %>%   # remova " " espaço
     
     rename(pop = WorldStandardPopulation)   # mude o nome da coluna para "pop", a coluna passada para stdpop = em calculate_dsr()
```

***CUIDADO:*** Se você tentar utilizar a função `str_replace_all()` para remover o *símbolo* de adição, ele não irá funcionar pois é um símbolo especial. “Ignore” o caráter especial ao colocar duas barras invertidas na frente, como em `str_replace_call(column, "\\+", "")`.

### Crie um conjunto de dados com uma população padrão

Finalmente, o pacote **PHEindicatormethods**, detalhado [abaixo](#standard_phe), trabalha com as populações padrões unidas aos dados dos países e contagens da população. Então, nós iremos criar um banco de dados chamado `all_data` para isto.

``` r
all_data <- left_join(country_data, standard_pop_clean, by=c("age_cat5", "Sex"))
```

O conjunto de dados inteiro ficou assim:

## 21.3 pacote **PHEindicatormethods**

Calculamos as taxas normalizadas com o pacote **PHEindicatormethods**. Este pacote permite calcular tanto taxas normalizadas diretamente, como taxas normalizadas indiretamente. Nós iremos mostrar como realizar ambos cálculos.

Neste seção, iremos utilizar os dados no objeto `all_data`, criado no fim da seção de Preparação. Estes dados possuem a população dos países, quantidade de mortes, e a população padrão mundial. Você pode vê-lo [aqui](#standard_all).

### Taxas normalizadas diretamente

Abaixo, primeiro agrupamos os dados por País, e então aplicamos a função `calculate_dsr()` para obter taxas diretamente normalizadas por país.

De nota - `calculate_dsr()` precisa da população de referência (padrão) como uma **coluna dentro de uma tabela de dados específica para cada país**. Informe o nome dessa coluna no argumento `stdpop =`. No exemplo abaixo, essa coluna é `pop`.

Para mais informações, utilize `?calculate_dsr`, ou acesse os links na seção de Referências.

``` r
# Calcule as taxas por país diretamente normalizadas para idade e sexo
mortality_ds_rate_phe <- all_data %>%
     group_by(Country) %>%
     PHEindicatormethods::calculate_dsr(
          x = Deaths,                 # coluna com o número observado de eventos
          n = Population,             # coluna com a população não-normalizada para cada estrato
          stdpop = pop)               # populações padronizadas para cada estrato

# Printa a tabela
knitr::kable(mortality_ds_rate_phe)
```

| Country | total_count | total_pop | value | lowercl | uppercl | confidence | statistic | method |
|:---|---:|---:|---:|---:|---:|:---|:---|:---|
| A | 11344 | 86790567 | 23.56686 | 23.08107 | 24.05944 | 95% | dsr per 100000 | Dobson |
| B | 9955 | 52898281 | 19.32549 | 18.45516 | 20.20882 | 95% | dsr per 100000 | Dobson |

### Taxas normalizadas indiretamente

Para normalização indireta, você precisa de uma população de referência com o número de óbitos e a quantidade da população por estrato. Neste exemplo, nós iremos calcular as taxas para o país A *utilizando o país B como população de referência*, uma vez que a população de referência em `standard_pop_clean` não possui a quantidade de mortes por estrato.

Abaixo, primeiro criamos a população de referência do país B. Então, passamos os dados populacionais e de mortalidade do país A, combinamos ele com a população de referência, e passamos para a função `calculate_ISRate()`, para obter taxas indiretamente normalizadas. Claro, você pode fazer isto vice versa.

De nota - no exemplo abaixo, a população de referência é fornecida como um data frame separado. Neste caso, nós garantimos que os vetores `x =`, `n =`, `x_ref =` e `n_ref =` são todos ordenados pelos mesmos valores da categoria de padronização (estrato) como nos nossos dados específicos dos países, uma vez que os registros serão ligados pela posição na tabela.

Para mais informações, utilize `?phr_isr`, ou acesse os links na seção de Referências.

``` r
# Crie a população de referência
refpopCountryB <- country_data %>% 
  filter(Country == "B") 

# Calcule taxas para o país A indiretamente normalizada por idade e sexo
mortality_is_rate_phe_A <- country_data %>%
     filter(Country == "A") %>%
     PHEindicatormethods::calculate_ISRate(
          x = Deaths,                 # coluna com o número observado de eventos
          n = Population,             # coluna com população não padronizada para cada estrato
          x_ref = refpopCountryB$Deaths,  # quantidade referência de mortes  para cada estrato
          n_ref = refpopCountryB$Population)  # população de referência para cada estrato

# Printa a tabela
knitr::kable(mortality_is_rate_phe_A)
```

| observed | expected | ref_rate | value | lowercl | uppercl | confidence | statistic | method |
|---:|---:|---:|---:|---:|---:|:---|:---|:---|
| 11344 | 15847.42 | 18.81914 | 13.47123 | 13.22446 | 13.72145 | 95% | indirectly standardised rate per 100000 | Byars |

## 21.4 Recursos

Para outro exemplo utilizando **PHEindicatormethods**, por favor vá a [esse website](https://mran.microsoft.com/snapshot/2018-10-22/web/packages/PHEindicatormethods/vignettes/IntroductiontoPHEindicatormethods.html)

Veja o arquivo de referência do **PHEindicatormethods** [em pdf](https://cran.r-project.org/web/packages/PHEindicatormethods/PHEindicatormethods.pdf)
