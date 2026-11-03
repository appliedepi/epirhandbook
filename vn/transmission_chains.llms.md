# 37  Chuỗi lây nhiễm

## 37.1 Tổng quan

Công cụ chính để xử lý, phân tích và trực quan hóa chuỗi lây nhiễm và dữ liệu theo dõi tiếp xúc là package **epicontacts**, được phát triển bởi những chuyên gia làm việc tại RECON. Hãy thử biểu đồ tương tác bên dưới bằng cách di chuột qua các nút để biết thêm thông tin, kéo-thả để di chuyển chúng và nhấp vào chúng để đánh dấu các trường hợp phía dưới.

## 37.2 Chuẩn bị

### Gọi packages

Đầu tiên hãy tải các package tiêu chuẩn cần thiết để nhập và xử lý dữ liệu. Trong cuốn sách này, chúng tôi nhấn mạnh đến hàm `p_load()` từ package **pacman**, sẽ cài đặt package nếu cần *và* gọi chúng ra để sử dụng. Bạn cũng có thể gọi các package bằng hàm `library()` từ **base** R. Xem chương [R cơ bản](basics.llms.md) để biết thêm thông tin về các package trong R.

``` r
pacman::p_load(
   rio,          # File import
   here,         # File locator
   tidyverse,    # Data management + ggplot2 graphics
   remotes       # Package installation from github
)
```

Bạn sẽ sử dụng phiên bản phát triển của **epicontacts**, có thể được cài đặt từ github bằng cách sử dụng hàm `p_install_github()` từ package **pacman**. Bạn chỉ cần chạy lệnh này dưới đây một lần, không phải bất cứ khi nào bạn sử dụng package (sau đó, bạn có thể sử dụng hàm `p_load()` như bình thường).

``` r
pacman::p_install_gh("reconhub/epicontacts@timeline")
```

### Nhập dữ liệu

Chúng ta nhập bộ dữ liệu về các trường hợp bệnh từ một vụ dịch Ebola mô phỏng. Nếu bạn muốn tải xuống dữ liệu để làm theo từng bước, hãy xem hướng dẫn trong chương [Tải sách và dữ liệu](download.llms.md). Bộ dữ liệu được nhập bằng hàm `import()` từ package **rio**. Xem chương [Nhập xuất dữ liệu](importing.llms.md) để biết các cách nhập dữ liệu khác nhau.

``` r
# import the linelist
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

50 hàng đầu tiên của bộ dữ liệu `linelist` được hiển thị bên dưới. Mối quan tâm đặc biệt là các cột `case_id`, `generation`, `infector`, và `source`.

### Tạo đối tượng epicontacts

Sau đó, chúng ta cần tạo một đối tượng **epicontacts**, với yêu cầu hai kiểu dữ liệu như sau:

- Một bộ dữ liệu `linelist` ghi lại các trường hợp trong đó các cột là các biến và các hàng tương ứng với các trường hợp duy nhất
- Một danh sách các cạnh (edge) thể hiện liên kết giữa các quan sát trên ID duy nhất (có thể là liên hệ, sự kiện lây nhiễm, v.v.)

Bởi vì chúng ta đã có sẵn bộ dữ liệu `linelist`, chúng ta chỉ cần tạo một danh sách các đường liên kết giữa các trường hợp, cụ thể hơn là giữa các ID. Chúng ta có thể trích xuất các đường liên kết lây nhiễm từ bộ số liệu `linelist` bằng cách liên kết cột `infector` với cột `case_id`. Tại đây, chúng ta cũng có thể thêm các “thuộc tính cạnh - edge properties”, nghĩa là bất kỳ biến nào mô tả mối liên kết giữa hai trường hợp, không phải bản thân các trường hợp đó. Để minh họa, chúng ta sẽ thêm một biến `location` mô tả vị trí của sự kiện truyền nhiễm và một biến mô tả khoảng thời gian tiếp xúc tính bằng ngày.

Trong đoạn code dưới đây, hàm `transmute` thuộc package **dplyr** tương tự như hàm `mutate`, ngoại trừ nó chỉ giữ các cột mà chúng ta đã chỉ định trong hàm. Hàm `drop_na` sẽ lọc ra bất kỳ hàng nào mà các cột được chỉ định có giá trị `NA` ; trong trường hợp này, chúng ta chỉ muốn giữ lại các hàng mà tác nhân lây nhiễm đã biết.

``` r
## generate contacts
set.seed(1)
contacts <- linelist %>%
  transmute(
    infector = infector,
    case_id = case_id,
    location = sample(c("Community", "Nosocomial"), n(), TRUE),
    duration = sample.int(10, n(), TRUE)
  ) %>%
  drop_na(infector)
