# 19  単変量と多変量回帰

この章では、変数間の関連性（オッズ比、リスク比、ハザード比など）を調べるために、`glm()` といった **base** R の基本的な回帰関数と **gtsummary** パッケージの使い方を説明します。また、**broom** パッケージの `tidy()` のような関数を使用して、回帰の出力を整えます。

1.  単変量: 2 ×2 表
2.  層別：Mantel-Haenszel 推定
3.  多変量：変数選択、モデル選択、最終的な結果の表
4.  フォレストプロット

Cox 比例ハザード回帰分析については、[生存時間解析](survival_analysis.llms.md)を参照してください。

***注釈:*** この章では、複数の説明変数を持つ回帰を*多変量（multivariable）*と呼びます。この意味で、*多変数（multivariate）*モデルは、複数のアウトカムを持つ回帰を示します。より詳しくは、こちらの[論説](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3518362/)を参照してください。

## 19.1 準備

### パッケージの読み込み

以下のコードを実行すると、分析に必要なパッケージが読み込まれます。このハンドブックでは、パッケージを読み込むために、**pacman** パッケージの `p_load()` を主に使用しています。`p_load()` は、必要に応じてパッケージをインストールし、現在の R セッションで使用するためにパッケージを読み込む関数です。また、すでにインストールされたパッケージは、R の基本パッケージである **base** の `library()` を使用して読み込むこともできます。R のパッケージに関する詳細は [R の基本](basics.llms.md) の章をご覧ください。

``` r
pacman::p_load(
  rio,          # ファイルのインポート
  here,         # ファイルパスの指定
  tidyverse,    # データ管理と ggplot2 での可視化
  stringr,      # テキストの編集 
  purrr,        # tidy な方法でのオブジェクトの反復
  gtsummary,    # 統計量や検定の要約 
  broom,        # 回帰の結果を整然化
  lmtest,       # 尤度比検定
  parameters,   # 回帰の結果を整然化するための代替手段
  see, # フォレストプロットを可視化するための代替手段
  appliedepidata # 本ハンドブックで使用するサンプルデータ
  )
```

### データの読み込み

エボラ出血熱の流行をシミュレートしたデータセットをインポートします。`appliedepidata::get_data(name = "linelist_cleaned_rds")` で直接読み込めます（詳細は[ハンドブックとデータのダウンロード](download.llms.md)のページを参照）。

``` r
# ラインリストのインポート
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

ラインリストの始めの 50 行は次のように表示されます。

### データの前処理

#### 説明変数を保存

説明変数の列名を文字ベクトルとして保存します。この文字ベクトルは後で使用します。

``` r
## 関心のある変数を定義
explanatory_vars <- c("gender", "fever", "chills", "cough", "aches", "vomit")
```

#### 1 と 0 に変換

以下では、説明変数の列（はい・いいえ（“yes”/“no”）、男性・女性（“m”/“f”）と死亡・生存（“dead”/“alive”））をロジスティック回帰モデルの解析がうまくいく形（**1 / 0**）へ変換します。これを効率的に行うために、**dplyr** パッケージの `across()` を使って、複数の列を一度に変換します。それぞれの列に適用する関数は `case_when()` （この関数も **dplyr** パッケージ）です。この関数は、特定の変数に対して 1 と 0 に変換するロジックを適用する。`across()` と `case_when()` については[データクリーニングと主要関数](cleaning.llms.md)の章を参照してください。

注釈: 下記コード中の「.」は、ある時点で `across()` 処理されている列を表します。

``` r
## 2 値変数（yes/no などが格納されている変数）を 0/1 に変換
linelist <- linelist %>%  
  mutate(across(                                      
    .cols = all_of(c(explanatory_vars, "outcome")),  ## 各列と「アウトカム」に対する処理であることを指定
    .fns = ~case_when(                              
      . %in% c("m", "yes", "Death")   ~ 1,           ## 男性、はい、死亡を 1 に変換
      . %in% c("f", "no",  "Recover") ~ 0,           ## 女性、いいえ、回復を 0 に変換
      TRUE                            ~ NA_real_)    ## それ以外は欠測値に変換
    )
  )
```

#### 欠測値のある行を削除

欠測値を含む行を削除するために、**tidyr** パッケージの関数の `drop_na()` が使用できます。しかし、この処理を行いたいのは、対象となる列の値に欠測がある時だけです。

まず行わなければいけないことは、先に作成した `explanatory_vars` ベクトルに列 `age` が含まれるか確認することです（前述の `case_when()` 操作は 2 値変数のみに対応しているため、`age` はエラーになります）。次に、`linelist` を `drop_na()` に渡して、`outcome` 列や `explanatory_vars` のいずれかで値が欠測している行を削除します。

コードを実行する前に、`linelist` オブジェクトの行数は `nrow(linelist)` で確認できます。

``` r
## age_category を説明変数に追加 
explanatory_vars <- c(explanatory_vars, "age_cat")

