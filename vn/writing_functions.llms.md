# 44  Viết hàm

## 44.1 Chuẩn bị

### Gọi packages

Đoạn code này hiển thị việc tải các gói lệnh cần thiết cho phân tích. Trong cuốn sổ tay này, chúng tôi nhấn mạnh đến hàm `p_load()` trong package **pacman**, giúp cài đặt package nếu cần thiết *và* gọi chúng ra để sử dụng. Các package đã cài đặt cũng có thể được gọi ra bằng hàm `library()` từ **base** R. Xem chương [R cơ bản](basics.llms.md) để biết thêm thong tin về các packages trong R.

### Nhập dữ liệu

Chúng tôi nhập bộ số liệu của các ca bệnh được mô phỏng từ một vụ dịch Ebola. Nếu muốn tải số liệu để làm theo từng bước, xem hướng dẫn trong chương [Tải sách và dữ liệu](download.llms.md). Bộ số liệu được nhập vào bằng hàm `import()` từ package **rio**. Xem chương [Nhập xuất số liệu](importing.llms.md) để biết các cách nhập dữ liệu khác.

Chúng tôi cũng sẽ sử dụng một vài số liệu về bệnh cúm do H7N9 xảy ra năm 2013 ở phần cuối của chương này.

## 44.2 Hàm

Các hàm rất hữu ích trong lập trình vì chúng cho phép tạo ra các code dễ hiểu hơn, ngắn hơn và ít bị lỗi hơn (với điều kiện là bản thân hàm đó không có lỗi).

Nếu bạn đã xem đến chương này, có nghĩa là bạn đã đi qua vô số các hàm bởi vì trong R, mỗi toán tử là một lần gọi hàm `+, for, if, [, $, { …`. Ví dụ, `x + y` là tương đương với`'+'(x, y)`

R là một ngôn ngữ cung cấp nhiều khả năng nhất để thực hiện các hàm và cung cấp đầy đủ các công cụ để người dùng dễ dàng viết chúng. Chúng ta không nên nghĩ các hàm là cố định ở đầu hay ở cuối chuỗi lập trình, R cung cấp các khả năng sử dụng chúng như thể chúng là các véc tơ và thậm chí sử dụng chúng bên trong các hàm, danh sách…

Có rất nhiều nguồn nâng cao về lập trình hướng chức năng và chúng tôi sẽ chỉ cung cấp cho bạn một cái nhìn bao quát để giúp bạn bắt đầu với lập trình hướng chức năng với các ví dụ thực tế, ngắn gọn. Sau đó, bạn có thể truy cập thêm các tài liệu tham khảo ở phía dưới.

## 44.3 Tại sao chúng ta sử dụng hàm?

Trước khi trả lời câu hỏi này, điều quan trọng cần lưu ý là chúng ta đã biết các mẹo để viết các hàm đầu tiên trong R trong chương [Lặp, vòng lặp và danh sách](iteration.llms.md) trong cuốn sổ tay này. Nói tóm lại, việc sử dụng “if/else” và vòng lặp thường là một phần cốt lõi trong nhiều hàm vì chúng dễ dàng giúp mở rộng tính ứng dụng code của chúng ta, cho phép nhiều điều kiện hoặc lặp lại code cho các tác vụ lặp lại.

- Tôi có đang lặp lại nhiều lần cùng một đoạn code để áp dụng nó cho một biến hoặc số liệu khác không?

- Loại bỏ nó có rút ngắn đáng kể số dòng code tổng thể và giúp việc thực hiện nhanh hơn không?

- Đoạn code có thể sử dụng lại với giá trị khác ở nhiều vị trí trong code không?

Nếu một trong những trả lời cho các câu hỏi bên trên là “CÓ”, bạn có thể sẽ cần phải viết hàm

## 44.4 Cách viết hàm trong R

Các hàm trong R có ba thành phần chính:

- phần hình thức `formals()` là danh sách các đối số mà kiểm soát cách chúng ta có thể gọi hàm

- phần thân `body()` là đoạn code bên trong hàm, vd: bên trong hoặc theo sau các dấu ngoặc, tùy thuộc vào cách chúng ta viết nó

và,

- phần môi trường thực hiện `environment()` để giúp chúng ta xác định vị trí các biến trong hàm và xác định cách các hàm tìm giá trị.