```

Bây giờ chúng ta có thể tạo đối tượng **epicontacts** bằng cách sử dụng hàm `make_epicontacts`. Chúng ta cần chỉ định cột trong bộ dữ liệu `linelist` trỏ đến mã định danh trường hợp duy nhất (ID), cũng như cột trong điểm tiếp xúc tới mã định danh duy nhất của các trường hợp có liên quan trong mỗi liên kết. Các liên kết này có tính định hướng, nghĩa là việc lây nhiễm sẽ đi *từ* người lây nhiễm *đến* ca bệnh, vì vậy chúng ta cần chỉ định các đối số `from` và `to` cho phù hợp. Chúng ta cũng đặt đối số `directed` thành `TRUE`, điều này sẽ ảnh hưởng đến các hoạt động về sau.

``` r
## generate epicontacts object
epic <- make_epicontacts(
  linelist = linelist,
  contacts = contacts,
  id = "case_id",
  from = "infector",
  to = "case_id",
  directed = TRUE
)
```

Sau khi kiểm tra các đối tượng **epicontacts**, chúng ta có thể thấy rằng cột `case_id` trong bộ dữ liệu `linelist` đã được đổi tên thành `id` và các cột `case_id` và cột `infector` trong liên hệ đã được đổi tên thành `from` và `to`. Điều này đảm bảo tính nhất quán trong các hoạt động xử lý, trực quan và phân tích tiếp theo.

``` r
## view epicontacts object
epic
```


    /// Epidemiological Contacts //

      // class: epicontacts
      // 5,888 cases in linelist; 3,800 contacts; directed 

      // linelist

    # A tibble: 5,888 × 30
       id     generation date_infection date_onset date_hospitalisation date_outcome
       <chr>       <dbl> <date>         <date>     <date>               <date>      
     1 5fe599          4 2014-05-08     2014-05-13 2014-05-15           NA          
     2 8689b7          4 NA             2014-05-13 2014-05-14           2014-05-18  
     3 11f8ea          2 NA             2014-05-16 2014-05-18           2014-05-30  
     4 b8812a          3 2014-05-04     2014-05-18 2014-05-20           NA          
     5 893f25          3 2014-05-18     2014-05-21 2014-05-22           2014-05-29  
     6 be99c8          3 2014-05-03     2014-05-22 2014-05-23           2014-05-24  
     7 07e3e8          4 2014-05-22     2014-05-27 2014-05-29           2014-06-01  
     8 369449          4 2014-05-28     2014-06-02 2014-06-03           2014-06-07  
     9 f393b4          4 NA             2014-06-05 2014-06-06           2014-06-18  
    10 1389ca          4 NA             2014-06-05 2014-06-07           2014-06-09  
    # ℹ 5,878 more rows
    # ℹ 24 more variables: outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>,
    #   age_years <dbl>, age_cat <fct>, age_cat5 <fct>, hospital <chr>, lon <dbl>,
    #   lat <dbl>, infector <chr>, source <chr>, wt_kg <dbl>, ht_cm <dbl>,
    #   ct_blood <dbl>, fever <chr>, chills <chr>, cough <chr>, aches <chr>,
    #   vomit <chr>, temp <dbl>, time_admission <chr>, bmi <dbl>,
    #   days_onset_hosp <dbl>

      // contacts

    # A tibble: 3,800 × 4
       from   to     location   duration
       <chr>  <chr>  <chr>         <int>
     1 f547d6 5fe599 Community         7
     2 f90f5f b8812a Community         5
     3 11f8ea 893f25 Nosocomial        6
     4 aec8ec be99c8 Community         7
     5 893f25 07e3e8 Community         7
     6 133ee7 369449 Community         3
     7 996f3a 2978ac Community         5
     8 133ee7 57a565 Community        10
     9 37a6f6 fc15ef Community         3
    10 9f6884 2eaa9a Community         8
    # ℹ 3,790 more rows

## 37.3 Xử lý

### Chia nhỏ bộ dữ liệu

Phương thức `subset()` cho các đối tượng **epicontacts** cho phép lọc các mạng lưới dựa trên các thuộc tính của bộ dữ liệu `linelist` (“thuộc tính nút”) và cơ sở dữ liệu tiếp xýc (“thuộc tính cạnh”). Các giá trị này phải được chuyển đổi dưới dạng danh sách đã đặt tên cho đối số tương ứng. Ví dụ: trong đoạn code bên dưới, chúng tôi chỉ giữ lại các trường hợp nam giới trong bộ số liệu `linelist` có ngày lây nhiễm từ tháng 4 đến tháng 7 năm 2014 (ngày tháng được chỉ định dưới dạng khoảng) và các liên kết lây nhiễm xảy ra trong bệnh viện.

``` r
sub_attributes <- subset(
  epic,
  node_attribute = list(
    gender = "m",
    date_infection = as.Date(c("2014-04-01", "2014-07-01"))
  ), 
  edge_attribute = list(location = "Nosocomial")
)
sub_attributes
```


    /// Epidemiological Contacts //

      // class: epicontacts
      // 69 cases in linelist; 1,941 contacts; directed 

      // linelist

    # A tibble: 69 × 30
       id     generation date_infection date_onset date_hospitalisation date_outcome
       <chr>       <dbl> <date>         <date>     <date>               <date>      
     1 5fe599          4 2014-05-08     2014-05-13 2014-05-15           NA          
     2 893f25          3 2014-05-18     2014-05-21 2014-05-22           2014-05-29  
     3 2978ac          4 2014-05-30     2014-06-06 2014-06-08           2014-06-15  
     4 57a565          4 2014-05-28     2014-06-13 2014-06-15           NA          
     5 fc15ef          6 2014-06-14     2014-06-16 2014-06-17           2014-07-09  
     6 99e8fa          7 2014-06-24     2014-06-28 2014-06-29           2014-07-09  
     7 f327be          6 2014-06-14     2014-07-12 2014-07-13           2014-07-14  
     8 90e5fe          5 2014-06-18     2014-07-13 2014-07-14           2014-07-16  
     9 a47529          5 2014-06-13     2014-07-17 2014-07-18           2014-07-26  
    10 da8ecb          5 2014-06-20     2014-07-18 2014-07-20           2014-08-01  
    # ℹ 59 more rows
    # ℹ 24 more variables: outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>,
    #   age_years <dbl>, age_cat <fct>, age_cat5 <fct>, hospital <chr>, lon <dbl>,
    #   lat <dbl>, infector <chr>, source <chr>, wt_kg <dbl>, ht_cm <dbl>,
    #   ct_blood <dbl>, fever <chr>, chills <chr>, cough <chr>, aches <chr>,
    #   vomit <chr>, temp <dbl>, time_admission <chr>, bmi <dbl>,
    #   days_onset_hosp <dbl>

      // contacts

    # A tibble: 1,941 × 4
       from   to     location   duration
       <chr>  <chr>  <chr>         <int>
     1 11f8ea 893f25 Nosocomial        6
     2 a75c7f 7f5a01 Nosocomial        1
     3 a15e13 f327be Nosocomial        7
     4 beb26e 959170 Nosocomial       10
     5 567136 8ebf6e Nosocomial        4
     6 894024 e56412 Nosocomial        2
     7 a2086d a47529 Nosocomial        4
     8 d6584f f5c142 Nosocomial       10
     9 312ecf 3ad520 Nosocomial        1
    10 52ea64 062638 Nosocomial        5
    # ℹ 1,931 more rows

Chúng ta có thể sử dụng hàm `thin` để lọc trong bộ số liệu `linelist` để bao gồm các trường hợp được tìm thấy trong danh sách “contacts” bằng cách đặt đối số `what = "linelist"`, hoặc lọc trong danh sách “contacts” để bao gồm các trường hợp được tìm thấy trong bộ số liệu `linelist` bằng cách đặt đối số `what = "contacts"`. Trong đoạn code dưới đây, chúng ta đang lọc thêm từ đối tượng epicontacts để chỉ giữ lại các đường liên kết lây nhiễm có liên quan đến các trường hợp nam giới bị lây nhiễm giữa tháng 4 và tháng 7 mà chúng ta đã lọc ở trên. Chúng ta có thể thấy rằng chỉ có 3 liên kết lây nhiễm đã biết phù hợp với đặc điểm đó.

``` r
sub_attributes <- thin(sub_attributes, what = "contacts")
nrow(sub_attributes$contacts)
```

    [1] 3

Bên cạnh việc subset theo thuộc tính nút (node) và cạnh (edge), các mạng liên kết có thể được cắt tỉa để chỉ bao gồm các thành phần được kết nối với một số nút nhất định. Đối số `cluster_id` sẽ lấy một vectơ chứa ID các ca bệnh và trả về danh sách của các cá nhân được liên kết một cách trực tiếp hoặc gián tiếp tới các ID đó. Trong đoạn code dưới đây, chúng ta có thể thấy rằng tổng cộng 13 trường hợp trong bộ số liệu `linelist` có liên quan đến các cụm chứa `2ae019` và `71577a`.

``` r
sub_id <- subset(epic, cluster_id = c("2ae019","71577a"))
nrow(sub_id$linelist)
```

    [1] 13

Phương pháo `subset()` cho các đối tượng `epicontacts` cũng cho phép lọc theo kích thước cụm bằng cách sử dụng các đối số `cs`, `cs_min` và `cs_max`. Trong đoạn code bên dưới, chúng ta chỉ giữ lại các trường hợp được liên kết với các cụm 10 trường hợp hoặc lớn hơn và có thể thấy rằng 271 trường hợp trong trong bộ số liệu `linelist` có liên quan đến các cụm đó.

``` r
sub_cs <- subset(epic, cs_min = 10)
nrow(sub_cs$linelist)
```

    [1] 271

### Truy cập thông tin ID

Hàm `get_id()` truy xuất thông tin về ID ca bệnh trong bộ dữ liệu và có thể được tham số hóa như sau:

- **linelist**: ID trong bộ dữ liệu `linelist`
- **contacts**: ID trong bộ dữ liệu contact (kết hợp “from” và “to”)
- **from**: ID trong cột “from” của bộ dữ liệu contact
- **to**: ID trong cột “to” của bộ dữ liệu contact
- **all**: các ID xuất hiện ở bất kỳ một trong hai bộ dữ liệu
- **common**: các ID xuất hiện trong cả bộ dữ liệu contact và bộ dữ liệu `linelist`

Ví dụ: xem 10 ID đầu tiên trong bộ dữ liệu contact?

``` r
contacts_ids <- get_id(epic, "contacts")
head(contacts_ids, n = 10)
```

     [1] "f547d6" "f90f5f" "11f8ea" "aec8ec" "893f25" "133ee7" "996f3a" "37a6f6"
     [9] "9f6884" "4802b1"

Có bao nhiêu ID được tìm thấy trong cả hai bộ dữ liệu tiếp xúc và `linelist`?

``` r
length(get_id(epic, "common"))
```

    [1] 4352

## 37.4 Trực quan hóa

### Biểu đồ cơ bản

Tất cả các hình ảnh trực quan của các đối tượng **epicontacts** được xử lý bởi hàm `plot`. Trước tiên, chúng ta sẽ lọc đối tượng **epicontacts** để chỉ bao gồm các trường hợp có ngày bắt đầu vào tháng 6 năm 2014 bằng cách sử dụng hàm `subset`, và chỉ bao gồm các tiếp xúc được liên kết với các trường hợp đó bằng cách sử dụng hàm `thin`.

``` r
## subset epicontacts object
sub <- epic %>%
  subset(
    node_attribute = list(date_onset = c(as.Date(c("2014-06-30", "2014-06-01"))))
  ) %>%
 thin("contacts")
