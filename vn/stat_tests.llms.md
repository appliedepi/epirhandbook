# 18  Các kiểm định thống kê cơ bản

Chương này sẽ trình bày cách để thực hiện các phép kiểm định thống kê cơ bản bằng cách sử dụng **base** R, **rstatix**, và **gtsummary**.

- Kiểm định t  
- Kiểm định Shapiro-Wilk  
- Kiểm định tổng thứ hạng Wilcoxon  
- Kiểm định Kruskal-Wallis  
- Kiểm định Chi-squared (Chi bình phương)  
- Tương quan giữa các biến định lượng

…nhiều kiểm định khác có thể được thực hiện, nhưng chúng tôi chỉ trình bày các kiểm định thông dụng và cung cấp đường dẫn tới các tài liệu tham khảo thêm.

Mỗi package được đề cập bên trên đều có một số ưu điểm và khuyết điểm nhất định:

- Sử dụng các câu lệnh của **base** để in các kết quả đầu ra thống kê trong R Console  
- Sử dụng các câu lệnh của **rstatix** để cho kết quả dưới dạng data frame hoặc khi muốn thực hiện các kiểm định theo nhóm  
- Sử dụng các câu lệnh của **gtsummary** khi muốn kết quả là các bảng biểu có thể sử dụng được ngay

## 18.1 Các bước chuẩn bị

### Gọi các packages

Đoạn code này hiển thị việc gọi các package cần thiết cho phân tích. Trong cuốn sổ tay này, chúng tôi nhấn mạnh đến hàm `p_load()` trong package **pacman**, cài đặt gói lệnh nếu cần thiết *và* gọi chúng ra để sử dụng. Các package đã cài đặt cũng có thể được gọi ra bằng `library()` từ **base** R. Xem thêm thông tin các package của R trong chương [R cơ bản](basics.llms.md).

``` r
pacman::p_load(
  rio,          # File import
  here,         # File locator
  skimr,        # get overview of data
  tidyverse,    # data management + ggplot2 graphics, 
  gtsummary,    # summary statistics and tests
  rstatix,      # statistics
  corrr,        # correlation analayis for numeric variables
  janitor,      # adding totals and percents to tables
  flextable, # converting tables to HTML
  appliedepidata # example datasets used in this handbook
  )
```

### Nhập số liệu

Chúng ta nhập bộ số liệu của các ca bệnh về một vụ dịch Ebola mô phỏng. Tải trực tiếp bằng `appliedepidata::get_data(name = "linelist_cleaned_rds")` (xem trang [Tải sách và dữ liệu](download.llms.md) để biết chi tiết).

``` r
# import the linelist
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

50 hàng đầu tiên của bộ dữ liệu linelist được hiển thị như dưới đây.

## 18.2 Các kiểm định trong **base** R

Các lệnh trong **base** R có thể được sử dụng để thực hiện các kiểm định thống kê. Các câu lệnh tương đối đơn giản và kết quả sẽ hiển thị trong bảng điều khiển R Console. Tuy nhiên, kết quả đầu ra thường dưới dạng liệt kê, vì thế sẽ khó thao tác hơn nếu muốn sử dụng kết quả trong các thao tác tiếp theo.

### Kiểm định t

Một [kiểm định t](https://en.wikipedia.org/wiki/Student%27s_t-test), hay còn được gọi là “Student’s t-Test”, thường được sử dụng để xác định có sự khác biệt có ý nghĩa thống kê giữa giá trị trung bình của hai nhóm. Bên dưới là cú pháp để thực hiện kiểm định này tùy thuộc vào các cột có trong cùng một data frame hay không.

**Cú pháp 1:** Đây là cú pháp khi cột của biến liên tục và phân loại nằm trong cùng một data frame. Đặt biến liên tục bên trái và biến phân loại bên phải của phương trình. Ghi rõ bộ số liệu sau `data =`. Các tùy chọn khác như số liệu bắt cặp, viết thêm `paired = TRUE`, khoảng tin cậy, viết thêm `conf.level =` (mặc định là 0.95), và giả thuyết thay thế `alternative =` (hai đuôi - “two.sided”, hoặc một đuôi nhỏ hơn hay lớn hơn - “less”, or “greater”). Gõ `?t.test` để biết thêm chi tiết.

``` r
## compare mean age by outcome group with a t-test
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

**Cú pháp 2:** Đây là cú pháp khi so sánh hai véc tơ dạng số. Ví dụ như hai cột nằm trong hai bộ số liệu khác nhau.

``` r
t.test(df1$age_years, df2$age_years)
```