## 対象となる変数の情報が欠測している行を削除
linelist <- linelist %>% 
  drop_na(any_of(c("outcome", explanatory_vars)))
```

`linelist` オブジェクトに残っている行数は `nrow(linelist)` で確認できます。

## 19.2 単変量

[記述統計表の作り方](tables_descriptive.llms.md)の章と同様に、事例によって使用する R パッケージが決まります。ここでは単変量解析を行うための 2 つのオプションを紹介します。

- **base** R で利用可能な関数を使用して、結果をすぐにコンソールに表示します。また、**broom** パッケージを使用して、出力を整然化します。
- モデルに対して **gtsummary** パッケージを使用して、出版原稿レベルの出力を得ます。

### **base** R

#### 線形回帰

**base** R 関数の `lm()` は線形回帰を実行し、連続尺度の応答と説明変数との関連を、線形の関係があるという仮定のもとで評価します。

式を応答と説明変数の列名をチルダ（~）で分けた formula として与え、利用するデータを `data =` で指定しましょう。後で利用するために、実行結果のモデルを R オブジェクトとして定義しておきます。

``` r
lm_results <- lm(ht_cm ~ age, data = linelist)
```

そうすると、 `summary()` をモデルの結果に対して実行することができ、回帰係数（推定値）、P 値、残差などの統計指標を確認することができます。

``` r
summary(lm_results)
```


    Call:
    lm(formula = ht_cm ~ age, data = linelist)

    Residuals:
         Min       1Q   Median       3Q      Max 
    -128.579  -15.854    1.177   15.887  175.483 

    Coefficients:
                Estimate Std. Error t value Pr(>|t|)    
    (Intercept)  69.9051     0.5979   116.9   <2e-16 ***
    age           3.4354     0.0293   117.2   <2e-16 ***
    ---
    Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

    Residual standard error: 23.75 on 4165 degrees of freedom
    Multiple R-squared:  0.7675,    Adjusted R-squared:  0.7674 
    F-statistic: 1.375e+04 on 1 and 4165 DF,  p-value: < 2.2e-16

`summary()` の代わりに、**broom** パッケージの `tidy()` を使って、結果を表にまとめることもできます。結果より、年齢が 1 歳上がるごとに身長が 3.5 cm ずつ高くなり、これは統計的にも有意であることがわかりました。

``` r
tidy(lm_results)
```

    # A tibble: 2 × 5
      term        estimate std.error statistic p.value
      <chr>          <dbl>     <dbl>     <dbl>   <dbl>
    1 (Intercept)    69.9     0.598       117.       0
    2 age             3.44    0.0293      117.       0

この回帰の結果を **ggplot** パッケージを使って表すこともできます。これを行うためには、まず **broom** パッケージの `augment()` を使って、観測データ点とモデルに当てはめた直線を 1 つのデータフレームに取り込みます。

``` r
## 回帰した点と観測データを 1 つのデータフレームにまとめる
points <- augment(lm_results)

## 年齢を x 軸としてプロット
ggplot(points, aes(x = age)) + 
  ## 身長を追加
  geom_point(aes(y = ht_cm)) + 
  ## 得られた回帰直線を追加
  geom_line(aes(y = .fitted), colour = "red")
```

[![](regression_files/figure-html/lin_reg_res_plot-1.png)](regression_files/figure-html/lin_reg_res_plot-1.png)

`geom_smooth()` を使って、**ggplot** パッケージに単純な線形回帰の直線を追加することも可能です。

``` r
## データをプロット
 ggplot(linelist, aes(x = age, y = ht_cm)) + 
  ## 観測データを表示
  geom_point() + 
  ## 回帰直線を追加
  geom_smooth(method = "lm", formula = y ~ x, se = FALSE)
