# 45  Tương tác với thư mục làm việc

Trong chương này, chúng tôi sẽ bao gồm các tình huống phổ biến, nơi chúng ta sẽ tạo, tương tác, lưu và nhập với thư mục.

## 45.1 Chuẩn bị

### **fs** package

Package **fs** thuộc hệ sinh thái **tidyverse** giúp thuận tiện cho việc tương tác với thư mục, cải thiện một số hàm trong **base** R. Trong các phần bên dưới, chúng ta sẽ dùng các hàm từ **fs**.

``` r
pacman::p_load(
  fs,             # file/directory interactions
  rio,            # import/export
  here,           # relative file pathways
  tidyverse)      # data management and visualization
```

### In thư mục dưới dạng cây biểu đồ dendrogram

Sử dụng hàm `dir_tree()` từ package **fs**.

Cung cấp đường dẫn thư mục cho đối số `path =`. Sử dụng `recurse = FALSE` để hiển thị chỉ một cấp độ, hoặc `recurse = TRUE` để hiển thị tất cả các tập tin trong tất cả các thư mục con. Bên dưới chúng ta sử dụng hàm `here()` như một cách viết tốc ký cho dự án R và chỉ định thư mục con “data” của nó, mà chứa số liệu ví dụ của cuốn sổ tay này. Chúng ta thiết lập nó để hiện thị tất cả các tệp bên trong thư mục “data” và các thư mục con của nó.

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

## 45.2 Liệt kê các tập tin trong một thư mục

Để chỉ liệt kê các tên tập tin trong một thư mục, chúng ta có thể sử dụng hàm `dir()` từ **base** Ví dụ, lệnh này liệt kê tên các tập tin của các tập tin trong thư mục con có tên “linelists” trong thư mục “example” của một dự án R. Đường dẫn tập tin tương đối được cung cấp bằng cách sử dụng hàm `here()` (đọc thêm trong chương [Nhập xuất dữ liệu](importing.llms.md)).

``` r
# file names
dir(here("data", "example", "linelists"))
```

    [1] "20201007linelist.csv"          "case_linelist_2020-10-02.csv" 
    [3] "case_linelist_2020-10-03.csv"  "case_linelist_2020-10-04.csv" 
    [5] "case_linelist_2020-10-05.csv"  "case_linelist_2020-10-08.xlsx"
    [7] "case_linelist20201006.csv"    

Để liệt kê đường dẫn đầy đủ của các tập tin trong thư mục, chúng ta có thể sử dụng hàm `dir_ls()` từ package **fs**. Một cách khác là dùng hàm `list.files()` trong **base** R.

``` r
# file paths
dir_ls(here("data", "example", "linelists"))
```

    data/example/linelists/20201007linelist.csv
    data/example/linelists/case_linelist20201006.csv
    data/example/linelists/case_linelist_2020-10-02.csv
    data/example/linelists/case_linelist_2020-10-03.csv
    data/example/linelists/case_linelist_2020-10-04.csv
    data/example/linelists/case_linelist_2020-10-05.csv
    data/example/linelists/case_linelist_2020-10-08.xlsx

Để lấy tất cả thông tin chi tiết của mỗi tập tin trong một thư mục (ví dụ: đường dẫn, ngày sửa đổi, .v.v.), chúng ta có thể sử dụng hàm `dir_info()` của package **fs**.

Điều này có thể đặc biệt hữu ích nếu chúng ta muốn trích xuất thời gian sửa đổi sau cùng của tập tin, ví dụ như nếu chúng ta muốn nhập phiên bản mới nhất của tập tin. Ví dụ cho việc này, xem trong chương [Nhập xuất dữ liệu](importing.llms.md).

``` r
# file info
dir_info(here("data", "example", "linelists"))
```

Sau đây là data frame được trả về. Cuộn qua phải để xem tất cả các cột.

## 45.3 Thông tin tệp

