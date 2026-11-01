# 45  Dizin etkileşimleri

Bu sayfada, dizinler (klasörler) oluşturduğunuz, etkileşimde bulunduğunuz, kaydettiğiniz ve içe aktardığınız genel senaryoları ele alıyoruz.

## 45.1 Hazırlık

### **fs** paketi

**fs** paketi, dizin etkileşimlerini kolaylaştıran ve bazı R **tabanı** fonksiyonlarını geliştiren bir **tidyverse** paketidir. Aşağıdaki bölümlerde genellikle **fs**’den gelen fonksiyonları kullanacağız.

``` r
pacman::p_load(
  fs,             # dosya/dizin etkileşimleri
  rio,            # içe aktar/dışa aktar
  here,           # göreceli dosya yolakları
  tidyverse)      # veri yönetimi ve görselleştirme
```

### Dizini bir dendrogram ağacı olarak yazdır

**fs**’den `dir_tree()` fonksiyonunu kullanın.

Klasör dosya yolunu `path =` olarak sağlayın. Yalnızca bir seviyeyi göstermek için `recurse = FALSE`, tüm alt seviyelerdeki tüm dosyaları göstermek için `recurse = TRUE` kullanın. Aşağıda, R projesi için kısayol olarak `here()` kullanıyoruz ve bu el kitabının örnek verilerini içeren “data” alt klasörünü belirledik. “data” ve alt klasörlerindeki tüm dosyaları gösterecek şekilde ayarladık.

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

## 45.2 Bir dizindeki dosyaları listeleyin

Bir dizindeki yalnızca dosya adlarını listelemek için R **tabanı**ndan `dir()` kullanabilirsiniz. Örneğin, bu komut, bir R projesindeki “example” klasörünün “linelists” alt klasöründeki dosyaların adlarını listeler. Göreli dosya yolu, ‘here()’ kullanılarak sağlanır (bunun hakkında daha fazla bilgiyi \[İçe aktarma ve dışa aktarma\] sayfasında okuyabilirsiniz).

``` r
# dosya adları
dir(here("data", "example", "linelists"))
```

    [1] "20201007linelist.csv"          "case_linelist_2020-10-02.csv" 
    [3] "case_linelist_2020-10-03.csv"  "case_linelist_2020-10-04.csv" 
    [5] "case_linelist_2020-10-05.csv"  "case_linelist_2020-10-08.xlsx"
    [7] "case_linelist20201006.csv"    

Dizin dosyalarının tam dosya yollarını listelemek için **fs**’den `dir_ls()` kullanabilirsiniz. R **tabanı**ndaki bir alternatif “list.files()”dir.

``` r
# dosya yolları
dir_ls(here("data", "example", "linelists"))
```

    data/example/linelists/20201007linelist.csv
    data/example/linelists/case_linelist20201006.csv
    data/example/linelists/case_linelist_2020-10-02.csv
    data/example/linelists/case_linelist_2020-10-03.csv
    data/example/linelists/case_linelist_2020-10-04.csv
    data/example/linelists/case_linelist_2020-10-05.csv
    data/example/linelists/case_linelist_2020-10-08.xlsx

Bir dizindeki her dosyayla ilgili tüm meta veri bilgilerini almak için (ör. yol, değişiklik tarihi vb.), **fs**’den `dir_info()` kullanabilirsiniz.

Bu, örneğin dosyanın en son sürümünü içe aktarmak istediğinizde, dosyanın son değişiklik zamanını çıkarmak istiyorsanız özellikle yararlı olabilir. Bunun bir örneği için \[İçe ve dışa aktar\] sayfasına bakın.

``` r
# dosya bilgisi
dir_info(here("data", "example", "linelists"))
```

İşte döndürülen veri çerçevesi. Tüm sütunları görmek için sağa kaydırın.

## 45.3 Dosya bilgisi

