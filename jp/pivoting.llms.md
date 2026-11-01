# 12  データの縦横変換

[![](../../images/pivoting/pivoting_500x500.png)](../../images/pivoting/pivoting_500x500.png)

データを管理する上で、*ピボットする*とは次の 2 つの工程のどちらかを指しています。

1.  *ピボットテーブル*（大きなデータテーブルを要約した統計表）を作成すること。
2.  表を縦長形式から横長形式へ、またはその逆へ変換すること。

**このページでは、後者の定義に焦点をあてます。**前者はデータ解析の重要なステップであり、[データのグループ化](grouping.llms.md) および [記述統計表の作り方](tables_descriptive.llms.md) の章で別に取り上げています。

本章では、データの形式について説明します。個々の変数が 1 つの列を持ち、個々の観測値が 1 つの行を持ち、個々の値が 1 つのセルを持つという「整然データ（tidy data）」の考え方を知っておくと便利です。このトピックについて詳しくは、R for Data Science の [こちら](https://r4ds.had.co.nz/tidy-data.html) の章をご参照ください。

## 12.1 準備

### パッケージの読み込み

以下のコードを実行すると、分析に必要なパッケージが読み込まれます。このハンドブックでは、パッケージを読み込むために、**pacman** パッケージの `p_load()` を主に使用しています。`p_load()` は、必要に応じてパッケージをインストールし、現在の R セッションで使用するためにパッケージを読み込む関数です。また、すでにインストールされたパッケージは、R の基本パッケージである **base** の `library()` を使用して読み込むこともできます。R のパッケージについて詳しくは [R の基礎](basics.llms.md) の章をご参照ください。

``` r
pacman::p_load(
  rio,          # ファイルをインポートする
  here,         # ファイルの場所を指定する
  kableExtra,   # Build and manipulate complex tables
  tidyverse,    # データ管理と ggplot2 を使用したデータ可視化のパッケージ
  appliedepidata) # 本ハンドブックで使用するサンプルデータ
```

### データのインポート

### マラリアの症例数のデータ

この章では、日ごとのマラリアの症例数について、施設別、年齢層別の架空のデータセットを使用します。`appliedepidata::get_data(name = "malaria_facility_count_data")` で直接読み込めます（詳細は[ハンドブックとデータのダウンロード](download.llms.md)のページを参照）。

``` r
# データをインポートする
count_data <- appliedepidata::get_data(name = "malaria_facility_count_data")
```

最初の 50 行を以下に表示します。

### 症例データのラインリスト

この章の後半では、エボラ出血熱の流行をシミュレーションした症例データセットも使用します。`appliedepidata::get_data(name = "linelist_cleaned_rds")` で直接読み込めます（詳細は[ハンドブックとデータのダウンロード](download.llms.md)のページを参照）。

``` r
# データセットをインポートする
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

## 12.2 横長から縦長へ

[![](../../images/pivoting/pivot_longer_new.png)](../../images/pivoting/pivot_longer_new.png)

### 「横長」形式

データは「横長」形式で入力・保存されることがよくあります。つまり、研究対象者の特性や回答が 1 つの行に保存されるのです。この形式は表示する上では便利かもしれませんが、一部の分析には適していません。

先述の準備のセクションでインポートした `count_data` のデータセットを例にとってみましょう。各行が「施設利用日」を表していることがわかります。実際の症例数（1 番右の列）は「横長」形式で格納されており、ある施設利用日のすべての年齢層の情報が 1 行に格納されています。

このデータセットのそれぞれの観測値は、 2020-05-16 から 2020-08-12 までのある日付の、 65 施設のうちの 1 施設におけるマラリアの症例数を指しています。これらの施設は、1 つの `Province` （North）と 4 つの`District`（Spring、Bolo、Dingo、Barnard）に位置しています。このデータセットでは、マラリアの 総症例数と、3 つの年齢層（4 歳未満、5 ～ 14 歳、15 歳以上）におけるマラリアの症例数が含まれています。

このような「横長」のデータは、列見出しが実際には「変数」を表しておらず、仮想的な「年齢層」の*値*を表しているため、「整然データ」の基準に従っているとは言えません。

この形式は、情報を表で表示したり、症例報告書からデータを入力（Excel など）する際に便利です。しかし、解析段階においては、通常、これらのデータは「整然データ」基準に沿った「縦長」形式に変換した方が扱いやすいです。特に R パッケージの **ggplot2** は、データが 「縦長」形式である場合に最適に機能します。

マラリアの*総*症例数を時系列で視覚化することは、現在のデータ形式でも難しくありません。

``` r
count_data %>% 
  drop_na(malaria_tot) %>% 
  ggplot() +
  geom_col(aes(x = data_date, y = malaria_tot), width = 1)
```

[![](pivoting_files/figure-html/unnamed-chunk-10-1.png)](pivoting_files/figure-html/unnamed-chunk-10-1.png)

しかし、この総症例数に対する各年齢層の相対的な寄与を表示したいとしたらどうでしょうか。この場合、関心のある変数（年齢層）が単一の列としてデータセットに含まれていることを確認する必要があります。関心のある変数が単一の列であれば、[ggplot2](https://ggplot2.tidyverse.org/) で図の「見栄え」を調整する `aes()` 引数で指定することができます。

### `pivot_longer()`

**tidyr** の関数 `pivot_longer()` は、データを「長く」します。**tidyr** は、R パッケージの **tidyverse** の一部です。

`pivot_longer()` は、変換する列の範囲（`cols =` に指定）を受け取ります。したがって、データセットの一部だけを操作することが可能です。ここでは、症例数の列だけをピボットしたいので、この関数は、マラリアのデータに適しています。

この処理では、2 つの「新しい」列が作成されます。1 つはカテゴリ（以前の列名）で、もう 1 つは対応する値（例：症例数）で構成されます。これらの新しい列の名前は、初期値のままでも構いませんが、`names_to =` や `values_to =` を用いて独自の名前を指定することもできます。

それでは、`pivot_longer()` を実際に使ってみましょう。

### 標準的な縦横変換

**tidyr** の `pivot_longer()` を使用し、「横長」データを 「縦長」 形式に変換していきます。具体的には、マラリアの症例数のデータを表す 4 つの数値列を、*年齢層*を保持する列と対応する*値*を保持する列の 2 つの新しい列に変換します。

``` r
df_long <- count_data %>% 
  pivot_longer(
    cols = c(`malaria_rdt_0-4`, `malaria_rdt_5-14`, `malaria_rdt_15`, `malaria_tot`)
  )

df_long
```

新しく作成されたデータフレーム（`df_long`）は行数が増え（12,152 vs 3,038）、縦に*長く*なっていることに注目してください。元のデータセットの各行が、`df_long` では 4 行に別れ、`df_long` の長さは元のデータセットの 4 倍の長さになっています。4 行に別れた行はそれぞれ、年齢層（4 歳未満、5 ～ 14 歳、15 歳以上、総数）ごとのマラリアの症例数を表しています。

新しいデータセットは、長くなっただけでなく、列の数が 10 から 8 に減っています。元のデータセットでは 4 つの列（`malaria_` で始まる列）に格納されていたデータが、新しいデータセットでは 2 つの列に格納されているためです。

これらの 4 つの列の列名はすべて `malaria_` で始まるので、便利な “tidyselect” 関数である `starts_with()` を使用しても同じ結果を得ることができます（これらのヘルパー関数についての詳細は、[データクリーニングと主要関数](cleaning.llms.md) の章をご参照ください）。

``` r
# tidyselectのヘルパー関数で列を指定する
count_data %>% 
  pivot_longer(
    cols = starts_with("malaria_")
  )
```

    # A tibble: 12,152 × 8
       location_name data_date  submitted_date Province District newid name    value
       <chr>         <date>     <date>         <chr>    <chr>    <int> <chr>   <int>
     1 Facility 1    2020-08-11 2020-08-12     North    Spring       1 malari…    11
     2 Facility 1    2020-08-11 2020-08-12     North    Spring       1 malari…    12
     3 Facility 1    2020-08-11 2020-08-12     North    Spring       1 malari…    23
     4 Facility 1    2020-08-11 2020-08-12     North    Spring       1 malari…    46
     5 Facility 2    2020-08-11 2020-08-12     North    Bolo         2 malari…    11
     6 Facility 2    2020-08-11 2020-08-12     North    Bolo         2 malari…    10
     7 Facility 2    2020-08-11 2020-08-12     North    Bolo         2 malari…     5
     8 Facility 2    2020-08-11 2020-08-12     North    Bolo         2 malari…    26
     9 Facility 3    2020-08-11 2020-08-12     North    Dingo        3 malari…     8
    10 Facility 3    2020-08-11 2020-08-12     North    Dingo        3 malari…     5
    # ℹ 12,142 more rows

位置による指定

``` r
# 位置で列を指定する
count_data %>% 
  pivot_longer(
    cols = 6:9
  )
```

列名の範囲による指定

``` r
# 連続する列の範囲を指定する
count_data %>% 
  pivot_longer(
    cols = `malaria_rdt_0-4`:malaria_tot
  )
```

この 2 つの新しい列には `name` と `value` という初期値の列名が与えられていますが、`names_to` と `values_to` という引数を使うことで、これらを上書きして、より意味のある列名を付けることができます。そうしておくと、その列に何の変数が格納されているかを思い出すのに便利です。ここでは、`age_group` と `counts` という列名をつけてみましょう。

``` r
df_long <- 
  count_data %>% 
  pivot_longer(
    cols = starts_with("malaria_"),
    names_to = "age_group",
    values_to = "counts"
  )

df_long
```

    # A tibble: 12,152 × 8
       location_name data_date  submitted_date Province District newid age_group    
       <chr>         <date>     <date>         <chr>    <chr>    <int> <chr>        
     1 Facility 1    2020-08-11 2020-08-12     North    Spring       1 malaria_rdt_…
     2 Facility 1    2020-08-11 2020-08-12     North    Spring       1 malaria_rdt_…
     3 Facility 1    2020-08-11 2020-08-12     North    Spring       1 malaria_rdt_…
     4 Facility 1    2020-08-11 2020-08-12     North    Spring       1 malaria_tot  
     5 Facility 2    2020-08-11 2020-08-12     North    Bolo         2 malaria_rdt_…
     6 Facility 2    2020-08-11 2020-08-12     North    Bolo         2 malaria_rdt_…
     7 Facility 2    2020-08-11 2020-08-12     North    Bolo         2 malaria_rdt_…
     8 Facility 2    2020-08-11 2020-08-12     North    Bolo         2 malaria_tot  
     9 Facility 3    2020-08-11 2020-08-12     North    Dingo        3 malaria_rdt_…
    10 Facility 3    2020-08-11 2020-08-12     North    Dingo        3 malaria_rdt_…
    # ℹ 12,142 more rows
    # ℹ 1 more variable: counts <int>

この新しいデータセットを [ggplot2](https://ggplot2.tidyverse.org/) に渡して、新しい列 `count` を Y 軸に、もう一つの新しい列 `age_group` を `fill =` 引数（列の色）に指定することができます。以下のコードを実行すると、マラリアの症例数を年齢層ごとに積み上げた棒グラフが作成されます。

``` r
df_long %>% 
  drop_na(counts) %>% 
  ggplot() +
  geom_col(
    mapping = aes(x = data_date, y = counts, fill = age_group),
    width = 1
  )
```

[![](pivoting_files/figure-html/unnamed-chunk-16-1.png)](pivoting_files/figure-html/unnamed-chunk-16-1.png)

この新しいプロットと先ほど作ったプロットを比較してみてください。*問題点に気づきましたか？*

調査データを扱うときによくある問題に遭遇しました。`malaria_tot` 列からの総症例数も含まれているため、プロットの各棒の大きさは、実際の大きさの 2 倍になっています。

この問題はいくつかの方法で対処することができます。一つの方法としては、`ggplot()` に渡す前に、データセットから総症例数を単純に除外することです。

``` r
df_long %>% 
  filter(age_group != "malaria_tot") %>% 
  drop_na(counts) %>% 
  ggplot() +
  geom_col(
    aes(x = data_date, y = counts, fill = age_group),
    width = 1
  )
```

[![](pivoting_files/figure-html/unnamed-chunk-17-1.png)](pivoting_files/figure-html/unnamed-chunk-17-1.png)

また、もう一つの方法として、`pivot_longer()` を実行する際にこの変数（`malaria_tot` 列）を除くことで、別の変数としてデータセットに保持することも可能です。新しい行を埋めるために、この変数の値がどのように「拡張」されるかを見てみましょう。

``` r
count_data %>% 
  pivot_longer(
    cols = `malaria_rdt_0-4`:malaria_rdt_15,   # 総症例数の列は含まない
    names_to = "age_group",
    values_to = "counts"
  )
```

    # A tibble: 9,114 × 9
       location_name data_date  submitted_date Province District malaria_tot newid
       <chr>         <date>     <date>         <chr>    <chr>          <int> <int>
     1 Facility 1    2020-08-11 2020-08-12     North    Spring            46     1
     2 Facility 1    2020-08-11 2020-08-12     North    Spring            46     1
     3 Facility 1    2020-08-11 2020-08-12     North    Spring            46     1
     4 Facility 2    2020-08-11 2020-08-12     North    Bolo              26     2
     5 Facility 2    2020-08-11 2020-08-12     North    Bolo              26     2
     6 Facility 2    2020-08-11 2020-08-12     North    Bolo              26     2
     7 Facility 3    2020-08-11 2020-08-12     North    Dingo             18     3
     8 Facility 3    2020-08-11 2020-08-12     North    Dingo             18     3
     9 Facility 3    2020-08-11 2020-08-12     North    Dingo             18     3
    10 Facility 4    2020-08-11 2020-08-12     North    Bolo              49     4
    # ℹ 9,104 more rows
    # ℹ 2 more variables: age_group <chr>, counts <int>

### 複数のデータ型を含むデータのピボット

上記の例は、「縦長変換する」列がすべて同じデータ型（文字型、数字型、ロジカル型など）である場合にうまく機能します。

しかし、疫学者や疫学業務担当者が扱う仕事の領域では、非専門家によって作成され、独特で標準的ではない論理に従ったデータを扱う場合が多くあります。Hadley Wickham は、**Tidy Data** の原則に関する彼の[重要な論文](https://vita.had.co.nz/papers/tidy-data.pdf)で（Tolstoy の一文を参照して）次のように指摘しています。「整然データセットは家族のように、どれも似ているが、乱雑なデータセットは乱雑のあり方がそれぞれ異なっている。」

特によくある問題は、異なるデータ型のデータを含む列をピボットする必要があることです。このピボットでは、これらの異なるデータ型を 1 つの列に格納することになりますが、これは好ましい状況ではありません。これによって生じた混乱を切り分けるためには様々なアプローチがありますが、`pivot_longer()` を使用して、自分でこのような状況を作らないようにするための重要なステップがあります。

3 つの項目 A 、B、C のそれぞれについて、異なる時点で時系列による観測が行われた状況を考えてみましょう。例えば、個人（エボラ出血熱患者の接触者を 21 日間毎日追跡する）や、遠隔地の村の保健所がまだ機能しているかどうか年に 1 回確認することなどが挙げられます。接触者追跡の例を使ってみましょう。データが以下のように保存されているとします。

見ての通り、少し複雑なデータになっています。各行には 1 つの項目に関する情報が格納されていますが、時間が進むにつれて時系列がどんどん右に流れています。さらに、列のデータ型は日付型と文字型が交互になっています。

筆者が遭遇した特にひどい例は、コレラの調査データで、**4 年間***毎日* 8 列の新しい観測値が追加されたものでした。筆者のノートパソコンでは、このデータが保存されている Excel ファイルを開くだけで 10 分以上かかりました！

このデータを扱うには、データフレームを縦長形式に変換する必要がありますが、各項目の観測ごとに、日付型の列（`date` 列）と文字型の列（`character` 列; status を表す列）の分離を維持する必要があります。そうしないと、1 つの列の中に変数の種類が混在してしまう可能性があるからです（データ管理や整然データにおいて、一番「やってはいけないこと」です）。

``` r
df %>% 
  pivot_longer(
    cols = -id,
    names_to = c("observation")
  )
```

    # A tibble: 18 × 3
       id    observation value     
       <chr> <chr>       <chr>     
     1 A     obs1_date   2021-04-23
     2 A     obs1_status Healthy   
     3 A     obs2_date   2021-04-24
     4 A     obs2_status Healthy   
     5 A     obs3_date   2021-04-25
     6 A     obs3_status Unwell    
     7 B     obs1_date   2021-04-23
     8 B     obs1_status Healthy   
     9 B     obs2_date   2021-04-24
    10 B     obs2_status Healthy   
    11 B     obs3_date   2021-04-25
    12 B     obs3_status Healthy   
    13 C     obs1_date   2021-04-23
    14 C     obs1_status Missing   
    15 C     obs2_date   2021-04-24
    16 C     obs2_status Healthy   
    17 C     obs3_date   2021-04-25
    18 C     obs3_status Healthy   

上記では、ピボットによって日付列と文字列が 1 つの列の `value` に統合されています。R は列全体を文字型に変換することで対応し、日付の機能は失われています。

このような事態を防ぐには、元の列名の構文構造を利用します。このデータセットでは、観測番号、アンダースコア、そして “status” または “date” のいずれかを用いた共通の命名構造があります。この構文を利用して、ピボットした後にこれら 2 つのデータ型を別々の列に保持することが可能です。

この操作を行う手順は、以下の通りです。

- `names_to =` 引数に文字ベクトルを指定し、2 番目の項目に (`".value"`) を指定する。この特別な用語は、ピボットした列がその列名に含まれる文字に基づいて分割されることを示します。

- また、`names_sep =` の引数には、「分割」する文字を指定する必要があります。ここでは、アンダースコア “\_” です。

このように、新しい列の命名と分割は、既存の列名のアンダースコア “\_” を中心に行われる。

``` r
df_long <- 
  df %>% 
  pivot_longer(
    cols = -id,
    names_to = c("observation", ".value"),
    names_sep = "_"
  )

df_long
```

    # A tibble: 9 × 4
      id    observation date       status 
      <chr> <chr>       <chr>      <chr>  
    1 A     obs1        2021-04-23 Healthy
    2 A     obs2        2021-04-24 Healthy
    3 A     obs3        2021-04-25 Unwell 
    4 B     obs1        2021-04-23 Healthy
    5 B     obs2        2021-04-24 Healthy
    6 B     obs3        2021-04-25 Healthy
    7 C     obs1        2021-04-23 Missing
    8 C     obs2        2021-04-24 Healthy
    9 C     obs3        2021-04-25 Healthy

**仕上げに**

`date` 列は現在*文字型*であることに注意してください。[日付型データ](dates.llms.md) の章で説明した `mutate()` と `as_date()` 関数を使用すると、適切な日付型に簡単に変換できます。

また、**stringr** パッケージの `str_remove_all()` を使用し、“obs” を削除して数値形式に変換することで、 `observation` 列も数字型（`numeric`）に変換できます（詳しくは、[文字型データ](characters_strings.llms.md) の章をご参照ください）。

``` r
df_long <- 
  df_long %>% 
  mutate(
    date = date %>% lubridate::as_date(),
    observation = 
      observation %>% 
      str_remove_all("obs") %>% 
      as.numeric()
  )

df_long
```

    # A tibble: 9 × 4
      id    observation date       status 
      <chr>       <dbl> <date>     <chr>  
    1 A               1 2021-04-23 Healthy
    2 A               2 2021-04-24 Healthy
    3 A               3 2021-04-25 Unwell 
    4 B               1 2021-04-23 Healthy
    5 B               2 2021-04-24 Healthy
    6 B               3 2021-04-25 Healthy
    7 C               1 2021-04-23 Missing
    8 C               2 2021-04-24 Healthy
    9 C               3 2021-04-25 Healthy

そして、この形式のデータを用いることにより、例えば、記述的なヒートマップをプロットするなどの作業を始めることができます。

``` r
ggplot(data = df_long, mapping = aes(x = date, y = id, fill = status)) +
  geom_tile(colour = "black") +
  scale_fill_manual(
    values = 
      c("Healthy" = "lightgreen", 
        "Unwell" = "red", 
        "Missing" = "orange")
  )
```

[![](pivoting_files/figure-html/unnamed-chunk-23-1.png)](pivoting_files/figure-html/unnamed-chunk-23-1.png)

## 12.3 縦長から横長へ

[![](../../images/pivoting/pivot_wider_new.png)](../../images/pivoting/pivot_wider_new.png)

場合によっては、データセットを横長形式に変換したいことがあります。このような場合は、`pivot_wider()` 関数を使用します。

典型的な使用例としては、分析結果を読み手にとって理解しやすい形式（[見やすい表の作り方](tables_presentation.llms.md) の章を参照）に変換する場合です。つまり、1 つの主題に関する情報が複数の行にまたがっているデータセットを、その情報が 1 つの行に格納される形式に変換することが必要な場合です。

### データ

この章では、1 つの症例が1 行に含まれる症例ラインリスト（[準備](#pivot_prep) のセクションを参照）を使用することにします。

以下に、最初の 50 行を示します。

例えば、性別で年齢層ごとの個体数を知りたいとします。

``` r
df_wide <- 
  linelist %>% 
  count(age_cat, gender)

df_wide
```

       age_cat gender   n
    1      0-4      f 640
    2      0-4      m 416
    3      0-4   <NA>  39
    4      5-9      f 641
    5      5-9      m 412
    6      5-9   <NA>  42
    7    10-14      f 518
    8    10-14      m 383
    9    10-14   <NA>  40
    10   15-19      f 359
    11   15-19      m 364
    12   15-19   <NA>  20
    13   20-29      f 468
    14   20-29      m 575
    15   20-29   <NA>  30
    16   30-49      f 179
    17   30-49      m 557
    18   30-49   <NA>  18
    19   50-69      f   2
    20   50-69      m  91
    21   50-69   <NA>   2
    22     70+      m   5
    23     70+   <NA>   1
    24    <NA>   <NA>  86

これは縦長のデータセットで、**ggplot2** での視覚化には最適ですが、表での表示には適していません。

``` r
ggplot(df_wide) +
  geom_col(aes(x = age_cat, y = n, fill = gender))
```

[![](pivoting_files/figure-html/unnamed-chunk-27-1.png)](pivoting_files/figure-html/unnamed-chunk-27-1.png)

### `pivot_wider()`

そのため、`pivot_wider()` を使用し、データを報告書に表として載せるのに適した形式に変換していきます。  
引数 `names_from` は、新しい*列名*を生成する*ための*列を指定し、引数 `values_from` は、セルに入力する*値*を取得する*ための*列を指定します。`id_cols =` はオプションですが、ピボット化されるべきでない列名のベクトルを提供することができ、これによって各行を識別することができます。

``` r
table_wide <- 
  df_wide %>% 
  pivot_wider(
    id_cols = age_cat,
    names_from = gender,
    values_from = n
  )

table_wide
```

    # A tibble: 9 × 4
      age_cat     f     m  `NA`
      <fct>   <int> <int> <int>
    1 0-4       640   416    39
    2 5-9       641   412    42
    3 10-14     518   383    40
    4 15-19     359   364    20
    5 20-29     468   575    30
    6 30-49     179   557    18
    7 50-69       2    91     2
    8 70+        NA     5     1
    9 <NA>       NA    NA    86

この表は、より読みやすいので、報告書に掲載するのに適しています。さらに、**flextable** や **knitr** などのパッケージを使うと、よりきれいな表に編集することができます。編集する方法は、[見やすい表の作り方](tables_presentation.llms.md) の章で詳しく説明されています。

``` r
table_wide %>% 
  janitor::adorn_totals(c("row", "col")) %>% # 行と列の合計を表示する
  knitr::kable() %>% 
  kableExtra::row_spec(row = 10, bold = TRUE) %>% 
  kableExtra::column_spec(column = 5, bold = TRUE) 
```

| age_cat |    f |    m |  NA | Total |
|:--------|-----:|-----:|----:|------:|
| 0-4     |  640 |  416 |  39 |  1095 |
| 5-9     |  641 |  412 |  42 |  1095 |
| 10-14   |  518 |  383 |  40 |   941 |
| 15-19   |  359 |  364 |  20 |   743 |
| 20-29   |  468 |  575 |  30 |  1073 |
| 30-49   |  179 |  557 |  18 |   754 |
| 50-69   |    2 |   91 |   2 |    95 |
| 70+     |   NA |    5 |   1 |     6 |
| NA      |   NA |   NA |  86 |    86 |
| Total   | 2807 | 2803 | 278 |  5888 |

------------------------------------------------------------------------

## 12.4 欠損値の穴埋め

`pivot` の後、そしてより一般的には `bind` の後、いくつかのセルに空白ができてしまい、それを埋めたいと思うことがあります。

### データ

例えば、2 つのデータセットがあり、それぞれ測定番号、施設名、その時点の症例数の観測値があるとします。しかし、2 番目のデータセットには、最初のデータセットには含まれていない変数 `Year` が含まれています。

``` r
df1 <- 
  tibble::tribble(
       ~Measurement, ~Facility, ~Cases,
                  1,  "Hosp 1",     66,
                  2,  "Hosp 1",     26,
                  3,  "Hosp 1",      8,
                  1,  "Hosp 2",     71,
                  2,  "Hosp 2",     62,
                  3,  "Hosp 2",     70,
                  1,  "Hosp 3",     47,
                  2,  "Hosp 3",     70,
                  3,  "Hosp 3",     38,
       )

df1 
```

    # A tibble: 9 × 3
      Measurement Facility Cases
            <dbl> <chr>    <dbl>
    1           1 Hosp 1      66
    2           2 Hosp 1      26
    3           3 Hosp 1       8
    4           1 Hosp 2      71
    5           2 Hosp 2      62
    6           3 Hosp 2      70
    7           1 Hosp 3      47
    8           2 Hosp 3      70
    9           3 Hosp 3      38

``` r
df2 <- 
  tibble::tribble(
    ~Year, ~Measurement, ~Facility, ~Cases,
     2000,            1,  "Hosp 4",     82,
     2001,            2,  "Hosp 4",     87,
     2002,            3,  "Hosp 4",     46
  )

df2
```

    # A tibble: 3 × 4
       Year Measurement Facility Cases
      <dbl>       <dbl> <chr>    <dbl>
    1  2000           1 Hosp 4      82
    2  2001           2 Hosp 4      87
    3  2002           3 Hosp 4      46

`bind_rows()` でこの 2 つのデータセットを結合すると、最初のデータセットに作成された `Year` 変数は、`NA` で埋められます。

``` r
df_combined <- 
  bind_rows(df1, df2) %>% 
  arrange(Measurement, Facility)

df_combined
```

    # A tibble: 12 × 4
       Measurement Facility Cases  Year
             <dbl> <chr>    <dbl> <dbl>
     1           1 Hosp 1      66    NA
     2           1 Hosp 2      71    NA
     3           1 Hosp 3      47    NA
     4           1 Hosp 4      82  2000
     5           2 Hosp 1      26    NA
     6           2 Hosp 2      62    NA
     7           2 Hosp 3      70    NA
     8           2 Hosp 4      87  2001
     9           3 Hosp 1       8    NA
    10           3 Hosp 2      70    NA
    11           3 Hosp 3      38    NA
    12           3 Hosp 4      46  2002

### `fill()`

`Year` は特に時間的な傾向を調べるのに有効な変数であるため、`NA` を埋めたいとしましょう。この場合、`fill()` を使用し、埋める列と方向（この場合は**上 “up”**）を指定することで、空白のセルを*埋める*ことができます。

``` r
df_combined %>% 
  fill(Year, .direction = "up")
```

    # A tibble: 12 × 4
       Measurement Facility Cases  Year
             <dbl> <chr>    <dbl> <dbl>
     1           1 Hosp 1      66  2000
     2           1 Hosp 2      71  2000
     3           1 Hosp 3      47  2000
     4           1 Hosp 4      82  2000
     5           2 Hosp 1      26  2001
     6           2 Hosp 2      62  2001
     7           2 Hosp 3      70  2001
     8           2 Hosp 4      87  2001
     9           3 Hosp 1       8  2002
    10           3 Hosp 2      70  2002
    11           3 Hosp 3      38  2002
    12           3 Hosp 4      46  2002

あるいは、下方向に埋めるため、データを並べ替えることもできます。

``` r
df_combined <- 
  df_combined %>% 
  arrange(Measurement, desc(Facility))

df_combined
```

    # A tibble: 12 × 4
       Measurement Facility Cases  Year
             <dbl> <chr>    <dbl> <dbl>
     1           1 Hosp 4      82  2000
     2           1 Hosp 3      47    NA
     3           1 Hosp 2      71    NA
     4           1 Hosp 1      66    NA
     5           2 Hosp 4      87  2001
     6           2 Hosp 3      70    NA
     7           2 Hosp 2      62    NA
     8           2 Hosp 1      26    NA
     9           3 Hosp 4      46  2002
    10           3 Hosp 3      38    NA
    11           3 Hosp 2      70    NA
    12           3 Hosp 1       8    NA

``` r
df_combined <- 
  df_combined %>% 
  fill(Year, .direction = "down")

df_combined
```

    # A tibble: 12 × 4
       Measurement Facility Cases  Year
             <dbl> <chr>    <dbl> <dbl>
     1           1 Hosp 4      82  2000
     2           1 Hosp 3      47  2000
     3           1 Hosp 2      71  2000
     4           1 Hosp 1      66  2000
     5           2 Hosp 4      87  2001
     6           2 Hosp 3      70  2001
     7           2 Hosp 2      62  2001
     8           2 Hosp 1      26  2001
     9           3 Hosp 4      46  2002
    10           3 Hosp 3      38  2002
    11           3 Hosp 2      70  2002
    12           3 Hosp 1       8  2002

これで、図を作成するのに便利なデータセットができました。

``` r
ggplot(df_combined) +
  aes(Year, Cases, fill = Facility) +
  geom_col()
```

[![](pivoting_files/figure-html/unnamed-chunk-34-1.png)](pivoting_files/figure-html/unnamed-chunk-34-1.png)

しかし、報告書に表として掲載するには向いていないデータセットですので、この縦長形式で整頓されていないデータフレームを、横長形式で整頓されたデータフレームに変換する練習をしてみましょう。

``` r
df_combined %>% 
  pivot_wider(
    id_cols = c(Measurement, Facility),
    names_from = "Year",
    values_from = "Cases"
  ) %>% 
  arrange(Facility) %>% 
  janitor::adorn_totals(c("row", "col")) %>% 
  knitr::kable() %>% 
  kableExtra::row_spec(row = 5, bold = TRUE) %>% 
  kableExtra::column_spec(column = 5, bold = TRUE) 
```

| Measurement | Facility | 2000 | 2001 | 2002 | Total |
|:------------|:---------|-----:|-----:|-----:|------:|
| 1           | Hosp 1   |   66 |   NA |   NA |    66 |
| 2           | Hosp 1   |   NA |   26 |   NA |    26 |
| 3           | Hosp 1   |   NA |   NA |    8 |     8 |
| 1           | Hosp 2   |   71 |   NA |   NA |    71 |
| 2           | Hosp 2   |   NA |   62 |   NA |    62 |
| 3           | Hosp 2   |   NA |   NA |   70 |    70 |
| 1           | Hosp 3   |   47 |   NA |   NA |    47 |
| 2           | Hosp 3   |   NA |   70 |   NA |    70 |
| 3           | Hosp 3   |   NA |   NA |   38 |    38 |
| 1           | Hosp 4   |   82 |   NA |   NA |    82 |
| 2           | Hosp 4   |   NA |   87 |   NA |    87 |
| 3           | Hosp 4   |   NA |   NA |   46 |    46 |
| Total       | \-       |  266 |  245 |  162 |   673 |

この場合、変数 `Measurement` を追加すると表の作成に支障が出るため、`Facility` 、`Year` 、`Cases` の 3 つの変数のみを含めるように指定する必要があります。

``` r
df_combined %>% 
  pivot_wider(
    names_from = "Year",
    values_from = "Cases"
  ) %>% 
  knitr::kable()
```

| Measurement | Facility | 2000 | 2001 | 2002 |
|------------:|:---------|-----:|-----:|-----:|
|           1 | Hosp 4   |   82 |   NA |   NA |
|           1 | Hosp 3   |   47 |   NA |   NA |
|           1 | Hosp 2   |   71 |   NA |   NA |
|           1 | Hosp 1   |   66 |   NA |   NA |
|           2 | Hosp 4   |   NA |   87 |   NA |
|           2 | Hosp 3   |   NA |   70 |   NA |
|           2 | Hosp 2   |   NA |   62 |   NA |
|           2 | Hosp 1   |   NA |   26 |   NA |
|           3 | Hosp 4   |   NA |   NA |   46 |
|           3 | Hosp 3   |   NA |   NA |   38 |
|           3 | Hosp 2   |   NA |   NA |   70 |
|           3 | Hosp 1   |   NA |   NA |    8 |

## 12.5 参考資料

便利な [チュートリアル](https://datacarpentry.org/r-socialsci/03-dplyr-tidyr/index.html) はこちら