```

[![](regression_files/figure-html/geom_smooth-1.png)](regression_files/figure-html/geom_smooth-1.png)

より詳細なチュートリアルは、この章の最後にある参考資料を参照してください。

#### ロジスティック回帰

**stats** パッケージ（**base** R の一部）の `glm()` は、一般化線形モデル（GLM: Generalized Linear Models）のあてはめに使われます。

`glm()` は単変量および多変量のロジスティック回帰に使われます（例えば、オッズ比が得られる）。核となる部分は次の通りです。

``` r
# glm() の引数
glm(formula, family, data, weights, subset, ...)
```

- `formula =` モデルは、アウトカムを左に説明変数をチルダの右に配置した式として `glm()` に設定されます。
- `family =` この引数は実行するモデルのタイプを決めます。ロジスティック回帰の場合は `family = "binomial"` を、ポアソン回帰の場合は `family = "poisson"` を使います。他の例は下の表に示します。
- `data =` 使用するデータフレームを設定します。

必要であれば、`family = familytype(link = "linkfunction"))` 構文を使ってリンク関数を設定します。他の分布族や、`weights =` や `subset =` などのオプション引数については、ヘルプドキュメントで詳しく説明されています（`?glm`）。

| 分布族               | リンク関数のデフォルト                       |
|----------------------|----------------------------------------------|
| `"binomial"`         | `(link = "logit")`                           |
| `"gaussian"`         | `(link = "identity")`                        |
| `"Gamma"`            | `(link = "inverse")`                         |
| `"inverse.gaussian"` | `(link = "1/mu^2")`                          |
| `"poisson"`          | `(link = "log")`                             |
| `"quasi"`            | `(link = "identity", variance = "constant")` |
| `"quasibinomial"`    | `(link = "logit")`                           |
| `"quasipoisson"`     | `(link = "log")`                             |

`glm()` を実行する際には、結果を名前付きの R オブジェクトとして保存するのが一般的です。そうすることで、以下のように `summary()` を使って結果をコンソールに表示させたり、結果に対して他の操作（例：指数変換）を行ったりすることができます。

負の二項回帰を実行する必要がある場合は、**MASS** パッケージを使用します。`glm.nb()` は `glm()` と同じ構文を使います。様々な回帰を段階的に知りたい場合は、[UCLA stats のページ](https://stats.idre.ucla.edu/other/dae/)を見てください。

#### 単変量の `glm()`

この例では、異なる年齢カテゴリと死亡というアウトカム（準備セクションで死亡を 1 と変換しました）との関連を評価しています。以下は、`age_cat` によるアウトカムの単変量モデルです。モデルの出力を `model` として保存し、`summary()` でコンソールに出力します。出力される推定値は*対数オッズ*であり、ベースラインレベルは `age_cat` の 1 番目の因子水準（レベル）（“0 - 4”）です。

``` r
model <- glm(outcome ~ age_cat, family = "binomial", data = linelist)
summary(model)
```


    Call:
    glm(formula = outcome ~ age_cat, family = "binomial", data = linelist)

    Coefficients:
                  Estimate Std. Error z value Pr(>|z|)   
    (Intercept)   0.233738   0.072805   3.210  0.00133 **
    age_cat5-9   -0.062898   0.101733  -0.618  0.53640   
    age_cat10-14  0.138204   0.107186   1.289  0.19726   
    age_cat15-19 -0.005565   0.113343  -0.049  0.96084   
    age_cat20-29  0.027511   0.102133   0.269  0.78765   
    age_cat30-49  0.063764   0.113771   0.560  0.57517   
    age_cat50-69 -0.387889   0.259240  -1.496  0.13459   
    age_cat70+   -0.639203   0.915770  -0.698  0.48518   
    ---
    Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

    (Dispersion parameter for binomial family taken to be 1)

        Null deviance: 5712.4  on 4166  degrees of freedom
    Residual deviance: 5705.1  on 4159  degrees of freedom
    AIC: 5721.1

    Number of Fisher Scoring iterations: 4

与えた変数のベースラインレベルを変更するには、列のデータ型が因子であることを確認し、`fct_relevel()` で希望するレベルを最初の位置に移動させます（[因子（ファクタ）型データ](factors.llms.md)の章を参照してください）。例えば、下の例では、列 `age_cat` に対して、“20-29” をベースラインとして設定してから、修正したデータフレームを `glm()` に渡しています。

``` r
linelist %>% 
  mutate(age_cat = fct_relevel(age_cat, "20-29", after = 0)) %>% 
  glm(formula = outcome ~ age_cat, family = "binomial") %>% 
  summary()