Belirli bir dosya hakkında meta veri bilgilerini çıkarmak için, **fs**’den `file_info()` (veya R **tabanı**ndan `file.info()`) kullanabilirsiniz.

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))
```

Burada sonucu dizine eklemek ve yalnızca “modification_time” değerini döndürmek için `$` kullanıyoruz.

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))$modification_time
```

    [1] "2026-11-01 15:52:14 UTC"

## 45.4 Var olup olmadığını kontrol edin

### R nesneleri

Bir R nesnesinin \* R içinde \* olup olmadığını kontrol etmek için R **tabanı**ndan ‘exists()’ kullanabilirsiniz (nesne adını tırnak içinde sağlayın).

``` r
exists("linelist")
```

    [1] FALSE

Bazı R **tabanı** paketlerinin, sahne arkasında “data” gibi genel nesne adları kullandığını ve `inherit = FALSE` belirtilmediği sürece TRUE olarak görüneceğini unutmayın. Bu, veri kümenizi “data” olarak adlandırmamanın bir nedenidir.

``` r
exists("data")
```

    [1] TRUE

``` r
exists("data", inherit = FALSE)
```

    [1] FALSE

Bir fonksiyon yazıyorsanız, bir argümanın mevcut olup olmadığını kontrol etmek için ‘exists()’ yerine ‘missing()’ kullanmalısınız.

### Dizinler

Bir dizinin var olup olmadığını kontrol etmek için, **fs**’den `is_dir()` dizinine dosya yolunu (ve dosya adını) sağlayın. “TRUE” yazısının yazdırıldığını görmek için sağa kaydırın.

``` r
is_dir(here("data"))
```

    data 
    TRUE 

Alternatif olarak R **tabanı**ndan `file.exists()` kullanılabilir.

### Dosyalar

Belirli bir dosyanın var olup olmadığını kontrol etmek için **fs**’den `is_file()` kullanın. “TRUE” yazısının yazdırıldığını görmek için sağa kaydırın.

``` r
is_file(here("data", "case_linelists", "linelist_cleaned.rds"))
```

    data/case_linelists/linelist_cleaned.rds 
                                        TRUE 

R **tabanı**ndaki bir alternatif `file.exists()`tir.

## 45.5 Oluşturmak

### Dizinler

Yeni bir dizin (klasör) oluşturmak için **fs**’den `dir_create()` kullanabilirsiniz. Dizin zaten mevcutsa, üzerine yazılmaz ve hiçbir hata döndürülmez.

``` r
dir_create(here("data", "test"))
```

Bir alternatif, dizin zaten mevcutsa bir hata gösterecek olan R **tabanı**ndaki `dir.create()`dir. Buna karşılık, bu senaryoda `dir_create()` sessiz olacaktır.

### Dosyalar

**fs**’den `file_create()` ile (boş) bir dosya oluşturabilirsiniz. Dosya zaten mevcutsa, üzerine yazılmaz veya değiştirilmez.

``` r
file_create(here("data", "test.rds"))
```

R **tabanı**ndaki alternatifi `file.create()`. Ancak dosya zaten mevcutsa, bu seçenek dosyayı kesecektir. `file_create()` kullanırsanız, dosya değişmeden kalacaktır.

### Yoksa oluştur

YAPIM AŞAMASINDA…

## 45.6 Silmek

### R nesneleri

Bir R nesnesini kaldırmak için R **tabanı**ndan ‘rm()’ kullanın.

### Dizinler

**fs**’den `dir_delete()` kullanın.

### Dosyalar

Dosyaları **fs** içinden `file_delete()` ile silebilirsiniz.

## 45.7 Diğer dosyaları çalıştırma

### `source()`

Bir R betiğini başka bir R betiğinden çalıştırmak için `source()` komutunu kullanabilirsiniz (R **tabanı**ndan).

``` r
source(here("scripts", "cleaning_scripts", "clean_testing_data.R"))
```

