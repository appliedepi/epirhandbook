# 18  基本的な統計的検定

この章では、**base**R、**rstatix**、**gtsummary** を使って、基本的な統計的検定を行う方法を紹介します。

- T 検定
- Shapiro-Wilk 検定
- Wilcoxon の順位和検定
- Kruskal-Wallis 検定
- カイ二乗検定
- 数値変数間の相関

…他にも様々な検定を行うことができますが、ここでは一般的なものだけを紹介し、それ以外のものにはドキュメントへのリンクを張っています。

上記の各パッケージには、それぞれ利点と欠点があります：

- **base** R の関数を使用して、R コンソールに統計的な出力を表示します。

- データフレームで結果を表示する場合や、グループごとに検定を実行したい場合は、**rstatix** パッケージの関数を使用します。

- 出版用の表を素早く表示したい場合は、**gtsummary** を使用します。

## 18.1 準備

### パッケージを読み込む

以下のコードを実行すると、分析に必要なパッケージが読み込まれます。このハンドブックでは、パッケージを読み込むために、pacman パッケージの p_load() を主に使用しています。p_load() は、必要に応じてパッケージをインストールし、現在の R セッションで使用するためにパッケージを読み込む関数です。また、すでにインストールされたパッケージは、R の基本パッケージである base の library() を使用して読み込むこともできます。R のパッケージに関する詳細は [R basics](basics.llms.md) の章をご覧ください。

``` r
pacman::p_load(
  rio,          # ファイルをインポートする
  here,         # ファイルの位置決める
  skimr,        # データの概要を把握する
  tidyverse,    # データ管理 + ggplot2 グラフィックス 
  gtsummary,    # 要約統計と検定をする
  rstatix,      # 統計を行う
  corrr,        # 数値変数の相関分析を行う
  janitor,      # 表に合計値とパーセンテージを加える
  flextable, # 表をHTMLに変換する
  appliedepidata # 本ハンドブックで使用するサンプルデータ
  )
```

### データをインポートする

エボラ出血熱の流行をシミュレートしたデータセットをインポートします。`appliedepidata::get_data(name = "linelist_cleaned_rds")` で直接読み込めます（詳細は[ハンドブックとデータのダウンロード](download.llms.md)のページを参照）。