Một khi đã tạo hàm, chúng ta có thể kiểm tra mỗi thành phần này bằng cách gọi các hàm liên kết.

## 44.5 Cấu trúc và cú pháp cơ bản

- Một hàm cần được đặt tên cẩn thận theo đúng công việc của nó để có thể hiểu được khi chúng ta đọc tên hàm. A Thực tế, điều này đã được sử dụng trong phần lớn các kiến trúc của base R. Các hàm như `mean()`, `print()`, `summary()` có những cái tên đúng như nhiệm vụ của nó

- Một hàm cần các đối số như là số liệu để thực hiện và các đối tượng khác mà có thể là các giá trị tĩnh trong một danh sách các tùy chọn khác

- Và cuối cùng, một hàm sẽ cho kết quả đầu ra dựa trên nhiệm vụ cốt lõi của nó và các đối số đã được đưa ra. Thông thường, chúng ta sẽ sử dụng các hàm có sẵn như `print()`, `return()`… để tạo ra kết quả đầu ra. Kết quả đầu ra có thể là giá trị logic, một số, một ký tự, một data frame…mà gọi ngắn gọn là đối tượng của R.

Về cơ bản, đây là thành phần của một hàm:

``` r
function_name <- function(argument_1, argument_2, argument_3){
  
           function_task
  
           return(output)
}
```

Chúng ta tạo hàm đầu tiên với tên gọi là `contain_covid19()`.

``` r
contain_covid19 <- function(barrier_gest, wear_mask, get_vaccine){
  
                            if(barrier_gest == "yes" & wear_mask == "yes" & get_vaccine == "yes" ) 
       
                            return("success")
  
  else("please make sure all are yes, this pandemic has to end!")
}
```

Sau đó, chúng ta kiểm tra các thành phần của hàm vừa mới được tạo ra.

``` r
formals(contain_covid19)
```

    $barrier_gest


    $wear_mask


    $get_vaccine

``` r
body(contain_covid19)
```

    {
        if (barrier_gest == "yes" & wear_mask == "yes" & get_vaccine == 
            "yes") 
            return("success")
        else ("please make sure all are yes, this pandemic has to end!")
    }

``` r
environment(contain_covid19)
```

    <environment: R_GlobalEnv>

Bây giờ, chúng ta sẽ kiểm tra hàm này. Để gọi hàm đã biết, chúng ta sử dụng nó như sử dụng tất cả các hàm trong R, tức là bằng cách viết tên hàm và thêm các đối số cần phải có.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "yes")
```

    [1] "success"

Chúng ta có thể viết lại tên của mỗi đối số cho cẩn thận. Nhưng kể cả khi không cụ thể chúng, code cũng sẽ thực hiện vì R đã nhớ vị trí của mỗi đối số. Vì thế, miễn là chúng ta đặt các giá trị của các đối số theo đúng thứ tự, chúng ta có thể bỏ qua việc viết tên các đối số khi gọi hàm.

``` r
contain_covid19("yes", "yes", "yes")
```

    [1] "success"

Sau đó, hãy xem điều gì sẽ xảy ra nếu một trong các giá trị là `"no"` hoặc **not** `"yes"`.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "no")
```

    [1] "please make sure all are yes, this pandemic has to end!"

Nếu chúng ta cung cấp các đối số không nhận diện được, chúng ta sẽ gặp lỗi:

``` r
contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", get_vaccine = "no")
```

`Error in contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", : could not find function "contain_covid19"`

***LƯU Ý:*** Một số hàm (hầu hết là rất ngắn và không phức tạp) có thể không cần tên và có thể sử dụng trực tiếp trên một dòng code hoặc bên trong một hàm khác để thực hiện tác vụ nhanh chóng. Các hàm này được gọi là **hàm ẩn danh** .

Ví dụ bên dưới là một hàm ẩn danh đầu tiên mà chỉ giữ các biến ký tự trong bộ số liệu.

``` r
linelist %>% 
  dplyr::slice_head(n=10) %>%  #equivalent to R base "head" function and that return first n observation of the  dataset
  select(function(x) is.character(x)) 
```

Sau đó, một hàm khác chọn mỗi quan sát thứ hai của bộ số liệu (có thể thích hợp khi chúng ta có số liệu dọc với nhiều bản ghi cho một bệnh nhân, ví dụ sau khi đã sắp xếp theo ngày hoặc theo lần khám). Trong trường hợp này, việc viết hàm thích hợp bên ngoài gói lệnh dplyr sẽ là `function (x) (x%%2 == 0)` để áp dụng đối với véc tơ chứa tất cả các số hàng.