```


    Call:
    glm(formula = outcome ~ age_cat, family = "binomial", data = .)

    Coefficients:
                 Estimate Std. Error z value Pr(>|z|)    
    (Intercept)   0.26125    0.07163   3.647 0.000265 ***
    age_cat0-4   -0.02751    0.10213  -0.269 0.787652    
    age_cat5-9   -0.09041    0.10090  -0.896 0.370220    
    age_cat10-14  0.11069    0.10639   1.040 0.298133    
    age_cat15-19 -0.03308    0.11259  -0.294 0.768934    
    age_cat30-49  0.03625    0.11302   0.321 0.748390    
    age_cat50-69 -0.41540    0.25891  -1.604 0.108625    
    age_cat70+   -0.66671    0.91568  -0.728 0.466546    
    ---
    Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

    (Dispersion parameter for binomial family taken to be 1)

        Null deviance: 5712.4  on 4166  degrees of freedom
    Residual deviance: 5705.1  on 4159  degrees of freedom
    AIC: 5721.1

    Number of Fisher Scoring iterations: 4

#### 結果の表示

ほとんどの用途では、上記の出力にいくつかの修正を加える必要があります。**broom** パッケージの `tidy()` は、モデルの結果を見やすくするために便利です。

ここでは、モデルの出力とカウントの表を組み合わせる方法を紹介します。

1.  *指数変換された*対数オッズ比の推定値と信頼区間を得るために、モデルを `tidy()` に渡し、 `exponentiate = TRUE` と `conf.int = TRUE` を設定します。

``` r
model <- glm(outcome ~ age_cat, family = "binomial", data = linelist) %>% 
  tidy(exponentiate = TRUE, conf.int = TRUE) %>%        # 指数変換し信頼区間を算出
  mutate(across(where(is.numeric), ~ round(.x, digits = 2)))  # 全ての数値列を四捨五入
```

以下の表は、整然化された `model` の出力です:

2.  これらのモデルの結果とカウントの表を組み合わせます。下記では、**janitor** パッケージの `tabyl()` を使ってクロス集計表を作成します。これは[記述統計表の作り方](tables_descriptive.llms.md)の章で説明しています。

``` r
counts_table <- linelist %>% 
  janitor::tabyl(age_cat, outcome)
```

この `counts_table` データフレームは、次のように見えます:

これで `bind_cols()`（**dplyr** パッケージ）を使って `counts_table` と結果 `model` を水平方向に結合することができます。`bind_cols()` では、2 つのデータフレームの行が完全に整列していなければならないことを注意してください。このコードでは、一連の引き渡し過程の中で結合しているので、渡されたオブジェクト `counts_table` を表す `.` を使って、そのオブジェクトと `model` を結合しています。最後に、`select()` を使って必要な列とその順番を選択し、**base** R の `round()` で小数点以下 2 桁に指定した四捨五入を全ての数値列に適用しています。

``` r
combined <- counts_table %>%           # カウントの集計表から始める
  bind_cols(., model) %>%              # 回帰の出力と結合
  select(term, 2:3, estimate,          # 変数を選択し、列の並べ直し
         conf.low, conf.high, p.value) %>% 
  mutate(across(where(is.numeric), ~ round(.x, digits = 2))) ## 小数点以下 2 桁に四捨五入
```

結合されたデータフレームの外観は以下の通りです。これは **flextable** パッケージの関数を使って画像として綺麗に印刷されます。[見やすい表の作り方](tables_presentation.llms.md)では、**flextable** パッケージを使ったこのような表のカスタマイズ方法を説明していますが、**knitr** や **GT** などの他のさまざまなパッケージを使うこともできます。

``` r
combined <- combined %>% 
  flextable::qflextable()
```

#### 複数の単変量モデルの反復方法

以下では、`glm()` と `tidy()` を使った方法を紹介します。よりシンプルな方法については、**gtsummary** パッケージのセクションを参照してください。

いくつかの曝露変数のモデルを立て、単変量のオッズ比（つまり、変数同士で調整しない）を生成するためには、下記のアプローチが使えます。まず、**stringr** パッケージの `str_c()` を使って単変量のモデル式を作成します（[文字型・文字列型データ](characters_strings.llms.md)を参照）。次に、それぞれのモデル式に対して `glm()` の回帰を実行し、それぞれの `glm()` の結果を `tidy()` に渡します。最後に **tidyr** パッケージの `bind_rows()` を使って全てのモデルの出力を縦に結合します。このアプローチでは、**purrr** パッケージの `map()` を使って反復処理を行います。このツールのより詳しい情報は[ループと反復処理・リストの操作](iteration.llms.md)を参照してください。

1.  説明変数の列名のベクトルを作成します。このベクトルはこの章の準備セクションで `explanatory_vars` としてすでに作っています。

2.  `str_c()` を使って複数の文字列としてのモデル式を作成します。ここでは左に `outcome`、右に `explanatory_vars` から得られる列名を指定します。ピリオド `.` が `explanatory_vars` の列名に置き換わります。

``` r
explanatory_vars %>% str_c("outcome ~ ", .)
```

    [1] "outcome ~ gender"  "outcome ~ fever"   "outcome ~ chills" 
    [4] "outcome ~ cough"   "outcome ~ aches"   "outcome ~ vomit"  
    [7] "outcome ~ age_cat"

3.  この文字列としてのモデル式を `map()` に渡して、各入力に適用する関数として `~glm()` に設定します。`glm()` の中では、`as.formula(.x)` を回帰式として設定します。ここで、 `.x` は上のステップで定義した文字列としての式で置き換えられます。`map()` は各文字列の式を反復し、それぞれの回帰を実行します。

4.  この最初の `map()` の出力は 2 番目の `map()` コマンドに渡されることにより、回帰の出力に対して `tidy()` が適用されます。

5.  最後に、2 番目の `map()` の出力（整然化されたデータフレームのリスト）が `bind_rows()` で縦に結合され、全ての単変量の結果が単一のデータフレームになります。

``` r
models <- explanatory_vars %>%       # 関心のある変数から始める
  str_c("outcome ~ ", .) %>%         # 各変数を式にする（"アウトカム ~ 関心のある変数"）
  
  # 各単変量の式を反復
  map(                               
    .f = ~glm(                       # 式を一つ一つ glm() に渡す
      formula = as.formula(.x),      # glm() の中で、文字列としての式は .x である
      family = "binomial",           # glm のタイプ（ロジスティック）を指定
      data = linelist)) %>%          # データセット
  
  # 上記から得られた glm 回帰の出力を整然化
  map(
    .f = ~tidy(
      .x, 
      exponentiate = TRUE,           # 指数変換 
      conf.int = TRUE)) %>%          # 信頼区間を算出
  
  # 回帰の出力のリストを一つのデータフレームとして結合
  bind_rows() %>% 
  
  # 全ての数値列を四捨五入
  mutate(across(where(is.numeric), ~ round(.x, digits = 2)))
