# 50  Data Table

Cuốn sổ tay này tập trung vào các hàm của **dplyr** và toán tử pipe của **magrittr** `%>%` như một phương pháp để làm sạch và nhóm dữ liệu, tuy nhiên package **data.table** cũng cung cấp một giải pháp thay thế mà bạn có thể sử dụng trong quá trình làm việc với R của mình.

## 50.1 Giới thiệu về data table

Một data table là một cấu trúc dữ liệu 2-chiều giống như một data frame mà cho phép thực hiện các thao tác phân nhóm phức tạp. Cú pháp data.table được cấu trúc để có thể thực hiện các thao tác trên hàng, cột và nhóm.

Cấu trúc là **DT\[i, j, by\]**, được chia thành 3 phần; đối số **i, j** và **by**. Đối số **i** cho phép tạo tập con trên các hàng được yêu cầu, đối số **j** cho phép bạn vận hành trên cột và đối số **by** cho phép bạn vận hành theo nhóm.

Chương này sẽ giải quyết các chủ đề sau:

- Nhập dữ liệu và sử dụng `fread()` và `fwrite()`
- Chọn và lọc các hàng bằng cách sử dụng đối số **i**
- Sử dụng các hàm trợ giúp `%like%`, `%chin%`, `%between%`
- Chọn và tính toán trên các cột bằng cách sử dụng đối số **j**
- Tính toán theo nhóm bằng cách sử dụng đối số **by**
- Thêm và cập nhật dữ liệu vào data table bằng cách sử dụng `:=`

## 50.2 Gọi package và nhập dữ liệu

### Gọi package

Sử dụng hàm `p_load()` từ **pacman**, chúng ta sẽ gọi (và cài đặt nếu cần) các package cần thiết cho phân tích này.

``` r
pacman::p_load(
  data.table, # để nhóm và làm sạch dữ liệu
  tidyverse   # cho phép dùng hàm pipe (%>%) trong chương này
  ) 
```

### Nhập dữ liệu

Chương này sẽ khám phá một số hàm cốt lõi của **data.table** thông qua bộ số liệu linelist đã được nhắc đền nhiều lần trong sổ tay này.

Chúng ta nhập bộ dữ liệu về các trường hợp từ một vụ dịch Ebola mô phỏng. Tải trực tiếp bằng `appliedepidata::get_data(name = "linelist_cleaned_excel")` (xem trang [Tải sách và dữ liệu](download.llms.md) để biết chi tiết). Từ đây chúng tôi sử dụng `data.table()` để chuyển data frame thành data table.

``` r
linelist <- appliedepidata::get_data(name = "linelist_cleaned_excel") %>% data.table()
```

Hàm `fread()` được sử dụng để nhập trực tiếp các delimited files phổ biến, chẳng hạn như tệp .csv, trực tiếp sang định dạng data table. Hàm này và đối tác của nó, `fwrite()`, được sử dụng để ghi data.table dưới dạng các delimited files phổ biến, là các tùy chọn rất nhanh và hiệu quả về mặt tính toán đối với cơ sở dữ liệu lớn.

20 hàng đầu tiên của `linelist`:

Các lệnh base R như `dim()` được sử dụng cho data frame cũng có thể được sử dụng cho data table

``` r
dim(linelist) #cho biết số hàng và số cột của data table
```

    [1] 5888   30

## 50.3 Đối số i: chọn và lọc hàng

Nhắc lại cấu trúc **DT\[i, j, by\]**, chúng ta có thể lọc các hàng bằng cách sử dụng số hàng hoặc biểu thức logic. Đối số i là đối số đầu tiên; do đó, cú pháp **DT\[i\]** hoặc **DT\[i,\]** có thể được sử dụng.

Ví dụ đầu là việc truy xuất 5 hàng đầu tiên của data table, ví dụ thứ hai là tập hợp các trường hợp từ 18 tuổi trở lên và ví dụ thứ ba là tập hợp các trường hợp từ 18 tuổi trở lên nhưng không được chẩn đoán tại Bệnh viện Trung tâm (Central Hospital):