``` r
linelist %>%   
   slice_head(n=20) %>% 
   tibble::rownames_to_column() %>% # add indices of each obs as rownames to clearly see the final selection
   filter(row_number() %%2 == 0)
```

Một code trong base R có thể thực hiện tác vụ tương đương:

``` r
linelist_firstobs <- head(linelist, 20)

linelist_firstobs[base::Filter(function(x) (x%%2 == 0), seq(nrow(linelist_firstobs))),]
```

***THẬN TRỌNG:*** Mặc dù đúng là việc sử dụng hàm có thể giúp chúng ta viết code, tuy nhiên, việc viết một số hàm hay sửa hàm có thể tốn thời gian nếu chưa được suy nghĩ thấu đáo, viết đầy đủ và kết quả là báo lỗi. Vì lý do này, đầu tiên chúng ta nên viết code trước, chạy thử và đảm bảo nó thực hiện những gì chúng ta mong muốn và sau đó chuyển nó vào trong một hàm với ba thành phần chính như đã liệt kê bên trên.

## 44.6 Các ví dụ

### Trả về các bảng tỷ lệ cho một số cột

Đúng vậy, chúng ta đã có các hàm trong nhiều package mà cho phép tóm tắt thông tin một cách dễ dàng và đẹp mắt. Nhưng chúng ta vẫn cố gắng thử tạo ra hàm riêng trong những bước đầu tiên để làm quen với việc viết hàm.

Trong ví dụ này, chúng tôi muốn chỉ ra cách viết một hàm đơn giản để tránh việc sao chép và dán cùng một code nhiều lần.

``` r
proptab_multiple <- function(my_data, var_to_tab){
  
  #print the name of each variable of interest before doing the tabulation
  print(var_to_tab)

  with(my_data,
       rbind( #bind the results of the two following function by row
        #tabulate the variable of interest: gives only numbers
          table(my_data[[var_to_tab]], useNA = "no"),
          #calculate the proportions for each variable of interest and round the value to 2 decimals
         round(prop.table(table(my_data[[var_to_tab]]))*100,2)
         )
       )
}


proptab_multiple(linelist, "gender")
```

    [1] "gender"

               f       m
    [1,] 2807.00 2803.00
    [2,]   50.04   49.96

``` r
proptab_multiple(linelist, "age_cat")
```

    [1] "age_cat"

             0-4     5-9  10-14  15-19   20-29 30-49 50-69 70+
    [1,] 1095.00 1095.00 941.00 743.00 1073.00   754 95.00 6.0
    [2,]   18.87   18.87  16.22  12.81   18.49    13  1.64 0.1

``` r
proptab_multiple(linelist, "outcome")
```

    [1] "outcome"

           Death Recover
    [1,] 2582.00 1983.00
    [2,]   56.56   43.44

***MẸO:*** Như đã trình bày bên trên, việc chú thích cho các hàm là rất quan trọng, là một thói quen lập trình nói chung. BHãy nhớ rằng mục đích của một hàm là làm cho code sẵn sàng để đọc, ngắn hơn và hiệu quả hơn. Sau đó, người đọc có thể hiểu được hàm này sẽ làm gì chỉ bằng cách đọc tên nó và có thêm thông tin chi tiết khi đọc các chú thích.

Cách thứ hai là sử dụng hàm này trong một hàm khác thông qua vòng lặp để thực hiện quá trình một cách đồng thời:

``` r
for(var_to_tab in c("gender","age_cat",  "outcome")){
  
  print(proptab_multiple(linelist, var_to_tab))
  
}
```

    [1] "gender"
               f       m
    [1,] 2807.00 2803.00
    [2,]   50.04   49.96
    [1] "age_cat"
             0-4     5-9  10-14  15-19   20-29 30-49 50-69 70+
    [1,] 1095.00 1095.00 941.00 743.00 1073.00   754 95.00 6.0
    [2,]   18.87   18.87  16.22  12.81   18.49    13  1.64 0.1
    [1] "outcome"
           Death Recover
    [1,] 2582.00 1983.00
    [2,]   56.56   43.44