```

今回は、複数の単変量回帰の結果を結合しているため、`models` の最終的なオブジェクトが長くなっています。クリックすると `model` の全ての行が表示されます。

先に示したように、各説明変数の `linelist` から集計表を作成し、`models` に結合して、見栄えの良い表を作ることができます。まず、変数定義からはじめて、`map()` を使って、その変数を反復処理させます。この反復処理には、**dplyr** パッケージの関数を使って集計表を作成するユーザー定義関数を用います。そして、その結果を組み合わせ、`models` の結果と結合します。

``` r
## それぞれの説明変数に対して処理
univ_tab_base <- explanatory_vars %>% 
  map(.f = 
    ~{linelist %>%                ## linelist から始める
        group_by(outcome) %>%     ## アウトカムごとにデータをグループ化
        count(.data[[.x]]) %>%    ## 関心のある変数に対して集計
        pivot_wider(              ## 横長形式に変換（クロス集計表として）
          names_from = outcome,
          values_from = n) %>% 
        drop_na(all_of(.x)) %>%         ## 欠測行を削除
        rename("variable" = all_of(.x)) %>%      ## 関心のある列の変数名を "variable" に変更
        mutate(variable = as.character(variable))} ## 文字列に変換しないと、2 値でない（カテゴリカル）変数が因子として出てきてしまい結合できない
      ) %>% 
  
  ## 集計結果のリストを 1 つのデータフレームとして結合
  bind_rows() %>% 
  
  ## 回帰の結果と結合
  bind_cols(., models) %>% 
  
  ## 関心のある列のみ抽出
  select(term, 2:3, estimate, conf.low, conf.high, p.value) %>% 
  
  ## 四捨五入する小数点位置を指定
  mutate(across(where(is.numeric), ~ round(.x, digits = 2)))
```

以下は、上で作成したデータフレームです。この表を綺麗な HTML 出力に変換する方法（例えば、**flextable** パッケージの使用）については、[見やすい表の作り方](tables_presentation.llms.md)の章を参照してください。

### **gtsummary** パッケージ

以下では、**gtsummary** パッケージの `tbl_uvregression()` の使い方を紹介します。[記述統計表の作り方](tables_descriptive.llms.md)の章に示したように、**gtsummary** パッケージの関数は統計解析を行い、*かつ*プロフェッショナルな外観の出力を作成するのに良い仕事をします。この関数は単変量の回帰分析の結果の表を作成します。

`linelist` から必要な列（説明変数とアウトカム変数）のみ選択し、それを `tbl_uvregression()` に渡します。これにより、準備のセクションで `explanatory_vars` として定義したそれぞれの列（gender、fever、chills、cough、aches、vomit と age_cat）に対して単変量回帰を行います。

この関数に対して、`method =` として `glm` （引用符はいらない）を、`y =` にアウトカム列を、ロジスティック回帰を行いたい場合は `method.args =` に `family = binomial` を指定し、さらに結果を指数変換するように指示しています。

出力は HTML で、カウントが含まれます。

``` r
univ_tab <- linelist %>% 
  dplyr::select(all_of(explanatory_vars), outcome) %>% ## 関心のある変数を選択

  tbl_uvregression(                         ## 単変量解析の表を生成
    method = glm,                           ## 実行したい回帰（一般化線形モデル）を定義
    y = outcome,                            ## アウトカム変数を定義
    method.args = list(family = binomial),  ## 実行したい glm のタイプを定義（ここではロジスティック）
    exponentiate = TRUE                     ## 対数オッズ比ではなくオッズ比を得るために指数変換を指定
  )