Bu, yukarıdaki R komut dosyasını görüntülemeye ve komut dosyasının sağ üst köşesindeki “Kaynak” düğmesine tıklamaya eşdeğerdir. Bu, betiği çalıştıracak, ancak özellikle istenmedikçe sessizce yapacak (R konsoluna çıktı yok). Soru-cevap modunda R konsolu aracılığıyla bir kullanıcıyla etkileşim kurmak için “source()” kullanma örnekleri için \[Etkileşimli konsol\] sayfasındaki sayfaya bakabilirsiniz.

[![](../../images/source_button.png)](../../images/source_button.png)

### `render()`

“render()”, en sık R işaretleme komut dosyaları için kullanılan “source()”un bir varyasyonudur. R işaretleme dosyası olan `input =` ve ayrıca `output_format =` (tipik olarak “html_document”, “pdf_document”, “word_document”, ““) sağlamaktadır.

Daha fazla ayrıntı için \[R Markdown ile Raporlar\] hakkındaki sayfaya bakabilirsiniz. Ayrıca “render()” belgelerine [buradan](https://rmarkdown.rstudio.com/docs/reference/render.html) veya “?render” girerek bakabilirsiniz.

### Dosyaları dizinde çalıştırın

Bir *for loop* oluşturabilir ve bunu ‘dir()’ ile tanımlanan bir dizindeki her dosyayı ‘source()’ için kullanabilirsiniz.

``` r
for(script in dir(here("scripts"), pattern = ".R$")) {   # R Project'in "scripts" klasöründeki her bir komut dosyası adı için (.R uzantılı)
  source(here("scripts", script))                        # dosyayı, komut dosyaları klasöründe bulunan eşleşen adla kaynaklayın
}
```

Yalnızca belirli komut dosyalarını çalıştırmak istiyorsanız, bunları şu şekilde adlarıyla tanımlayabilirsiniz:

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

**fs** ve R **tabanı** fonksiyonlarının [karşılaştırması](https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html)

### Dosyaları dizine aktarın

Tek tek dosyaları içe ve dışa aktarmak için \[İçe ve dışa aktarma\] hakkındaki sayfaya bakabilirsiniz.

Ayrıca dosya meta verilerine bakarak *veya* dosya adındaki bir tarihe dayalı olarak en son dosyayı otomatik olarak içe aktarma yöntemleri için \[İçe ve dışa aktar\] sayfasına bakabilirsiniz.

**purrr** paketinin aşağıdakileri gösterdiği bir örnek için \[Yineleme, döngüler ve listeler\] hakkındaki sayfaya bakabilirsiniz:

- Bir veri çerçevesini bölme ve birden çok CSV dosyası olarak kaydetme
- Bir veri çerçevesini bölme ve her bir parçayı tek bir Excel çalışma kitabında ayrı bir sayfa olarak kaydetme
- Birden fazla CSV dosyasını içe aktarma ve bunları tek bir veri çerçevesinde birleştirme
- Birden çok sayfa içeren bir Excel çalışma kitabını içe aktarma ve bunları tek bir veri çerçevesinde birleştirme

## 45.8 R **tabanı**

Belirtilen bir dizindeki dosyaları listelemekle aynı işlemi gerçekleştiren `list.files()` ve `dir()` fonksiyonlarına aşağıda bakın. “ignore.case =” veya aranacak belirli bir desen belirtebilirsiniz.

``` r
list.files(path = here("data"))

list.files(path = here("data", "example"), pattern = "\\.csv$")
# dir(path = here("data", "example"), pattern = "\\.csv$")

list.files(path = here("data", "example"), pattern = "hospital", ignore.case = TRUE)
```

Bir dosya şu anda “açık” ise, klasörünüzde “~\$hospital_linelists.xlsx” gibi bir yaklaşık işareti olacak şekilde görüntülenir.

## 45.9 Kaynaklar

https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html