Một cách đơn giản hơn có thể là sử dụng “apply” trong base R thay vì dùng “for loop” như được trình bày bên dưới:

***MẸO:*** R thường được định nghĩa như một ngôn ngữ lập trình hướng chức năng và hầu như bất cứ lúc nào chúng ta thực hiện một dòng code, chúng ta đang sử dụng một số hàm có sẵn. Một thói quen tốt để cảm thấy thoải mái hơn với việc viết hàm là thường xuyên nhìn bên trong cách các hàm cơ bản được viết mà chúng ta sử dụng hàng ngày. Phím tắt để làm như vậy là chọn tên hàm và sau đó bấm `Ctrl+F2` hoặc `fn+F2` hoặc `Cmd+F2` (tùy thuộc vào máy tính của bạn) .

## 44.7 Sử dụng **purrr**: viết các hàm với vòng lặp

### Sửa đổi kiểu biến trên nhiều cột trong một bộ số liệu

Giả sử nhiều biến kiểu ký tự trong bộ số liệu gốc `linelist` cần được thay đổi thành “factor” nhằm mục đích phân tích và vẽ biểu đồ. Thay vì lặp lại bước nhiều lần, chúng ta có thể sử dụng hàm `lapply()` để chuyển đổi tất cả các biến có liên quan trong một dòng code.

***THẬN TRỌNG:*** hàm `lapply()` trả về một danh sách, vì thế, sử dụng danh sách này có thể đòi hỏi một sửa đổi bổ sung như là một bước cuối cùng.

Bước tương tự có thể được thực hiện bằng cách sử dụng hàm `map_if()` từ package **purrr**

``` r
linelist_factor2 <- linelist %>%
  purrr::map_if(is.character, as.factor)


linelist_factor2 %>%
        glimpse()
```

    List of 30
     $ case_id             : Factor w/ 5888 levels "00031d","00086d",..: 2134 3022 396 4203 3084 4347 179 1241 5594 430 ...
     $ generation          : num [1:5888] 4 4 2 3 3 3 4 4 4 4 ...
     $ date_infection      : Date[1:5888], format: "2014-05-08" NA ...
     $ date_onset          : Date[1:5888], format: "2014-05-13" "2014-05-13" ...
     $ date_hospitalisation: Date[1:5888], format: "2014-05-15" "2014-05-14" ...
     $ date_outcome        : Date[1:5888], format: NA "2014-05-18" ...
     $ outcome             : Factor w/ 2 levels "Death","Recover": NA 2 2 NA 2 2 2 1 2 1 ...
     $ gender              : Factor w/ 2 levels "f","m": 2 1 2 1 2 1 1 1 2 1 ...
     $ age                 : num [1:5888] 2 3 56 18 3 16 16 0 61 27 ...
     $ age_unit            : Factor w/ 2 levels "months","years": 2 2 2 2 2 2 2 2 2 2 ...
     $ age_years           : num [1:5888] 2 3 56 18 3 16 16 0 61 27 ...
     $ age_cat             : Factor w/ 8 levels "0-4","5-9","10-14",..: 1 1 7 4 1 4 4 1 7 5 ...
     $ age_cat5            : Factor w/ 18 levels "0-4","5-9","10-14",..: 1 1 12 4 1 4 4 1 13 6 ...
     $ hospital            : Factor w/ 6 levels "Central Hospital",..: 4 3 6 5 2 5 3 3 3 3 ...
     $ lon                 : num [1:5888] -13.2 -13.2 -13.2 -13.2 -13.2 ...
     $ lat                 : num [1:5888] 8.47 8.45 8.46 8.48 8.46 ...
     $ infector            : Factor w/ 2697 levels "00031d","002e6c",..: 2594 NA NA 2635 180 1799 1407 195 NA NA ...
     $ source              : Factor w/ 2 levels "funeral","other": 2 NA NA 2 2 2 2 2 NA NA ...
     $ wt_kg               : num [1:5888] 27 25 91 41 36 56 47 0 86 69 ...
     $ ht_cm               : num [1:5888] 48 59 238 135 71 116 87 11 226 174 ...
     $ ct_blood            : num [1:5888] 22 22 21 23 23 21 21 22 22 22 ...
     $ fever               : Factor w/ 2 levels "no","yes": 1 NA NA 1 1 1 NA 1 1 1 ...
     $ chills              : Factor w/ 2 levels "no","yes": 1 NA NA 1 1 1 NA 1 1 1 ...
     $ cough               : Factor w/ 2 levels "no","yes": 2 NA NA 1 2 2 NA 2 2 2 ...
     $ aches               : Factor w/ 2 levels "no","yes": 1 NA NA 1 1 1 NA 1 1 1 ...
     $ vomit               : Factor w/ 2 levels "no","yes": 2 NA NA 1 2 2 NA 2 2 1 ...
     $ temp                : num [1:5888] 36.8 36.9 36.9 36.8 36.9 37.6 37.3 37 36.4 35.9 ...
     $ time_admission      : Factor w/ 1072 levels "00:10","00:29",..: NA 308 746 415 514 589 609 297 409 387 ...
     $ bmi                 : num [1:5888] 117.2 71.8 16.1 22.5 71.4 ...
     $ days_onset_hosp     : num [1:5888] 2 1 2 2 1 1 2 1 1 2 ...