## 単変量の結果の表を出力
univ_tab
```

[TABLE]

この表の出力は、テキストラベルを調整したり、P 値によって行を太字にしたりするなど、さまざまな変更を加えることができます。チュートリアルは[こちら](http://www.danieldsjoberg.com/gtsummary/articles/tbl_regression.html)やオンラインサイトを参照してください。

## 19.3 層別

**gtsummary** パッケージを使った層別解析は現在も継続して開発しています。この章は追って更新します。

## 19.4 多変量

多変量回帰分析をするために、またしても 2 つのアプローチを提案します。

- `glm()` と `tidy()`
- **gtsummary** パッケージ

これらのワークフローはそれぞれ似ていて、最後のステップで最終的に表にまとめるところだけが違います。

### 多変量回帰分析の実施

ここでは、`glm()` を使います。（単変量解析と違って）プラス記号（ `+` ）で説明変数を区切ることで、式の右辺に変数を追加していきます。

全ての説明変数を使ってモデルを実行するには、次のようにします:

``` r
mv_reg <- glm(outcome ~ gender + fever + chills + cough + aches + vomit + age_cat, family = "binomial", data = linelist)

summary(mv_reg)
```


    Call:
    glm(formula = outcome ~ gender + fever + chills + cough + aches + 
        vomit + age_cat, family = "binomial", data = linelist)

    Coefficients:
                  Estimate Std. Error z value Pr(>|z|)
    (Intercept)   0.069054   0.131726   0.524    0.600
    gender        0.002448   0.065133   0.038    0.970
    fever         0.004309   0.080522   0.054    0.957
    chills        0.034112   0.078924   0.432    0.666
    cough         0.138584   0.089909   1.541    0.123
    aches        -0.070705   0.104078  -0.679    0.497
    vomit         0.086098   0.062618   1.375    0.169
    age_cat5-9   -0.063562   0.101851  -0.624    0.533
    age_cat10-14  0.136372   0.107275   1.271    0.204
    age_cat15-19 -0.011074   0.113640  -0.097    0.922
    age_cat20-29  0.026552   0.102780   0.258    0.796
    age_cat30-49  0.059569   0.116402   0.512    0.609
    age_cat50-69 -0.388964   0.262384  -1.482    0.138
    age_cat70+   -0.647443   0.917375  -0.706    0.480

    (Dispersion parameter for binomial family taken to be 1)

        Null deviance: 5712.4  on 4166  degrees of freedom
    Residual deviance: 5700.2  on 4153  degrees of freedom
    AIC: 5728.2

    Number of Fisher Scoring iterations: 4

2 つの変数とそれらの交互作用項は、`+` の代わりにアスタリスク（ `*` ）で変数を区切ることでモデルに含めることができます。また交互作用項のみを指定する場合は、コロン（ `:` ）で区切ります。例えば次の通りです。

``` r
glm(outcome ~ gender + age_cat * fever, family = "binomial", data = linelist)
```

*オプション*として、下記コードを使うことで、あらかじめ定義された列名のベクトルと `str_c()` を使って上記コードを再生成することもできます。これは、説明変数の名前が変更される場合や、全てを再入力したくない場合に便利です。

``` r
## 全ての関心のある変数に対して回帰を実行
mv_reg <- explanatory_vars %>%  ## 説明変数の列名ベクトルから始める
  str_c(collapse = "+") %>%     ## 全ての関心のある説明変数名をプラス記号で区切って結合
  str_c("outcome ~ ", .) %>%    ## アウトカムと上記文字列を結合し、モデル式の形にする
  glm(family = "binomial",      ## glm のタイプをロジスティックとして定義
      data = linelist)          ## データセットを定義
```

#### モデルの構築

任意の説明変数を含む様々なモデルを保存しながら、段階的にモデルを構築することができます。また以下に示すように、**lmtest** パッケージの `lrtest()` を使ってこれらのモデルを尤度比検定で比較することができます:

***注釈:*** **base** の `anova(model1, model2, test = "Chisq")` を使っても同じ結果を得ることができます。

``` r
model1 <- glm(outcome ~ age_cat, family = "binomial", data = linelist)
model2 <- glm(outcome ~ age_cat + gender, family = "binomial", data = linelist)

