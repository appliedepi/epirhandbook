# 21  Tỷ suất chuẩn hóa

Chương này sẽ hướng dẫn cách chuẩn hóa một kết quả như là tỷ suất tử vong hoặc nhập viện theo các đặc điểm của tuổi và giới.

Trang này sử dụng package **PHEindicatormethods**.

Chúng ta bắt đầu bằng cách làm rõ quá trình chuẩn bị/làm sạch/kết nối số liệu, vì việc này thường được thực hiện khi kết nối số liệu dân số từ nhiều quốc gia, số liệu dân số chuẩn, tử vong,.v.v.

## 21.1 Tổng quan

Có hai cách để chuẩn hóa: trực tiếp và gián tiếp. Giả sử chúng ta muốn chuẩn hóa tỷ suất tử vong theo tuổi và giới của quốc gia A và quốc gia B, và so sánh tỷ suất chuẩn hóa giữa hai quốc gia này

- Đối với chuẩn hóa trực tiếp, chúng ta phải biết dân số nguy cơ và số tử vong theo từng tầng của tuổi và giới của quốc gia A và B. Một tầng trong ví dụ của chúng ta là phụ nữ trong nhóm tuổi từ 15-44.  
- Đối với chuẩn hóa gián tiếp, chúng ta chỉ cần biết tổng số tử vong và cấu trúc tuổi và giới của mỗi quốc gia. Vì thế, phương án này là khả khi tỷ suất tử vong hoặc dân số theo tuổi và giới không có sẵn. Hơn nữa, chuẩn hóa gián tiếp được ưa chuộng hơn khi có số lượng nhỏ trong các tầng, vì các ước tính trong chuẩn hóa trực tiếp sẽ bị ảnh hưởng bởi các thay đổi quan trọng khi lấy mẫu.

## 21.2 Chuẩn bị

Để chỉ dẫn cách thực hiện chuẩn hóa, chúng ta tạo ra dân số và số tử vong của quốc gia A và B theo tuổi (trong các nhóm tuổi của mỗi 5 tuổi) và giới (nữ, nam). Để các bộ số liệu có thể sử dụng được, chúng ta sẽ thực hiện các bước chuẩn bị như sau:

1.  Gọi các packages  
2.  Tải các bộ số liệu  
3.  Nối số liệu dân số và tử vong của hai quốc gia
4.  Xoay trục bộ số liệu dọc/dài hơn để có một hàng là một tầng theo tuổi-giới
5.  Làm sạch quần thể tham chiếu (dân số thế giới chuẩn) và kết nối nó với số liệu của quốc gia

Trong trường hợp này, số liệu của chúng ta có thể có các định dạng khác nhau. Có lẽ số liệu của chúng ta theo tỉnh, thành phố, hoặc khu vực dịch vụ khác. Chúng ta có thể có một hàng cho mỗi ca tử vong và các thông tin về tuổi và giới cho mỗi trường hợp (hoặc một tỷ lệ có ý nghĩa) của các ca tử vong này. Trong trường hợp này, hãy xem các chương về [Nhóm dữ liệu](grouping.llms.md), [Xoay trục dữ liệu](pivoting.llms.md), và [Bảng mô tả](tables_descriptive.llms.md) để tạo một bộ số liệu với số lượng tử vong và dân số theo tầng của tuổi-giới tính.

