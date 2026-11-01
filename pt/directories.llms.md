# 45  Interações de diretório

Nesta página, cobrimos cenários comuns onde você cria, interage, salva e importa com diretórios (pastas).

## 45.1 Preparação

### Pacote **fs**

O **fs** é um pacote do **tidyverse** que facilita as interações de diretório, melhorando algumas das funções do R **base**. Nas seções a seguir, usaremos frequentemente as funções do **fs**.

``` r
pacman::p_load(
  fs,             # Interações de arquivo / diretório
  rio,            # Importar / Exportar
  here,           # Caminhos de arquivo respectivos
  tidyverse)      # Gerenciamento e visualização de dados
```

### Imprimir diretório como uma árvore de dendrograma

Use a função `dir_tree()` do **fs**.

Forneça o caminho da pasta do arquivo para `path =`. Use `recurse = FALSE` para mostrar apenas um nível, ou `recurse = TRUE` para mostrar todos os arquivos em todos os subníveis. Abaixo, usamos `here()` como uma abreviação para o projeto R e especificamos sua subpasta “data” (dados), que contém os dados de exemplo deste manual. Nós o configuramos para exibir todos os arquivos na pasta supra citada e suas subpastas.

``` r
fs::dir_tree(path = here("data"), recurse = TRUE)
```

    data
    ├── case_linelists
    │   └── linelist_cleaned.rds
    ├── example
    │   ├── central_hospital.csv
    │   ├── district_weekly_count_data.xlsx
    │   ├── fluh7n9_china_2013.csv
    │   ├── hospital_linelists.xlsx
    │   ├── linelists
    │   │   ├── 20201007linelist.csv
    │   │   ├── case_linelist20201006.csv
    │   │   ├── case_linelist_2020-10-02.csv
    │   │   ├── case_linelist_2020-10-03.csv
    │   │   ├── case_linelist_2020-10-04.csv
    │   │   ├── case_linelist_2020-10-05.csv
    │   │   └── case_linelist_2020-10-08.xlsx
    │   ├── military_hospital.csv
    │   ├── missing.csv
    │   ├── other.csv
    │   ├── port_hospital.csv
    │   └── st_marks_maternity_hospital.csv
    ├── flexdashboard
    │   ├── outbreak_dashboard.Rmd
    │   ├── outbreak_dashboard.html
    │   └── outbreak_dashboard_test.html
    └── malaria_app
        ├── app.R
        ├── data
        │   └── facility_count_data.rds
        ├── funcs
        │   └── plot_epicurve.R
        ├── global.R
        ├── malaria_app.Rproj
        ├── server.R
        └── ui.R

## 45.2 Listar arquivos em um diretório

Para listar apenas os nomes dos arquivos em um diretório, você pode usar `dir()` do R **base**. Por exemplo, este comando lista os nomes dos arquivos na subpasta “linelists” da pasta “example” em um projeto R. O caminho de arquivo respectivo é fornecido usando `here()` (sobre o qual você pode ler mais na página [Importar e exportar](importing.llms.md)).

``` r
# Nomes de arquivos
dir(here("data", "example", "linelists"))
```

    [1] "20201007linelist.csv"          "case_linelist_2020-10-02.csv" 
    [3] "case_linelist_2020-10-03.csv"  "case_linelist_2020-10-04.csv" 
    [5] "case_linelist_2020-10-05.csv"  "case_linelist_2020-10-08.xlsx"
    [7] "case_linelist20201006.csv"    

Para listar os caminhos completos dos arquivos do diretório, você pode usar `dir_ls()` de **fs**. Uma alternativa é `list.files()` do R **base** .

``` r
# Caminhos de arquivos
dir_ls(here("data", "example", "linelists"))
```

    data/example/linelists/20201007linelist.csv
    data/example/linelists/case_linelist20201006.csv
    data/example/linelists/case_linelist_2020-10-02.csv
    data/example/linelists/case_linelist_2020-10-03.csv
    data/example/linelists/case_linelist_2020-10-04.csv
    data/example/linelists/case_linelist_2020-10-05.csv
    data/example/linelists/case_linelist_2020-10-08.xlsx

Para obter todas as informações de metadados sobre cada arquivo em um diretório (por exemplo, caminho, data de modificação, etc.), você pode usar `dir_info()` de **fs**.

Isso pode ser particularmente útil se você deseja extrair a hora da última modificação do arquivo, por exemplo, se deseja importar a versão mais recente. Para obter um exemplo disso, consulte a página [Importar e exportar](importing.llms.md).

``` r
# Informações do arquivo
dir_info(here("data", "example", "linelists"))
```

Aqui está o dataframe que retorna. Role para a direita para ver todas as colunas.

## 45.3 Informações do arquivo

Para extrair informações de metadados sobre um arquivo específico, você pode usar `file_info()` de **fs** (ou `file.info()` do R **base**).

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))
```

Aqui usamos o `$` para indexar o resultado e retornar apenas o valor `modification_time`.

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))$modification_time
```

    [1] "2026-11-01 15:52:14 UTC"

## 45.4 Verifique se existe

### Objetos R

Você pode usar `exists()` do R **base** para verificar se um objeto existe *dentro do* R (forneça o nome do objeto entre aspas).

``` r
exists("linelist")
```

    [1] FALSE

Observe que alguns pacotes do R **base** usam nomes de objetos genéricos como “data” (que significa “dados” em inglês) nos bastidores, que aparecerão como TRUE a menos que `inherit = FALSE` seja especificado. Este é um dos motivos para não nomear o conjunto de dados como “data”.