```

Sau đó, chúng ta có thể tạo biểu đồ cơ bản, có tính tương tác rất đơn giản như sau:

``` r
## plot epicontacts object
plot(
  sub,
  width = 700,
  height = 700
)
```

Bạn có thể di chuyển các nút xung quanh bằng cách kéo chúng, di chuột qua chúng để biết thêm thông tin và nhấp vào chúng để đánh dấu các trường hợp được kết nối.

Có một số lượng lớn các đối số để tùy chỉnh biểu đồ này. Chúng ta sẽ trình bày những vấn đề chính ở đây, nhưng bạn có thể xem thêm tài liệu thông qua lệnh `?vis_epicontacts` (hàm được gọi khi sử dụng biểu đồ trên đối tượng **epicontacts**) để có được mô tả đầy đủ về các đối số của hàm.

#### Trực quan hóa các thuộc tính của nút

Màu nút, hình dạng nút và kích thước nút có thể được ánh xạ tới một cột nhất định trong bộ số liệu `linelist` bằng cách sử dụng các đối số `node_color`, `node_shape` và `node_size`. Điều này tương tự với cú pháp `aes` mà bạn có thể thấy trong **ggplot2**.

Màu sắc, hình dạng và kích thước cụ thể của các nút có thể được chỉ định như sau:

- **Màu sắc** thông qua đối số `col_pal`, bằng cách cung cấp một danh sách tên được chỉ định cho từng màu cụ thể như được thực hiện bên dưới hoặc bằng cách cung cấp một hàm bảng màu như `colorRampPalette(c("black", "red", "orange"))`, mà sẽ giúp cung cấp một dải màu giữa các màu được chỉ định.

- **Hình dạng** bằng cách chuyển một danh sách đã đặt tên đến đối số `shapes`, chỉ định một hình dạng cho mỗi phần tử duy nhất trong cột bộ số liệu `linelist` được chỉ định bởi đối số `node_shape`. Xem `codeawesome` để biết các hình dạng có sẵn.

- **Kích thước** bằng cách chuyển một phạm vi kích thước của các nút tới đối số `size_range`.

Dưới đây là một ví dụ, trong đó màu sắc thể hiện cho outcome, hình dạng thể hiện cho giới tính và kích thước thể hiện cho độ tuổi:

``` r
plot(
  sub, 
  node_color = "outcome",
  node_shape = "gender",
  node_size = "age",
  col_pal = c(Death = "firebrick", Recover = "green"),
  shapes = c(f = "female", m = "male"),
  size_range = c(40, 60),
  height = 700,
  width = 700
)
```

#### Trực quan hóa các thuộc tính cạnh

Màu, độ dày và kiểu đường có thể được ánh xạ tới một cột nhất định trong bộ dữ liệu tiếp xúc bằng cách sử dụng các đối số `edge_color`, `edge_width` và `edge_linetype`. Các màu cụ và độ dày của các cạnh có thể được chỉ định như sau:

- **Màu sắc** thông qua đối số `edge_col_pal`, theo cách tương tự được sử dụng cho `col_pal`.

- **Độ rộng** bằng cách chuyển phạm vi kích thước của các nút tới đối số `width_range`.

Dưới đây là ví dụ:

``` r
plot(
  sub, 
  node_color = "outcome",
  node_shape = "gender",
  node_size = 'age',
  col_pal = c(Death = "firebrick", Recover = "green"),
  shapes = c(f = "female", m = "male"),
  size_range = c(40, 60),
  edge_color = 'location',
  edge_linetype = 'location',
  edge_width = 'duration',
  edge_col_pal = c(Community = "orange", Nosocomial = "purple"),
  width_range = c(1, 3),
  height = 700,
  width = 700
)
```

### Trục thời gian

Chúng ta cũng có thể trực quan hóa mạng lây nhiễm dọc theo trục thời gian bằng cách ánh xạ đối số `x_axis` vào một cột trong bộ số liệu `linelist`. Trong ví dụ dưới đây, trục x biểu thị ngày bắt đầu triệu chứng. Chúng ta cũng đã chỉ định đối số `arrow_size` để đảm bảo các mũi tên không quá lớn và đặt `label = FALSE` để làm cho hình bớt lộn xộn.

``` r
plot(
  sub,
  x_axis = "date_onset",
  node_color = "outcome",
  col_pal = c(Death = "firebrick", Recover = "green"),
  arrow_size = 0.5,
  node_size = 13,
  label = FALSE,
  height = 700,
  width = 700
)
```

Có một số lượng lớn các đối số bổ sung để cụ thể hơn cách mà mạng lưới này được hiển thị dọc theo trục thời gian, bạn có thể kiểm tra thông qua lệnh `?vis_temporal_interactive` (hàm được gọi khi sử dụng hàm `plot` trên đối tượng **epicontacts** với đối số `x_axis` được chỉ định). Chúng tôi sẽ mô tả kỹ hơn ở bên dưới.

#### Chỉ định hình dạng cây lây nhiễm

Có hai hình dạng chính mà cây lây nhiễm có thể giả định, được chỉ định bằng cách sử dụng đối số `network_shape`. Đầu tiên là hình dạng nhánh `branching` như hình trên, trong đó một cạnh thẳng nối hai nút bất kỳ. Đây là cách trình bày trực quan nhất, tuy nhiên có thể dẫn đến các cạnh chồng lên nhau trong một mạng kết nối dày đặc. Kiểu hình thứ hai là `rectangle`, sẽ tạo ra một cái cây giống như cây phát sinh loài. Ví dụ:

``` r
plot(
  sub,
  x_axis = "date_onset",
  network_shape = "rectangle",
  node_color = "outcome",
  col_pal = c(Death = "firebrick", Recover = "green"),
  arrow_size = 0.5,
  node_size = 13,
  label = FALSE,
  height = 700,
  width = 700
)
```

Mỗi nút có thể được gán một vị trí dọc duy nhất bằng cách chuyển đổi đối số `position_dodge`. Vị trí của các trường hợp không được kết nối (tức là không có lây nhiễm được báo cáo) được xác định bằng cách sử dụng đối số `unlinked_pos`.

``` r
plot(
  sub,
  x_axis = "date_onset",
  network_shape = "rectangle",
  node_color = "outcome",
  col_pal = c(Death = "firebrick", Recover = "green"),
  position_dodge = TRUE,
  unlinked_pos = "bottom",
  arrow_size = 0.5,
  node_size = 13,
  label = FALSE,
  height = 700,
  width = 700
)
```

Vị trí của nút “mẹ” so với các nút “con” có thể được xác định bằng cách sử dụng đối số `parent_pos`. Tùy chọn mặc định là đặt nút “mẹ” ở giữa, tuy nhiên nó có thể được đặt ở dưới cùng (`parent_pos = 'bottom'`) hoặc ở trên cùng (`parent_pos = 'top'`).

``` r
plot(
  sub,
  x_axis = "date_onset",
  network_shape = "rectangle",
  node_color = "outcome",
  col_pal = c(Death = "firebrick", Recover = "green"),
  parent_pos = "top",
  arrow_size = 0.5,
  node_size = 13,
  label = FALSE,
  height = 700,
  width = 700
)
```

#### Lưu biểu đồ

Bạn có thể lưu một biểu đồ dưới dạng tệp tin html tương tác, độc lập với hàm `visSave` từ package **VisNetwork**:

``` r
plot(
  sub,
  x_axis = "date_onset",
  network_shape = "rectangle",
  node_color = "outcome",
  col_pal = c(Death = "firebrick", Recover = "green"),
  parent_pos = "top",
  arrow_size = 0.5,
  node_size = 13,
  label = FALSE,
  height = 700,
  width = 700
) %>%
  visNetwork::visSave("network.html")