lmtest::lrtest(model1, model2)
```

    Likelihood ratio test

    Model 1: outcome ~ age_cat
    Model 2: outcome ~ age_cat + gender
      #Df  LogLik Df Chisq Pr(>Chisq)
    1   8 -2852.6                    
    2   9 -2852.6  1 2e-04     0.9883

他の方法は、各モデルのオブジェクトを受け取り、**stats** パッケージの `step()` を適用することです。この関数では、モデルを構築する際に使用したい変数選択の方向を指定します。

``` r
## AIC に基づいた変数増加法によりモデルを選択
## "backward" や "both" を指定することで変数選択の方法を調整できる
final_mv_reg <- mv_reg %>%
  step(direction = "forward", trace = FALSE)
```

また数値の表示をわかりやすくするために、指数表記をオフにすることもできます:

``` r
options(scipen=999)
```

単変量解析のセクションで説明したように、モデルの出力を `tidy()` に渡して、対数オッズ比と信頼区間を指数変換します。最後に、全ての数値列を小数点以下 2 桁に四捨五入します。スクロールして全ての行を確認してください。

``` r
mv_tab_base <- final_mv_reg %>% 
  broom::tidy(exponentiate = TRUE, conf.int = TRUE) %>%  ## 推定値の整然化されたデータフレームを得る
  mutate(across(where(is.numeric), ~ round(.x, digits = 2)))          ## 四捨五入
```

結果として得られたデータフレームは以下のようになります:

### 単変量と多変量の解析結果の結合

#### **gtsummary** パッケージを使った結合

**gtsummary** パッケージは `tbl_regression()` を提供しており、回帰の結果（この場合は `glm()`）を受け取り、美しくまとめた表を作成します。

``` r
## 最終的な回帰モデルの結果の表を表示
mv_tab <- tbl_regression(final_mv_reg, exponentiate = TRUE)
```

表を確認しましょう。

``` r
mv_tab
```

[TABLE]

また、**gtsummary** パッケージで作成したいくつかの異なる表を `tbl_merge()` で結合することができます。ここでは、多変量回帰分析の結果を、[上](#reg_gt_uni)で作成した**gtsummary** パッケージの**単変量**の結果と結合させています。

``` r
## 単変量結果を結合 
tbl_merge(
  tbls = list(univ_tab, mv_tab),                          # 結合
  tab_spanner = c("**Univariate**", "**Multivariable**")) # ヘッダー名を設定
```

[TABLE]

#### **dplyr** を使った結合

`glm()` / `tidy()` の単変量と多変量の出力を結合する別の方法として、**dplyr** パッケージの結合関数があります。

- 先に示した単変量の結果（カウントを含む `univ_tab_base`）と、整然化された多変量の結果 `mv_tab_base` を結合します。
- `select()` を使って、必要な列だけを残し、その順序を指定し、名前を変更します。
- 実数型である全ての列に対して `round()` を適用して、小数点以下 2 桁に四捨五入します。

``` r
## 単変量と多変量の表を結合
left_join(univ_tab_base, mv_tab_base, by = "term") %>% 
  ## 列を選択し、名前を変更
  select( # 新しい名前 = 古い名前
    "characteristic" = term, 
    "recovered"      = "0", 
    "dead"           = "1", 
    "univ_or"        = estimate.x, 
    "univ_ci_low"    = conf.low.x, 
    "univ_ci_high"   = conf.high.x,
    "univ_pval"      = p.value.x, 
    "mv_or"          = estimate.y, 
    "mvv_ci_low"     = conf.low.y, 
    "mv_ci_high"     = conf.high.y,
    "mv_pval"        = p.value.y 
  ) %>% 
  mutate(across(where(is.double), ~ round(.x, 2)))   