Để trích xuất thông tin chi tiết của một tập tin cụ thể, chúng ta có thể sử dụng hàme `file_info()` từ package **fs** (hoặc `file.info()` từ **base** R).

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))
```

Ở đây, chúng ta sử dụng ký hiệu `$` để chỉ rõ kết quả và xuất chỉ mỗi giá trị về thời gian sửa đổi `modification_time`.

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))$modification_time
```

    [1] "2026-11-01 15:52:14 UTC"

## 45.4 Kiểm tra sự tồn tại

### Đối tượng R

Bạn có thể sử dụng hàm `exists()` trong **base** R để kiểm tra xem một đối tượng R có tồn tại *bên trong* môi trường R hay không (cung cấp tên đối tượng trong dấu ngoặc kép).

``` r
exists("linelist")
```

    [1] FALSE

Lưu ý rằng một số gói lệnh trong **base** R sử dụng các tên chung làm tên cho các đối tượng như “data” trong môi trường R, mà kết quả kiểm tra sẽ là TRUE trừ khi chúng ta chỉ rõ `inherit = FALSE`. Đây là một lý do để không đặt tên cho bộ số liệu của chúng ta là “data”.

``` r
exists("data")
```

    [1] TRUE

``` r
exists("data", inherit = FALSE)
```

    [1] FALSE

Nếu bạn đang viết một hàm, bạn nên sử dụng hàm `missing()` từ **base** R để kiểm tra xem có một đối số hiện diện hay không, thay vì dùng hàm `exists()`.

### Thư mục

Để kiểm tra xem một thư mục có tồn tại không, cung cấp đường dẫn tập tin (và tên tập tin) đến hàm `is_dir()` của package **fs**. Cuộn qua bên phải để thấy thông báo `TRUE` được in ra.

``` r
is_dir(here("data"))
```

    data 
    TRUE 

Một cách làm khác là dùng hàm `file.exists()` từ **base** R.

### Tệp

Để kiểm tra xem một tập tin cụ thể có tồn tại hay không, sử dụng hàm `is_file()` của package **fs**. Cuộn qua bên phải để thấy thông báo `TRUE` được in ra.

``` r
is_file(here("data", "case_linelists", "linelist_cleaned.rds"))
```

    data/case_linelists/linelist_cleaned.rds 
                                        TRUE 

Một cách làm khác là dùng hàm `file.exists()` từ **base** R.

## 45.5 Tạo mới

### Thư mục

Để tạo một thư mục mới, bạn có thể sử dụng hàm `dir_create()` từ package **fs**. Nếu thư mục đã tồn tại, thư mục này sẽ không bị ghi đè và không bị trả lại lỗi.

``` r
dir_create(here("data", "test"))
```

Một cách làm khác là dùng hàm `dir.create()` từ **base** R, mà sẽ hiển thị lỗi nếu thư mục đó đã tồn tại. Ngược lại, `dir_create()` sẽ không thông báo gì.

### Tệp

Chúng ta có thể tạo một tâp tin (rỗng) bằng hàm `file_create()` từ package **fs**. Nếu tập tin này đã tồn tại, nó sẽ không bị ghi đè hoặc thay đổi.

``` r
file_create(here("data", "test.rds"))
```

Một cách làm khác là dùng hàm `file.create()` từ **base** R. Nhưng nếu tập tin này đã tồn tại, tùy chọn này sẽ cắt xén tập tin đó. Nếu dùng hàm `file_create()` tập tin này sẽ được giữ nguyên.

### Tạo nếu không tồn tại

ĐANG XÂY DỰNG

## 45.6 Xóa

### Đối tượng R

Dùng hàm `rm()` từ **base** R để loại bỏ một đối tượng R.

### Thư mục

Dùng hàm `dir_delete()` từ package **fs**.

### Tệp

Chúng ta có thể xóa các tệp bằng hàm `file_delete()` từ package **fs**.