```

Rất tiếc, việc lưu các kết quả đầu ra mạng lưới lây nhiễm này dưới dạng hình ảnh trở nên khó khăn và bạn cần lưu dưới dạng tệp tin html và sau đó chụp ảnh màn hình của tệp tin này bằng backage **webshot**. Trong đoạn code dưới đây, chúng ta đang chuyển đổi tệp tin html được lưu ở trên thành dạng file ảnh PNG:

``` r
webshot(url = "network.html", file = "network.png")
```

### Dòng thời gian

Bạn cũng có thể thêm dòng thời gian cho mạng lưới truyền nhiễm, được biểu diễn trên trục x của mỗi trường hợp. Nó có thể được sử dụng để trực quan hóa các vị trí ca bệnh, hoặc thời gian dẫn đến outcome. Để tạo dòng thời gian, chúng ta cần tạo một data.frame gồm ít nhất ba cột bao gồm ID, ngày bắt đầu của “sự kiện” và ngày kết thúc của “sự kiện”. Bạn cũng có thể thêm bất kỳ cột giá trị nào khác mà sau đó có thể được ánh xạ tới các thuộc tính nút và cạnh của dòng thời gian. Trong đoạn code dưới đây, chúng ta tạo một dòng thời gian từ ngày bắt đầu có triệu chứng đến ngày có outcome và giữ các biến outcome và bệnh viện mà chúng ta đã sử dụng để xác định hình dạng và màu sắc của nút. Lưu ý rằng bạn có thể có nhiều hơn một dòng thời gian hàng/sự kiện cho mỗi trường hợp, ví dụ: nếu một trường hợp được chuyển viện giữa nhiều bệnh viện.

``` r
## generate timeline
timeline <- linelist %>%
  transmute(
    id = case_id,
    start = date_onset,
    end = date_outcome,
    outcome = outcome,
    hospital = hospital
  ) %>%
  filter(id %in% get_id(sub, "common"), !is.na(start), !is.na(end))
