# 35  Sơ đồ và biểu đồ

[![](../../images/flow_chart.png)](../../images/flow_chart.png)

[![](../../images/sankey_diagram.png)](../../images/sankey_diagram.png)

Chương này này bao gồm hướng dẫn sử dụng code để vẽ:

- Biểu đồ flow diagram bằng **DiagrammeR** và ngôn ngữ DOT  
- Biểu đồ Alluvial/Sankey  
- Chuỗi sự kiện theo thời gian

## 35.1 Chuẩn bị

### Gọi packages

Đoạn code dưới đây hiển thị cách gọi các packages cần thiết cho các phân tích. Trong cuốn sách này, chúng tôi nhấn mạnh đến hàm `p_load()` từ package **pacman**, cài đặt gói nếu cần *và* gọi nó ra để sử dụng. Bạn cũng có thể gọi các packages đã cài đặt với hàm `library()` từ **base** R. Xem chương [R cơ bản](basics.llms.md) để biết thêm thông tin về các package R.

``` r
pacman::p_load(
  DiagrammeR,     # for flow diagrams
  networkD3,      # For alluvial/Sankey diagrams
  tidyverse,      # data management and visualization
  appliedepidata) # dữ liệu ví dụ được sử dụng trong sổ tay này
```

### Nhập dữ liệu

Hầu hết nội dung trong chương này không yêu cầu bộ dữ liệu. Tuy nhiên, trong phần sơ đồ Sankey, chúng ta sẽ sử dụng bộ dữ liệu linelist từ một vụ dịch Ebola mô phỏng. Tải trực tiếp bằng `appliedepidata::get_data(name = "linelist_cleaned_rds")` (xem trang [Tải sách và dữ liệu](download.llms.md) để biết chi tiết).