```

    # A tibble: 20 × 11
       characteristic recovered  dead univ_or univ_ci_low univ_ci_high univ_pval
       <chr>              <dbl> <dbl>   <dbl>       <dbl>        <dbl>     <dbl>
     1 (Intercept)          909  1168    1.28        1.18         1.4       0   
     2 gender               916  1174    1           0.88         1.13      0.97
     3 (Intercept)          340   436    1.28        1.11         1.48      0   
     4 fever               1485  1906    1           0.85         1.17      0.99
     5 (Intercept)         1472  1877    1.28        1.19         1.37      0   
     6 chills               353   465    1.03        0.89         1.21      0.68
     7 (Intercept)          272   309    1.14        0.97         1.34      0.13
     8 cough               1553  2033    1.15        0.97         1.37      0.11
     9 (Intercept)         1636  2114    1.29        1.21         1.38      0   
    10 aches                189   228    0.93        0.76         1.14      0.51
    11 (Intercept)          931  1144    1.23        1.13         1.34      0   
    12 vomit                894  1198    1.09        0.96         1.23      0.17
    13 (Intercept)          338   427    1.26        1.1          1.46      0   
    14 age_cat5-9           365   433    0.94        0.77         1.15      0.54
    15 age_cat10-14         273   396    1.15        0.93         1.42      0.2 
    16 age_cat15-19         238   299    0.99        0.8          1.24      0.96
    17 age_cat20-29         345   448    1.03        0.84         1.26      0.79
    18 age_cat30-49         228   307    1.07        0.85         1.33      0.58
    19 age_cat50-69          35    30    0.68        0.41         1.13      0.13
    20 age_cat70+             3     2    0.53        0.07         3.2       0.49
    # ℹ 4 more variables: mv_or <dbl>, mvv_ci_low <dbl>, mv_ci_high <dbl>,
    #   mv_pval <dbl>

## 19.5 フォレストプロット

このセクションでは、回帰の結果を図示する方法を示します。**ggplot2** パッケージを使って自分自身でプロットを作成する方法と、**easystats** と呼ばれるメタパッケージ（多くのパッケージを含むパッケージ）を使う方法があります。

**ggplot2** パッケージに慣れていない方は、[ggplot の基礎](ggplot_basics.llms.md)の章をご参照ください。

### **ggplot2** パッケージ

`ggplot()` を使って、多変量回帰の結果の要素をプロットすることで、フォレストプロットを構築できます。下の “geoms” を使ってプロットのレイヤーを追加していきます:

- `geom_point()` を使った推定値の図示
- `geom_errorbar()` を使った信頼区間の図示
- `geom_vline()` を使った OR = 1 を表す垂直線の図示

プロットする前に、**forcats** パッケージの `fct_relevel()` を使って、y 軸上の変数 / レベルの順序を設定すると良いでしょう。（設定しないと）`ggplot()` は、年齢カテゴリに対して英数字順に表示するといった期待通りの結果を返さないかもしれません（例えば「30」が「5」より前に表示されます）。詳しくは[因子（ファクタ）型データ](factors.llms.md)を参照してください。

``` r
## 多変量の結果から切片項を削除
mv_tab_base %>% 
  
  # y 軸上に示される変数 / レベルの順序を指定
  mutate(term = fct_relevel(
    term,
    "vomit", "gender", "fever", "cough", "chills", "aches",
    "age_cat5-9", "age_cat10-14", "age_cat15-19", "age_cat20-29",
    "age_cat30-49", "age_cat50-69", "age_cat70+")) %>%
  
  # "intercept" の行をプロットから削除
  filter(term != "(Intercept)") %>% 
  
  ## y 軸に変数を x 軸に推定値（OR）をプロット
  ggplot(aes(x = estimate, y = term)) +
  
  ## 点推定値をポイントとして図示
  geom_point() + 
  
  ## 信頼区間をエラーバーとして追加
  geom_errorbar(aes(xmin = conf.low, xmax = conf.high)) + 
  
  ## OR = 1 を示す参照をダッシュ線で示す
  geom_vline(xintercept = 1, linetype = "dashed")
```

[![](regression_files/figure-html/ggplot_forest-1.png)](regression_files/figure-html/ggplot_forest-1.png)

### **easystats** パッケージ

**ggplot2** パッケージが提供する細かいレベルの制御をしたくない場合は、代わりに **easystats** パッケージの組み合わせを使用することができます。

**parameters** パッケージの `model_parameters()` は **broom** パッケージの `tidy()` と同じ処理を行います。**see** パッケージは、これらの出力を受け取り `ggplot()` オブジェクトとしてデフォルトのフォレストプロットを作成します。

``` r
pacman::p_load(easystats)

## 多変量の結果から切片項を削除
final_mv_reg %>% 
  model_parameters(exponentiate = TRUE) %>% 
  plot()
```

[![](regression_files/figure-html/easystats_forest-1.png)](regression_files/figure-html/easystats_forest-1.png)

## 19.6 参考資料

この章の内容は、これらの資料やオンラインの動作例を参考にしています。

[Linear regression in R](https://www.datacamp.com/community/tutorials/linear-regression-R)

[gtsummary](http://www.danieldsjoberg.com/gtsummary/articles/tbl_regression.html)

[UCLA stats page](https://stats.idre.ucla.edu/other/dae/)

[sthda stepwise regression](http://www.sthda.com/english/articles/36-classification-methods-essentials/150-stepwise-logistic-regression-essentials-in-r/)