```

Sau đó, chúng ta chuyển phần tử dòng thời gian vào đối số `timeline`. Chúng ta có thể ánh xạ các thuộc tính dòng thời gian với màu sắc, hình dạng và kích thước của nút dòng thời gian theo cùng một cách đã xác định trong các phần trước, ngoại trừ việc chúng ta có hai nút: nút bắt đầu và nút kết thúc của mỗi dòng thời gian, có các đối số riêng biệt. Ví dụ: `tl_start_node_color` xác định cột dòng thời gian nào được ánh xạ với màu của nút bắt đầu, trong khi `tl_end_node_shape` xác định cột dòng thời gian nào được ánh xạ tới hình dạng của nút kết thúc. Chúng ta cũng có thể ánh xạ màu, độ dày, kiểu đường kẻ và nhãn vào *cạnh* dòng thời gian thông qua các đối số `tl_edge_`.

Xem `?vis_temporal_interactive` (hàm được gọi khi vẽ biểu đồ một đối tượng epicontacts) để biết tài liệu chi tiết về các đối số. Mỗi đối số cũng được chú thích trong đoạn code bên dưới:

``` r
## define shapes
shapes <- c(
  f = "female",
  m = "male",
  Death = "user-times",
  Recover = "heartbeat",
  "NA" = "question-circle"
)