Kiểm định t cũng được sử dụng để xác định có sự khác biệt có ý nghĩa thống kê giữa giá trị trung bình của mẫu với một số giá trị cụ thể. Đây là phép kiểm định t cho một mẫu với trung bình quần thể giả thuyết/đã biết như `mu =`:

``` r
t.test(linelist$age_years, mu = 45)
```

### Kiểm định Shapiro-Wilk

[Kiểm định Shapiro-Wilk](https://en.wikipedia.org/wiki/Shapiro%E2%80%93Wilk_test) có thể được sử để xác định xem một mẫu có phân bố bình thường/phân bố chuản hay không (một giả định của nhiều kiểm định khác, ví dụ như kiểm định t). Tuy nhiên, phép kiểm định này chỉ có thể được sử dụng cho một mẫu có từ 3 đến 5000 quan sát. Đối với cỡ mẫu lớn hơn, nên sử dụng biểu đồ [quantile-quantile plot](https://ggplot2.tidyverse.org/reference/geom_qq.html).

``` r
shapiro.test(linelist$age_years)
```

### Kiểm định tổng thứ hạng Wilcoxon

Kiểm định tổng thứ hạng Wilcoxon, hay còn gọi là [kiểm định Mann–Whitney U](https://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U_test), thường được sử dụng để giúp xác định xem hai mẫu có cùng phân bố hay không khi quần thể của chúng không có phân bố chuẩn hoặc có phương sai không bằng nhau.

``` r
## compare age distribution by outcome group with a wilcox test
wilcox.test(age_years ~ outcome, data = linelist)
```


        Wilcoxon rank sum test with continuity correction

    data:  age_years by outcome
    W = 2501868, p-value = 0.8308
    alternative hypothesis: true location shift is not equal to 0

### Kiểm định Kruskal-Wallis

[Kiểm định Kruskal-Wallis](https://en.wikipedia.org/wiki/Kruskal%E2%80%93Wallis_one-way_analysis_of_variance) là một phần mở rộng của kiểm định tổng thứ hạng Wilcoxon mà có thể được sử dụng để kiểm định sự khác biệt trong phân bố của nhiều hơn hai mẫu. Khi có hai mẫu được sử dụng, nó cho kết quả giống như của kiểm định tổng thứ hạng Wilcoxon.

``` r
## compare age distribution by outcome group with a kruskal-wallis test
kruskal.test(age_years ~ outcome, linelist)
```


        Kruskal-Wallis rank sum test

    data:  age_years by outcome
    Kruskal-Wallis chi-squared = 0.045675, df = 1, p-value = 0.8308

### Kiểm định Chi bình phương

[Kiểm định Chi bình phương của Pearson](https://en.wikipedia.org/wiki/Chi-squared_test) được sử dụng trong kiểm tra sự khác biệt có ý nghĩa thống kê giữa các biến phân loại.

``` r
## compare the proportions in each group with a chi-squared test
chisq.test(linelist$gender, linelist$outcome)
```


        Pearson's Chi-squared test with Yates' continuity correction

    data:  linelist$gender and linelist$outcome
    X-squared = 0.0011841, df = 1, p-value = 0.9725

## 18.3 **rstatix** package

Package **rstatix** cho phép thực hiện các kiểm định thống kê và truy xuất kết quả “dễ sử dụng cho các tính toán tiếp theo”. Có nghĩa là kết quả xuất tự động thành một data frame để có thể thực hiện các thao tác tiếp theo. Nó cũng dễ dàng để nhóm dữ liệu mà sẽ được chuyền vào các hàm, ở đó các thống kê được thực hiện cho từng nhóm.

### Tóm tắt thống kê

Hàm `get_summary_stats()` là một cách thực hiện tóm tắt thống kê nhanh. Chỉ cần đưa bộ số liệu và chỉ định các cột muốn phân tích vào hàm này. Nếu không có cột nào được cụ thể, tóm tắt thống kê sẽ tính toán cho tất cả các cột.

Tóm tắt thống kê đầy đủ sẽ cho kết quả mặc định như sau: số quan sát (n), giá trị nhỏ nhất, giá trị lớn nhất, trung vị, giá trị tứ phân vị thứ nhất (25%), giá trị tứ phân vị thứ ba (75%), khoảng tứ phân vị, độ lệch tuyệt đối của trung vị (mad), trung bình, độ lệch chuẩn, sai số chuẩn và khoảng tin cậy của trung bình.

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

Có thể tóm tắt một số giá trị thống kê bằng cách cung cấp một trong số các giá trị sau đến `type =`: “full”, “common”, “robust”, “five_number”, “mean_sd”, “mean_se”, “mean_ci”, “median_iqr”, “median_mad”, “quantile”, “mean”, “median”, “min”, “max”.

Nó cũng có thể được sử dụng với số liệu đã được nhóm, sao cho một hàng được trả về cho mỗi biến nhóm:

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

Bạn cũng có thể sử dụng **rstatix** để thực hiện các kiểm định thống kê:

### Kiểm định t

Sử dụng cú pháp công thức để chỉ định cột biến liên tục và cột biến phân loại:

``` r
linelist %>% 
  t_test(age_years ~ gender)
```

    # A tibble: 1 × 10
      .y.   group1 group2    n1    n2 statistic    df        p    p.adj p.adj.signif
    * <chr> <chr>  <chr>  <int> <int>     <dbl> <dbl>    <dbl>    <dbl> <chr>       
    1 age_… f      m       2807  2803     -21.3 4902. 9.89e-97 9.89e-97 ****        

Hoặc sử dụng `~ 1` và ghi rõ `mu =` cho kiểm định t một mẫu. Cú pháp này có thể sử dụng để thực hiện cho nhóm.

``` r
linelist %>% 
  t_test(age_years ~ 1, mu = 30)
```

    # A tibble: 1 × 7
      .y.       group1 group2         n statistic    df     p
    * <chr>     <chr>  <chr>      <int>     <dbl> <dbl> <dbl>
    1 age_years 1      null model  5802     -84.2  5801     0

Nếu có thể, các kiểm định thống kê có thể thực hiện theo nhóm, như được trình bày bên dưới.

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

### Kiểm định Shapiro-Wilk

Như đã đề cập bên trên, cỡ mẫu phải nằm trong khoảng từ 3 đến 5000.

``` r
linelist %>% 
  head(500) %>%            # first 500 rows of case linelist, for example only
  shapiro_test(age_years)
```

    # A tibble: 1 × 3
      variable  statistic        p
      <chr>         <dbl>    <dbl>
    1 age_years     0.917 6.67e-16

### Kiểm định tổng thứ hạng Wilcoxon

``` r
linelist %>% 
  wilcox_test(age_years ~ gender)
```

    # A tibble: 1 × 9
      .y.       group1 group2    n1    n2 statistic        p    p.adj p.adj.signif
    * <chr>     <chr>  <chr>  <int> <int>     <dbl>    <dbl>    <dbl> <chr>       
    1 age_years f      m       2807  2803   2829274 3.47e-74 3.47e-74 ****        

### Kiểm định Kruskal-Wallis

Cũng được biết như kiểm định Mann-Whitney U.

``` r
linelist %>% 
  kruskal_test(age_years ~ outcome)
```

    # A tibble: 1 × 6
      .y.           n statistic    df     p method        
    * <chr>     <int>     <dbl> <int> <dbl> <chr>         
    1 age_years  5888    0.0457     1 0.831 Kruskal-Wallis

### Kiểm định Chi bình phương

Hàm kiểm định Chi bình phương chấp nhận một bảng, vì vậy đầu tiên là tạo một bảng chéo. Có nhiều cách để tạo một bảng chéo (xem chương [Bảng mô tả](tables_descriptive.llms.md)) nhưng ở đây chúng ta sử dụng hàm `tabyl()` từ **janitor** avà bỏ cột ngoài cùng bên trái của nhãn giá trị trước khi đưa vào hàm `chisq_test()`.

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

Có rất nhiều hàm và kiểm định thống kê có thể được thực hiện bằng các hàm trong package **rstatix**. Đọc các tài liệu về **rstatix** [online ở đây](https://github.com/kassambara/rstatix) hoặc gõ ?rstatix.

## 18.4 `gtsummary` package

Sử dụng package **gtsummary** nếu bạn đang muốn thêm kết quả của một kiểm định thống kê vào một bảng đẹp được tạo ra bằng package này (như đã được mô tả trong phần **gtsummary** của chương [Bảng mô tả](tables_descriptive.llms.md#tbl_gt)).

Khi thực hiện các kiểm định so sánh bằng hàm `tbl_summary`, dùng thêm hàm `add_p` để đưa cột giá trị p và kiểm định được sử dụng vào bảng. Có thể xuất nhiều giá trị p mà được hiệu chỉnh cho nhiều kiểm định bằng cách dùng thêm hàm `add_q`. Gõ lệnh `?tbl_summary` để biết thêm chi tiết.

### Kiểm định Chi bình phương

Được sử dụng để so sánh các tỷ lệ của một biến phân loại trong hai nhóm. Kiểm định thống kê mặc định cho biến phân loại trong hàm `add_p()` là kiểm định Chi bình phương về tính độc lập với hiệu chỉnh liên tục, nhưng nếu có bất kỳ giá trị kỳ vọng nào nhỏ hơn 5 thì kiểm định chính xác của Fisher sẽ được sử dụng.

``` r
linelist %>% 
  select(gender, outcome) %>%    # keep variables of interest
  drop_na(outcome) %>%
  tbl_summary(by = outcome) %>%  # produce summary table and specify grouping variable
  add_p()                        # specify what test to perform
```

[TABLE]

### Kiểm định t

Được sử dụng để so sánh sự khác biệt về trung bình của một biến liên tục trong hai nhóm. Ví dụ như so sánh tuổi trung bình với kết cục của bệnh nhân.

``` r
linelist %>% 
  select(age_years, outcome) %>%             # keep variables of interest
  drop_na(outcome) %>%
  tbl_summary(                               # produce summary table
    statistic = age_years ~ "{mean} ({sd})", # specify what statistics to show
    by = outcome) %>%                        # specify the grouping variable
  add_p(age_years ~ "t.test")                # specify what tests to perform
```

[TABLE]

### Kiểm định tổng thứ hạng Wilcoxon

Được dùng để so sánh sự phân bố của một biến liên tục trong hai nhóm. Kiểm định mặc định là kiểm định tổng thứ hang Wilcoxon và trung vị (khoảng tứ phân vị IQR) khi so sánh hai nhóm. Tuy nhiên, đối với số liệu không có phân bố chuẩn hoặc so sánh nhiều nhóm, kiểm định Kruskal-wallis là kiểm định thích hợp hơn.

``` r
linelist %>% 
  select(age_years, outcome) %>%                       # keep variables of interest
  drop_na(outcome) %>%
  tbl_summary(                                         # produce summary table
    statistic = age_years ~ "{median} ({p25}, {p75})", # specify what statistic to show (this is default so could remove)
    by = outcome) %>%                                  # specify the grouping variable
  add_p(age_years ~ "wilcox.test")                     # specify what test to perform (default so could leave brackets empty)
```

[TABLE]

### Kiểm định Kruskal-wallis

Được sử dụng để so sánh sự phân bố của một biến liên tục trong hai hay nhiều nhóm, bất kể số liệu có phân bố chuẩn hay không.

``` r
linelist %>% 
  select(age_years, outcome) %>%                       # keep variables of interest
  drop_na(outcome) %>%
  tbl_summary(                                         # produce summary table
    statistic = age_years ~ "{median} ({p25}, {p75})", # specify what statistic to show (default, so could remove)
    by = outcome) %>%                                  # specify the grouping variable
  add_p(age_years ~ "kruskal.test")                    # specify what test to perform
```

[TABLE]

## 18.5 Tương quan

Mối tương quan giữa các biến định lượng có thể được khảo sát bằng cách sử dụng package **corrr** thuộc **tidyverse**. Package này cho phép tính các hệ số tương quan bằng phương pháp Pearson, Kendall hoặc Spearman. Gói lệnh này tạo ra một bảng kết quả, và `stretch()` chuyển bảng đó thành data frame dạng dài để vẽ bằng **ggplot2**.

``` r
correlation_tab <- linelist %>% 
  select(generation, age, ct_blood, days_onset_hosp, wt_kg, ht_cm) %>%   # keep numeric variables of interest
  correlate()      # create correlation table (using default pearson)

correlation_tab    # print
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
## remove duplicate entries (the table above is mirrored) 
correlation_tab <- correlation_tab %>% 
  shave()

## view correlation table 
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
## plot correlations 
correlation_tab %>% 
  stretch(na.rm = TRUE) %>% 
  ggplot(aes(x = x, y = y, colour = r, size = abs(r))) +
  geom_point() +
  scale_colour_gradient2(limits = c(-1, 1)) +
  labs(x = NULL, y = NULL)
```

[![](stat_tests_files/figure-html/unnamed-chunk-20-1.png)](stat_tests_files/figure-html/unnamed-chunk-20-1.png)

## 18.6 Nguồn

Phần lớn thông tin trong phần này được phỏng theo các nguồn sau:

[gtsummary](http://www.danieldsjoberg.com/gtsummary/articles/tbl_summary.html) [dplyr](https://dplyr.tidyverse.org/articles/grouping.html) [corrr](https://corrr.tidymodels.org/articles/using-corrr.html) [sthda correlation](http://www.sthda.com/english/wiki/correlation-test-between-two-variables-in-r)
