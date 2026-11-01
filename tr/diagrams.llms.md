# 35  Diyagramlar ve çizelgeler

[![](../../images/flow_chart.png)](../../images/flow_chart.png)

[![](../../images/sankey_diagram.png)](../../images/sankey_diagram.png)

Bu sayfa, aşağıdaki başlıkları kapsamaktadır:

- \*\*DiagrammeR\* ve DOT dilini kullanan akış şemaları
- Alluvial/Sankey diyagramları  
- Etkinlik zaman çizelgeleri

## 35.1 Hazırlık

### Paketleri yükleme

Bu kod parçası, analizler için gerekli olan paketlerin yüklenmesini gösterir. Bu el kitabında, gerekirse paketi kuran ve kullanım için yükleyen **pacman** paketinin `p_load()` işlevini vurguluyoruz. Ayrıca, R tabanından `library()` ile kurulu paketleri yükleyebilirsiniz. R paketleri hakkında daha fazla bilgi için R temelleri sayfasına bakabilirsiniz.

``` r
pacman::p_load(
  DiagrammeR,     # akış diyagramları için
  networkD3,      # Alluvial/Sankey diyagramları için
  tidyverse,      # veri yönetimi ve görselleştirme
  appliedepidata) # bu el kitabında kullanılan örnek veriler
```

### Verileri içe aktarma

Bu sayfadaki içeriğin çoğu bir veri seti gerektirmez. Ancak, Sankey diyagramı bölümünde, simüle edilmiş bir Ebola salgınından vaka satır listesini kullanacağız. Doğrudan `appliedepidata::get_data(name = "linelist_cleaned_rds")` ile yükleyin (ayrıntılar için [El kitabı ve veri indirme](download.llms.md) sayfasına bakın).