## define colours
colours <- c(
  Death = "firebrick",
  Recover = "green",
  "NA" = "grey"
)

## make plot
plot(
  sub,
  ## max x coordinate to date of onset
  x_axis = "date_onset",
  ## use rectangular network shape
  network_shape = "rectangle",
  ## mape case node shapes to gender column
  node_shape = "gender",
  ## we don't want to map node colour to any columns - this is important as the
  ## default value is to map to node id, which will mess up the colour scheme
  node_color = NULL,
  ## set case node size to 30 (as this is not a character, node_size is not
  ## mapped to a column but instead interpreted as the actual node size)
  node_size = 30,
  ## set transmission link width to 4 (as this is not a character, edge_width is
  ## not mapped to a column but instead interpreted as the actual edge width)
  edge_width = 4,
  ## provide the timeline object
  timeline = timeline,
  ## map the shape of the end node to the outcome column in the timeline object
  tl_end_node_shape = "outcome",
  ## set the size of the end node to 15 (as this is not a character, this
  ## argument is not mapped to a column but instead interpreted as the actual
  ## node size)
  tl_end_node_size = 15,
  ## map the colour of the timeline edge to the hospital column
  tl_edge_color = "hospital",
  ## set the width of the timeline edge to 2 (as this is not a character, this
  ## argument is not mapped to a column but instead interpreted as the actual
  ## edge width)
  tl_edge_width = 2,
  ## map edge labels to the hospital variable
  tl_edge_label = "hospital",
  ## specify the shape for everyone node attribute (defined above)
  shapes = shapes,
  ## specify the colour palette (defined above)
  col_pal = colours,
  ## set the size of the arrow to 0.5
  arrow_size = 0.5,
  ## use two columns in the legend
  legend_ncol = 2,
  ## set font size
  font_size = 15,
  ## define formatting for dates
  date_labels = c("%d %b %Y"),
  ## don't plot the ID labels below nodes
  label = FALSE,
  ## specify height
  height = 1000,
  ## specify width
  width = 1200,
  ## ensure each case node has a unique y-coordinate - this is very important
  ## when using timelines, otherwise you will have overlapping timelines from
  ## different cases
  position_dodge = TRUE
)
```

## 37.5 Phân tích

### Tổng hợp

Chúng ta có thể xem tổng quan về một số thuộc tính mạng lưới bằng cách sử dụng hàm `summary`.

``` r
## summarise epicontacts object
summary(epic)
```


    /// Overview //
      // number of unique IDs in linelist: 5888
      // number of unique IDs in contacts: 5511
      // number of unique IDs in both: 4352
      // number of contacts: 3800
      // contacts with both cases in linelist: 56.868 %

    /// Degrees of the network //
      // in-degree summary:
       Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
     0.0000  0.0000  1.0000  0.5392  1.0000  1.0000 

      // out-degree summary:
       Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
     0.0000  0.0000  0.0000  0.5392  1.0000  6.0000 

      // in and out degree summary:
       Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
      0.000   1.000   1.000   1.078   1.000   7.000 

    /// Attributes //
      // attributes in linelist:
     generation date_infection date_onset date_hospitalisation date_outcome outcome gender age age_unit age_years age_cat age_cat5 hospital lon lat infector source wt_kg ht_cm ct_blood fever chills cough aches vomit temp time_admission bmi days_onset_hosp

      // attributes in contacts:
     location duration

Ví dụ, chúng ta có thể thấy rằng chỉ có 57% các tiếp xúc có cả hai trường hợp trong bộ số liệu `linelist`; điều này có nghĩa là chúng ta không có dữ liệu trong bộ số liệu `linelist` về một số lượng đáng kể các trường hợp liên quan đến các chuỗi lây nhiễm này.

### Đặc điểm ghép cặp

Hàm `get_pairwise()` cho phép xử lý (các) biến trong bộ số liệu `linelist` theo từng cặp trong bộ dữ liệu tiếp xúc. Ở ví dụ dưới đây, ngày khởi phát bệnh được trích xuất từ bộ số liệu `linelist` để tính toán sự khác biệt giữa ngày khởi phát bệnh cho từng cặp. Giá trị được tạo ra từ phép so sánh này đại diện cho **khoảng nối tiếp (serial interval - si)**.

``` r
si <- get_pairwise(epic, "date_onset")   
summary(si)
```

       Min. 1st Qu.  Median    Mean 3rd Qu.    Max.     NAs 
       0.00    5.00    9.00   11.01   15.00   99.00    1820 

``` r
tibble(si = si) %>%
  drop_na(si) %>%
  ggplot(aes(si)) +
  geom_histogram(bins = 30) +
  labs(
    x = "Serial interval",
    y = "Frequency"
  )