``` r
# linelist のインポートをする
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

linelist の最初の50行が下のように表示されます。

## 18.2 base R

**base** R の関数を使って、統計的検定を行うことができます。コマンドは比較的簡単で、結果は R のコンソールに表示されるので簡単に見ることができます。しかし、出力は、通常、リストですので、結果を次の操作で使用したい場合は、操作が難しくなります。

### T 検定

「スチューデントの t 検定」とも呼ばれる[ｔ検定](https://en.wikipedia.org/wiki/Student%27s_t-test)は、通常、2つのグループ間で何らかの数値変数の平均値に有意差があるかどうかを判定するために使用されます。ここでは、列が同じデータフレーム内にあるかどうかに応じて、この検定を行うための構文を示します。

構文1：これは、数値列とカテゴリー列が同じデータフレームにある場合の構文です。数式の左側に数値列を、右側にカテゴリー列を用意します。データセットを `data =`で指定します。オプションとして、`paired = TRUE`、`conf.level =` (初期設定は0.95)、`alternative =` (“two.sided”、 “less”、 “greater” のいずれか)を設定します。詳細を知りたい場合は `?t.test` と入力してください。

``` r
##ｔ検定を使用してアウトカムグループごとに平均年齢を比較する
t.test(age_years ~ gender, data = linelist)
```


        Welch Two Sample t-test

    data:  age_years by gender
    t = -21.344, df = 4902.3, p-value < 2.2e-16
    alternative hypothesis: true difference in means between group f and group m is not equal to 0
    95 percent confidence interval:
     -7.571920 -6.297975
    sample estimates:
    mean in group f mean in group m 
           12.60207        19.53701 

構文2：この代替構文を使って、2つの別々の数値ベクトルを比較することができます。たとえば、2 つの列が異なるデータセットにある場合です。

``` r
t.test(df1$age_years, df2$age_years)
```

また，t 検定は，標本平均がある特定の値と有意に異なるかどうかを判定するためにも使用できます。ここでは、既知/仮説の母平均を `mu =`として、1標本の t 検定を行います。

``` r
t.test(linelist$age_years, mu = 45)
```

### Shapiro-Wilk 検定

[Shapiro-Wilk 検定](https://en.wikipedia.org/wiki/Shapiro%E2%80%93Wilk_test)は，標本が正規分布の母集団から得られたものであるかどうかを判定するために使用できます（t 検定など，他の多くの検定や分析の仮定）．ただし，これは3件から5000件まで観察サンプルにしか使用できません。より大きなサンプルでは，[分位数-分位数 プロット](https://ggplot2.tidyverse.org/reference/geom_qq.html)を使用することが有用かもしれません。

``` r
shapiro.test(linelist$age_years)
```

### Wilcoxon の順位和検定

Wilcoxon の順位和検定（[Mann–Whitney の U 検定](https://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U_test)とも呼ばれる）は、2つの数値サンプルの母集団が正規分布していない場合や、不均等な分散を持つ場合に、そのサンプルが同じ分布から来ているかどうかを判断するためによく使用されます。

``` r
## Wilcoxon の検定を使用してアウトカムグループごとに年齢の分布を比較する
wilcox.test(age_years ~ outcome, data = linelist)
```


        Wilcoxon rank sum test with continuity correction

    data:  age_years by outcome
    W = 2501868, p-value = 0.8308
    alternative hypothesis: true location shift is not equal to 0

### Kruskal-Wallis 検定

[Kruskal-Wallis 検定](https://en.wikipedia.org/wiki/Kruskal%E2%80%93Wallis_one-way_analysis_of_variance)は、Wilcoxon の順位和検定を拡張したもので、2つ以上のサンプルの分布の違いを検定するのに使用できます。2つのサンプルしか使用しない場合は、Wilcoxon の順位和検定と同じ結果が得られます。

``` r
##  Kruskal-Wallis 検定を使用して、アウトカムグループごとに年齢の分布を比較する
kruskal.test(age_years ~ outcome, linelist)
```


        Kruskal-Wallis rank sum test

    data:  age_years by outcome
    Kruskal-Wallis chi-squared = 0.045675, df = 1, p-value = 0.8308

### カイ二乗検定

[Pearson のカイ二乗検定](https://en.wikipedia.org/wiki/Chi-squared_test)は、カテゴリー変数のグループ間の有意差を検定する際に使用されます。

``` r
## 各グループにおける割合をカイ二乗検定で比較する
chisq.test(linelist$gender, linelist$outcome)
```


        Pearson's Chi-squared test with Yates' continuity correction

    data:  linelist$gender and linelist$outcome
    X-squared = 0.0011841, df = 1, p-value = 0.9725

## 18.3 **rstatix** パッケージ

**rstatix** パッケージは、「パイプ・フレンドリー」なフレームワークで統計的検定を実行し、結果を取得する機能を提供します。結果は自動的にデータフレームに格納されるので、結果に対して後続の操作を行うことができます。また、関数に渡されるデータをグループ化して、グループごとに統計を実行することも容易です。

### 要約統計

`get_summary_stats()` は、要約統計を素早く表示する方法です。データセットをこの関数に繋げて、分析したい列を指定するだけです。列が指定されていない場合は、すべての列の統計量が計算されます。

デフォルトでは、数、最大値、最小値、中央値、25パーセンタイル値、75パーセンタイル値、四分位範囲、中央絶対偏差 (mad)、平均、標準偏差、標準誤差、平均値の信頼区間という全ての種類の要約統計量が表示されます。

``` r
linelist %>%
  rstatix::get_summary_stats(age, temp)