``` r
# satır listesini içe aktar
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

Çizgi listesinin ilk 50 satırı aşağıda gösterilmiştir.

## 35.2 Akış diyagramları

Grafikler/akış şemaları oluşturmak için R paketi olan **DiagrammeR** kullanılabilir. Akış şemaları ister statik olabilirler veya isterse bir veri kümesindeki değişikliklere göre kısıtlı bir şekilde dinamik olarak ayarlanabilirler.

**Araçlar**

`grViz()` fonksiyonu bir “Graphviz” diyagramı oluşturmak için kullanılır. Bu fonksiyon, diyagramı oluşturmak için talimatlar içeren bir karakter dizisi girişini kabul eder. Bu dizi içinde, talimatlar [DOT](https://graphviz.org/doc/info/lang.html) adı verilen farklı bir dilde yazılmıştır - temel bilgileri öğrenmek oldukça kolaydır.

**Temel yapı**

1.  `grViz("` talimatlarını açın
2.  Grafiğin yönlülüğünü ve adını belirtin ve parantezleri açın, örn. `digraph my_flow_chart {`
3.  Grafik ifadesi (düzen, sıralama yönü)
4.  Düğüm ifadeleri (düğüm oluşturma)
5.  Kenar ifadeleri (düğümler arasında bağlantılar verir)
6.  Talimatları kapatın `}")`

### Basit örnekler

Aşağıda iki basit örnek verilmiştir

Çok minimal bir örnek:

``` r
# Minimal bir grafik
DiagrammeR::grViz("digraph {
  
graph[layout = dot, rankdir = LR]

a
b
c

a -> b -> c
}")
```

Biraz daha uygulamalı halk sağlığı bağlamına sahip bir örnek:

``` r
grViz("                           # All instructions are within a large character string
digraph surveillance_diagram {    # digraph', 'yönlü grafik' anlamına gelir, ardından grafik adı
  
  # grafik ifadesi
  #################
  graph [layout = dot,
         rankdir = TB,
         overlap = true,
         fontsize = 10]
  
  # düğümler
  #######
  node [shape = circle,           # shape = circle
       fixedsize = true
       width = 1.3]               # width of circles
  
  Primary                         # names of nodes
  Secondary
  Tertiary

  # kenarlar
  #######
  Primary   -> Secondary [label = ' case transfer']
  Secondary -> Tertiary [label = ' case transfer']
}
")
```

### Sözdizimi

**Temel sözdizimi**

Düğüm adları veya kenar ifadeleri boşluk, noktalı virgül veya yeni satırlarla ayrılabilir.

**Sıra yönü**

Grafik ifadesi içindeki `rankdir` argümanı ayarlanarak bir çizim soldan sağa hareket edecek şekilde yeniden yönlendirilebilir. Varsayılan değer TB’dir (yukarıdan aşağıya), ancak LR (soldan sağa), RL veya BT olabilir.

**Düğüm adları**

Düğüm adları, yukarıdaki basit örnekte olduğu gibi tek kelime olabilir. Çok kelimeli adları veya özel karakterleri (örneğin parantezler, tireler) kullanmak için düğüm adını tek tırnak (’ ’) içine koyun. Kısa bir düğüm adına sahip olmak ve aşağıda köşeli parantez \[ \] içinde gösterildiği gibi bir *etiket* atamak daha kolay olabilir. Düğümün adında yeni bir satır olmasını istiyorsanız, bunu bir etiket aracılığıyla yapmalısınız - aşağıda gösterildiği gibi düğüm etiketinde tek tırnak içinde `\n` kullanmalısınız.

**Alt gruplar**  
Kenar ifadeleri içinde, küme parantezleri ({ }) ile kenarın her iki tarafında alt gruplar oluşturulabilir. Kenar daha sonra parantez içindeki tüm düğümlere uygulanır - bu bir kısa gösterimdir.

**Düzenler**

- dot (`rankdir` argümanını TB, LR, RL, BT seçeneklerinden biri olarak belirleyin)
- neato  
- twopi  
- circo

**Düğümler - düzenlenebilir nitelikler**

- `label` (metin, çok kelimeli ise tek tırnak içinde)  
- `fillcolor` (birçok olası renk)  
- `fontcolor`  
- `alpha` (şeffaflık 0-1)  
- `shape` (ellipse, oval, diamond, egg, plaintext, point, square, triangle)  
- `style`  
- `sides`  
- `peripheries`  
- `fixedsize` (h x w)  
- `height`  
- `width`  
- `distortion`  
- `penwidth` (şekil kenarlığının genişliği)  
- `x` (sola/sağa yer değiştirme)  
- `y` (yukarı/aşağı yer değiştirme)  
- `fontname`  
- `fontsize`  
- `icon`

**Kenarlar - düzenlenebilir nitelikler**

- `arrowsize`  
- `arrowhead` (normal, box, crow, curve, diamond, dot, inv, none, tee, vee)  
- `arrowtail`  
- `dir` (yön, )  
- `style` (dashed, …)  
- `color`  
- `alpha`  
- `headport` (ok başının önündeki metin)  
- `tailport` (ok kuyruğunun arkasındaki metin)  
- `fontname`  
- `fontsize`  
- `fontcolor`  
- `penwidth` (ok genişliği)  
- `minlen` (minimum uzunluk)

**Renk adları**: onaltılık değerler veya ‘X11’ renk adları, X11 ayrıntıları için [buraya bakabilirsiniz.](http://rich-iannone.github.io/DiagrammeR/graphviz_and_mermaid.html)

### Karmaşık örnekler

Aşağıdaki örnek, gsurveillance_diagram genişleterek karmaşık düğüm adları, gruplandırılmış kenarlar, renkler ve stil ekler

    DiagrammeR::grViz("               # Tüm talimatlar büyük bir karakter dizisi
    digraph surveillance_diagram {    # digraph', 'yönlü grafik' anlamına gelir, ardından grafik adı
      
      # grafik ifadesi
      #################
      graph [layout = dot,
             rankdir = TB,            # yukarıdan aşağıya düzen
             fontsize = 10]
      

      # düğümler (daireler)
      #################
      node [shape = circle,           # shape = daire
           fixedsize = true
           width = 1.3]                      
      
      Primary   [label = 'Primary\nFacility'] 
      Secondary [label = 'Secondary\nFacility'] 
      Tertiary  [label = 'Tertiary\nFacility'] 
      SC        [label = 'Surveillance\nCoordination',
                 fontcolor = darkgreen] 
      
      # kenarlar
      #######
      Primary   -> Secondary [label = ' case transfer',
                              fontcolor = red,
                              color = red]
      Secondary -> Tertiary [label = ' case transfer',
                              fontcolor = red,
                              color = red]
      
      # gruplanmış kenar
      {Primary Secondary Tertiary} -> SC [label = 'case reporting',
                                          fontcolor = darkgreen,
                                          color = darkgreen,
                                          style = dashed]
    }
    ")

**Alt grafik kümeleri**

Düğümleri kutulu kümeler halinde gruplamak için, onları aynı adlandırılmış alt grafik (`subgraph name {}`) içine koyun. Her bir alt grafiğin bir sınırlayıcı kutu içinde tanımlanmasını sağlamak için, aşağıdaki 4 kutu ile gösterildiği gibi alt grafiğin adına “cluster” ile başlayın.

    DiagrammeR::grViz("             # Tüm talimatlar büyük bir karakter dizisi içindedir
    digraph surveillance_diagram {  # 'digraph', 'yönlü grafik' anlamına gelir, ardından grafik adı
      
      # grafik ifadesi
      #################
      graph [layout = dot,
             rankdir = TB,            
             overlap = true,
             fontsize = 10]
      

      # düğümler (daireler)
      #################
      node [shape = circle,                  # shape = daire
           fixedsize = true
           width = 1.3]                      # dairelerin genişliği
      
      subgraph cluster_passive {
        Primary   [label = 'Primary\nFacility'] 
        Secondary [label = 'Secondary\nFacility'] 
        Tertiary  [label = 'Tertiary\nFacility'] 
        SC        [label = 'Surveillance\nCoordination',
                   fontcolor = darkgreen] 
      }
      
      # düğümler (kutular)
      ###############
      node [shape = box,                     # düğüm şekli
            fontname = Helvetica]            # düğümdeki metin yazı tipi
      
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

      
      # kenarlar
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

**Düğüm şekilleri**

[Linkteki rehberden](http://rich-iannone.github.io/DiagrammeR/) alınan aşağıdaki örnek, uygulanan düğüm şekillerini ve seri kenar bağlantıları için bir kısayol gösterir.

``` r
DiagrammeR::grViz("digraph {

graph [layout = dot, rankdir = LR]

# düğümlerin global stillerini tanımlar. İstersek bunları kutuda geçersiz kılabiliriz
node [shape = rectangle, style = filled, fillcolor = Linen]

data1 [label = 'Dataset 1', shape = folder, fillcolor = Beige]
data2 [label = 'Dataset 2', shape = folder, fillcolor = Beige]
process [label =  'Process \n Data']
statistical [label = 'Statistical \n Analysis']
results [label= 'Results']

# düğüm kimlikleri ile kenar tanımları
{data1 data2}  -> process -> statistical -> results
}")
```

### Çıktılar

Çıktılar nasıl işlenir ve kaydedilir:

- Çıktılar, varsayılan olarak Dosyalar, Grafikler, Paketler ve Yardım’ın yanında sağ altta RStudio’nun Görüntüleyici bölmesinde görünecektir.  
- Dışa aktarmak için Görüntüleyiciden “Görüntü olarak kaydet” veya “Panoya kopyala” yapabilirsiniz. Grafik belirtilen boyuta ayarlanacaktır.

### Parametreli şekiller

Size önerebileceğimiz güzel bir rehberden bir alıntı ile başlamak istiyoruz: https://mikeyharper.uk/flowcharts-in-r-using-diagrammer/

“Parametreli şekiller: Şekilleri R içinde tasarlamanın büyük bir yararı, R değerlerini doğrudan akış şemalarımıza okuyarak şekilleri doğrudan analizimizle bağlayabilmemizdir. Örneğin, bir işlemin her aşamasından sonra değerleri kaldıran bir filtreleme işlemi oluşturduğunuzu varsayalım, işleminizin her aşamasından sonra veri kümesinde kalan değerlerin sayısını gösteren bir şekle sahip olabilirsiniz. Bunu yapmak için, @@X sembolünü doğrudan şeklin içinde kullanabilir, ardından grafiğin alt bilgisinde \[X\]: kullanarak buna başvurabilirsiniz, burada X benzersiz bir sayısal dizindir.”

Parametrelendirme ilgilendiğiniz bir şeyse, bu rehberi incelemenizi öneririz.

## 35.3 Alluvial/Sankey Diyagramları

### Paketleri yükleme

Bu kod parçası, analizler için gerekli olan paketlerin yüklenmesini gösterir. Bu el kitabında, gerekirse paketi kuran ve kullanım için yükleyen **pacman** paketinin `p_load()` işlevini vurguluyoruz. Ayrıca, R tabanından `library()` ile kurulu paketleri yükleyebilirsiniz. R paketleri hakkında daha fazla bilgi için R temelleri sayfasına bakabilirsiniz.

Diyagramı oluşturmak için **networkD3** paketini ve ayrıca veri hazırlama adımları için **tidyverse**’i yüklüyoruz.

``` r
pacman::p_load(
  networkD3,
  tidyverse)
```

### Veri kümesinden grafik yapma

Bağlantıları bir veri kümesinde çizme. Aşağıda bu paketi vaka satırı listesinde kullanmayı gösteriyoruz. [Çevrimiçi bir eğitime ulaşmak için bu linke tıklayabilirsiniz.](https://www.r-graph-gallery.com/321-introduction-to-interactive-sankey-diagram-2.html).

Her benzersiz yaş kategorisi ve hastane kombinasyonu için vaka sayılarını alarak başlıyoruz. Anlaşılır olması için yaş kategorisine ait eksik değerleri kaldırdık. Ayrıca `hospital` ve `age_cat` sütunlarını sırasıyla `source` ve `target` olarak yeniden etiketliyoruz. Bunlar alluvial diyagramının iki yüzü olacaktır.

``` r
# hastane ve yaş kategorisine göre sayımlar
links <- linelist %>% 
  drop_na(age_cat) %>% 
  select(hospital, age_cat) %>%
  count(hospital, age_cat) %>% 
  rename(source = hospital,
         target = age_cat)
```

Veri kümesi şimdi şöyle görünmektedir:

Şimdi `name` sütunu altında tüm diyagram düğümlerinin bir veri çerçevesini oluşturuyoruz. Bu, `hospital` ve `age_cat`’e ait bütün değerlerden oluşmaktadır. Birleştirmeden önce hepsinin karakter sınıfı olduğundan emin olmalı ve kimlik sütunlarını etiketler yerine sayı olacak şekilde ayarlamalıyız:

``` r
# Benzersiz düğüm adları
nodes <- data.frame(
  name=c(as.character(links$source), as.character(links$target)) %>% 
    unique()
  )

nodes  # yazdır
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

Yukarıda oluşturduğumuz link veri çerçevesini `count()` ile düzenliyoruz. Düğümler arasındaki bağlantıları gerçekten yansıtacak/oluşturacak iki sayısal sütun `IDsource` ve `IDtarget` ekliyoruz. Bu sütunlar, kaynak ve hedef düğümlerin satır numaralarını (konumunu) tutacaktır. 1 çıkarılır, böylece bu konum numaraları 0’dan başlar (1 değil).

``` r
# isimlerle değil sayılarla eşleştirir
links$IDsource <- match(links$source, nodes$name)-1 
links$IDtarget <- match(links$target, nodes$name)-1
```

Bağlantı veri kümesi şimdi şöyle görünür:

Şimdi Sankey diyagramını `sankeyNetwork()` ile çizebiliriz. Konsolda `?sankeyNetwork` komutunu çalıştırarak her bir bağımsız değişkeni hakkında daha fazla bilgi edinebilirsiniz. `iterations = 0` olarak ayarlamadığınız sürece düğümlerinizin sırasının beklendiği gibi olmayabileceğini unutmayın.

``` r
# grafik
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
  iterations = 0)        # düğüm sırasının verilerdeki gibi olduğundan emin olun
p
```

Burada hasta çıktısının da dahil edildiği bir örnek verilmiştir. Veri hazırlama adımında, yaş ile hastane arasındaki ve hastane ile sonuç arasındaki vaka sayılarını ayrı ayrı hesaplamamız gerektiğine ve ardından tüm bu sayıları `bind_rows()` ile birbirine bağlamamız gerektiğine dikkat etmelisiniz.

``` r
# hastane ve yaş kategorisine göre sayımlar
age_hosp_links <- linelist %>% 
  drop_na(age_cat) %>% 
  select(hospital, age_cat) %>%
  count(hospital, age_cat) %>% 
  rename(source = age_cat,          # yeniden adlandır
         target = hospital)

hosp_out_links <- linelist %>% 
    drop_na(age_cat) %>% 
    select(hospital, outcome) %>% 
    count(hospital, outcome) %>% 
    rename(source = hospital,       # yeniden adlandır
           target = outcome)

# bağlantıları birleştir
links <- bind_rows(age_hosp_links, hosp_out_links)

# Benzersiz düğüm adları
nodes <- data.frame(
  name=c(as.character(links$source), as.character(links$target)) %>% 
    unique()
  )

# Kimlik numaraları oluştur
links$IDsource <- match(links$source, nodes$name)-1 
links$IDtarget <- match(links$target, nodes$name)-1

# grafik
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

## 35.4 Etkinlik zaman çizelgeleri

Belirli olayları gösteren bir zaman çizelgesi oluşturmak için `vistime` paketini kullanabilirsiniz.

[Linkteki bu gösterimi inceleyebilirsiniz](https://cran.r-project.org/web/packages/vistime/vignettes/vistime-vignette.html#ex.-2-project-planning)

``` r
# paketi yükle
pacman::p_load(vistime,  # zaman çizelgesini hazırla
               plotly    # etkileşimli görselleştirme için
               )
```

İşte kodladığımız olaylar veri seti:

``` r
p <- vistime(data)    # vistime'ı uygula

library(plotly)

# 1. adım: bir listeye dönüştür
pp <- plotly_build(p)

# 2. adım: İşaretleyici boyutu
for(i in 1:length(pp$x$data)){
  if(pp$x$data[[i]]$mode == "markers") pp$x$data[[i]]$marker$size <- 10
}

# 3. adım: metin boyutu
for(i in 1:length(pp$x$data)){
  if(pp$x$data[[i]]$mode == "text") pp$x$data[[i]]$textfont$size <- 10
}


# 4. adım: metin konumu
for(i in 1:length(pp$x$data)){
  if(pp$x$data[[i]]$mode == "text") pp$x$data[[i]]$textposition <- "right"
}

#yazdır
pp
```

## 35.5 DAG’ler

Yukarıda açıklandığı gibi **DiagammeR** paketini ve DOT dilini kullanarak manuel olarak bir DAG oluşturabilirsiniz.

Alternatif olarak, **ggdag** ve **dagitty** gibi paketler de var.

[DAG’lere giriş ggdag gösterimi](https://cran.r-project.org/web/packages/ggdag/vignettes/intro-to-dags.html)

[R’deki dag’lere nedensellik](https://www.r-bloggers.com/2019/08/causal-inference-with-dags-in-r/#:~:text=In%20a%20DAG%20all%20the,for%20drawing%20and%20analyzing%20DAGs.)

## 35.6 Kaynaklar

[DOT diliyle ilgili yukarıdakilerin çoğu bu sitedeki öğreticiden uyarlanmıştır.](https://mikeyharper.uk/flowcharts-in-r-using-diagrammer/)

[DiagammeR hakkında daha ayrıntılı bir eğitim daha](http://rich-iannone.github.io/DiagrammeR/)

[Sankey diagramları hakkında bu sayfa](https://www.displayr.com/sankey-diagrams-r/)