### Vòng lặp tạo biểu đồ cho nhiều giá trị khác nhau của biến

Ở đây, chúng ta sẽ tạo biểu đồ tròn để xem phân bố outcome của bệnh nhân trong đợt dịch H7N9 cho từng tỉnh tại Trung Quốc. Thay vì lặp lại code cho từng tỉnh, chúng ta chỉ áp dụng một hàm mà chúng ta sẽ tạo ra.

``` r
#precising options for the use of highchart
options(highcharter.theme =   highcharter::hc_theme_smpl(tooltip = list(valueDecimals = 2)))


#create a function called "chart_outcome_province" that takes as argument the dataset and the name of the province for which to plot the distribution of the outcome.

chart_outcome_province <- function(data_used, prov){
  
  tab_prov <- data_used %>% 
    filter(province == prov,
           !is.na(outcome))%>% 
    group_by(outcome) %>% 
    count() %>%
    adorn_totals(where = "row") %>% 
    adorn_percentages(denominator = "col", )%>%
    mutate(
        perc_outcome= round(n*100,2))
  
  
  tab_prov %>%
    filter(outcome != "Total") %>% 
  highcharter::hchart(
    "pie", hcaes(x = outcome, y = perc_outcome),
    name = paste0("Distibution of the outcome in:", prov)
    )
  
}

chart_outcome_province(flu_china, "Shanghai")
```

``` r
chart_outcome_province(flu_china,"Zhejiang")
```

``` r
chart_outcome_province(flu_china,"Jiangsu")
```

### Vòng lặp tạo bảng cho nhiều giá trị khác nhau của biến

Ở đây, chúng ta sẽ tạo ba chỉ số để tóm tắt một bảng và chúng ta muốn tạo bảng này theo từng tỉnh. Các chỉ số của chúng ta là khoảng thời gian từ lúc khởi phát bệnh đến lúc nhập viện, tỷ lệ hồi phục và tuổi trung vị của các ca bệnh.

``` r
indic_1 <- flu_china %>% 
  group_by(province) %>% 
  mutate(
    date_hosp= strptime(date_of_hospitalisation, format = "%m/%d/%Y"),
    date_ons= strptime(date_of_onset, format = "%m/%d/%Y"), 
    delay_onset_hosp= as.numeric(date_hosp - date_ons)/86400,
    mean_delay_onset_hosp = round(mean(delay_onset_hosp, na.rm=TRUE ), 0)) %>%
  select(province, mean_delay_onset_hosp)  %>% 
  distinct()
     

indic_2 <-  flu_china %>% 
            filter(!is.na(outcome)) %>% 
            group_by(province, outcome) %>% 
            count() %>%
            pivot_wider(names_from = outcome, values_from = n) %>% 
    adorn_totals(where = "col") %>% 
    mutate(
        perc_recovery= round((Recover/Total)*100,2))%>% 
  select(province, perc_recovery)
    
    
    
indic_3 <-  flu_china %>% 
            group_by(province) %>% 
            mutate(
                    median_age_cases = median(as.numeric(na_if(age, "?")), na.rm = TRUE)
            ) %>% 
  select(province, median_age_cases)  %>% 
  distinct()

#join the three indicator datasets

table_indic_all <- indic_1 %>% 
  dplyr::left_join(indic_2, by = "province") %>% 
        left_join(indic_3, by = "province")


#print the indicators in a flextable


print_indic_prov <-  function(table_used, prov){
  
  #first transform a bit the dataframe for printing ease
  indic_prov <- table_used %>%
    filter(province==prov) %>%
    pivot_longer(names_to = "Indicateurs", cols = 2:4) %>% 
   mutate( indic_label = factor(Indicateurs,
   levels= c("mean_delay_onset_hosp","perc_recovery","median_age_cases"),
   labels=c("Mean delay onset-hosp","Percentage of recovery", "Median age of the cases"))
   ) %>% 
    ungroup(province) %>% 
    select(indic_label, value)
  

    tab_print <- flextable(indic_prov)  %>%
    theme_vanilla() %>% 
    flextable::fontsize(part = "body", size = 10) 
    
    
     tab_print <- tab_print %>% 
                  autofit()   %>%
                  set_header_labels( 
                indic_label= "Indicateurs", value= "Estimation") %>%
    flextable::bg( bg = "darkblue", part = "header") %>%
    flextable::bold(part = "header") %>%
    flextable::color(color = "white", part = "header") %>% 
    add_header_lines(values = paste0("Indicateurs pour la province de: ", prov)) %>% 
bold(part = "header")
 
 tab_print <- colformat_double(tab_print,
   digits = 2,
   na_str = "-")

tab_print 
    
}




print_indic_prov(table_indic_all, "Shanghai")
```