```

    # A tibble: 2 × 13
      variable     n   min   max median    q1    q3   iqr    mad  mean     sd    se
      <fct>    <dbl> <dbl> <dbl>  <dbl> <dbl> <dbl> <dbl>  <dbl> <dbl>  <dbl> <dbl>
    1 age       5802   0    84     13     6    23      17 11.9    16.1 12.6   0.166
    2 temp      5739  35.2  40.8   38.8  38.2  39.2     1  0.741  38.6  0.977 0.013
    # ℹ 1 more variable: ci <dbl>

`type =` に以下の値のいずれかを指定することで、返す要約統計量の一部を指定することができます。full”、“common”、“robust”、“five_number”、“mean_sd”、“mean_se”、“mean_ci”、“median_iqr”、“median_mad”、“quantile”、“mean”、“median”、“min”、“max”

グループ化されたデータにも使用でき、グループ化された変数ごとに行として返される。

``` r
linelist %>%
  group_by(hospital) %>%
  rstatix::get_summary_stats(age, temp, type = "common")
```

    # A tibble: 12 × 11
       hospital     variable     n   min   max median   iqr  mean     sd    se    ci
       <chr>        <fct>    <dbl> <dbl> <dbl>  <dbl> <dbl> <dbl>  <dbl> <dbl> <dbl>
     1 Central Hos… age        445   0    58     12    15    15.7 12.5   0.591 1.16 
     2 Central Hos… temp       450  35.2  40.4   38.8   1    38.5  0.964 0.045 0.089
     3 Military Ho… age        884   0    72     14    18    16.1 12.4   0.417 0.818
     4 Military Ho… temp       873  35.3  40.5   38.8   1    38.6  0.952 0.032 0.063
     5 Missing      age       1441   0    76     13    17    16.0 12.9   0.339 0.665
     6 Missing      temp      1431  35.8  40.6   38.9   1    38.6  0.97  0.026 0.05 
     7 Other        age        873   0    69     13    17    16.0 12.5   0.422 0.828
     8 Other        temp       862  35.7  40.8   38.8   1.1  38.5  1.01  0.034 0.067
     9 Port Hospit… age       1739   0    68     14    18    16.3 12.7   0.305 0.598
    10 Port Hospit… temp      1713  35.5  40.6   38.8   1.1  38.6  0.981 0.024 0.046
    11 St. Mark's … age        420   0    84     12    15    15.7 12.4   0.606 1.19 
    12 St. Mark's … temp       410  35.9  40.6   38.8   1.1  38.5  0.983 0.049 0.095

また、**rstatix** を使って統計的な検定を行うこともできます。

### T 検定

数式の構文を使って、数値とカテゴリーの列を指定します。

``` r
linelist %>% 
  t_test(age_years ~ gender)
```

    # A tibble: 1 × 10
      .y.   group1 group2    n1    n2 statistic    df        p    p.adj p.adj.signif
    * <chr> <chr>  <chr>  <int> <int>     <dbl> <dbl>    <dbl>    <dbl> <chr>       
    1 age_… f      m       2807  2803     -21.3 4902. 9.89e-97 9.89e-97 ****        

また、`~ 1` を使用し、 `mu =` を指定すると、1標本の T 検定を行うことができます。これは、グループごとに行うこともできます。

``` r
linelist %>% 
  t_test(age_years ~ 1, mu = 30)
```

    # A tibble: 1 × 7
      .y.       group1 group2         n statistic    df     p
    * <chr>     <chr>  <chr>      <int>     <dbl> <dbl> <dbl>
    1 age_years 1      null model  5802     -84.2  5801     0

該当する場合は、以下のようにグループごとに統計的検定を行うことができます。

``` r
linelist %>% 
  group_by(gender) %>% 
  t_test(age_years ~ 1, mu = 18)
```

    # A tibble: 3 × 8
      gender .y.       group1 group2         n statistic    df         p
    * <chr>  <chr>     <chr>  <chr>      <int>     <dbl> <dbl>     <dbl>
    1 f      age_years 1      null model  2807    -29.8   2806 7.52e-170
    2 m      age_years 1      null model  2803      5.70  2802 1.34e-  8
    3 <NA>   age_years 1      null model   192     -3.80   191 1.96e-  4

### **Shapiro-Wilk 検定**

前述の通り、サンプルサイズは3～5000の間でなければなりません。

``` r
linelist %>% 
  head(500) %>%      # 例として、linelist での最初の500行の症例
  shapiro_test(age_years)
```

    # A tibble: 1 × 3
      variable  statistic        p
      <chr>         <dbl>    <dbl>
    1 age_years     0.917 6.67e-16

### **Wilcoxon** の順位和検定

``` r
linelist %>% 
  wilcox_test(age_years ~ gender)