```

[![](transmission_chains_files/figure-html/transmission_chains_pairwise-1.png)](transmission_chains_files/figure-html/transmission_chains_pairwise-1.png)

`get_pairwise()` sẽ diễn giải phân lớp của cột đang được sử dụng để so sánh và sẽ điều chỉnh phương pháp so sánh các giá trị của nó cho phù hợp. Đối với số và ngày (như ví dụ **si** ở trên), hàm sẽ trừ các giá trị. Khi được áp dụng cho các cột là ký tự hoặc phân loại, `get_pairwise()` sẽ gán các giá trị lại với nhau. Bởi vì hàm cũng cho phép xử lý tùy ý (xem đối số “f”), các kết hợp rời rạc này có thể dễ dàng được mô tả và phân tích.

``` r
head(get_pairwise(epic, "gender"), n = 10)
```

     [1] "f -> m" NA       "m -> m" NA       "m -> f" "f -> f" NA       "f -> m"
     [9] NA       "m -> f"

``` r
get_pairwise(epic, "gender", f = table)
```

               values.to
    values.from   f   m
              f 464 516
              m 510 468

``` r
fisher.test(get_pairwise(epic, "gender", f = table))
```


        Fisher's Exact Test for Count Data

    data:  get_pairwise(epic, "gender", f = table)
    p-value = 0.03758
    alternative hypothesis: true odds ratio is not equal to 1
    95 percent confidence interval:
     0.6882761 0.9892811
    sample estimates:
    odds ratio 
     0.8252575 

Ở đây, chúng ta thấy có một mối liên hệ có ý nghĩa thống kê giữa các liên kết lây nhiễm và giới tính.

### Xác định cụm

Hàm `get_clusters()` có thể được sử dụng để xác định các thành phần được kết nối trong một đối tượng `epicontacts`. Đầu tiên, chúng ta sử dụng nó để truy xuất `data.frame` chứa thông tin cụm:

``` r
clust <- get_clusters(epic, output = "data.frame")
table(clust$cluster_size)
```


       1    2    3    4    5    6    7    8    9   10   11   12   13   14 
    1536 1680 1182  784  545  342  308  208  171  100   99   24   26   42 

``` r
ggplot(clust, aes(cluster_size)) +
  geom_bar() +
  labs(
    x = "Cluster size",
    y = "Frequency"
  )