``` r
exists("data")
```

    [1] TRUE

``` r
exists("data", inherit = FALSE)
```

    [1] FALSE

Se você está escrevendo uma função, deve usar `missing()` do R **base** para verificar se um argumento está presente ou não, ao invés de `exists()`.

### Diretórios

Para verificar se existe um diretório, forneça o caminho do arquivo (e nome do arquivo) para `is_dir()` de **fs**. Role para a direita para ver que retorna `TRUE`.

``` r
is_dir(here("data"))
```

    data 
    TRUE 

Uma alternativa é `file.exists()` do R **base**.

### Arquivos

Para verificar se um arquivo específico existe, use `is_file()` de **fs**. Role para a direita para ver que retorna `TRUE`.

``` r
is_file(here("data", "case_linelists", "linelist_cleaned.rds"))
```

    data/case_linelists/linelist_cleaned.rds 
                                        TRUE 

Uma alternativa no R **base** é `file.exists()`.

## 45.5 Criar

### Diretórios

Para criar um novo diretório (pasta), você pode usar `dir_create()` de **fs**. Se o diretório já existir, ele não será criado novamente e não será retornado nenhum erro.

``` r
dir_create(here("data", "test"))
```

Uma alternativa é `dir.create()` do R **base**, que mostrará um erro se o diretório já existir. Em contraste, `dir_create()` neste cenário será silencioso.

### Arquivos

Você pode criar um arquivo (vazio) com `file_create()` de **fs**. Se o arquivo já existir, ele não será criado novamente ou alterado.

``` r
file_create(here("data", "test.rds"))
```

`file.create()` é uma alternativa no R **base**. Mas se o arquivo já existe, esta opção irá truncá-lo. Se você usar `file_create()` o arquivo não será alterado.

### Criar se não existir

EM CONSTRUÇÃO

## 45.6 Deletar

### Objetos R

Use `rm()` do R **base** para remover um objeto R.

### Diretórios

Use `dir_delete()` de **fs**.

### Arquivos

Você pode excluir arquivos com `file_delete()` de **fs**.

## 45.7 Executando outros arquivos

### `source()`

Para executar um script R a partir de outro script R, você pode usar o comando `source()` (do R **base**).

``` r
source(here("scripts", "cleaning_scripts", "clean_testing_data.R"))
```

Isso é equivalente a visualizar o script R acima e clicar no botão “Source” (Fonte) no canto superior direito do script. Isso executará o script, mas silenciosamente (sem saída para o console do R), a menos que seja especificada esta intenção. Veja a página \[Console interativo\] para exemplos de uso da `source()` para interagir com um usuário através do console R no modo pergunta e resposta.

[![](../../images/source_button.png)](../../images/source_button.png)

### `render()`

`render()` é uma variação de `source()` mais frequentemente usada para scripts R markdown. Você fornece o `input =` que é o arquivo Rmarkdown (.Rmd), e também o `output_format =` (normalmente “html_document”, “pdf_document”, “word_document”, ““)

Consulte a página [Relatórios com R Markdown](rmarkdown.llms.md) para obter mais detalhes. Veja também a documentação para `render()` [aqui](https://rmarkdown.rstudio.com/docs/reference/render.html) ou inserindo `?render`.

### Executar arquivos em um diretório

Você pode criar um *for loop* e usá-lo em `source()` para todos os arquivos em um diretório, identificado com `dir()`. with `dir()`.

``` r
for(script in dir(here("scripts"), pattern = ".R$")) {   # Para cada nome de script na pasta "scripts" do Projeto R (com extensão .R)
  source(here("scripts", script))                        # Fonte dos arquivos com nomes correspondentes aos encontrados na pasta de scripts
}
```

Se você deseja apenas executar determinados scripts, pode identificá-los pelos nomes da seguinte forma:

``` r
scripts_to_run <- c(
     "epicurves.R",
     "demographic_tables.R",
     "survival_curves.R"
)

for(script in scripts_to_run) {
  source(here("scripts", script))
}
```

Aqui está uma [comparação](https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html) das funções de **fs** e R **base**.

### Importar arquivos em um diretório

Consulte a página [Importar e exportar](importing.llms.md) para importar e exportar arquivos individuais.

Consulte também a página [Importar e exportar](importing.llms.md) para métodos que importem automaticamente o arquivo mais recente, com base em uma data no nome do arquivo *ou* nos metadados do arquivo.

Veja na página [Iteração, loops e listas](iteration.llms.md) um exemplo com o pacote **purrr** demonstrando:

- Dividir um dataframe e salvá-lo como vários arquivos CSV
- Dividir um dataframe e salvar cada parte em uma planilha separada dentro de uma pasta de trabalho do Excel
- Importar vários arquivos CSV e combiná-los em um dataframe
- Importar uma pasta de trabalho do Excel com várias planilhas e combiná-las em um único dataframe

## 45.8 R **base**

Veja abaixo as funções `list.files()` e `dir()`, que realizam a mesma operação de listar arquivos dentro de um diretório especificado. Você pode especificar `ignore.case =` ou um padrão específico para procurar.

``` r
list.files(path = here("data"))

list.files(path = here("data", "example"), pattern = "\\.csv$")
# dir(path = here("data", "example"), pattern = "\\.csv$")

list.files(path = here("data", "example"), pattern = "hospital", ignore.case = TRUE)
```

Se um arquivo estiver “aberto” no momento, ele será exibido em sua pasta com um til na frente, como “~\$hospital_linelists.xlsx”.

## 45.9 Recursos

https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html