```

    # A tibble: 1 × 9
      .y.       group1 group2    n1    n2 statistic        p    p.adj p.adj.signif
    * <chr>     <chr>  <chr>  <int> <int>     <dbl>    <dbl>    <dbl> <chr>       
    1 age_years f      m       2807  2803   2829274 3.47e-74 3.47e-74 ****        

### **Kruskal-Wallis** 検定

Mann–Whitney の U 検定としても知られています。

``` r
linelist %>% 
  kruskal_test(age_years ~ outcome)
```

    # A tibble: 1 × 6
      .y.           n statistic    df     p method        
    * <chr>     <int>     <dbl> <int> <dbl> <chr>         
    1 age_years  5888    0.0457     1 0.831 Kruskal-Wallis

### カイ二乗検定

カイ二乗検定の関数は表をもとに実施しますので、まずクロス集計を作成します。クロス集計を作成する方法はたくさんありますが（[記述表](tables_descriptive.llms.md)を参照）、ここでは **janitor** パッケージの `tabyl()` を使用し、`chisq_test()` に渡す前に値ラベルの左端の列を削除します。

``` r
linelist %>% 
  tabyl(gender, outcome) %>% 
  select(-1) %>% 
  chisq_test()
```

    # A tibble: 1 × 6
          n statistic     p    df method          p.signif
    * <dbl>     <dbl> <dbl> <int> <chr>           <chr>   
    1  5888      3.53 0.473     4 Chi-square test ns      

**rstatix** パッケージの関数では、さらに多くの関数や統計検定を実行できます。rstatix パッケージのドキュメントをオンラインで見るには、[ここをクリック](https://github.com/kassambara/rstatix)するか、?rstatix を入力してください。

## 18.4 `gtsummary` パッケージ

本パッケージで作成したきれいな表に統計的な検定の結果を追加したい場合は、**gtsummary** パッケージを使用してください（「[記述表](tables_descriptive.llms.md)」章の **gtsummary** セクションで説明しています）。

`tbl_summary()` で比較の統計的検定を行うには、テーブルに `add_p()` を追加し、使用する検定を指定します。`add_q()` を使用して、多重検定で補正された p 値を得ることができる。詳細は `?tbl_summary` を実行してください。

### カイ二乗検定

2つのグループにおけるカテゴリー変数の割合を比較します。カテゴリー変数に適用された場合の `add_p()` へのデフォルトの統計的検定は、連続性補正を用いた独立性のカイ二乗検定ですが、予想される算出数が5未満の場合は、フィッシャーの正確検定が用いられます。

``` r
linelist %>% 
  select(gender, outcome) %>%    # 興味のある変数を投入
  drop_na(outcome) %>%
  tbl_summary(by = outcome) %>%  # 要約表の作成とグループ化をする変数を指定
  add_p()                        # 実行する検定の指定
```

[TABLE]

### T 検定

2つのグループにおける連続変数の平均値の差を比較します。例えば、患者の転帰ごとに平均年齢を比較します。

``` r
linelist %>% 
  select(age_years, outcome) %>%             # 興味のある変数を投入
  drop_na(outcome) %>%
  tbl_summary(                               # 要約表を作成
    statistic = age_years ~ "{mean} ({sd})", # 表示したい要約統計量を指定
    by = outcome) %>%                        # グループ化する変数を指定
  add_p(age_years ~ "t.test")                # 実行する検定を指定
```

[TABLE]

### **Wilcoxon** の順位和検定

2つのグループにおける連続変数の分布を比較します。デフォルトでは、2つのグループを比較する際に Wilcoxon の順位和検定と中央値（四分位範囲）を使用します。しかし、非正規分布のデータや複数のグループを比較する場合は、Kruskal-Wallis 検定を使用することがより適切です。

``` r
linelist %>% 
  select(age_years, outcome) %>%                       # 興味ある変数を投入
  drop_na(outcome) %>%
  tbl_summary(                                         # 要約表を作成
    statistic = age_years ~ "{median} ({p25}, {p75})", # 表示したい統計量を指定(これは初期値なので取り除くことができる)
    by = outcome) %>%                                  # グループ化する変数を指定
  add_p(age_years ~ "wilcox.test")                     # 実行する検定を指定（これはデフォルトなので括弧内は取り除くことが可能）