``` r
linelist[1:5] #trả về hàng thứ 1 đến hàng thứ 5
linelist[age >= 18] #lấy các ca bệnh từ 18 tuổi trở lên
linelist[age >= 18 & hospital != "Central Hospital"] #lấy các ca bệnh từ 18 tuổi trở lên nhưng không được chẩn đoán tại Central Hospital
```

Sử dụng .N trong đối số i đại diện cho tổng số hàng trong data table. Điều này có thể được sử dụng để subset dữ liệu dựa trên số thứ tự hàng:

``` r
linelist[.N] #trả về hàng cuối cùng
linelist[15:.N] #trả về từ hàng thứ 15 đến hàng cuối cùng
```

### Sử dụng hàm trợ giúp để lọc

Data table sử dụng các hàm trợ giúp để việc subset các hàng trở nên dễ dàng. Hàm `%like%` được sử dụng để khớp với một pattern trong cột, `%chin%` được sử dụng để khớp với một ký tự cụ thể và hàm trợ giúp `%between%` được sử dụng để khớp các cột dạng số nằm trong một phạm vi xác định trước.

Trong các ví dụ dưới đây, chúng ta: \* lọc các hàng mà biến hospital có chứa “Hospital” \* lọc các hàng có kết quả là “Recover” hoặc “Death” \* lọc các hàng trong độ tuổi 40-60

``` r
linelist[hospital %like% "Hospital"] #lọc các hàng mà biến hospital có chứa “Hospital”
linelist[outcome %chin% c("Recover", "Death")] #lọc các hàng có outcome là “Recover” hoặc “Death”
linelist[age %between% c(40, 60)] #lọc các hàng có tuổi trong khoảng 40-60

#%between% phải nhận một vector độ dài 2, trong khi %chin% có thể nhận vector độ dài >= 1
```

## 50.4 Đối số j: chọn và tính toán trên cột

Sử dụng cấu trúc **DT\[i, j, by\]**, chúng ta có thể chọn cột bằng cách sử dụng số hoặc tên. Đối số **j** là đối số thứ hai; do đó, cú pháp **DT\[, j\]** được sử dụng. Để tạo điều kiện tính toán trên đối số **j**, cột được bao quanh bằng cách sử dụng `list()` hoặc `.()`.

### Chọn cột

Ví dụ đầu tiên lấy các cột thứ nhất, thứ ba và thứ năm của data table, ví dụ thứ hai chọn tất cả các cột ngoại trừ các cột height, weight và gender. Ví dụ thứ ba sử dụng `.()` phía trước để chọn cột **case_id** và **outcome**.

``` r
linelist[ , c(1,3,5)]
linelist[ , -c("gender", "age", "wt_kg", "ht_cm")]
linelist[ , list(case_id, outcome)] #linelist[ , .(case_id, outcome)] cũng cho kết quả như vậy
```

### Tính toán trên cột

Bằng cách kết hợp các đối số **i** và **j**, có thể lọc các hàng và tính toán trên các cột. Sử dụng **.N** trong đối số **j** cũng thể hiện cho tổng số hàng trong data table và có thể hữu ích để trả về số hàng sau khi lọc.

Trong các ví dụ dưới đây, chúng tôi: \* Đếm số trường hợp nằm viện trên 7 ngày \* Tính tuổi trung bình của các trường hợp tử vong tại military hospital \* Tính toán độ lệch chuẩn, trung vị, tuổi trung bình của các trường hợp đã khỏi bệnh tại Central Hospital

``` r
linelist[days_onset_hosp > 7 , .N]
```

    [1] 189

``` r
linelist[hospital %like% "Military" & outcome %chin% "Death", .(mean(age, na.rm = T))] #na.rm = T loại bỏ các giá trị N/A
```

            V1
         <num>
    1: 15.9084

