# 45  ディレクトリの操作

この章では、ディレクトリ(フォルダー)の作成、操作、保存、インポートに関する一般的なシナリオを説明します。

## 45.1 準備

### **fs** パッケージ

**fs** パッケージは、R の **base** パッケージ（以下 base R）関数のいくつかを改良し、ディレクトリの操作を簡単にし **tidyverse** パッケージの一部です。以下のセクションでは、しばしば **fs** パッケージからの関数を使用します。

``` r
pacman::p_load(
  fs,             # ファイル、ディレクトリの操作
  rio,            # インポート・エクスポート
  here,           # 相対ファイルパス
  tidyverse)      # データの管理と可視化
```

### ディレクトリをデンドログラムツリーで表示する

**fs** パッケージの `dir_tree()` 関数を使用します。

`path =` にフォルダのファイルパスを指定します。1つの階層のみを表示するには `recurse = FALSE`、全てのサブディレクトリの全てのファイルを表示するには `recurse = TRUE` を指定します。 以下では、`here()` を R プロジェクトの略称として使用し、そのサブフォルダの “data” を指定しています。“data” には、このハンドブックのサンプルデータが格納されています。 “data” とそのサブフォルダ内のすべてのファイルを表示するように設定します。

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

## 45.2 ディレクトリ内のファイルを一覧表示する

ディレクトリ内のファイル名だけをリストアップするには、**base** R の `dir()` を使用します。 例えば、下記のコマンドは R プロジェクトの “example” フォルダの “linelists” サブフォルダ内のファイル名をリストアップしています。相対的なファイルパスは `here()` を使ってえられます (詳しくは [データのインポート・エクスポート](importing.llms.md) 章を参照してください)。

``` r
# ファイル名
dir(here("data", "example", "linelists"))
```

    [1] "20201007linelist.csv"          "case_linelist_2020-10-02.csv" 
    [3] "case_linelist_2020-10-03.csv"  "case_linelist_2020-10-04.csv" 
    [5] "case_linelist_2020-10-05.csv"  "case_linelist_2020-10-08.xlsx"
    [7] "case_linelist20201006.csv"    

ディレクトリのファイルのフルパスをリストアップするには、**fs** パッケージの `dir_ls()` を使用できます。 **base** R を使う場合は `list.files()` です。

``` r
# ファイルパス
dir_ls(here("data", "example", "linelists"))
```

    data/example/linelists/20201007linelist.csv
    data/example/linelists/case_linelist20201006.csv
    data/example/linelists/case_linelist_2020-10-02.csv
    data/example/linelists/case_linelist_2020-10-03.csv
    data/example/linelists/case_linelist_2020-10-04.csv
    data/example/linelists/case_linelist_2020-10-05.csv
    data/example/linelists/case_linelist_2020-10-08.xlsx

ディレクトリ内の各ファイルに関するすべてのメタデータ情報(パス、更新日など)を得るには、 **fs** パッケージの `dir_info()` を使用します。

これは、ファイルの最終更新時刻を抽出したい場合、例えば、最新バージョンのファイルをインポートしたい場合などに特に有効です。この例については、[データのインポート・エクスポート](importing.llms.md) の章を参照してください。

``` r
# ファイル情報
dir_info(here("data", "example", "linelists"))
```

以下は、関数から返されたデータフレームです。すべての列を見るには右にスクロールしてください。

## 45.3 ファイルの情報

特定のファイルに関するメタデータ情報を抽出するには，**fs** パッケージの `file_info()` (または **base** R の `file.info()`) を使用します。

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))
```

ここでは、`$` を使って結果のインデックスを指定し、`modification_time` の値のみを返すようにしています。

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))$modification_time
```

    [1] "2026-11-01 15:52:14 UTC"

## 45.4 存在するか確認する

### R オブジェクト

R オブジェクトが R *の中に*存在するかどうかを調べるには、**base** R の `exists()` を使用します(オブジェクト名を引用符で囲み渡してください)。

``` r
exists("linelist")
```

    [1] FALSE

**base** R パッケージの中には、“data” のような一般的なオブジェクト名を裏で使用しているものがあり、そういったオブジェクトは `inherit = FALSE` が指定されない限り、TRUE として表示されることに注意してください。これが、データセットに “data” という名前をつけない理由の 1 つです。

``` r
exists("data")
```

    [1] TRUE

``` r
exists("data", inherit = FALSE)
```

    [1] FALSE

関数を書く場合、引数として渡した値が存在するかどうかを調べるには `exists()` ではなく、 **base** R の `missing()` を使うべきです。

### ディレクトリ

ディレクトリが存在するかどうかを調べるには，**fs** パッケージの `is_dir()` にファイルパス(とファイル名)を与えてください．右にスクロールすると `TRUE` が表示されていることがわかります。

``` r
is_dir(here("data"))
```

    data 
    TRUE 

代替としては、**base** R の `file.exists()` があります。

### ファイル

