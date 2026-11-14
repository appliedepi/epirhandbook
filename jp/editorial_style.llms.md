# 1  編集前記・技術注記

本章では、このハンドブックの制作におけるアプローチの哲学、スタイル、具体的な編集上の留意項目について説明します。

## 1.1 疫学や公衆衛生に関わる業務のための R

**目的:** 疫学業務や研究で頻繁に直面する課題に対する対処法の実例を扱い、素早く使用できる R のリファレンスマニュアルとしてオンラインでも [オフライン](download.llms.md)でも機能する

### 本書の使い方

- 左側にある目次を参照する、又は検索ボックスを使用します。  
- 各章にあるコードをコピーしたい場合は、「コピー（copy）」アイコンをクリックしてください。  
- 例題で使用されている [サンプルデータ](download.llms.md) を使用すると、本書の内容をお手元の環境で実践しながら学ぶことができます。

**オフライン版の使い方**

[ハンドブックとデータのダウンロード](download.llms.md) の章をご覧ください。

## 1.2 アプローチとスタイル

本書の潜在的な読者層は広いと考えています。R を初めて使う人はもちろん、より良い R の使い方やそのヒントを探している経験豊富な R ユーザーにもきっと役立ててもらえるはずです。そのため、本書は理解しやすく、簡潔である必要があり、R に慣れていない人でもコードを適用し、コードが何をしているのかをたどることができるよう、*十分な*説明を行うことを心がけました。

その他のポイント

- 本書は、比較的簡単な事例を用いたコードの参考書であり、*R やデータサイエンスの完全な教科書ではありません。*
- 本書は、応用疫学で R を使用するための*ハンドブック*であり、応用疫学の手法や科学に関するマニュアルではありません。
- 本書は、継続的に更新されていく文書を目指しています。それぞれのタスクに最適な R のパッケージは頻繁に変わるため、このハンドブックでどのパッケージの使用を重視するかに関する議論を歓迎します。

### R パッケージ

**多くの選択肢**

R の学習で最も難しいことの 1 つは、特定のタスクに対してどの R パッケージを使うべきかを把握することです。あるタスクで悪戦苦闘しているうちに、「あれ、1 つのコマンドで全部やってくれる R パッケージがあるじゃないか！」と気づくことはよくあります。

このハンドブックでは、各タスクを完了するために少なくとも 2 つの方法を用いるようにしています。1 つは試行錯誤を重ねた方法（おそらく**base** R か tidyverse パッケージ）、もう 1 つはその目的のためにカスタマイズされた特別な R パッケージを使用する方法です。パッケージがダウンロードできない、あるいはうまく動作しない場合に備えて、いくつかの選択肢を用意しておきたいと思います。

使用するパッケージの選択にあたっては、一般的な利用者によってテストされ吟味されたもの、典型的な作業内で使用するパッケージの数が最小であるもの、安定しているもの（あまり頻繁に変更されない）、そしてシンプルかつ簡単にタスクを達成するパッケージと手法を優先的に選びました。