| Indicateurs pour la province de: Shanghai |            |
|-------------------------------------------|------------|
| Indicateurs                               | Estimation |
| Mean delay onset-hosp                     | 4.00       |
| Percentage of recovery                    | 46.67      |
| Median age of the cases                   | 67.00      |

``` r
print_indic_prov(table_indic_all, "Jiangsu")
```

| Indicateurs pour la province de: Jiangsu |            |
|------------------------------------------|------------|
| Indicateurs                              | Estimation |
| Mean delay onset-hosp                    | 6.00       |
| Percentage of recovery                   | 71.43      |
| Median age of the cases                  | 55.00      |

## 44.8 Mẹo và thực hành tốt để các hàm hoạt động tốt

Lập trình hàm có nghĩa là để dễ dàng viết và đọc code. Tuy nhiên, điều ngược lại có thể xảy ra. Những mẹo dưới đây sẽ giúp bạn có một đoạn code gọn gàng và dễ đọc.

### Đặt tên và cú pháp

- Tránh sử dụng ký tự có thể đã được sử dụng bởi các hàm khác đã tồn tại trong môi trường làm việc của chúng ta

- Nên đặt tên hàm ngắn gọn và dễ hiểu cho người đọc

- Ưu tiên sử dụng động từ làm tên hàm và danh từ làm tên các đối số.

### Tên cột và lượng giá tính gọn gàng

Nếu bạn muốn biết cách tham chiếu *tên cột* để đưa vào code của bạn như một đối số, hãy đọc [hướng dẫn lập trình của tidyverse](https://dplyr.tidyverse.org/articles/programming.html) này. Trong số các chủ đề, nên đọc về *tidy evaluation* và sử dụng *embrace* `{ }` “hai dấu ngoặc nhọn”

Ví dụ: đây là đoạn code mẫu từ trang hướng dẫn được đề cập bên trên:

``` r
var_summary <- function(data, var) {
  data %>%
    summarise(n = n(), min = min({{ var }}), max = max({{ var }}))
}
mtcars %>% 
  group_by(cyl) %>% 
  var_summary(mpg)
```

### Kiểm tra và xử lý lỗi

Công việc của hàm càng phức tạp thì khả năng xảy ra lỗi càng cao. Vì thế, đôi khi cần phải thêm một vài kiểm tra bên trong hàm để giúp nhanh chóng biết được lỗi ở đâu và tìm cách sửa nó.

- Rất nên đưa một hàm kiểm tra tính thiếu sót của một đối số bằng cách sử dụng `missing(argument)`. Việc kiểm tra đơn giản này trả về giá trị “TRUE” hoặc “FALSE”.

``` r
contain_covid19_missing <- function(barrier_gest, wear_mask, get_vaccine){
  
  if (missing(barrier_gest)) (print("please provide arg1"))
  if (missing(wear_mask)) print("please provide arg2")
  if (missing(get_vaccine)) print("please provide arg3")


  if (!barrier_gest == "yes" | wear_mask =="yes" | get_vaccine == "yes" ) 
       
       return ("you can do better")
  
  else("please make sure all are yes, this pandemic has to end!")
}


contain_covid19_missing(get_vaccine = "yes")
```

    [1] "please provide arg1"
    [1] "please provide arg2"

    Error in `contain_covid19_missing()`:
    ! argument "barrier_gest" is missing, with no default

- Sử dụng hàm `stop()` để dễ phát hiện lỗi hơn.

``` r
contain_covid19_stop <- function(barrier_gest, wear_mask, get_vaccine){
  
  if(!is.character(barrier_gest)) (stop("arg1 should be a character, please enter the value with `yes`, `no` or `sometimes"))
  
  if (barrier_gest == "yes" & wear_mask =="yes" & get_vaccine == "yes" ) 
       
       return ("success")
  
  else("please make sure all are yes, this pandemic has to end!")
}