``` r
linelist[hospital == "Central Hospital" & outcome == "Recover", 
                 .(mean_age = mean(age, na.rm = T),
                   median_age = median(age, na.rm = T),
                   sd_age = sd(age, na.rm = T))] #cú pháp này không dùng các hàm hỗ trợ nhưng vẫn cho kết quả như vậy
```

       mean_age median_age   sd_age
          <num>      <num>    <num>
    1: 16.85185         14 12.93857

Hãy nhớ rằng việc sử dụng .() bao quanh đối số j sẽ tạo điều kiện thuận lợi cho việc tính toán, trả về data table và cho phép đặt tên cột.

## 50.5 Đối số by: tính toán theo nhóm

Đối số **by** là đối số thứ ba trong cấu trúc **DT\[i, j, by\]**. Đối số **by** chấp nhận cả vectơ ký tự và cú pháp `list()` hoặc `.()`. Sử dụng cú pháp `.()` trong đối số **by** cho phép đổi tên cột một cách nhanh chóng.

Trong các ví dụ dưới đây, chúng ta:  
\* nhóm số trường hợp theo bệnh viện \* trường hợp từ 18 tuổi trở lên, tính chiều cao và cân nặng trung bình theo giới tính và theo tình trạng hồi phục hay tử vong \* trong những lần nhập viện kéo dài trên 7 ngày, đếm số trường hợp theo tháng họ nhập viện và theo bệnh viện họ nằm

``` r
linelist[, .N, .(hospital)] #số ca bệnh theo bệnh viện
```

                                   hospital     N
                                     <char> <int>
    1:                                Other   885
    2:                              Missing  1469
    3: St. Mark's Maternity Hospital (SMMH)   422
    4:                        Port Hospital  1762
    5:                    Military Hospital   896
    6:                     Central Hospital   454

``` r
linelist[age > 18, .(mean_wt = mean(wt_kg, na.rm = T),
                             mean_ht = mean(ht_cm, na.rm = T)), .(gender, outcome)] #NA đại diện cho các nhóm có dữ liệu bị thiếu
```

       gender outcome  mean_wt  mean_ht
       <char>  <char>    <num>    <num>
    1:      m Recover 71.90227 178.1977
    2:      f   Death 63.27273 159.9448
    3:      m   Death 71.61770 175.4726
    4:      f    <NA> 64.49375 162.7875
    5:      m    <NA> 72.65505 176.9686
    6:      f Recover 62.86498 159.2996
    7:   <NA> Recover 67.21429 175.2143
    8:   <NA>   Death 69.16667 170.7917
    9:   <NA>    <NA> 70.25000 175.5000

``` r
linelist[days_onset_hosp > 7, .N, .(month = month(date_hospitalisation), hospital)]
```

        month                             hospital     N
        <num>                               <char> <int>
     1:     5                    Military Hospital     3
     2:     6                        Port Hospital     4
     3:     7                        Port Hospital     8
     4:     8 St. Mark's Maternity Hospital (SMMH)     5
     5:     8                    Military Hospital     9
     6:     8                                Other    10
     7:     8                        Port Hospital    10
     8:     9                        Port Hospital    28
     9:     9                              Missing    27
    10:     9                     Central Hospital    10
    11:     9 St. Mark's Maternity Hospital (SMMH)     6
    12:    10                              Missing     2
    13:    10                    Military Hospital     3
    14:     3                        Port Hospital     1
    15:     4                    Military Hospital     1
    16:     5                                Other     2
    17:     5                     Central Hospital     1
    18:     5                              Missing     1
    19:     6                              Missing     7
    20:     6 St. Mark's Maternity Hospital (SMMH)     2
    21:     6                    Military Hospital     1
    22:     7                    Military Hospital     3
    23:     7                                Other     1
    24:     7                              Missing     2
    25:     7 St. Mark's Maternity Hospital (SMMH)     1
    26:     8                     Central Hospital     2
    27:     8                              Missing     6
    28:     9                                Other     9
    29:     9                    Military Hospital    11
    30:    10                        Port Hospital     3
    31:    10                                Other     4
    32:    10 St. Mark's Maternity Hospital (SMMH)     1
    33:    10                     Central Hospital     1
    34:    11                              Missing     2
    35:    11                        Port Hospital     1
    36:    12                        Port Hospital     1
        month                             hospital     N
        <num>                               <char> <int>