``` r
# import the linelist
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

50 hàng đầu tiên của linelist được hiển thị bên dưới:

## 35.2 Sơ đồ flow

Chúng ta có thể sử dụng package R **DiagrammeR** để vẽ biểu đồ/sơ đồ flow. Chúng có thể là sơ đồ tĩnh hoặc có động dựa thay đổi theo những thay đổi trong tập dữ liệu.

**Công cụ**

Hàm `grViz()` được sử dụng để tạo sơ đồ “Graphviz”. Hàm này chấp nhận một *chuỗi ký tự đầu vào chứa các hướng dẫn* để tạo sơ đồ. Trong chuỗi đó, các hướng dẫn được viết bằng một ngôn ngữ khác, được gọi là ngôn ngữ [DOT](https://graphviz.org/doc/info/lang.html) - khá dễ dàng để học những điều cơ bản.

**Cấu trúc cơ bản**

1.  Mở hướng dẫn `grViz("`  
2.  Chỉ định hướng và tên của biểu đồ, đồng thời mở ngoặc, vd: `digraph my_flow_chart {`
3.  Câu lệnh biểu đồ (bố cục, hướng sắp xếp các biến số)  
4.  Câu lệnh nút (tạo nút)
5.  Câu lệnh Edges (cung cấp liên kết giữa các nút)  
6.  Đóng các hướng dẫn `}")`

### Ví dụ đơn giản

Dưới đây là hai ví dụ đơn giản

Một ví dụ rất đơn giản:

``` r
# A minimal plot
DiagrammeR::grViz("digraph {
  
graph[layout = dot, rankdir = LR]

a
b
c

a -> b -> c
}")
```

Một ví dụ khác áp dụng trong y tế công cộng:

``` r
grViz("                           # All instructions are within a large character string
digraph surveillance_diagram {    # 'digraph' means 'directional graph', then the graph name 
  
  # graph statement
  #################
  graph [layout = dot,
         rankdir = TB,
         overlap = true,
         fontsize = 10]
  
  # nodes
  #######
  node [shape = circle,           # shape = circle
       fixedsize = true
       width = 1.3]               # width of circles
  
  Primary                         # names of nodes
  Secondary
  Tertiary

  # edges
  #######
  Primary   -> Secondary [label = ' case transfer']
  Secondary -> Tertiary [label = ' case transfer']
}
")
```

### Cú pháp

**Cú pháp cơ bản**

Tên nút hoặc biểu thức cạnh, có thể được phân tách bằng dấu cách, dấu chấm phẩy hoặc dòng mới.

**Điều hướng**

Một biểu đồ có thể được định hướng lại để di chuyển từ trái sang phải bằng cách điều chỉnh đối số `rankdir` trong câu lệnh biểu đồ. Mặc định là TB (từ trên xuống dưới), nhưng nó có thể là LR (trái sang phải), RL hoặc BT.

**Tên nút**

Tên nút có thể là các từ đơn, như trong ví dụ đơn giản ở trên. Để sử dụng tên nhiều từ hoặc các ký tự đặc biệt (ví dụ: dấu ngoặc đơn, dấu gạch ngang), hãy đặt tên nút trong dấu ngoặc đơn (’ ‘). Có thể dễ dàng hơn để có một tên nút ngắn và gán một *nhãn*, như được hiển thị bên dưới trong dấu ngoặc vuông \[ \]. Nếu bạn muốn có một dòng mới trong tên của nút, bạn phải thực hiện điều đó thông qua một nhãn - sử dụng `\n` trong nhãn của nút trong dấu ngoặc đơn (’ ’), như được trình bày bên dưới.

**Nhóm phụ**

Trong các biểu thức cạnh, nhóm phụ có thể được tạo ở hai bên của cạnh bằng dấu ngoặc nhọn ({ }). Sau đó, cạnh áp dụng cho tất cả các nút trong dấu ngoặc - nó là cách viết tắt.

**Bố cục**

- dot (đặt đối số `rankdir` cho một trong các giá trị sau TB, LR, RL, BT, )
- neato  
- twopi  
- circo

**Nút - có thể chỉnh sửa**

- `label` (ký tự, trong dấu ngoặc đơn nếu nhiều từ)  
- `fillcolor` (nhiều màu)  
- `fontcolor`  
- `alpha` (độ trong suốt 0-1)  
- `shape` (ellipse, oval, diamond, egg, plaintext, point, square, triangle)  
- `style`  
- `sides`  
- `peripheries`  
- `fixedsize` (h x w)  
- `height`  
- `width`  
- `distortion`  
- `penwidth` (độ dày của đường viền)  
- `x` (dịch chuyển trái/phải)  
- `y` (dịch chuyển lên/xuống )  
- `fontname`  
- `fontsize`  
- `icon`

**Các cạnh - có thể chỉnh sửa**

- `arrowsize`  
- `arrowhead` (normal, box, crow, curve, diamond, dot, inv, none, tee, vee)  
- `arrowtail`  
- `dir` (điều hướng, )  
- `style` (gạch ngang, …)  
- `color`  
- `alpha`  
- `headport` (văn bản phía trước đầu mũi tên )  
- `tailport` (văn bản phía sau đuôi mũi tên)  
- `fontname`  
- `fontsize`  
- `fontcolor`  
- `penwidth` (độ dày của mũi tên)  
- `minlen` (chiều dài tối thiểu)

**Tên màu**: mã màu theo bảng mã hex hoặc tên màu ‘X11’, xem [tại đây để biết thông tin chi tiết về X11](http://rich-iannone.github.io/DiagrammeR/graphviz_and_mermaid.html)

### Ví dụ phức tạp

Ví dụ dưới đây mở rộng trên một sơ đồ giám sát, thêm các tên nút phức tạp, các cạnh được nhóm lại, màu sắc và style

    DiagrammeR::grViz("               # All instructions are within a large character string
    digraph surveillance_diagram {    # 'digraph' means 'directional graph', then the graph name 
      
      # graph statement
      #################
      graph [layout = dot,
             rankdir = TB,            # layout top-to-bottom
             fontsize = 10]
      

      # nodes (circles)
      #################
      node [shape = circle,           # shape = circle
           fixedsize = true
           width = 1.3]                      
      
      Primary   [label = 'Primary\nFacility'] 
      Secondary [label = 'Secondary\nFacility'] 
      Tertiary  [label = 'Tertiary\nFacility'] 
      SC        [label = 'Surveillance\nCoordination',
                 fontcolor = darkgreen] 
      
      # edges
      #######
      Primary   -> Secondary [label = ' case transfer',
                              fontcolor = red,
                              color = red]
      Secondary -> Tertiary [label = ' case transfer',
                              fontcolor = red,
                              color = red]
      
      # grouped edge
      {Primary Secondary Tertiary} -> SC [label = 'case reporting',
                                          fontcolor = darkgreen,
                                          color = darkgreen,
                                          style = dashed]
    }
    ")

**Các cụm biểu đồ phụ**

Để nhóm các nút thành các cụm có khung, hãy đặt chúng trong cùng một đồ thị con được đặt tên (`subgraph name {}`). Để xác định từng đồ thị con trong một khung giới hạn, hãy bắt đầu tên của đồ thị con bằng “cluster”, như được trình bày ở 4 khung bên dưới.

    DiagrammeR::grViz("             # All instructions are within a large character string
    digraph surveillance_diagram {  # 'digraph' means 'directional graph', then the graph name 
      
      # graph statement
      #################
      graph [layout = dot,
             rankdir = TB,            
             overlap = true,
             fontsize = 10]
      

      # nodes (circles)
      #################
      node [shape = circle,                  # shape = circle
           fixedsize = true
           width = 1.3]                      # width of circles
      
      subgraph cluster_passive {
        Primary   [label = 'Primary\nFacility'] 
        Secondary [label = 'Secondary\nFacility'] 
        Tertiary  [label = 'Tertiary\nFacility'] 
        SC        [label = 'Surveillance\nCoordination',
                   fontcolor = darkgreen] 
      }
      
      # nodes (boxes)
      ###############
      node [shape = box,                     # node shape
            fontname = Helvetica]            # text font in node
      
      subgraph cluster_active {
        Active [label = 'Active\nSurveillance'] 
        HCF_active [label = 'HCF\nActive Search']
      }
      
      subgraph cluster_EBD {
        EBS [label = 'Event-Based\nSurveillance (EBS)'] 
        'Social Media'
        Radio
      }
      
      subgraph cluster_CBS {
        CBS [label = 'Community-Based\nSurveillance (CBS)']
        RECOs
      }

      
      # edges
      #######
      {Primary Secondary Tertiary} -> SC [label = 'case reporting']

      Primary   -> Secondary [label = 'case transfer',
                              fontcolor = red]
      Secondary -> Tertiary [label = 'case transfer',
                              fontcolor = red]
      
      HCF_active -> Active
      
      {'Social Media' Radio} -> EBS
      
      RECOs -> CBS
    }
    ")

**Hình dạng nút**

Ví dụ dưới đây, tham khảo từ[tài liệu trực tuyến này](http://rich-iannone.github.io/DiagrammeR/), hiển thị các hình dạng nút được áp dụng và cách viết tắt cho các kết nối cạnh nối tiếp.

``` r
DiagrammeR::grViz("digraph {

graph [layout = dot, rankdir = LR]

# define the global styles of the nodes. We can override these in box if we wish
node [shape = rectangle, style = filled, fillcolor = Linen]

data1 [label = 'Dataset 1', shape = folder, fillcolor = Beige]
data2 [label = 'Dataset 2', shape = folder, fillcolor = Beige]
process [label =  'Process \n Data']
statistical [label = 'Statistical \n Analysis']
results [label= 'Results']

# edge definitions with the node IDs
{data1 data2}  -> process -> statistical -> results
}")
```

### Kết quả đầu ra

Cách xử lý và lưu kết quả đầu ra

- Kết quả đầu ra sẽ xuất hiện trong cửa sổ RStudio’s Viewer, theo mặc định ở phía dưới bên phải cùng với các mục Files, Plots, Packages, và Help.
- Để xuất, bạn có thể chọn “Save as image” để lưu dưới dạng ảnh hoặc “Copy to clipboard” để sao chép vào bộ nhớ tạm từ Viewer. Hình ảnh sẽ điều chỉnh theo kích thước được chỉ định.

### Đồ thị được tham số hóa

Mục này được trích dẫn từ nguồn sau: https://mikeyharper.uk/flowcharts-in-r-using-diagrammer/

“Các biểu đồ được tham số hóa: Lợi ích tuyệt vời của việc thiết kế các đồ thị trong R là chúng ta có thể kết nối các đồ thị trực tiếp với phân tích của mình bằng cách đọc các giá trị R trực tiếp vào flowchart của chúng ta. Ví dụ: giả sử bạn đã tạo một quy trình lọc để loại bỏ các giá trị sau mỗi giai đoạn của một quy trình, bạn có thể có một đồ thị hiển thị số lượng giá trị còn lại trong tập dữ liệu sau mỗi giai đoạn trong quy trình của bạn. Để làm điều này, chúng ta có thể sử dụng ký hiệu @@X trực tiếp trong đồ thị, sau đó tham chiếu tới footer của biểu đồ bằng cách sử dụng \[X\]:, trong đó X là chỉ số số duy nhất.”

Chúng tôi khuyến khích bạn xem lại hướng dẫn này nếu tham số hóa là điều bạn quan tâm.

## 35.3 Sơ đồ Alluvial/Sankey

### Gọi packages

Đoạn code dưới đây hiển thị cách gọi các packages cần thiết cho các phân tích. Trong cuốn sách này, chúng tôi nhấn mạnh đến hàm `p_load()` từ package **pacman**, cài đặt gói nếu cần *và* gọi nó ra để sử dụng. Bạn cũng có thể gọi các packages đã cài đặt với hàm `library()` từ **base** R. Xem chương [R cơ bản](basics.llms.md) để biết thêm thông tin về các package R.

Chúng ta gọi package **networkD3** để vẽ sơ đồ và package **tidyverse** cho các bước chuẩn bị dữ liệu.

``` r
pacman::p_load(
  networkD3,
  tidyverse)
```

### Vẽ đồ thị từ một tập dữ liệu

Vẽ những mối liên quan trong một tập dữ liệu. Dưới đây, chúng tôi minh họa việc sử dụng package này với bộ số liệu `linelist`. Hãy đọc thêm [hướng dẫn trực tuyến sau.](https://www.r-graph-gallery.com/321-introduction-to-interactive-sankey-diagram-2.html).

Chúng ta sẽ bắt đầu bằng cách lấy số lượng các trường hợp theo sự kết hợp của nhóm tuổi và bệnh viện. Chúng ta cũng xóa các giá trị thiếu nhóm tuổi để làm sạch. Chúng ta cũng gắn lại nhãn các cột `hospital` và cột `age_cat` tương ứng là `source` và `target`. Đây sẽ là hai mặt của sơ đồ Alluvial.

``` r
# counts by hospital and age category
links <- linelist %>% 
  drop_na(age_cat) %>% 
  select(hospital, age_cat) %>%
  count(hospital, age_cat) %>% 
  rename(source = hospital,
         target = age_cat)
```

Tập dữ liệu bây giờ trông như thế này:

Bây giờ chúng ta tạo một data frame cho tất cả các nút của sơ đồ, dưới cột `name`. Điều này bao gồm tất cả các giá trị cho cột `hospital` và cột `age_cat`. Lưu ý rằng chúng ta cần đảm bảo tất cả chúng đều có kiểu Ký tự trước khi kết hợp chúng và điều chỉnh cột ID thành dạng số thay vì dạng nhãn:

``` r
# The unique node names
nodes <- data.frame(
  name=c(as.character(links$source), as.character(links$target)) %>% 
    unique()
  )

nodes  # print
```

                                       name
    1                      Central Hospital
    2                     Military Hospital
    3                               Missing
    4                                 Other
    5                         Port Hospital
    6  St. Mark's Maternity Hospital (SMMH)
    7                                   0-4
    8                                   5-9
    9                                 10-14
    10                                15-19
    11                                20-29
    12                                30-49
    13                                50-69
    14                                  70+

Chúng ta tiếp tục chỉnh sửa data frame có tên `links` mà chúng ta đã tạo ở trên với hàm `count()`. Chúng ta thêm hai cột dạng số là cột `IDsource` và `IDtarget` để thực sự phản ánh/tạo liên kết giữa các nút. Các cột này sẽ giữ số thứ tự hàng (vị trí) của nút nguồn và nút đích. Số 1 sẽ bị trừ để các số vị trí này bắt đầu bằng 0 (không phải 1).

``` r
# match to numbers, not names
links$IDsource <- match(links$source, nodes$name)-1 
links$IDtarget <- match(links$target, nodes$name)-1
```

Tập dữ liệu link bây giờ trông như sau:

Bây giờ, chúng ta vẽ sơ đồ Sankey với hàm `sankeyNetwork()`. Bạn có thể đọc thêm về từng đối số bằng cách chạy lệnh `?sankeyNetwork` trong bảng điều khiển. Lưu ý rằng trừ khi bạn đặt `iterations = 0`, thứ tự các nút của bạn có thể sẽ không như bạn mong đợi.

``` r
# plot
######
p <- sankeyNetwork(
  Links = links,
  Nodes = nodes,
  Source = "IDsource",
  Target = "IDtarget",
  Value = "n",
  NodeID = "name",
  units = "TWh",
  fontSize = 12,
  nodeWidth = 30,
  iterations = 0)        # ensure node order is as in data
p
```

Đây là một ví dụ trong đó Kết quả của bệnh nhân cũng được bao gồm. Lưu ý trong bước chuẩn bị dữ liệu, chúng ta phải tính toán số lượng các trường hợp giữa tuổi và bệnh viện, và phân biệt biệt giữa bệnh viện và outcome - sau đó liên kết tất cả các số lượng này với nhau bằng hàm `bind_rows()`.

``` r
# counts by hospital and age category
age_hosp_links <- linelist %>% 
  drop_na(age_cat) %>% 
  select(hospital, age_cat) %>%
  count(hospital, age_cat) %>% 
  rename(source = age_cat,          # re-name
         target = hospital)

hosp_out_links <- linelist %>% 
    drop_na(age_cat) %>% 
    select(hospital, outcome) %>% 
    count(hospital, outcome) %>% 
    rename(source = hospital,       # re-name
           target = outcome)

# combine links
links <- bind_rows(age_hosp_links, hosp_out_links)

# The unique node names
nodes <- data.frame(
  name=c(as.character(links$source), as.character(links$target)) %>% 
    unique()
  )

# Create id numbers
links$IDsource <- match(links$source, nodes$name)-1 
links$IDtarget <- match(links$target, nodes$name)-1

# plot
######
p <- sankeyNetwork(Links = links,
                   Nodes = nodes,
                   Source = "IDsource",
                   Target = "IDtarget",
                   Value = "n",
                   NodeID = "name",
                   units = "TWh",
                   fontSize = 12,
                   nodeWidth = 30,
                   iterations = 0)
p
```

https://www.displayr.com/sankey-diagrams-r/

## 35.4 Chuỗi sự kiện trong thời gian

Để tạo dòng thời gian hiển thị các sự kiện cụ thể, bạn có thể sử dụng package `vistime`.

Xem thêm [vignette](https://cran.r-project.org/web/packages/vistime/vignettes/vistime-vignette.html#ex.-2-project-planning) này

``` r
# load package
pacman::p_load(vistime,  # make the timeline
               plotly    # for interactive visualization
               )
```

Đây là tập dữ liệu mà chúng ta sẽ bắt đầu sử dụng:

``` r
p <- vistime(data)    # apply vistime

library(plotly)

# step 1: transform into a list
pp <- plotly_build(p)

# step 2: Marker size
for(i in 1:length(pp$x$data)){
  if(pp$x$data[[i]]$mode == "markers") pp$x$data[[i]]$marker$size <- 10
}

# step 3: text size
for(i in 1:length(pp$x$data)){
  if(pp$x$data[[i]]$mode == "text") pp$x$data[[i]]$textfont$size <- 10
}


# step 4: text position
for(i in 1:length(pp$x$data)){
  if(pp$x$data[[i]]$mode == "text") pp$x$data[[i]]$textposition <- "right"
}

#print
pp
```

## 35.5 Sơ đồ DAGs

Bạn có thể tạo sơ đồ DAG theo cách thủ công bằng cách sử dụng package **DiagammeR** và ngôn ngữ DOT như đã mô tả ở trên.

Ngoài ra, có các package như **ggdag** và **daggity**

[Giới thiệu về sơ đồ DAGs](https://cran.r-project.org/web/packages/ggdag/vignettes/intro-to-dags.html)

[Suy luận nhân quả với dags trong R](https://www.r-bloggers.com/2019/08/causal-inference-with-dags-in-r/#:~:text=In%20a%20DAG%20all%20the,for%20drawing%20and%20analyzing%20DAGs.)

## 35.6 Tài nguyên học liệu

Phần lớn nội dung ở trên liên quan đến ngôn ngữ DOT được tham khảo từ hướng dẫn [này](https://mikeyharper.uk/flowcharts-in-r-using-diagrammer/)

Một tài liệu khác chuyên sâu hơn tại đây [Tài liệu về DiagammeR](http://rich-iannone.github.io/DiagrammeR/)

Xem thêm về [Sơ đồ Sankey tại đây](https://www.displayr.com/sankey-diagrams-r/)
