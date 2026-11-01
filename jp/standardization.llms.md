# 21  標準化率

この章では、年齢や性別などの背景によって入院や死亡などのアウトカムを標準化する方法について説明します。

このページでは **PHEindicatormethods** パッケージを利用します。

まず、データの準備・クリーニング・結合の手順を詳しく説明します。この手順は、複数の国の人口データ、標準化人口データ、死亡数などを結合するときによく行われます。

## 21.1 概要

標準化には直接法と間接法という2つの主要な方法があります。 例えば、A国とB国の年齢と性別で調整した標準化死亡率を求め、それらの標準化死亡率を比較したいとします。

- 直接法では、各A国とB国のそれぞれの年齢と性別層における、リスクに曝された人数と死亡数が分かっている必要があります。層の一例としては「女性で 15 - 44 歳」などになります。
- 間接法では、各国の総死亡数と年齢・性別構成だけが分かっていればよいです。つまり、年齢ごとおよび性別ごとの死亡率や人口データが利用できない場合であっても、間接法を用いることができます。各層の人数が少なく、直接法の各層の推定値がかなりサンプリング変動による影響を受けると考えられる場合、間接法がより望ましいです。

## 21.2 準備

標準化がどのように行われるのかを説明するため、国 A と B から得られた年齢（5歳刻みの分類）と性別（女性、男性）ごとの架空の人口と死亡数のデータを用います。データセットを解析できる形にするため、以下の工程で準備を行っていきます。

1.  パッケージの読み込み
2.  データの読み込み
3.  二国の人口データと死亡データの結合
4.  年齢性別層ごとに一列になっているデータを縦長に変換
5.  参照集団（世界標準人口）データをクリーニングし、二国のデータと結合

実際の状況では、あなたのデータはフォーマットが異なっていることもあります。県、市、または別の管轄区域で分けられているかもしれません。あるいは、一行が各死亡になっていて、それぞれの死亡者毎（または死亡者の大部分）で年齢と性別の情報が得られているかもしれません。この場合は、各年齢性別層の死亡数と人口のデータセットを作成するために、[データのグループ化](grouping.llms.md)、[Pivoting data](pivoting.llms.md)、[記述表](tables_descriptive.llms.md)の章を確認してください。