Data.table cũng cho phép các biểu thức chuỗi như sau:

``` r
linelist[, .N, .(hospital)][order(-N)][1:3] #thứ nhất lấy tất cả ca bệnh theo bệnh viện, thứ hai sắp xếp giảm dần, thứ ba lấy 3 bệnh viện có nhiều ca nhất
```

                hospital     N
                  <char> <int>
    1:     Port Hospital  1762
    2:           Missing  1469
    3: Military Hospital   896

Trong các ví dụ này, chúng ta đang tuân theo giả định rằng một hàng trong data table tương đương với một trường hợp mới, vì vậy chúng ta có thể sử dụng **.N** để thể hiện số hàng trong data table. Một hàm hữu ích khác thể hiện số lượng các trường hợp duy nhất là `uniqueN()`, hàm này trả về số lượng các giá trị duy nhất trong một đầu vào nhất định.

``` r
linelist[, .(uniqueN(gender))] #nhớ rằng .() trong đối số j trả về một data table
```

          V1
       <int>
    1:     3

Đáp án là 3, vì các giá trị duy nhất trong cột gender là m, f và N/A. So sánh với hàm base R là `unique()`, trả về tất cả các giá trị duy nhất trong một đầu vào nhất định:

``` r
linelist[, .(unique(gender))]
```

           V1
       <char>
    1:      m
    2:      f
    3:   <NA>

Để tìm số trường hợp duy nhất trong một tháng (month) nhất định, chúng tôi sẽ viết như sau:

``` r
linelist[, .(uniqueN(case_id)), .(month = month(date_hospitalisation))]
```

        month    V1
        <num> <int>
     1:     5    62
     2:     6   100
     3:     7   198
     4:     8   509
     5:     9  1170
     6:    10  1228
     7:    11   813
     8:    12   576
     9:     1   434
    10:     2   310
    11:     3   290
    12:     4   198

## 50.6 Thêm và cập nhật dữ liệu vào data table

Toán tử `:=` được sử dụng để thêm hoặc cập nhật dữ liệu trong data table. Việc thêm cột vào data table của bạn có thể được thực hiện theo những cách dưới đây:

``` r
linelist[, adult := age >= 18] #thêm một cột
linelist[, c("child", "wt_lbs") := .(age < 18, wt_kg*2.204)] #để thêm nhiều cột cần cú pháp c("") và list() hoặc .()
linelist[, `:=` (bmi_in_range = (bmi > 16 & bmi < 40),
                         no_infector_source_data = is.na(infector) | is.na(source))] #phương pháp này dùng := như một toán tử hàm `:=`
linelist[, adult := NULL] #xóa cột
```

Các tổ hợp phức tạp hơn nằm ngoài phạm vi của chương giới thiệu này, nhưng ý tưởng của chương này là cung cấp một giải pháp thay thế phổ biến và khả thi cho **dplyr** để phân nhóm và làm sạch dữ liệu. Package **data.table** là một package tốt giúp code gọn gàng và dễ đọc.

## 50.7 Tài nguyên học liệu

Để có thêm thông tin, dưới đây là một số tài nguyên hữu ích: \* <https://cran.r-project.org/web/packages/data.table/vignettes/datatable-intro.html> \* <https://github.com/Rdatatable/data.table> \* <https://s3.amazonaws.com/assets.datacamp.com/img/blog/data+table+cheat+sheet.pdf> \* <https://www.machinelearningplus.com/data-manipulation/datatable-in-r-complete-guide/> \* <https://www.datacamp.com/community/tutorials/data-table-r-tutorial>

Bạn có thể thực hiện bất kỳ chức năng tóm tắt nào trên dữ liệu được nhóm; xem Cheat Sheet tại đây để có thêm thông tin: <https://s3.amazonaws.com/assets.datacamp.com/blog_assets/datatable_Cheat_Sheet_R.pdf>