```

[TABLE]

### **Kruskal-Wallis** 検定

データが正規分布しているかどうかに関わらず、2つ以上のグループにおける連続変数の分布を比較します。

``` r
linelist %>% 
  select(age_years, outcome) %>%                       # 興味ある変数を投入
  drop_na(outcome) %>%
  tbl_summary(                                         # 要約表を作成
    statistic = age_years ~ "{median} ({p25}, {p75})", # 表示したい統計量を指定(これは初期値なので取り除くことができる)
    by = outcome) %>%                                  # グループ化する変数を指定
  add_p(age_years ~ "kruskal.test")                    # 実行する検定を指定
```

[TABLE]

## 18.5 相関

数値変数間の相関は、**tidyverse corrr** パッケージを使用して実施することができます。Pearson、Kendall tau、Spearman rho を使って相関を計算することができます。このパッケージは表を作成します。`stretch()` でその表を縦長のデータフレームに変換し、**ggplot2** でプロットします。

``` r
correlation_tab <- linelist %>% 
  select(generation, age, ct_blood, days_onset_hosp, wt_kg, ht_cm) %>%   # 興味ある変数を投入
  correlate()      # 相関係数表を作成 (初期設定ではPearsonを使用)

correlation_tab    # 表示す
```

    # A tibble: 6 × 7
      term            generation      age ct_blood days_onset_hosp    wt_kg    ht_cm
      <chr>                <dbl>    <dbl>    <dbl>           <dbl>    <dbl>    <dbl>
    1 generation        NA       -2.22e-2  0.179         -0.288    -0.0302  -0.00942
    2 age               -0.0222  NA        0.00849       -0.000635  0.833    0.877  
    3 ct_blood           0.179    8.49e-3 NA             -0.600    -0.00636  0.0181 
    4 days_onset_hosp   -0.288   -6.35e-4 -0.600         NA         0.0153  -0.00953
    5 wt_kg             -0.0302   8.33e-1 -0.00636        0.0153   NA        0.884  
    6 ht_cm             -0.00942  8.77e-1  0.0181        -0.00953   0.884   NA      

``` r
## 重複する項目を削除 (上記の表がミラーリングされている) 
correlation_tab <- correlation_tab %>% 
  shave()

## 相関係数表を表示
correlation_tab
```

    # A tibble: 6 × 7
      term            generation       age ct_blood days_onset_hosp  wt_kg ht_cm
      <chr>                <dbl>     <dbl>    <dbl>           <dbl>  <dbl> <dbl>
    1 generation        NA       NA        NA              NA       NA        NA
    2 age               -0.0222  NA        NA              NA       NA        NA
    3 ct_blood           0.179    0.00849  NA              NA       NA        NA
    4 days_onset_hosp   -0.288   -0.000635 -0.600          NA       NA        NA
    5 wt_kg             -0.0302   0.833    -0.00636         0.0153  NA        NA
    6 ht_cm             -0.00942  0.877     0.0181         -0.00953  0.884    NA

``` r
## 相関をプロット
correlation_tab %>% 
  stretch(na.rm = TRUE) %>% 
  ggplot(aes(x = x, y = y, colour = r, size = abs(r))) +
  geom_point() +
  scale_colour_gradient2(limits = c(-1, 1)) +
  labs(x = NULL, y = NULL)
```

[![](stat_tests_files/figure-html/unnamed-chunk-20-1.png)](stat_tests_files/figure-html/unnamed-chunk-20-1.png)

## 18.6 参考資料

この章における多くの情報はオンラインでのこれらのリソースより採用しています。

[gtsummary](http://www.danieldsjoberg.com/gtsummary/articles/tbl_summary.html) [dplyr](https://dplyr.tidyverse.org/articles/grouping.html) [corrr](https://corrr.tidymodels.org/articles/using-corrr.html) [sthda correlation](http://www.sthda.com/english/wiki/correlation-test-between-two-variables-in-r)