参照集団、標準人口のデータも必要です。この練習問題では `world_standard_population_by_sex` を使用します。世界標準人口は46ヶ国の人口に基づいており、1960年に作成されました。また、「標準」人口は沢山あります。例を挙げると、[NHS Scotland](https://www.opendata.nhs.scot/dataset/standard-populations) のウェブサイトはヨーロッパ標準人口、世界標準人口、スコットランド標準人口に関して非常に有益な情報源です。

### パッケージの読み込み

以下のコードを実行すると、分析に必要なパッケージが読み込まれます。このハンドブックでは、パッケージを読み込むために、pacman パッケージの p_load() を主に使用しています。p_load() は、必要に応じてパッケージをインストールし、現在の R セッションで使用するためにパッケージを読み込む関数です。また、すでにインストールされたパッケージは、R の基本パッケージである base （以下、base R）の library() を使用して読み込むこともできます。R のパッケージに関する詳細は [R basics](basics.llms.md) の章をご覧ください。

``` r
pacman::p_load(
     rio,                 # データのインポート・エクスポート
     here,                # ファイルの場所を特定
     stringr,             # 文字と文字列のクリーニング
     PHEindicatormethods, # 標準化のための代替のパッケージ
     tidyverse,           # データマネジメントと視覚化
     appliedepidata) # 本ハンドブックで使用するサンプルデータ
```

### 人口データの読み込み

このハンドブックの全事例データのダウンロード方法については [Download handbook and data](download.llms.md) の章を確認してください。以下の `appliedepidata::get_data()` を実行すると、標準化の章のデータを直接 R に読み込むことができます。

``` r
# Github から直接国 A の人口データをインポート
A_demo <- appliedepidata::get_data(name = "country_demographics")

# Github から直接国 A の死亡データをインポート
A_deaths <- appliedepidata::get_data(name = "deaths_countryA")

# Github から直接国 B の人口データをインポート
B_demo <- appliedepidata::get_data(name = "country_demographics_2")

# Github から直接国 B の死亡データをインポート
B_deaths <- appliedepidata::get_data(name = "deaths_countryB")

# Github から直接標準人口のデータをインポート
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

最初に、二ヶ国の人口データ（5歳毎に分類した男性と女性の人数）を読み込み、「国 A」と「国 B」の比較を行っていきます。

``` r
# 国 A
A_demo <- appliedepidata::get_data(name = "country_demographics")
```

``` r
# 国 B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")
```

### 死亡数の読み込み

興味のある期間中の年齢・性別毎の死亡数のデータもあります。以下の通り、各国の死亡数は別々のファイルに入っています。

国 A の死亡数

国 B の死亡数

### 人口・死亡数のクリーニング

これらのデータは以下の方法で結合し変換する必要があります。

- 二ヶ国の人口を一つのデータセットに結合し、各年齢性別層が一行になるように「縦長」に変形
- 二ヶ国の死亡数を一つのデータセットに結合し、各年齢性別層が一行になるように「縦長」に変形
- 死亡データを人口データに結合

最初に、二ヶ国の人口データを結合し、縦長変換して、軽微なクリーニングを行います。詳細については [Pivoting data](pivoting.llms.md) の章を確認してください。

``` r
pop_countries <- A_demo %>%               # 国 A のデータセットから開始
     bind_rows(B_demo) %>%                # 各列名が一致しているため、国 B のデータを列方向に結合
     pivot_longer(                        # 縦長に変換
          cols = c(m, f),                 # これらの列を1つに結合
          names_to = "Sex",               # カテゴリ（"m"または"f"）の情報を含む新しい列の名前
          values_to = "Population") %>%   # 数値の情報を含む新しい列の名前
     mutate(Sex = recode(Sex,             # 明確にするために各値を再コード化
          "m" = "Male",
          "f" = "Female"))
```

結合した人口データは、次のようになりました（クリックすることで国 A と B の両方を確認できます）。

次に、死亡数のデータセットについても同様の処理を行います。

``` r
deaths_countries <- A_deaths %>%     # 国 A の死亡数のデータセットから開始
     bind_rows(B_deaths) %>%         # 各列名が一致しているため、国 B のデータを列方向に結合
     pivot_longer(                   # 縦長に変換
          cols = c(Male, Female),    # これらの列を1つに結合
          names_to = "Sex",          # カテゴリ（"m"または"f"）の情報を含む新しい列の名前
          values_to = "Deaths") %>%  # 数値の情報を含む新しい列の名前
     rename(age_cat5 = AgeCat)       # 明確にするために名前を再変更
```

死亡数のデータは次のようになり、両国のデータが含まれています。

次に、共通の列 `Country`, `age_cat5`, `Sex` に基づいて死亡数と人口データを結合します。これにより、列 `Deaths` が追加されます。

``` r
country_data <- pop_countries %>% 
     left_join(deaths_countries, by = c("Country", "age_cat5", "Sex"))
```

さらに、変数 `Sex`, `age_cat5`, `Country` を因子型変数として分類し、水準の順序を **forcats** パッケージの `fct_relevel()` を用いて設定できます。詳細は [因子（ファクタ）型データ](factors.llms.md) の章を確認してください。なお、因子の水準を分類してもデータに目に見える変化はありません。ただし、`arrange()` コマンドを実行すると、データは国、年齢カテゴリ、性別でソートされます。

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

***注意：***各層の死亡数が少ない場合、年齢について10年または15年区切りのカテゴリの使用を検討してみてください

### 参照集団データの読み込み

最後に、直接標準化のために、参照集団（性別毎の世界「標準人口」）のデータを読み込みます。

``` r
# 参照集団
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

### 参照集団データのクリーニング

データフレーム `country_data` と `standard_pop_data` について、年齢カテゴリの値を揃える必要があります。

現段階では、`standard_pop_data` における `age_cat5` の列の値には “years” や “plus” といった単語が含まれていますが、`country_data` の方はそうなっていません。そのため、年齢カテゴリの値を揃えなくてはいけません。ここでは、[Characters and strings](characters_strings.llms.md) の章で解説した **stringr** パッケージの `str_replace_all()` を使用し、これらのパターンをスペースがない形（`""`）に置換します。

`calculate_dsr()` 関数は標準人口を `stdpop =` 引数で受け取るため、列の名前は何でも構いません。下のコードでは `stdpop = pop` としているため、列名を `"pop"` に変更しておきます。

``` r
# 列の各値から、特定の文字列を削除
standard_pop_clean <- standard_pop_data %>%
     mutate(
          age_cat5 = str_replace_all(age_cat5, "years", ""),  # "year" を削除
          age_cat5 = str_replace_all(age_cat5, "plus", ""),   # "plus" を削除
          age_cat5 = str_replace_all(age_cat5, " ", "")) %>%  # " " （スペース）を削除
     
     rename(pop = WorldStandardPopulation)                    # 列名を "pop" に変更（calculate_dsr() の stdpop = に渡す列）
```

***注意：*** `str_replace_all()` を使用してプラス*記号*を削除しようとしても、プラス記号が特別な記号なためうまくいきません。特別な記号の前にバックスラッシュを2つ入れて「エスケープ」する必要があります。例：`str_replace_call(column, "\\+", "")`。

### 参照集団のデータセット作成

最後に、[以下](#standard_phe)で詳細を説明する **PHEindicatormethods** パッケージでは、標準人口と各国のイベント数と人口データが一つにまとまっている事を想定しています。これにしたがって、`all_data` という名前のデータセットを作成します。

``` r
all_data <- left_join(country_data, standard_pop_clean, by=c("age_cat5", "Sex"))
```

完成したデータセットは以下のようになります。

## 21.3 **PHEindicatormethods** パッケージ

**PHEindicatormethods** パッケージを使用して標準化率を計算します。このパッケージでは、直接標準化も間接標準化も行うことができます。以下では、両方の例を示します。

この節では、データの準備の節の最後で作成したデータフレーム `all_data` を使用します。このデータフレームは各国の人口と死亡数、および世界標準人口が含まれています。このデータフレームについては[こちら](#standard_all)から確認できます。

### 直接標準化率

以下では、最初にデータを国ごとにグループ化し、各国の直接標準化率を求めるためにそれを `calculate_dsr()` に代入します。

注意点：`calculate_dsr()` では、参照集団のデータを**国毎のデータフレーム内の列**として与える必要があります。その列名を `stdpop =` 引数に指定します。以下の例では、この列は `pop` です。

詳しくは、ヘルプ `?calculate_dsr` またはその他の資料の節のリンクを確認してください。

``` r
# 各国の年齢と性別による直接標準化率の計算
mortality_ds_rate_phe <- all_data %>%
     group_by(Country) %>%
     PHEindicatormethods::calculate_dsr(
          x = Deaths,                 # 観測イベント数の列
          n = Population,             # 各層の非標準人口の列
          stdpop = pop)               # 各層の標準人口

# 結果の表示
knitr::kable(mortality_ds_rate_phe)
```

| Country | total_count | total_pop | value | lowercl | uppercl | confidence | statistic | method |
|:---|---:|---:|---:|---:|---:|:---|:---|:---|
| A | 11344 | 86790567 | 23.56686 | 23.08107 | 24.05944 | 95% | dsr per 100000 | Dobson |
| B | 9955 | 52898281 | 19.32549 | 18.45516 | 20.20882 | 95% | dsr per 100000 | Dobson |

### 間接標準化率

間接標準化のためには、参照集団の各層の死亡数と人口のデータが必要です。この例では、参照集団の `standard_pop_clean` に各層の死亡数が含まれていないので、*国 B を参照集団として用いて*国 A の間接標準化率を計算します。

以下では、最初に国 B から参照集団のデータを作成します。次に、間接標準化率を求めるため、国 A の死亡数と人口データと参照集団のデータを `calculate_ISRate()` に代入します。もちろん、国 A と B を逆にすることも可能です。

注意点：この例では、参照集団は別のデータフレームとして与えています。この場合、レコードが位置によってマッチングされるため、`x =`, `n =`, `x_ref =`, `n_ref =` のベクトルがすべて国毎のデータフレームの標準化カテゴリ（層）の値と同じ順序になっていることを確認する必要があります。

詳しくは、ヘルプ `?phr_isr` またはその他の資料の節のリンクを確認してください。

``` r
# 参照集団データを作成
refpopCountryB <- country_data %>% 
  filter(Country == "B") 

# 国 A の年齢と性別による間接標準化率の計算
mortality_is_rate_phe_A <- country_data %>%
     filter(Country == "A") %>%
     PHEindicatormethods::calculate_ISRate(
          x = Deaths,                        # 観測イベント数の列
          n = Population,                    # 各層の非標準人口の列
          x_ref = refpopCountryB$Deaths,     # 各層の参照死亡数
          n_ref = refpopCountryB$Population) # 各層の参照人口

# 結果の表示
knitr::kable(mortality_is_rate_phe_A)
```

| observed | expected | ref_rate | value | lowercl | uppercl | confidence | statistic | method |
|---:|---:|---:|---:|---:|---:|:---|:---|:---|
| 11344 | 15847.42 | 18.81914 | 13.47123 | 13.22446 | 13.72145 | 95% | indirectly standardised rate per 100000 | Byars |

## 21.4 参考資料

**PHEindicatormethods** を用いた別の例については、[このウェブサイト](https://mran.microsoft.com/snapshot/2018-10-22/web/packages/PHEindicatormethods/vignettes/IntroductiontoPHEindicatormethods.html)を見てください。

また、**PHEindicatormethods** の[参照マニュアルの pdf](https://cran.r-project.org/web/packages/PHEindicatormethods/PHEindicatormethods.pdf) も確認してください。