## 45.7 Chạy các tệp khác

### `source()`

Để chạy một R script từ một R script khác, bạn có thể sử dụng hàm `source()` (trong **base** R).

``` r
source(here("scripts", "cleaning_scripts", "clean_testing_data.R"))
```

Việc này tương đương với việc mở R script ở trên và bấm nút “Source” ở phía trên bên phải của tập lệnh. Điều này sẽ thực hiện tập lệnh này nhưng sẽ thực hiện một cách âm thầm (không có kết quả đầu ra trong bảng điều khiển R) trừ khi có chủ ý cụ thể. Xem các ví dụ ở chương \[Bảng điều khiển tương tác\] về cách sử dụng `source()` để tương tác với người dùng qua bảng điều khiên R ở chế độ hỏi và trả lời.

[![](../../images/source_button.png)](../../images/source_button.png)

### `render()`

Hàm `render()` là một biến thể của hàm `source()` mà thường được sử dụng nhất cho các tập lệnh của R markdown. Chúng ta cung cấp `input =` tập tin R markdown, và cũng vậy `output_format =` (thường là “html_document”, “pdf_document”, “word_document”, ““)

Xem chương [Báo cáo với R Markdown](rmarkdown.llms.md) để biết thêm chi tiết. Ngoài ra, bạn có thể xem thêm tài liệu về `render()` [tại đây](https://rmarkdown.rstudio.com/docs/reference/render.html) hoặc bằng cách gõ `?render`.

### Chạy các tệp trong một thư mục

Bạn có thể tạo một *vòng lặp for* và sử dụng nó để `source()` từng tệp trong một thư mục, đã được nhận dạng bởi hàm `dir()`.

``` r
for(script in dir(here("scripts"), pattern = ".R$")) {   # for each script name in the R Project's "scripts" folder (with .R extension)
  source(here("scripts", script))                        # source the file with the matching name that exists in the scripts folder
}
```

Nếu chúng ta chỉ muốn thực hiện một vài scripts, chúng ta có thể xác định chúng bằng tên như sau:

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

Đây là một [so sánh](https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html) giữa các hàm của **fs** và **base** R.

### Nhập tệp vào một thư mục

Xem chương \[Nhập xuất dữ liệu\] để nhập và xuất các tập tin riêng lẻ.

Ngoài ra cũng xem thêm chương \[Nhập xuất dữ liệu\] để biết các phương pháp nhập một cách tự động các tập tin gần đây nhất dựa trên ngày trong tên tập tin *hoặc* bằng cách xem các thông tin chi tiết của tập tin.

Xem một ví dụ trong chương \[Lặp, vòng lặp và danh sách\] để thấy rõ cách sử dụng package **purrr**:

- Để tách một data frame và lưu nó ra dưới dạng nhiều tập tin CSV  
- Tách một data frame và lưu từng phần vào một trang tính riêng biệt trong một tập tin Excel  
- Nhập nhiều tập tin CSV và kết hợp chúng thành một dataframe  
- Nhập một tập tin Excel có nhiều trang tính riêng biệt và kết hợp chúng thành một dataframe

## 45.8 **base** R

Xem bên dưới các hàm `list.files()` và `dir()`, thực hiện cùng một thao tác liệt kê các tập tin trong một thư mục cụ thể. Chúng ta có thể cụ thể cho đối số `ignore.case =` hoặc cụ thể một pattern để tìm kiếm.

``` r
list.files(path = here("data"))

list.files(path = here("data", "example"), pattern = "\\.csv$")
# dir(path = here("data", "example"), pattern = "\\.csv$")

list.files(path = here("data", "example"), pattern = "hospital", ignore.case = TRUE)
```

Nếu một tập tin hiện tại đang “mở”, nó sẽ hiện thị trong thư mục với dấu ngã phía trước, chẳng hạn như “~\$hospital_linelists.xlsx”.

## 45.9 Nguồn

https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html