contain_covid19_stop(barrier_gest=1, wear_mask="yes", get_vaccine = "no")
```

    Error in `contain_covid19_stop()`:
    ! arg1 should be a character, please enter the value with `yes`, `no` or `sometimes

- Như đã thấy khi chúng ta thực hiện hầu hết các hàm có sẵn, có các thông báo và cảnh báo có thể xuất hiện trong một số điều kiện nhất định. Chúng ta có thể tích hợp chúng trong các hàm đã viết bằng cách sử dụng hàm `message()` và `warning()`.

- Chúng ta cũng có thể xử lý lỗi bằng cách sử dụng hàm `safely()` để lấy một hàm làm đối số và thực hiện nó một cách an toàn. Trên thực tế, hàm sẽ thực hiện mà không dừng lại nếu nó gặp lỗi. Hàm `safely()` trả về kết quả đầu ra dưới dạng một **list** với hai đối tượng là kết quả và lỗi mà nó đã “bỏ qua”.

Chúng ta có thể kiểm tra bằng cách thực hiện hàm `mean()` trước, sau đó thực hiện nó với hàm `safely()`.

``` r
linelist %>% 
  select(where(is.numeric)) %>% 
  map(mean)
```

    $generation
    [1] 16.56165

    $age
    [1] NA

    $age_years
    [1] NA

    $lon
    [1] -13.23381

    $lat
    [1] 8.469638

    $wt_kg
    [1] 52.64487

    $ht_cm
    [1] 124.9633

    $ct_blood
    [1] 21.20686

    $temp
    [1] NA

    $bmi
    [1] 46.89023

    $days_onset_hosp
    [1] NA

``` r
safe_mean <- safely(mean)
linelist %>% 
  select(where(is.numeric)) %>% 
  map(safe_mean)
```

    $generation
    $generation$result
    [1] 16.56165

    $generation$error
    NULL


    $age
    $age$result
    [1] NA

    $age$error
    NULL


    $age_years
    $age_years$result
    [1] NA

    $age_years$error
    NULL


    $lon
    $lon$result
    [1] -13.23381

    $lon$error
    NULL


    $lat
    $lat$result
    [1] 8.469638

    $lat$error
    NULL


    $wt_kg
    $wt_kg$result
    [1] 52.64487

    $wt_kg$error
    NULL


    $ht_cm
    $ht_cm$result
    [1] 124.9633

    $ht_cm$error
    NULL


    $ct_blood
    $ct_blood$result
    [1] 21.20686

    $ct_blood$error
    NULL


    $temp
    $temp$result
    [1] NA

    $temp$error
    NULL


    $bmi
    $bmi$result
    [1] 46.89023

    $bmi$error
    NULL


    $days_onset_hosp
    $days_onset_hosp$result
    [1] NA

    $days_onset_hosp$error
    NULL

Như đã nói trước đây, chú thích rõ ràng trong các đoạn mã là một cách tốt để có tư liệu cho các công việc đã thực hiện.

## 44.9 Nguồn

[R for Data Science link](https://r4ds.had.co.nz/functions.html)

[Cheatsheet advance R programming](https://www.rstudio.com/wp-content/uploads/2016/02/advancedR.pdf)

[Cheatsheet purr Package](https://purrr.tidyverse.org/)

[Video-ACM talk by Hadley Wickham: The joy of functional programming (how does map_dbl work)](https://youtube.videoken.com/embed/bzUmK0Y07ck)