Chúng ta cũng cần một quần thể tham chiếu, dân số chuẩn. Với mục đích của thực hành này, chúng ta sẽ sử dụng bộ số liệu `world_standard_population_by_sex`. Dân số chuẩn này dựa trên dân số của 46 quốc gia và được tạo ra vào năm 1960. Có rất nhiều dân số “chuẩn” – ví dụ, trang web của [NHS Scotland](https://www.opendata.nhs.scot/dataset/standard-populations) cung cấp khá nhiều thông tin về Dân số Chuẩn của châu u, Dân số Chuẩn Thế giới, Dân số Chuẩn của Scotland.

### Gọi packages

Đoạn code này hiển thị việc gọi các package cần thiết cho các phân tích. Trong cuốn sách này, chúng tôi nhấn mạnh việc sử dụng hàm `p_load()` từ package **pacman**, giúp cài đặt các package cần thiết *và* gọi chúng ra để sử dụng. Bạn cũng có thể gọi các packages đã cài đặt với hàm `library()` của **base** R. Xem thêm chương [R cơ bản](basics.llms.md) để có thêm thông tin về các packages trong R.

``` r
pacman::p_load(
     rio,                 # import/export data
     here,                # locate files
     stringr,             # cleaning characters and strings
     PHEindicatormethods, # alternative for rate standardisation
     tidyverse,           # data management and visualization
     appliedepidata) # example datasets used in this handbook
```

### Tải số liệu dân số

Xem chương [Tải sách và dữ liệu](download.llms.md) để biết các hướng dẫn về cách tải tất cả các bộ số liệu mẫu trong cuốn số tay này. Bạn có thể nhập trực tiếp dữ liệu của chương Chuẩn hóa này vào R bằng các lệnh `appliedepidata::get_data()` sau:

``` r
# demographics for country A
A_demo <- appliedepidata::get_data(name = "country_demographics")

# deaths for country A
A_deaths <- appliedepidata::get_data(name = "deaths_countryA")

# demographics for country B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")

# import deaths for country B directly from Github
B_deaths <- appliedepidata::get_data(name = "deaths_countryB")

# import demographics for country B directly from Github
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

Trước tiên, chúng ta tải số liệu nhân khẩu (số lượng nam và nữ theo nhóm mỗi 5 tuổi) của hai quốc gia mà chúng ta sẽ so sánh, “Quốc gia A” và “Quốc gia B”.

``` r
# Country A
A_demo <- appliedepidata::get_data(name = "country_demographics")
```

``` r
# Country B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")
```

### Tải số liệu tử vong

Để thuận tiện cho việc thực hành, chúng ta cũng có số lượng tử vong theo tuổi và giới trong khoảng thời gian quan tâm. Số lượng tử vong của mỗi quốc gia nằm trong một tập tin riêng, được hiện thị bên dưới.

Số tử vong ở Quốc gia A

Số tử vong ở Quốc gia B

### Làm sạch số liệu dân số và tử vong

Chúng ta cần kết nối và chuyển đổi các số liệu này theo những cách sau:

- Liên kết dân số của các quốc gia vào một bộ số liệu và xoay trục thành bộ số liệu dạng “dọc/dài” để mỗi tầng tuổi-giới là một hàng  
- Liên kết số liệu tử vong của các quốc gia vào một bộ số liệu và xoay trục thành bộ số liệu dạng “dọc/dài” để mỗi tầng tuổi-giới là một hàng  
- Nối số liệu tử vong với số liệu dân số

Đầu tiên, chúng ta liên kết các bộ số liệu dân số quốc gia, chuyển đổi thành số liệu dạng dọc/dài hơn, và làm sạch số liệu. Xem chương [Xoay trục dữ liệu](pivoting.llms.md) để biết thêm chi tiết.

``` r
pop_countries <- A_demo %>%  # begin with country A dataset
     bind_rows(B_demo) %>%        # bind rows, because cols are identically named
     pivot_longer(                       # pivot longer
          cols = c(m, f),                   # columns to combine into one
          names_to = "Sex",                 # name for new column containing the category ("m" or "f") 
          values_to = "Population") %>%     # name for new column containing the numeric values pivoted
     mutate(Sex = recode(Sex,            # re-code values for clarity
          "m" = "Male",
          "f" = "Female"))
```

Số liệu dân số đã liên kết bây giờ trông giống như sau (nhấp qua để xem cột quốc gia A và B):

Và bây giờ, chúng ta thực hiện các thao tác tương tự trên hai bộ số liệu tử vong.

``` r
deaths_countries <- A_deaths %>%    # begin with country A deaths dataset
     bind_rows(B_deaths) %>%        # bind rows with B dataset, because cols are identically named
     pivot_longer(                  # pivot longer
          cols = c(Male, Female),        # column to transform into one
          names_to = "Sex",              # name for new column containing the category ("m" or "f") 
          values_to = "Deaths") %>%      # name for new column containing the numeric values pivoted
     rename(age_cat5 = AgeCat)      # rename for clarity
```

Số liệu tử vong bây giờ trông giống như sau và chứa số liệu của cả hai quốc gia:

Bây giờ, chúng ta nối số liệu tử vong và số liệu dân số dựa trên các cột chung `Country`, `age_cat5`, và `Sex`. Thao tác này sẽ thêm cột `Deaths`.

``` r
country_data <- pop_countries %>% 
     left_join(deaths_countries, by = c("Country", "age_cat5", "Sex"))
```

Bây giờ, chúng ta có thể phân loại các biến số `Sex`, `age_cat5`, và `Country` thành dạng factors và đặt thứ tự các giá trị của biến số bằng cách sử dụng hàm `fct_relevel()` từ package **forcats**, như được mô tả trong chương [Factors](factors.llms.md). Lưu ý rằng việc phân loại giá trị biến không thay đổi số liệu một cách rõ ràng, nhưng lệnh `arrange()` sẽ sắp xếp nó theo Quốc gia, nhóm tuổi và giới tính.

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

***CẨN TRỌNG:*** Nếu số trường hợp tử vong mỗi tầng là nhỏ, hãy cân nhắc chia nhóm tuổi mỗi 10-15 năm thay vì mỗi 5 năm cho các nhóm.

### Tải dân số tham chiếu

Cuối cùng, để chuẩn hóa trực tiếp, chúng ta nhập dân số tham chiếu (“dân số chuẩn” thế giới theo giới tính)

``` r
# Reference population
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

### Làm sach dân số tham chiếu

Các giá trị của biến tuổi trong bộ số liệu `country_data` và `standard_pop_data` cần phải được căn chỉnh.

Hiện tại, các giá trị của cột biến phân loại `age_cat5` trong bộ số liệu `standard_pop_data` có chứa từ “years” và “plus”, trong khi không có các từ này trong trong bộ số liệu `country_data`. Chúng ta cần phải chuyển đổi các giá trị này giống nhau. Chúng ta sẽ sử dụng hàm `str_replace_all()` từ package **stringr**, như được mô tả trong chương [Ký tự và chuỗi](characters_strings.llms.md), để thay thế thành những kiểu mẫu không có khoảng trắng `""`.

Hàm `calculate_dsr()` nhận dân số chuẩn qua đối số `stdpop =`, vì vậy cột này có thể có tên bất kỳ. Chúng ta đổi tên cột thành `"pop"` vì đoạn code bên dưới dùng `stdpop = pop`.

``` r
# Remove specific string from column values
standard_pop_clean <- standard_pop_data %>%
     mutate(
          age_cat5 = str_replace_all(age_cat5, "years", ""),   # remove "year"
          age_cat5 = str_replace_all(age_cat5, "plus", ""),    # remove "plus"
          age_cat5 = str_replace_all(age_cat5, " ", "")) %>%   # remove " " space
     
     rename(pop = WorldStandardPopulation)   # change col name to "pop", the column given to stdpop = in calculate_dsr()
```

***CẨN TRỌNG:*** Nếu chúng ta cố gắng sử dụng hàm `str_replace_all()` để loại bỏ *biểu tượng* dấu cộng, hàm này sẽ không thực hiện bởi vì nó là một biểu tượng đặc biệt. “Xử lý” các biểu tượng này bằng cách đặt hai dấu gạch chéo phía trước như trong lệnh `str_replace_call(column, "\\+", "")`.

### Tạo bộ số liệu với dân số chuẩn

Cuối cùng, package **PHEindicatormethods**, được trình bày chi tiết [bên dưới](#standard_phe), đòi hỏi dân số chuẩn đã được nối vào số ca tử vong và dân số của các quốc gia. Vì vậy, chúng ta sẽ tạo một bộ số liệu với tên `all_data` cho mục đích đó.

``` r
all_data <- left_join(country_data, standard_pop_clean, by=c("age_cat5", "Sex"))
```

Bộ số liệu hoàn chỉnh trông sẽ như thế này:

## 21.3 Package **PHEindicatormethods**

Chúng ta tính tỷ suất chuẩn hóa bằng package **PHEindicatormethods**. Package này cho phép chúng ta tính toán tỷ suất chuẩn hóa trực tiếp cũng như gián tiếp. Chúng tôi sẽ hướng dẫn cả hai.

Phần này chúng ta sẽ sử dụng bộ số liệu `all_data` được tạo ở cuối phần Chuẩn bị. Bộ số liệu này bao gồm dân số quốc gia, số tử vong và dân số tham chiếu. Bạn có thể xem nó ở [đây](#standard_all).

### Tỷ suất chuẩn hóa trực tiếp

Đầu tiên, chúng ta nhóm số liệu theo Quốc gia như bên dưới và sau đó chuyển số liệu vào hàm `calculate_dsr()` để có được tỷ suất chuẩn hóa trực tiếp theo quốc gia.

Lưu ý, `calculate_dsr()` yêu cầu dân số tham chiếu (chuẩn) được cung cấp dưới dạng một **cột bên trong số liệu của một quốc gia cụ thể**. Hãy chỉ định tên của cột này trong đối số `stdpop =`. Trong ví dụ bên dưới, cột này là `pop`.

Xem trợ giúp bằng cách gõ `?calculate_dsr` hoặc các liên kết trong phần Tài nguyên học liệu để biết thêm thông tin.

``` r
# Calculate rates per country directly standardized for age and sex
mortality_ds_rate_phe <- all_data %>%
     group_by(Country) %>%
     PHEindicatormethods::calculate_dsr(
          x = Deaths,                 # column with observed number of events
          n = Population,             # column with non-standard pops for each stratum
          stdpop = pop)               # standard populations for each stratum

# Print table
knitr::kable(mortality_ds_rate_phe)
```

| Country | total_count | total_pop | value | lowercl | uppercl | confidence | statistic | method |
|:---|---:|---:|---:|---:|---:|:---|:---|:---|
| A | 11344 | 86790567 | 23.56686 | 23.08107 | 24.05944 | 95% | dsr per 100000 | Dobson |
| B | 9955 | 52898281 | 19.32549 | 18.45516 | 20.20882 | 95% | dsr per 100000 | Dobson |

### Tỷ suất chuẩn hóa gián tiếp

Để chuẩn hóa gián tiếp, chúng ta cần dân số tham chiếu có số lượng tử vong và dân số theo tầng. Trong ví dụ này, chúng ta sẽ tính tỷ suất của quốc gia A bằng cách *sử dụng quốc gia B làm dân số tham chiếu*, vì dân số tham chiếu trong bộ số liệu `standard_pop_clean` không có số lượng tử vong theo tầng.

Trước tiên, chúng ta tạo dân số tham chiếu từ quốc gia B như bên dưới. Sau đó, chúng ta chuyển số liệu tử vong và dân số của quốc gia A, kết nối nó với dân số tham chiếu và chuyển nó vào hàm `calculate_ISRate()`, để có được tỷ suất chuẩn hóa gián tiếp. Dĩ nhiên, chúng ta cũng có thể làm ngược lại.

Lưu ý - trong ví dụ bên dưới, dân số tham chiếu được cung cấp dưới dạng một data frame riêng rẽ. Trong trường hợp này, chúng ta cần đảm bảo rằng các véctơ `x =`, `n =`, `x_ref =` và `n_ref =` tất cả được sắp đặt cùng giá trị với loại chuẩn hóa (theo đúng tầng) như được sắp đặt trong data frame quốc gia, vì vị trí các bản ghi/các hàng phải khớp với nhau.

Xem trợ giúp bằng cách gõ `?phr_isr` hoặc các liên kết trong phần Tài nguyên học liệu để biết thêm thông tin.

``` r
# Create reference population
refpopCountryB <- country_data %>% 
  filter(Country == "B") 

# Calculate rates for country A indirectly standardized by age and sex
mortality_is_rate_phe_A <- country_data %>%
     filter(Country == "A") %>%
     PHEindicatormethods::calculate_ISRate(
          x = Deaths,                 # column with observed number of events
          n = Population,             # column with non-standard pops for each stratum
          x_ref = refpopCountryB$Deaths,  # reference number of deaths for each stratum
          n_ref = refpopCountryB$Population)  # reference population for each stratum

# Print table
knitr::kable(mortality_is_rate_phe_A)
```

| observed | expected | ref_rate | value | lowercl | uppercl | confidence | statistic | method |
|---:|---:|---:|---:|---:|---:|:---|:---|:---|
| 11344 | 15847.42 | 18.81914 | 13.47123 | 13.22446 | 13.72145 | 95% | indirectly standardised rate per 100000 | Byars |

## 21.4 Tài nguyên học liệu

Với các ví dụ khác sử dụng package **PHEindicatormethods**, vui lòng xem tại [website này](https://mran.microsoft.com/snapshot/2018-10-22/web/packages/PHEindicatormethods/vignettes/IntroductiontoPHEindicatormethods.html)

Xem thêm **PHEindicatormethods** [tài liệu dưới dạng tệp pdf](https://cran.r-project.org/web/packages/PHEindicatormethods/PHEindicatormethods.pdf)