```

[![](transmission_chains_files/figure-html/transmission_chains_cluster-1.png)](transmission_chains_files/figure-html/transmission_chains_cluster-1.png)

Giờ chúng ta hãy xem xét các cụm lớn nhất. Đối với điều này, chúng ta thêm thông tin cụm vào đối tượng `epicontacts` và sau đó subset nó để chỉ giữ lại các cụm lớn nhất:

``` r
epic <- get_clusters(epic)
max_size <- max(epic$linelist$cluster_size)
plot(subset(epic, cs = max_size))
```

### Tính toán mức độ

Mức độ của một nút tương ứng với số cạnh hoặc kết nối của nó với các nút khác. `get_degree()` cung cấp một phương pháp dễ dàng để tính toán giá trị này cho các mạng lưới `epicontacts`. Mức độ cao trong ngữ cảnh này cho biết một cá nhân đã tiếp xúc với nhiều người khác. Đối sôs `type` chỉ ra rằng chúng ta muốn đếm cả mức độ trong và ngoài, đối số `only_linelist` chỉ ra rằng chúng ta chỉ muốn tính mức độ cho các trường hợp trong bộ số liệu `linelist`.

``` r
deg_both <- get_degree(epic, type = "both", only_linelist = TRUE)
```

Mười cá nhân nào có nhiều tiếp xúc nhất?

``` r
head(sort(deg_both, decreasing = TRUE), 10)
```

    916d0a 858426 6833d7 f093ea 11f8ea 3a4372 38fc71 c8c4d5 a127a7 02d8fd 
         7      6      6      6      5      5      5      5      5      5 

Số lượng tiếp xúc trung bình là bao nhiêu?

``` r
mean(deg_both)
```

    [1] 1.078473

## 37.6 Tham khảo

[Epicontacts page](https://www.repidemicsconsortium.org/epicontacts/index.html) cung cấp tổng quan về các hàm và package bao gồm một số thông tin chi tiết chuyên sâu hơn.

[Github page](http://github.com/reconhub/epicontacts) có thể được sử dụng để nêu vấn đề và yêu cầu chỉnh sửa.