このハンドブックでは、一般的に tidyverse の R パッケージや関数を優先的に紹介します。**tidyverse** はデータサイエンスのために設計された複数の R パッケージを集めたものであり、含まれているパッケージは、基礎となる文法やデータ構造を共有しています。すべての **tidyverse** パッケージは、**tidyverse** パッケージを介してインストールまたは読み込むことが可能です。詳しくは [tidyverse](https://www.tidyverse.org/) のウェブサイトをご覧ください。

また、本書の読者の中には、追加のパッケージをダウンロードするための信頼できるインターネット環境を利用できない方がいることを想定し、必要に応じて **base** R（R をインストールしたときに付属しているパッケージや関数）を用いた手法も紹介しています。

**関数とパッケージの明示的な関連付け**

R のチュートリアルで関数がコードで表示されても、それがどのパッケージのものかわからないとイライラすることがよくありますね！ 私たちはこのような状況を避けようとしています。

本書では、説明する際にパッケージ名は太字で書き（例：**dplyr**）、関数は次のように書いています： `mutate()` 。また、関数がどのパッケージから来たものかを明示するために、文章内でパッケージを参照するか、`dplyr::mutate()` のようにコード内でパッケージを明示するようにしています。冗長に見えるかもしれませんが、あえてそのように書いています。

パッケージや関数について詳しく知りたい方は、[Rの基礎](basics.llms.md) の章をご覧ください。

### コードのスタイル

このハンドブックでは、以下の理由に基づき、頻繁に「改行」をいれて、コードを「縦長」に表示しています。

- コードの細かい点について、コードのすぐ隣で `#` を使って説明コメントを書くことができる
- 一般的に、長い（縦長の）コードの方が読みやすい
- 狭い画面でも読みやすい（横スクロールが必要ない）
- インデントにより、どの引数がどの関数に属しているかがわかりやすい

以下に例を挙げます。

``` r
linelist %>% 
  group_by(hospital) %>%  # 病院ごとのグループの列
  slice_max(date, n = 1, with_ties = F) # 日付が同じ場合は最初の行を採用する
```

本書のスタイルに従うと、上のコードは、次のように書きます。

``` r
linelist %>% 
  group_by(hospital) %>% # 病院ごとのグループの列
  slice_max(
    date,                # グループごとに日付の最大値を持つ行を保持する 
    n = 1,               # 最も上段の 1 列を保持する 
    with_ties = F)       # 日付が同じ場合は最初の行を採用する
```

R コードは通常、改行やインデントの影響を受けません。コードを書く際は、カンマの後で改行すると、自動的なインデントが適用されます。

また、スペースをたくさん使っている理由は、その方が読みやすいからです（例えば、`n=1` ではなく `n = 1` ）。読み手に親切なコードを書きましょう！

### 用語解説

このハンドブックでは、一般的に「変数（variables）」や「観測値（observations）」ではなく「列（columns）」や「行（rows）」といった用語を使用します。この [「tidy data（データの前処理）」](https://tidyr.tidyverse.org/articles/tidy-data.html) の入門書で説明されているように、ほとんどの疫学統計データセットは、行（rows）、列（columns）、値（values）の構造で構成されています。

*変数*には、同じ基本属性（年齢層、転帰、発症日など）を測定した値が含まれます。*観測値*には、同じ単位（人、部位、実験試料など）で測定されたすべての値が含まれます。したがって、列や行と比較して、これらを具体的に定義することは困難であるでしょう。

「整理された」データセットでは、各列が変数、各行が観測値、各セルが 1 つの値です。しかし、あなたが扱うデータセットの中には、この型に当てはまらないものもあります。例えば、「横長」形式のデータセットでは、変数が複数の列にまたがっていることがあります（[データの縦横変換](pivoting.llms.md) の章で例をご覧ください）。同様に、観測値も複数の行にまたがって分割されていることもあります。

このハンドブックの大部分は、データの管理と変換に関するものなので、抽象的な観測値や変数よりも、行や列といったより具体的なデータ構造に言及する方が適切です。例外は主にデータ解析の章で生じ、そこでは変数や観測値への言及が多くなります。

### 注釈

ここでは、このハンドブックで書かれている注釈の種類を紹介します。

***注釈：***これは注釈です  
***ヒント：***これはヒントです  
***注意：***これは注意事項です  
***警告：***これは警告です

## 1.3 編集上の決定事項

以下では、パッケージや関数の選択に関して、編集上の重要な決定事項を記載しています。これらについて異なる意見がある場合や、新しいツールをご提供いただける場合は、こちらの [Github](https://github.com/appliedepi/epirhandbook_eng) ページに参加しメッセージをお送りください。

**パッケージ、関数、その他の編集上の決定事項の表**

| 項目 | 候補パッケージ・関数 | 推奨パッケージ・関数 | 簡単な説明 |
|----|----|----|----|
| 一般的なコーディング方法 | **tidyverse**, **data.table**, **base** | **tidyverse** を基本とし、**data.table** については 1 つの章を設け、インターネットを利用できない読者のために **base** の代替方法にも言及 | **tidyverse** 読みやすいコードや一般性の高いコードの作成のために使用される（一番教えられているパッケージ |
| パッケージの読み込み | `library()`,`install.packages()`, `require()`, **pacman** | **pacman** | ほとんどのパッケージのインストールと読み込みにおいて、コードの短縮と簡素化を実現する |
| インポートとエクスポート | **rio**, 他にも多数存在 | **rio** | 多くのファイルタイプに対応する手軽さ |
| 要約統計のためのグループ化 | **dplyr** `group_by()`, **stats** `aggregate()` | **dplyr** `group_by()` | **tidyverse** を重視する方針と一貫している |
| 縦横変換 | **tidyr** (pivot 系関数), **reshape2** (melt/cast), **tidyr** (spread/gather) | **tidyr** (pivot 系関数) | **reshape2** は廃止され、**tidyr** は 1.0.0 版から pivot 系関数を使用 |
| 列名のクリーニング | **linelist**, **janitor** | **janitor** | パッケージの集約を重視 |
| 時間データの取り扱い | **lubridate**, **aweek**, **tsibble**, **zoo** | **lubridate** 一般的なものと、特定のケースに対応するものとがある | lubridate の柔軟性、一貫性、パッケージ維持の見通し |
| ggplot ラベル | `labs()`, `ggtitle()`/`ylab()`/`xlab()` | `labs()` | すべてのラベルを一箇所でシンプルに修正 |
| 因子型への変換 | `factor()`, **forcats** | **forcats** | さまざまな関数も同じコマンドで因子に変換 |
| 流行曲線（エピカーブ） | **incidence**, **ggplot2**, **EpiCurve** | **incidence2** を素早く、**ggplot2** を詳細に | 信頼性 |
| 結合処理 | `paste()`, `paste0()`, `str_glue()`, `glue()` | `str_glue()` | **stringr** 内にあり paste 関数よりもシンプルな構文 |

## 1.4 主な修正履歴

| 日付               | 主な変更点     |
|--------------------|----------------|
| 2021 年 5 月 10 日 | 1.0.0 版の公開 |
| 2022 年11 月 20 日 | 1.0.1 版の公開 |

更新情報 1.0.1 版は以下の変更が適用されています。

- R のバージョンを 4.2 に更新しました
- データクリーニングと主要関数 : {linelist} パッケージから {matchmaker} パッケージへの変更、`case_when()` の例示コードから不溶な行を削除
- 日付型データ : {linelist} パッケージの関数 `guess_date()` から {parsedate} パッケージの関数 `parse_date()` への変更
- データの縦横変換 : `pivot_wider()` の `id_cols=` 引数の小変更
- 標本調査データ分析 : `plot_age_pyramid()` から `age_pyramid()` への変更、サンキー図（沖積図）をプロットするコードの小変更
- ヒートマップ : `agg_weeks` オブジェクト生成コードに `ungroup()` を追加
- 動的な図の作成 : `agg_weeks` オブジェクト作成時に `expand()` が意図通りに機能するために `ungroup()` を追加
- 時系列分析とアウトブレイクの検出 : すべての `trending::fit()` と `predict()` 内のオブジェクトに対して `data.frame()` を追加
- 複数回答データの分析 : `case_when()` から `ifelse()` への変更、データオブジェクト作成時に `across()` 引数を追加
- 感染連鎖 : より新しいバージョンの {epicontacts} パッケージを利用するように変更

## 1.5 謝辞および注意事項

このハンドブックは、世界各地の疫学者や疫学実務者の協力により、地方、州、県、国の各保健機関、世界保健機関（World Health Organization; WHO）、国境なき医師団（MSF）、病院や学術機関などでの経験をもとに作成されています。

本ハンドブックは、特定の団体から公認を得たものではありません。正確性を期していますが、本書の内容を保証するものではありません。

### 作成者

**編集者:** [Neale Batra](https://www.linkedin.com/in/neale-batra/)

**著者:** [Neale Batra](https://www.linkedin.com/in/neale-batra/), [Alex Spina](https://github.com/aspina7), [Paula Blomquist](https://www.linkedin.com/in/paula-bianca-blomquist-53188186/), [Finlay Campbell](https://github.com/finlaycampbell), [Henry Laurenson-Schafer](https://github.com/henryls1), [Isaac Florence](https://www.Twitter.com/isaacatflorence), [Natalie Fischer](https://www.linkedin.com/in/nataliefischer211/), [Aminata Ndiaye](https://twitter.com/aminata_fadl), [Liza Coyer](https://www.linkedin.com/in/liza-coyer-86022040/), [Jonathan Polonsky](https://twitter.com/jonny_polonsky), [Yurie Izawa](https://ch.linkedin.com/in/yurie-izawa-a1590319), [Chris Bailey](https://twitter.com/cbailey_58?lang=en), [Daniel Molling](https://www.linkedin.com/in/daniel-molling-4005716a/), [Isha Berry](https://twitter.com/ishaberry2), [Emma Buajitti](https://twitter.com/buajitti), [Mathilde Mousset](https://mathildemousset.wordpress.com/research/), [Sara Hollis](https://www.linkedin.com/in/saramhollis/), Wen Lin

**査読者および支援者:** Pat Keating, [Amrish Baidjoe](https://twitter.com/Ammer_B), Annick Lenglet, Margot Charette, Danielly Xavier, Marie-Amélie Degail Chabrat, Esther Kukielka, Michelle Sloan, Aybüke Koyuncu, Rachel Burke, Kate Kelsey, [Berhe Etsay](https://www.linkedin.com/in/berhe-etsay-5752b1154/), John Rossow, Mackenzie Zendt, James Wright, Laura Haskins, [Flavio Finger](https://ffinger.github.io), Tim Taylor, [Jae Hyoung Tim Lee](https://www.linkedin.com/in/jaehyoungtlee/), [Brianna Bradley](https://www.linkedin.com/in/brianna-bradley-bb8658155), [Wayne Enanoria](https://www.linkedin.com/in/wenanoria), Manual Albela Miranda, [Molly Mantus](https://www.linkedin.com/in/molly-mantus-174550150/), Pattama Ulrich, Joseph Timothy, Adam Vaughan, Olivia Varsaneux, Lionel Monteiro, Joao Muianga

日本語版翻訳者: 苅谷 瞳, 西田 典充, 齋藤 雄介, 馬場 美彦, 麸沢 美裕, 髙 勇羅, 藤井 亮輔, 浅野 裕太, 小山 佑奈, 山浦 礼子, 谷 拓朗, 川添 百合香, 中村 星斗, 西川 寛来, 長島 健悟, 茅野 大志, 伏見 淳, 平 友樹, 佐藤 俊太朗, 山口 征啓, 中根 優里, 堺 琴美, 石原 裕也

**図版制作者:** Calder Fong

### 資金支援

このハンドブックは、主にボランティアによってのべ数千時間をかけて作られました

このハンドブックは、実地疫学研修プログラム（Field Epidemiology Training Programs; FETPs）の世界的ネットワークである [TEPHINET](https://www.tephinet.org/) より、新型コロナウイルス感染症のための緊急助成金（COVID-19 emergency capacity-building grant）による支援を受けました。

運営面では、EPIET 同窓生の会（EPIET Alumni Network; [EAN](https://epietalumni.net/)）、とりわけ Annika Wendland から多大なる支援を受け、ここに謝意を示します。EPIET とは、介入疫学トレーニングのための欧州プログラム（European Programme for Intervention Epidemiology Training）の略称です。

本ハンドブックの作成にあたり、国境なき医師団（MSF）アムステルダム運営センター（Operational Centre Amsterdam; OCA）からもご支援いただき、ここに謝意を表します。

*本書は、国際保健タスクフォース（The Task Force for Global Health）のプログラムである TEPHINET を通じて、米国疾病対策センター（Centers for Disease Control and Prevention; CDC）から資金提供を受けた協力契約番号 NU2GGH001873 により作成されました。本書の内容は著者の責任によるものであり、CDC、米国保健福祉省（Department of Health and Human Services）、The Task Force for Global Health, Inc.またはTEPHINET の公式見解を必ずしも示すものではありません。*

### インスピレーション

本書の内容を作成・開発するための知識の元になった多くのチュートリアルやドキュメントは、各章のページでクレジットされています。

以下の資料が本書に多大なインスピレーションを与えてくれた主な参考資料は、以下の通りです。

[The “R4Epis” project](https://r4epis.netlify.app/) (MSF と RECON による共同プロジェクト)  
[R Epidemics Consortium (RECON)](https://www.repidemicsconsortium.org/)  
[R for Data Science book (R4DS)](https://r4ds.had.co.nz/)  
[bookdown: Authoring Books and Technical Documents with R Markdown](https://bookdown.org/yihui/bookdown/)  
[Netlify](https://www.netlify.com) によってこのウェブサイトはホストされています。

## 1.6 利用規約・投稿規約

### ライセンス

[![Creative Commons License](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/4.0/) Applied Epi Incorporated, 2021  
本書は、 [クリエイティブ・コモンズ 表示 - 非商用 - 継承 4.0 国際ライセンス（Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License）](http://creativecommons.org/licenses/by-nc-sa/4.0/)に基づき、Applied Epi Incorporated によってライセンスされています。

授業や疫学者養成研修プログラムの提供者は、本ハンドブックの使用や翻案について、お気軽にお問い合わせください。(email contact@appliedepi.org).

### 引用形式

Batra, Neale, et al. The Epidemiologist R Handbook. 2021. [![DOI](https://zenodo.org/badge/231610102.svg)](https://zenodo.org/badge/231610102.svg)  

### コントリビューション

本書の内容に貢献したい方は、まず Github のイシュー（Issues） またはメールにてご連絡ください。現在、本書の更新スケジュールやコントリビューターガイドを作成中です。

なお、本プロジェクトは、[コントリビューター行動規約（Contributor Code of Conduct）](https://contributor-covenant.org/version/2/0/CODE_OF_CONDUCT.html)と共に公開されていることにご注意ください。本プロジェクトに貢献すると、その規約に従うことに同意したことになります。

## 1.7 バージョン情報 (R・パッケージ)

このハンドブックで使用するすべてのパッケージを含む Docker イメージの、R およびすべての R パッケージのバージョンを以下に示します。

``` r
sessioninfo::session_info(pkgs = "installed", include_base = TRUE)
```

    ─ Session info ───────────────────────────────────────────────────────────────
     setting  value
     version  R version 4.6.0 (2026-04-24)
     os       Ubuntu 26.04 LTS
     system   x86_64, linux-gnu
     ui       X11
     language en_US:en
     collate  en_US.UTF-8
     ctype    en_US.UTF-8
     tz       Etc/UTC
     date     2026-11-14
     pandoc   3.7.0.2 @ /usr/bin/ (via rmarkdown)
     quarto   1.9.38 @ /usr/local/bin/quarto

    ─ Packages ───────────────────────────────────────────────────────────────────
     package              * version    date (UTC) lib source
     abind                  1.4-8      2024-09-12 [1] RSPM
     adagio                 0.9.2      2023-10-26 [1] RSPM
     anytime                0.3.13     2026-04-14 [1] RSPM
     ape                    5.8-1      2024-12-16 [1] RSPM
     aplot                  0.3.0      2026-06-23 [1] RSPM
     appliedepidata         0.0.0.9013 2026-11-02 [1] Github (appliedepi/appliedepidata@77036b1)
     apyramid               0.1.3      2023-02-14 [1] RSPM
     arm                    1.15-3     2026-04-15 [1] RSPM
     askpass                1.2.1      2024-10-04 [1] RSPM
     assertthat             0.2.1      2019-03-21 [1] RSPM
     aweek                  1.0.3      2022-10-06 [1] RSPM
     backports              1.5.1      2026-04-03 [1] RSPM
     base                 * 4.6.0      2026-04-24 [1] local
     base64enc              0.1-6      2026-02-02 [1] RSPM
     bayestestR             0.18.1     2026-05-24 [1] RSPM
     bigD                   0.3.1      2025-04-03 [1] RSPM
     binom                  1.1-1.1    2022-05-02 [1] RSPM
     BiocManager            1.30.27    2025-11-14 [1] RSPM
     bit                    4.6.0      2025-03-06 [1] RSPM
     bit64                  4.8.2      2026-05-19 [1] RSPM
     bitops                 1.0-9      2024-10-03 [1] RSPM
     blob                   1.3.0      2026-01-14 [1] RSPM
     boot                   1.3-32     2025-08-29 [1] CRAN (R 4.6.0)
     broom                  1.0.13     2026-05-14 [1] RSPM
     broom.helpers          1.22.0     2025-09-17 [1] RSPM
     bslib                  0.11.0     2026-05-16 [1] RSPM
     ca                     0.71.1     2020-01-24 [1] RSPM
     cachem                 1.1.0      2024-05-16 [1] RSPM
     callr                  3.8.0      2026-06-05 [1] RSPM
     car                    3.1-5      2026-02-03 [1] RSPM
     carData                3.0-6      2026-01-30 [1] RSPM
     cards                  0.8.0      2026-05-28 [1] RSPM
     cardx                  0.3.3      2026-05-29 [1] RSPM
     cellranger             1.1.0      2016-07-27 [1] RSPM
     CFtime                 1.7.3      2026-04-02 [1] RSPM
     checkmate              2.3.4      2026-02-03 [1] RSPM
     ciTools                0.6.1      2020-10-25 [1] RSPM
     class                  7.3-23     2025-01-01 [1] CRAN (R 4.6.0)
     classInt               0.4-11     2025-01-08 [1] RSPM
     cli                    3.6.6      2026-04-09 [1] RSPM
     clipr                  0.8.1      2026-05-25 [1] RSPM
     clock                  0.7.4      2026-01-13 [1] RSPM
     cluster                2.1.8.2    2026-02-05 [1] CRAN (R 4.6.0)
     cmprsk                 2.2-12     2024-05-19 [1] RSPM
     coarseDataTools        0.7.2      2025-04-11 [1] RSPM
     coda                   0.19-4.1   2024-01-31 [1] RSPM
     codetools              0.2-20     2024-03-31 [1] CRAN (R 4.6.0)
     colorspace             2.1-2      2025-09-22 [1] RSPM
     colourpicker           1.3.0      2023-08-21 [1] RSPM
     cols4all               0.10       2025-10-27 [1] RSPM
     commonmark             2.0.0      2025-07-07 [1] RSPM
     compiler               4.6.0      2026-04-24 [1] local
     conflicted             1.2.0      2023-02-01 [1] RSPM
     correlation            0.8.8      2025-07-08 [1] RSPM
     corrplot               0.95       2024-10-14 [1] RSPM
     corrr                  0.4.5      2025-08-18 [1] RSPM
     cowplot                1.2.0      2025-07-07 [1] RSPM
     crayon                 1.5.3      2024-06-20 [1] RSPM
     crosstalk              1.2.2      2025-08-26 [1] RSPM
     curl                   7.1.0      2026-04-22 [1] RSPM
     data.table             1.18.4     2026-05-06 [1] RSPM
     data.tree              1.2.0      2025-08-25 [1] RSPM
     datasets             * 4.6.0      2026-04-24 [1] local
     datawizard             1.3.1      2026-04-26 [1] RSPM
     DBI                    1.3.0      2026-02-25 [1] RSPM
     dbplyr                 2.6.0      2026-06-17 [1] RSPM
     deldir                 2.0-4      2024-02-28 [1] RSPM
     DEoptimR               1.2-0      2026-06-07 [1] RSPM
     Deriv                  4.2.0      2025-06-20 [1] RSPM
     desc                   1.4.3      2023-12-10 [1] RSPM
     diagram                1.6.5      2020-09-30 [1] RSPM
     DiagrammeR             1.0.12     2026-04-27 [1] RSPM
     dichromat              2.0-0.1    2022-05-02 [1] RSPM
     digest                 0.6.39     2025-11-19 [1] RSPM
     distcrete              1.0.3      2017-11-23 [1] RSPM
     distributional         0.8.1      2026-06-27 [1] RSPM
     doBy                   4.7.1      2025-12-02 [1] RSPM
     doParallel             1.0.17     2022-02-07 [1] RSPM
     dplyr                  1.2.1      2026-04-03 [1] RSPM
     DT                     0.34.0     2025-09-02 [1] RSPM
     dtplyr                 1.3.3      2026-02-11 [1] RSPM
     e1071                  1.7-17     2025-12-18 [1] RSPM
     easystats              0.7.6      2026-05-24 [1] RSPM
     ecmwfr                 2.0.3      2025-02-10 [1] RSPM
     effectsize             1.0.2      2026-03-11 [1] RSPM
     Epi                    2.65       2026-04-15 [1] RSPM
     epicontacts            1.2.0      2026-11-02 [1] Github (reconhub/epicontacts@e68f228)
     epidict                0.3.0      2026-11-02 [1] Github (R4EPI/epidict@af29299)
     EpiEstim               2.2-5      2025-06-27 [1] RSPM
     epikit                 0.2.0      2025-11-05 [1] RSPM
     EpiNow2                1.9.0      2026-06-16 [1] RSPM
     epitabulate            0.1.0      2026-11-02 [1] Github (R4EPI/epitabulate@6f5539d)
     epitrix                0.4.1      2025-07-25 [1] RSPM
     etm                    1.1.2      2025-04-12 [1] RSPM
     evaluate               1.0.5      2025-08-27 [1] RSPM
     evd                    2.3-7.1    2024-09-21 [1] RSPM
     exactRankTests         0.8-37     2026-05-04 [1] RSPM
     fabletools             0.8.0      2026-06-28 [1] RSPM
     fansi                  1.0.7      2025-11-19 [1] RSPM
     farver                 2.1.2      2024-05-13 [1] RSPM
     fastLink               0.6.1      2023-11-17 [1] RSPM
     fastmap                1.2.0      2024-05-15 [1] RSPM
     fastymd                0.1.5      2026-02-27 [1] RSPM
     feasts                 0.5.0      2026-02-09 [1] RSPM
     ff                     4.5.2      2025-01-13 [1] RSPM
     filelock               1.0.3      2023-12-11 [1] RSPM
     fitdistrplus           1.2-6      2026-01-24 [1] RSPM
     flexdashboard          0.6.3      2026-01-28 [1] RSPM
     flextable              0.9.12     2026-06-02 [1] RSPM
     fontawesome            0.5.3      2024-11-16 [1] RSPM
     fontBitstreamVera      0.1.1      2017-02-01 [1] RSPM
     fontLiberation         0.1.0      2016-10-15 [1] RSPM
     fontquiver             0.2.1      2017-02-01 [1] RSPM
     forcats                1.0.1      2025-09-25 [1] RSPM
     foreach                1.5.2      2022-02-02 [1] RSPM
     forecast               9.0.2      2026-03-18 [1] RSPM
     foreign                0.8-91     2026-01-29 [1] CRAN (R 4.6.0)
     formatR                1.14       2023-01-17 [1] RSPM
     formattable            0.2.1      2021-01-07 [1] RSPM
     Formula                1.2-5      2023-02-24 [1] RSPM
     fracdiff               1.5-4      2026-04-28 [1] RSPM
     fs                     2.1.0      2026-04-18 [1] RSPM
     furrr                  0.4.0      2026-03-31 [1] RSPM
     futile.logger          1.4.9      2025-12-29 [1] RSPM
     futile.options         1.0.1      2018-04-20 [1] RSPM
     future                 1.70.0     2026-03-14 [1] RSPM
     future.apply           1.20.2     2026-02-20 [1] RSPM
     gargle                 1.6.1      2026-01-29 [1] RSPM
     gclus                  1.3.3      2025-03-28 [1] RSPM
     gdtools                0.5.1      2026-05-25 [1] RSPM
     generics               0.1.4      2025-05-09 [1] RSPM
     geojsonsf              2.0.5      2025-11-26 [1] RSPM
     getPass                0.2-4      2023-12-10 [1] RSPM
     ggdist                 3.3.3      2025-04-23 [1] RSPM
     ggExtra                0.11.0     2025-09-01 [1] RSPM
     ggforce                0.5.0      2025-06-18 [1] RSPM
     ggfun                  0.2.0      2025-07-15 [1] RSPM
     gghighlight            0.5.0      2025-06-14 [1] RSPM
     ggiraph                0.9.6      2026-02-21 [1] RSPM
     ggnewscale             0.5.2      2025-06-20 [1] RSPM
     ggplot2                4.0.3      2026-04-22 [1] RSPM
     ggplotify              0.1.3      2025-09-20 [1] RSPM
     ggpubr                 0.6.3      2026-02-24 [1] RSPM
     ggrepel                0.9.8      2026-03-17 [1] RSPM
     ggsci                  5.1.0      2026-06-26 [1] RSPM
     ggsignif               0.6.4      2022-10-13 [1] RSPM
     ggtext                 0.1.2      2022-09-16 [1] RSPM
     ggtime                 0.2.0      2026-02-09 [1] RSPM
     ggtree                 4.2.1      2026-10-29 [1] Bioconduc~
     ggupset                0.4.1      2025-02-11 [1] RSPM
     glmnet                 5.0        2026-05-04 [1] RSPM
     globals                0.19.1     2026-03-13 [1] RSPM
     glue                   1.8.1      2026-04-17 [1] RSPM
     googledrive            2.1.2      2025-09-10 [1] RSPM
     googlesheets4          1.1.2.9000 2026-11-02 [1] Github (tidyverse/googlesheets4@55cd9fd)
     gower                  1.0.2      2024-12-17 [1] RSPM
     graphics             * 4.6.0      2026-04-24 [1] local
     grates                 1.8.0      2026-03-25 [1] RSPM
     grDevices            * 4.6.0      2026-04-24 [1] local
     grid                   4.6.0      2026-04-24 [1] local
     gridExtra              2.3.1      2026-06-25 [1] RSPM
     gridGraphics           0.5-1      2020-12-13 [1] RSPM
     gridtext               0.1.6      2026-02-19 [1] RSPM
     gt                     1.3.0      2026-01-22 [1] RSPM
     gtable                 0.3.6      2024-10-25 [1] RSPM
     gtools                 3.9.5      2023-11-20 [1] RSPM
     gtsummary              2.5.1      2026-05-30 [1] RSPM
     hardhat                1.4.3      2026-04-04 [1] RSPM
     haven                  2.5.5      2025-05-30 [1] RSPM
     here                   1.0.2      2025-09-15 [1] RSPM
     highcharter            0.9.5      2026-04-22 [1] RSPM
     highr                  0.12       2026-03-06 [1] RSPM
     hms                    1.1.4      2025-10-17 [1] RSPM
     htmltools              0.5.9      2025-12-04 [1] RSPM
     htmlwidgets            1.6.4      2023-12-06 [1] RSPM
     httpuv                 1.6.17     2026-03-18 [1] RSPM
     httr                   1.4.8      2026-02-13 [1] RSPM
     httr2                  1.2.3      2026-06-23 [1] RSPM
     i2extras               0.2.1.9000 2026-11-02 [1] Github (reconverse/i2extras@10fea67)
     ids                    1.0.1      2017-05-31 [1] RSPM
     igraph                 2.3.3      2026-06-26 [1] RSPM
     imputeTS               3.4        2025-08-25 [1] RSPM
     incidence              1.7.6      2025-06-19 [1] RSPM
     incidence2             2.6.4      2026-03-02 [1] RSPM
     inline                 0.3.21     2025-01-09 [1] RSPM
     insight                1.5.2      2026-06-28 [1] RSPM
     ipred                  0.9-15     2024-07-18 [1] RSPM
     isoband                0.3.0      2025-12-07 [1] RSPM
     iterators              1.0.14     2022-02-05 [1] RSPM
     janitor                2.2.1      2024-12-22 [1] RSPM
     jomo                   2.7-6      2023-04-15 [1] RSPM
     jpeg                   0.1-11     2025-03-21 [1] RSPM
     jquerylib              0.1.4      2021-04-26 [1] RSPM
     jsonlite               2.0.0      2025-03-27 [1] RSPM
     juicyjuice             0.1.0      2022-11-10 [1] RSPM
     kableExtra             1.4.0      2024-01-24 [1] RSPM
     KernSmooth             2.23-26    2025-01-01 [1] CRAN (R 4.6.0)
     keyring                1.4.1      2025-06-15 [1] RSPM
     knitr                  1.51       2025-12-20 [1] RSPM
     labeling               0.4.3      2023-08-29 [1] RSPM
     labelled               2.16.0     2025-10-22 [1] RSPM
     lambda.r               1.2.4      2019-09-18 [1] RSPM
     later                  1.4.8      2026-03-05 [1] RSPM
     lattice                0.22-9     2026-02-09 [1] CRAN (R 4.6.0)
     lava                   1.9.2      2026-06-30 [1] RSPM
     lazyeval               0.2.3      2026-04-04 [1] RSPM
     leafem                 0.2.5      2025-08-28 [1] RSPM
     leafgl                 0.2.4      2026-04-15 [1] RSPM
     leaflegend             1.2.8      2026-05-16 [1] RSPM
     leaflet                2.2.3      2025-09-04 [1] RSPM
     leaflet.providers      3.0.0      2026-03-18 [1] RSPM
     leafsync               0.1.0      2019-03-05 [1] RSPM
     lifecycle              1.0.5      2026-01-08 [1] RSPM
     listenv                1.0.0      2026-06-22 [1] RSPM
     litedown               0.9        2025-12-18 [1] RSPM
     lme4                   2.0-1      2026-03-05 [1] RSPM
     lmtest                 0.9-40     2022-03-21 [1] RSPM
     logger                 0.4.2      2026-05-10 [1] RSPM
     loo                    2.10.0     2026-06-26 [1] RSPM
     lpSolve                5.6.23     2024-12-14 [1] RSPM
     lubridate              1.9.5      2026-02-04 [1] RSPM
     lwgeom                 0.2-16     2026-05-03 [1] RSPM
     magrittr               2.0.5      2026-04-04 [1] RSPM
     maptiles               0.11.0     2025-12-12 [1] RSPM
     markdown               2.0        2025-03-23 [1] RSPM
     MASS                   7.3-65     2025-02-28 [1] CRAN (R 4.6.0)
     matchmaker             0.1.1      2020-02-21 [1] RSPM
     Matrix                 1.7-5      2026-03-21 [1] CRAN (R 4.6.0)
     MatrixModels           0.5-4      2025-03-26 [1] RSPM
     matrixStats            1.5.0      2025-01-07 [1] RSPM
     maxstat                0.7-26     2025-05-02 [1] RSPM
     mcmc                   0.9-8      2023-11-16 [1] RSPM
     MCMCpack               1.7-1      2024-08-27 [1] RSPM
     memoise                2.0.1      2021-11-26 [1] RSPM
     methods              * 4.6.0      2026-04-24 [1] local
     mgcv                   1.9-4      2025-11-07 [1] CRAN (R 4.6.0)
     mice                   3.19.0     2025-12-10 [1] RSPM
     microbenchmark         1.5.0      2024-09-04 [1] RSPM
     mime                   0.13       2025-03-17 [1] RSPM
     miniUI                 0.1.2      2025-04-17 [1] RSPM
     minqa                  1.2.8      2024-08-17 [1] RSPM
     mitml                  0.4-5      2023-03-08 [1] RSPM
     mitools                2.4        2019-04-26 [1] RSPM
     modelbased             0.16.0     2026-06-30 [1] RSPM
     modelr                 0.1.11     2023-03-22 [1] RSPM
     munsell                0.5.1      2024-04-01 [1] RSPM
     mvtnorm                1.4-1      2026-06-06 [1] RSPM
     naniar                 1.1.0      2024-03-05 [1] RSPM
     ncmeta                 0.4.0      2024-03-25 [1] RSPM
     networkD3              0.4.1      2025-04-14 [1] RSPM
     nlme                   3.1-169    2026-03-27 [1] CRAN (R 4.6.0)
     nloptr                 2.2.1      2025-03-17 [1] RSPM
     nnet                   7.3-20     2025-01-01 [1] CRAN (R 4.6.0)
     norm                   1.0-11.1   2023-06-18 [1] RSPM
     numDeriv               2016.8-1.1 2019-06-06 [1] RSPM
     officer                0.7.5      2026-05-15 [1] RSPM
     openssl                2.4.2      2026-06-09 [1] RSPM
     OpenStreetMap          0.4.1      2025-09-29 [1] RSPM
     ordinal                2025.12-29 2026-01-10 [1] RSPM
     otel                   0.2.0      2025-08-29 [1] RSPM
     pacman                 0.5.1      2019-03-11 [1] RSPM
     padr                   0.6.3      2024-11-21 [1] RSPM
     pak                    0.10.0     2026-06-07 [1] RSPM (R 4.6.0)
     pan                    2.0        2026-06-30 [1] RSPM
     parallel               4.6.0      2026-04-24 [1] local
     parallelly             1.48.0     2026-06-29 [1] RSPM
     parameters             0.29.2     2026-06-28 [1] RSPM
     parsedate              1.3.2      2024-12-09 [1] RSPM
     patchwork              1.3.2      2025-08-25 [1] RSPM
     pbkrtest               0.5.5      2025-07-18 [1] RSPM
     pcaPP                  2.0-5      2024-08-19 [1] RSPM
     performance            0.17.1     2026-06-30 [1] RSPM
     PerformanceAnalytics   2.1.0      2026-04-11 [1] RSPM
     permute                0.9-10     2026-02-06 [1] RSPM
     PHEindicatormethods    2.1.1      2025-11-18 [1] RSPM
     pillar                 1.11.1     2025-09-17 [1] RSPM
     pkgbuild               1.4.8      2025-05-26 [1] RSPM
     pkgconfig              2.0.3      2019-09-22 [1] RSPM
     plotly                 4.12.0     2026-01-24 [1] RSPM
     plotrix                3.8-14     2026-02-13 [1] RSPM
     plyr                   1.8.9      2023-10-02 [1] RSPM
     png                    0.1-9      2026-03-15 [1] RSPM
     polyclip               1.10-7     2024-07-23 [1] RSPM
     polyCub                0.9.4      2026-04-24 [1] RSPM
     polynom                1.4-1      2022-04-11 [1] RSPM
     posterior              1.7.0      2026-04-01 [1] RSPM
     primarycensored        1.5.1      2026-06-15 [1] RSPM
     processx               3.9.0      2026-04-22 [1] RSPM
     prodlim                2026.03.11 2026-03-11 [1] RSPM
     progressr              0.19.0     2026-03-31 [1] RSPM
     projections            0.6.1      2024-12-06 [1] RSPM
     promises               1.5.0      2025-11-01 [1] RSPM
     proxy                  0.4-29     2025-12-29 [1] RSPM
     ps                     1.9.3      2026-04-20 [1] RSPM
     purrr                  1.2.2      2026-04-10 [1] RSPM
     pyinit                 1.1.5      2026-01-08 [1] RSPM
     qap                    0.1-2      2022-06-27 [1] RSPM
     quadprog               1.5-8      2019-11-20 [1] RSPM
     quantmod               0.4.29     2026-06-28 [1] RSPM
     quantreg               6.1        2025-03-10 [1] RSPM
     QuickJSR               1.10.0     2026-05-17 [1] RSPM
     R.methodsS3            1.8.2      2022-06-13 [1] RSPM
     R.oo                   1.27.1     2025-05-02 [1] RSPM
     R.utils                2.13.0     2025-02-24 [1] RSPM
     R6                     2.6.1      2025-02-15 [1] RSPM
     ragg                   1.5.2      2026-03-23 [1] RSPM
     rappdirs               0.3.4      2026-01-17 [1] RSPM
     raster                 3.6-32     2025-03-28 [1] RSPM
     rbibutils              2.4.1      2026-01-21 [1] RSPM
     RColorBrewer           1.1-3      2022-04-03 [1] RSPM
     Rcpp                   1.1.1-1.1  2026-04-24 [1] RSPM
     RcppParallel           5.1.11-2   2026-03-05 [1] RSPM
     RcppRoll               0.3.2      2026-03-28 [1] RSPM
     Rdpack                 2.6.6      2026-02-08 [1] RSPM
     reactable              0.4.5      2025-12-01 [1] RSPM
     reactR                 0.6.1      2024-09-14 [1] RSPM
     readr                  2.2.0      2026-02-19 [1] RSPM
     readxl                 1.5.0      2026-05-16 [1] RSPM
     recipes                1.3.3      2026-05-30 [1] RSPM
     RecordLinkage          0.4-12.6   2026-01-25 [1] RSPM
     reformulas             0.4.4      2026-02-02 [1] RSPM
     registry               0.5-1      2019-03-05 [1] RSPM
     rematch                2.0.0      2023-08-30 [1] RSPM
     rematch2               2.1.2      2020-05-01 [1] RSPM
     remotes                2.5.0      2024-03-17 [1] RSPM
     report                 0.6.4      2026-05-04 [1] RSPM
     repr                   1.1.7      2024-03-22 [1] RSPM
     reprex                 2.1.1      2024-07-06 [1] RSPM
     reshape2               1.4.5      2025-11-12 [1] RSPM
     rio                    1.3.0      2026-04-02 [1] RSPM
     rJava                  1.0-18     2026-04-08 [1] RSPM
     rjson                  0.2.23     2024-09-16 [1] RSPM
     rlang                  1.2.0      2026-04-06 [1] RSPM
     rlist                  0.4.6.2    2021-09-03 [1] RSPM
     rmarkdown              2.31       2026-03-26 [1] RSPM
     RNetCDF                2.11-1     2025-04-30 [1] RSPM
     RobStatTM              1.0.11     2024-10-17 [1] RSPM
     robustbase             0.99-7     2026-02-05 [1] RSPM
     rpart                  4.1.27     2026-03-27 [1] CRAN (R 4.6.0)
     rprojroot              2.1.1      2025-08-26 [1] RSPM
     rrcov                  1.7-7      2025-04-21 [1] RSPM
     rsample                1.3.2      2026-01-30 [1] RSPM
     RSQLite                3.53.3     2026-06-30 [1] RSPM
     rstan                  2.32.7     2025-03-10 [1] RSPM
     rstantools             2.6.0      2026-01-10 [1] RSPM
     rstatix                0.7.3      2025-10-18 [1] RSPM
     rstudioapi             0.19.0     2026-06-11 [1] RSPM
     runner                 0.4.6      2026-01-31 [1] RSPM
     rvest                  1.0.5      2025-08-29 [1] RSPM
     s2                     1.1.11     2026-06-01 [1] RSPM
     S7                     0.2.2      2026-04-22 [1] RSPM
     sass                   0.4.10     2025-04-11 [1] RSPM
     scales                 1.4.0      2025-04-24 [1] RSPM
     see                    0.14.1     2026-06-29 [1] RSPM
     selectr                0.6-0      2026-06-23 [1] RSPM
     SemiCompRisks          3.4        2021-02-03 [1] RSPM
     seriation              1.5.8      2025-08-20 [1] RSPM
     servr                  0.33       2026-06-16 [1] RSPM
     sessioninfo            1.2.4      2026-06-04 [1] RSPM
     sf                     1.1-1      2026-05-06 [1] RSPM
     shape                  1.4.6.1    2024-02-23 [1] RSPM
     shiny                  1.14.0     2026-06-21 [1] RSPM
     shinyjs                2.1.1      2026-01-15 [1] RSPM
     sitrep                 0.4.1      2026-11-02 [1] Github (R4EPI/sitrep@72c205f)
     skimr                  2.2.2      2026-01-10 [1] RSPM
     slider                 0.3.3      2025-11-14 [1] RSPM
     snakecase              0.11.1     2023-08-27 [1] RSPM
     sodium                 1.4.0      2024-12-16 [1] RSPM
     sourcetools            0.1.7-2    2026-03-28 [1] RSPM
     sp                     2.2-1      2026-02-13 [1] RSPM
     spacesXYZ              1.6-0      2025-06-06 [1] RSPM
     SparseM                1.84-2     2024-07-17 [1] RSPM
     sparsevctrs            0.3.6      2026-01-27 [1] RSPM
     spatial                7.3-18     2025-01-01 [1] CRAN (R 4.6.0)
     spatstat.data          3.1-9      2025-10-18 [1] RSPM
     spatstat.geom          3.8-1      2026-05-23 [1] RSPM
     spatstat.univar        3.2-0      2026-05-18 [1] RSPM
     spatstat.utils         3.2-3      2026-05-10 [1] RSPM
     spData                 2.3.5      2026-05-04 [1] RSPM
     spdep                  1.4-2      2026-02-13 [1] RSPM
     splines                4.6.0      2026-04-24 [1] local
     SQUAREM                2026.1     2026-03-12 [1] RSPM
     srvyr                  1.3.1      2026-02-02 [1] RSPM
     StanHeaders            2.32.10    2024-07-15 [1] RSPM
     stars                  0.7-2      2026-04-03 [1] RSPM
     stats                * 4.6.0      2026-04-24 [1] local
     stats4                 4.6.0      2026-04-24 [1] local
     stinepack              1.5        2024-03-07 [1] RSPM
     stringdist             0.9.17     2026-01-16 [1] RSPM
     stringi                1.8.7      2025-03-27 [1] RSPM
     stringr                1.6.0      2025-11-04 [1] RSPM
     surveillance           1.25.0     2025-06-25 [1] RSPM
     survey                 4.5        2026-02-24 [1] RSPM
     survival               3.8-6      2026-01-16 [1] CRAN (R 4.6.0)
     survminer              0.5.2      2026-02-25 [1] RSPM
     svglite                2.2.2      2025-10-21 [1] RSPM
     sys                    3.4.3      2024-10-04 [1] RSPM
     systemfonts            1.3.2      2026-03-05 [1] RSPM
     tcltk                  4.6.0      2026-04-24 [1] local
     tensorA                0.36.2.1   2023-12-13 [1] RSPM
     terra                  1.9-34     2026-06-19 [1] RSPM
     textshaping            1.0.5      2026-03-06 [1] RSPM
     threejs                0.3.4      2025-04-21 [1] RSPM
     tibble                 3.3.1      2026-01-11 [1] RSPM
     tidyquant              1.0.12     2026-03-16 [1] RSPM
     tidyr                  1.3.2      2025-12-19 [1] RSPM
     tidyselect             1.2.1      2024-03-11 [1] RSPM
     tidytree               0.4.7      2026-01-08 [1] RSPM
     tidyverse              2.0.0      2023-02-22 [1] RSPM
     timechange             0.4.0      2026-01-29 [1] RSPM
     timeDate               4052.112   2026-01-28 [1] RSPM
     timetk                 2.9.1      2025-08-29 [1] RSPM
     tinytex                0.60       2026-06-16 [1] RSPM
     tmap                   4.4-1      2026-06-26 [1] RSPM
     tmaptools              3.3        2025-07-24 [1] RSPM
     tools                  4.6.0      2026-04-24 [1] local
     treeio                 1.36.1     2026-04-30 [1] Bioconduc~
     trending               0.1.0      2023-04-03 [1] RSPM
     truncnorm              1.0-9      2023-03-20 [1] RSPM
     tseries                0.10-61    2026-03-26 [1] RSPM
     tsfeatures             1.1.1      2023-08-28 [1] RSPM
     tsibble                1.2.0      2026-02-09 [1] RSPM
     TSP                    1.2.7      2026-03-23 [1] RSPM
     TTR                    0.24.4     2023-11-28 [1] RSPM
     tweenr                 2.0.3      2024-02-26 [1] RSPM
     tzdb                   0.5.0      2025-03-15 [1] RSPM
     ucminf                 1.2.3      2026-04-02 [1] RSPM
     units                  1.0-1      2026-03-11 [1] RSPM
     UpSetR                 1.4.1      2026-05-25 [1] RSPM
     urca                   1.3-4      2024-05-27 [1] RSPM
     utf8                   1.2.6      2025-06-08 [1] RSPM
     utils                * 4.6.0      2026-04-24 [1] local
     uuid                   1.2-2      2026-01-23 [1] RSPM
     V8                     8.2.0      2026-04-21 [1] RSPM
     vctrs                  0.7.3      2026-04-11 [1] RSPM
     vegan                  2.7-5      2026-05-25 [1] RSPM
     viridis                0.6.5      2024-01-29 [1] RSPM
     viridisLite            0.4.3      2026-02-04 [1] RSPM
     visdat                 0.6.0      2023-02-02 [1] RSPM
     visNetwork             2.1.4      2025-09-04 [1] RSPM
     vistime                1.3.0      2026-03-28 [1] RSPM
     vroom                  1.7.1      2026-03-31 [1] RSPM
     warp                   0.2.3      2026-01-13 [1] RSPM
     webshot                0.5.5      2023-06-26 [1] RSPM
     withr                  3.0.3      2026-06-19 [1] RSPM
     wk                     0.9.5      2025-12-18 [1] RSPM
     writexl                1.5.4      2025-04-15 [1] RSPM
     xfun                   0.59       2026-06-19 [1] RSPM
     XML                    3.99-0.23  2026-03-20 [1] RSPM
     xml2                   1.6.0      2026-06-22 [1] RSPM
     xtable                 1.8-8      2026-02-22 [1] RSPM
     xts                    0.14.2     2026-02-28 [1] RSPM
     yaml                   2.3.12     2025-12-10 [1] RSPM
     yardstick              1.4.0      2026-04-07 [1] RSPM
     ympes                  1.9.0      2025-04-14 [1] RSPM
     yulab.utils            0.2.4      2026-02-02 [1] RSPM
     yyjsonr                0.1.22     2026-04-05 [1] RSPM
     zip                    3.0.0      2026-06-10 [1] RSPM
     zoo                    1.8-15     2025-12-15 [1] RSPM

     [1] /opt/R/4.6.0/lib/R/library
     * ── Packages attached to the search path.

    ──────────────────────────────────────────────────────────────────────────────