特定のファイルが存在するかどうかを調べるには、**fs** パッケージの `is_file()` を使用します。下記の関数の結果を右にスクロールすると `TRUE` が表示されることがわかります。

``` r
is_file(here("data", "case_linelists", "linelist_cleaned.rds"))
```

    data/case_linelists/linelist_cleaned.rds 
                                        TRUE 

**base** R での代替は `file.exists()` です。

## 45.5 作成

### ディレクトリ

新しいディレクトリ(フォルダ)を作成するには、**fs** パッケージの `dir_create()` を使用します。すでにディレクトリが存在する場合は、上書きされず、エラーも返されません。

``` r
dir_create(here("data", "test"))
```

代替として、**base** R の `dir.create()` があります。これはディレクトリがすでに存在する場合はエラーを表示します。一方、`dir_create()` はエラーを返しません。

### ファイル

空のファイルは **fs** パッケージの `file_create()` で作成できます。ファイルがすでに存在する場合は、上書きされたり変更されたりすることはありません。

``` r
file_create(here("data", "test.rds"))
```

**base** R での代替手段は `file.create()` です。しかし、ファイルがすでに存在する場合、この代替手段はファイルの中身を空にします。`file_create()` を使用すれば、ファイルは変更されずに残ります。

### 存在しない場合にのみ作成する

作成中

## 45.6 削除

### R オブジェクト

R オブジェクトを削除するには、**base** R の `rm()` を使用します。

### ディレクトリ

**fs** パッケージの `dir_delete()` を使用します。

### ファイル

**fs** パッケージの `file_delete()` でファイルを削除できます。

## 45.7 他のファイルを実行する

### `source()`

ある R スクリプトを別の R スクリプト中から実行する場合、**base** R の `source()` コマンドを使用できます。

``` r
source(here("scripts", "cleaning_scripts", "clean_testing_data.R"))
```

以下は、上記の R スクリプトを表示し、スクリプトの右上にある “Source” ボタンをクリックすることと同じです。これはスクリプトを実行しますが、特に意図しない限り出力なく実行されます(R コンソールへの出力はありません)。\[Interactive console\] の章で、`source()` を使って R コンソールでユーザーと対話する例を参照してください。

[![](../../images/source_button.png)](../../images/source_button.png)

### `render()`

`render()` は `source()` のバリエーションで、R markdown のスクリプトで最もよく使用されます。R markdown ファイルを `input =` に指定し、`output_format =` (典型的には “html_document”、“pdf_document”、“word_document”、“” のいずれか) を指定します。

詳しくは [R Markdown で作るレポート](rmarkdown.llms.md) をご覧ください。また `render()` のドキュメントを[こちらから](https://rmarkdown.rstudio.com/docs/reference/render.html)、もしくは `?render` と入力して参照してください。

### ディレクトリ内のファイルを実行する

*for ループ* を作成し、それを使って `dir()` で識別されるディレクトリ内のすべてのファイルを `source()` できます。

``` r
for(script in dir(here("scripts"), pattern = ".R$")) {   # R プロジェクトの "scripts" フォルダにある各スクリプト名(拡張子 .R)に対して
  source(here("scripts", script))                        # scripts フォルダに存在する、同じ名前のファイルをソースとする
}
```

特定のスクリプトだけを実行したい場合は、次のように名前で識別できます。

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

こちらは **fs** パッケージの関数と **base** R 関数の[比較](https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html)です。

### ディレクトリ内のファイルをインポートする

個別のファイルのインポートとエクスポートについては、[データのインポート・エクスポート](importing.llms.md) の章をご覧ください。

また、ファイル名に含まれる日付をもとに、*または*ファイルのメタデータを見て、自動的に最新のファイルをインポートする方法についても [データのインポート・エクスポート](importing.llms.md) の章を参照してください。

**purrr** パッケージによるデモの例については、[ループと反復処理・リストの操作](iteration.llms.md) の章を参照してください:

- データフレームを分割し、複数の CSV ファイルとして保存する
- データフレームを分割し、1つの Excel ワークブック内で各パーツを別のシートとして保存する
- 複数の CSV ファイルを取り込み、1 つのデータフレームにまとめる
- 複数のシートを持つ Excel ワークブックをインポートして、1 つのデータフレームにまとめる

## 45.8 **base** R

以下の `list.files()` と `dir()` 関数をご覧ください。これらは指定したディレクトリ内のファイルをリストアップするという同じ操作を行います。 `ignore.case =` や検索する特定のパターンを指定できます。

``` r
list.files(path = here("data"))

list.files(path = here("data", "example"), pattern = "\\.csv$")
# dir(path = here("data", "example"), pattern = "\\.csv$")

list.files(path = here("data", "example"), pattern = "hospital", ignore.case = TRUE)
```

現在「開いている」ファイルは、「~\$hospital_linelists.xlsx」のように、先頭にチルダを付けてフォルダ内に表示されます。

## 45.9 参考資料

https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html
