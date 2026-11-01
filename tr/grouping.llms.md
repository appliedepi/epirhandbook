# 13  Verileri Gruplama

[![](../../images/grouping_1500x500.png)](../../images/grouping_1500x500.png)

Bu sayfa, tanımlayıcı analiz için verilerin nasıl gruplandırılacağını ve toplanacağını kapsar. Ortak ve kullanımı kolay fonksiyonlar için **tidyverse** paket ailesini kullanır.

Verileri gruplamak, veri yönetimi ve analizinin temel bir bileşenidir. Gruplandırılmış veriler istatistiksel olarak grup tarafından özetlenir ve grup tarafından çizilebilir. **dplyr** paketindeki fonksiyonlar (**tidyverse**’in bir parçası) gruplandırmayı ve sonraki işlemleri oldukça kolaylaştırır.

Bu sayfa aşağıdaki konuları ele alacaktır:

- `group_by()` fonksiyonuyla verileri gruplayın
- Grubun verilerini kaldırma
- `summarise()` istatistiklerle gruplandırılmış veriler
- `count()` ve `tally()` arasındaki fark
- gruplandırılmış verilere uygulanan `arrange()`
- gruplandırılmış verilere uygulanan `filter()`
- gruplandırılmış verilere uygulanan `mutate()`
- gruplandırılmış verilere uygulanan `select()`
- Alternatif olarak R **tabanı** `aggregate()` komutu

## 13.1 Hazırlık

### Paketleri yükleyin

Bu kod parçası, analizler için gereken paketlerin yüklenmesini gösterir. Bu el kitabında, gerekirse paketi kuran *ve* kullanım için yükleyen **pacman**’dan `p_load()` vurgusunu yapıyoruz. R **tabanı**ndan `library()` ile kurulu paketleri de yükleyebilirsiniz. R paketleri hakkında daha fazla bilgi için [R basics](basics.llms.md) sayfasına bakabilirsiniz.

``` r
pacman::p_load(
  rio,       # verileri içe aktarma
  here,      # dosyaları konumlama
  tidyverse, # veriyi temizleme, işleme ve grafikleştirme (dplyr dahil)
  janitor,   # toplam satır ve süruna ekleme yapma
  appliedepidata) # bu el kitabında kullanılan örnek veriler
```

### Verileri içe aktar

Simüle edilmiş bir Ebola salgınından vakaların veri setini içe aktarıyoruz. Doğrudan `appliedepidata::get_data(name = "linelist_cleaned_rds")` ile yükleyin (ayrıntılar için [El kitabı ve veri indirme](download.llms.md) sayfasına bakın).

``` r
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

“linelist”in ilk 50 satırı:

## 13.2 Gruplandırma

**dplyr**’den `group_by()` fonsiyonu, satırları kendisine belirtilen sütundaki benzersiz değerlere göre gruplandırır. Birden çok sütun belirtilirse, satırlar sütunlar boyunca benzersiz değer kombinasyonlarına göre gruplanır. Her benzersiz değer (veya değer kombinasyonu) bir grup oluşturur. Veri kümesinde veya hesaplamalarda sonraki değişiklikler daha sonra her grup bağlamında gerçekleştirilebilir.

Örneğin, aşağıdaki komut “linelist”i alır ve satırları “outcome” sütunundaki benzersiz değerlere göre gruplayarak çıktıyı yeni bir “ll_by_outcome” veri çerçevesi olarak kaydeder. Gruplandırma sütunu/sütunları, ‘group_by()’ fonksiyonunun parantezlerin içine yerleştirilir.

``` r
ll_by_outcome <- linelist %>% 
  group_by(outcome)
```

**Veri kümesinde algılanabilir bir değişiklik olmadığını unutmayın** `group_by()` çalıştırıldıktan sonra, `mutate()`, `summarise()` veya `arrange()` gibi başka bir **dplyr** fiili “gruplandırılmış” veri çerçevesine *kadar* uygulanır.

Bununla birlikte, veri çerçevesini yazdırarak gruplamaları “görebilirsiniz”. Gruplandırılmış bir veri çerçevesi yazdırdığınızda, bunun yazdırıldığında hangi gruplamaların uygulandığını ve kaç tane olduğunu gösteren bir [`tibble` sınıf nesnesine](https://tibble.tidyverse.org/) dönüştürüldüğünü göreceksiniz - başlık satırının hemen üstüne yazılır.

``` r
# hangi grupların aktif olduğunu görmek için yazdır
ll_by_outcome
```

    # A tibble: 5,888 × 30
    # Groups:   outcome [3]
       case_id generation date_infection date_onset date_hospitalisation
       <chr>        <dbl> <date>         <date>     <date>              
     1 5fe599           4 2014-05-08     2014-05-13 2014-05-15          
     2 8689b7           4 NA             2014-05-13 2014-05-14          
     3 11f8ea           2 NA             2014-05-16 2014-05-18          
     4 b8812a           3 2014-05-04     2014-05-18 2014-05-20          
     5 893f25           3 2014-05-18     2014-05-21 2014-05-22          
     6 be99c8           3 2014-05-03     2014-05-22 2014-05-23          
     7 07e3e8           4 2014-05-22     2014-05-27 2014-05-29          
     8 369449           4 2014-05-28     2014-06-02 2014-06-03          
     9 f393b4           4 NA             2014-06-05 2014-06-06          
    10 1389ca           4 NA             2014-06-05 2014-06-07          
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_outcome <date>, outcome <chr>, gender <chr>,
    #   age <dbl>, age_unit <chr>, age_years <dbl>, age_cat <fct>, age_cat5 <fct>,
    #   hospital <chr>, lon <dbl>, lat <dbl>, infector <chr>, source <chr>,
    #   wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>, chills <chr>,
    #   cough <chr>, aches <chr>, vomit <chr>, temp <dbl>, time_admission <chr>,
    #   bmi <dbl>, days_onset_hosp <dbl>

### Benzersiz gruplar

**Oluşturulan gruplar, gruplandırma sütunlarında her benzersiz değer kombinasyonunu yansıtır.**

Grupları *ve her gruptaki* satır sayısını görmek için gruplanmış verileri ‘tally()’ öğesine iletin. Sadece benzersiz, sayısız grupları görmek için `group_keys()` öğesine geçebilirsiniz.

Aşağıda, “sonuç” gruplandırma sütununda **üç** benzersiz değer olduğunu görün: “Ölüm”, “İyileşme” ve “NA”. `nrow(linelist %>% filter(outcome == "Death"))` ölümler, `nrow(linelist %>% filter(outcome == "Recover"))` iyileşme ve `nrow(linelist %>% filter(is.na(outcome)))` sonucu kaydedilmemiş vaka olduğunu görün.

``` r
linelist %>% 
  group_by(outcome) %>% 
  tally()
```

    # A tibble: 3 × 2
      outcome     n
      <chr>   <int>
    1 Death    2582
    2 Recover  1983
    3 <NA>     1323

Birden fazla sütuna göre gruplandırabilirsiniz. Aşağıda, veri çerçevesi “sonuç” ve “cinsiyet”e göre gruplandırılır ve ardından hesaplanır. “Sonuç” ve “cinsiyet”in her benzersiz kombinasyonunun kendi grubu olarak nasıl kaydedildiğine dikkat edin - her iki sütun için de eksik değerler dahil edilmektedir.

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally()
```

    # A tibble: 9 × 3
    # Groups:   outcome [3]
      outcome gender     n
      <chr>   <chr>  <int>
    1 Death   f       1227
    2 Death   m       1228
    3 Death   <NA>     127
    4 Recover f        953
    5 Recover m        950
    6 Recover <NA>      80
    7 <NA>    f        627
    8 <NA>    m        625
    9 <NA>    <NA>      71

### Yeni sütunlar

Ayrıca, “group_by()” ifadesinin *içinde* yeni bir gruplandırma sütunu da oluşturabilirsiniz. Bu, ‘group_by()’dan önce ’mutate()’ çağrısına eşdeğerdir. Hızlı bir tablolama için bu stil kullanışlı olabilir, ancak kodunuzda daha fazla netlik için bu sütunu kendi `mutate()` adımında oluşturmayı ve ardından `group_by()` ile bağlantı kurmayı düşünün.

``` r
# group_by() komut satırı listesi %>% *içinde* oluşturulan bir ikili sütuna dayalı grup verileri
linelist %>% 
  group_by(
    age_class = ifelse(age >= 18, "adult", "child")) %>% 
  tally(sort = T)
```

    # A tibble: 3 × 2
      age_class     n
      <chr>     <int>
    1 child      3618
    2 adult      2184
    3 <NA>         86

### Gruplandırma sütunlarını ekle/bırak

Varsayılan olarak, zaten gruplanmış veriler üzerinde `group_by()` çalıştırırsanız, eski gruplar kaldırılacak ve yenileri uygulanacaktır. Mevcut gruplara yeni gruplar eklemek istiyorsanız, `.add = TRUE` değişkenini ekleyin.

``` r
# Çıktıya göre gruplama
by_outcome <- linelist %>% 
  group_by(outcome)

# İlave olarak cinsiyet olarak gruplama eklemesi
by_outcome_gender <- by_outcome %>% 
  group_by(gender, .add = TRUE)
```

\*\* Tüm grupları tut\*\*

Bir sınıf faktörü sütununda gruplandırırsanız, şu anda verilerde mevcut olmayan faktör seviyeleri olabilir. Bu sütunda gruplandırırsanız, varsayılan olarak mevcut olmayan seviyeler bırakılır ve grup olarak dahil edilmez. Bunu, tüm seviyelerin gruplar halinde görüneceği şekilde değiştirmek için (verilerde mevcut olmasa bile), `group_by()` komutunuzda `.drop = FALSE` değerini ayarlayın.

## 13.3 Grubu kaldır

Gruplandırılmış veriler, ‘ungroup()’ aracılığıyla özellikle işlenene kadar gruplanmış olarak kalacaktır. Grubu çözmeyi unutursanız, yanlış hesaplamalara yol açabilir! Aşağıda tüm gruplamaların kaldırılmasına ilişkin bir örnek verilmiştir:

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally() %>% 
  ungroup()
```

Ayrıca, sütun adını “ungroup()” içine yerleştirerek yalnızca belirli sütunlar için gruplamayı kaldırabilirsiniz.

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally() %>% 
  ungroup(gender) # cinsiyete göre gruplamayı kaldır, sonuca göre gruplamayı bırak
```

***NOT:*** `count()` fiili saydıktan sonra verilerin grubunu otomatik olarak çözer.

## 13.4 Özetleme

Özet tablolarının “summarise()” ile nasıl oluşturulacağına ilişkin ayrıntılı bir açıklama için \[Tanımlayıcı tablolar\] sayfasının **dplyr** bölümüne bakın. Burada, gruplandırılmış verilere uygulandığında davranışının nasıl değiştiğini kısaca ele alıyoruz.

**dplyr** fonksiyonu`summarise()` (veya `summarize()`) bir veri çerçevesi alır ve onu tanımladığınız özet istatistikleri içeren sütunlarla birlikte *yeni* bir özet veri çerçevesine dönüştürür. Gruplandırılmamış bir veri çerçevesinde, tüm satırlardan özet istatistikler hesaplanacaktır. Gruplandırılmış verilere ‘summarise()’ uygulamak, *her grup için* bu özet istatistikleri üretir.

`summarise()` sözdizimi, **yeni** özet sütun(lar)ının adlarını, bir eşittir işaretini ve ardından aşağıda gösterildiği gibi verilere uygulanacak istatistiksel bir fonksiyon sağlayacak şekildedir. Örneğin, “min()”, “max()”, “median()” veya “sd()”. İstatistiksel fonksiyon içinde, üzerinde çalışılacak sütunu ve ilgili herhangi bir değişkeni listeleyebilir (ör. “na.rm = TRUE”). Mantıksal bir ölçütü karşılayan satırların sayısını saymak için `sum()` kullanabilirsiniz (çift eşittir `==` ile).

Aşağıda, *gruplandırılmış veriler olmadan* uygulanan bir `summarise()` örneği verilmiştir. Döndürülen istatistikler, tüm veri kümesinden üretilir.

``` r
# gruplandırılmamış satır listesindeki özet istatistikler
linelist %>% 
  summarise(
    n_cases  = n(),
    mean_age = mean(age_years, na.rm=T),
    max_age  = max(age_years, na.rm=T),
    min_age  = min(age_years, na.rm=T),
    n_males  = sum(gender == "m", na.rm=T))
```

      n_cases mean_age max_age min_age n_males
    1    5888 16.01831      84       0    2803

Buna karşılık, aşağıda gruplanmış verilere uygulanan aynı “summarise()” ifadesi yer almaktadır. İstatistikler, her bir “sonuç” grubu için hesaplanır. Gruplandırma sütunlarının yeni veri çerçevesine nasıl taşınacağına dikkat edin.

``` r
# gruplandırılmış satır listesindeki özet istatistikler
linelist %>% 
  group_by(outcome) %>% 
  summarise(
    n_cases  = n(),
    mean_age = mean(age_years, na.rm=T),
    max_age  = max(age_years, na.rm=T),
    min_age  = min(age_years, na.rm=T),
    n_males    = sum(gender == "m", na.rm=T))
```

    # A tibble: 3 × 6
      outcome n_cases mean_age max_age min_age n_males
      <chr>     <int>    <dbl>   <dbl>   <dbl>   <int>
    1 Death      2582     15.9      76       0    1228
    2 Recover    1983     16.1      84       0     950
    3 <NA>       1323     16.2      69       0     625

***İPUCU:*** TÖzetleme işlevi hem Birleşik Krallık hem de ABD yazımıyla çalışır - `summarise()` ve `summarize()` aynı fonksiyonu çağırır.

## 13.5 Sayımlar ve seriler

`count()` ve `tally()` benzer işlevsellik sağlar ancak farklıdır. “tally()” ve “count()” arasındaki fark hakkında daha fazla bilgiyi [buradan](https://dplyr.tidyverse.org/reference/tally.html) okuyabilirsiniz.

### `tally()`

“tally()”, “summarise(n = n())” ifadesinin kısaltmasıdır ve verileri *gruplandırmaz*. Bu nedenle, gruplandırılmış çetelelere ulaşmak için bir ‘group_by()’ komutunu izlemesi gerekir. Önce en büyük grupları görmek için `sort = TRUE` ekleyebilirsiniz.

``` r
linelist %>% 
  tally()
```

         n
    1 5888

``` r
linelist %>% 
  group_by(outcome) %>% 
  tally(sort = TRUE)
```

    # A tibble: 3 × 2
      outcome     n
      <chr>   <int>
    1 Death    2582
    2 Recover  1983
    3 <NA>     1323

### `count()`

Buna karşılık, “count()” şunları yapar:

1.  belirtilen sütun(lar)a `group_by()` uygular
2.  “summarise()” uygular ve grup başına satır sayısıyla “n” sütununu döndürür
3.  `ungroup()` uygular

``` r
linelist %>% 
  count(outcome)
```

      outcome    n
    1   Death 2582
    2 Recover 1983
    3    <NA> 1323

Tıpkı ‘group_by()’ ile olduğu gibi, ‘count()’ komutu için de yeni bir sütun oluşturabilirsiniz:

``` r
linelist %>% 
  count(age_class = ifelse(age >= 18, "adult", "child"), sort = T)
```

      age_class    n
    1     child 3618
    2     adult 2184
    3      <NA>   86

`count()`, sayımları daha üst düzeyde toplama (“rolling up”) işleviyle birden çok kez çağrılabilir. Örneğin, her bir cinsiyet için mevcut hastanelerin sayısını özetlemek için aşağıdakileri çalıştırın. Son sütunun adının, netlik için varsayılan “n” yerine değiştirildiğini unutmayın (`name =` ile).

``` r
linelist %>% 
  # benzersiz sonuç-cinsiyet gruplarına göre sayımlar üretmek
  count(gender, hospital) %>% 
  #cinsiyete göre satırları toplayın (3) ve cinsiyete göre hastane sayısını sayın (6)
  count(gender, name = "hospitals per gender" ) 
```

      gender hospitals per gender
    1      f                    6
    2      m                    6
    3   <NA>                    6

### Sayıları ekle

‘count()’ ve ‘summarise()’in aksine, diğer tüm veri çerçevesi sütunlarını korurken grup başına satır sayısıyla yeni bir ’n’ sütunu eklemek için ‘add_count()’ kullanabilirsiniz.

Bu, yeni `n` sütunundaki bir grubun sayım numarasının grubun her satırına yazdırılacağı anlamına gelir. Gösteri amacıyla, bu sütunu ekliyoruz ve daha sonra daha kolay görüntüleme için sütunları yeniden düzenliyoruz. Başka bir örnek için aşağıdaki [grup boyutuna göre filtrele](#group_filter_grp_size) bölümüne bakabilirsiniz.

``` r
linelist %>% 
  as_tibble() %>%                   # daha güzel baskı için tibble'a dönüştürün
  add_count(hospital) %>%           # hastaneye göre sayılarla n sütunu ekle
  select(hospital, n, everything()) # demo amaçlı yeniden düzenlemek
```

    # A tibble: 5,888 × 31
       hospital                       n case_id generation date_infection date_onset
       <chr>                      <int> <chr>        <dbl> <date>         <date>    
     1 Other                        885 5fe599           4 2014-05-08     2014-05-13
     2 Missing                     1469 8689b7           4 NA             2014-05-13
     3 St. Mark's Maternity Hosp…   422 11f8ea           2 NA             2014-05-16
     4 Port Hospital               1762 b8812a           3 2014-05-04     2014-05-18
     5 Military Hospital            896 893f25           3 2014-05-18     2014-05-21
     6 Port Hospital               1762 be99c8           3 2014-05-03     2014-05-22
     7 Missing                     1469 07e3e8           4 2014-05-22     2014-05-27
     8 Missing                     1469 369449           4 2014-05-28     2014-06-02
     9 Missing                     1469 f393b4           4 NA             2014-06-05
    10 Missing                     1469 1389ca           4 NA             2014-06-05
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_hospitalisation <date>, date_outcome <date>,
    #   outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>, age_years <dbl>,
    #   age_cat <fct>, age_cat5 <fct>, lon <dbl>, lat <dbl>, infector <chr>,
    #   source <chr>, wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>,
    #   chills <chr>, cough <chr>, aches <chr>, vomit <chr>, temp <dbl>,
    #   time_admission <chr>, bmi <dbl>, days_onset_hosp <dbl>

### Toplamları ekle

“tally()” veya “count()” kullandıktan sonra toplam *sum* satırlarını veya sütunlarını kolayca eklemek için [Tanımlayıcı tablolar](tables_descriptive.llms.md#tbl_janitor) sayfasının **janitor** bölümüne bakın. Bu paket, toplamları eklemek ve yüzdeleri göstermek için dönüştürmek için ‘adorn_totals()’ ve ‘adorn_percentages()’ gibi fonksiyonlar sunar. Aşağıda kısa bir örnek verilmiştir:

``` r
linelist %>%                                  # vaka satır listesi 
  tabyl(age_cat, gender) %>%                  # iki sütunun çapraz tablo sayımları
  adorn_totals(where = "row") %>%             # toplam satır ekle
  adorn_percentages(denominator = "col") %>%  # sütun paydası ile oranlara dönüştürme
  adorn_pct_formatting() %>%                  # oranları yüzdelere çevir
  adorn_ns(position = "front") %>%            # "count (percent)" olarak göster
  adorn_title(                                # başlıkları ayarla
    row_name = "Age Category",
    col_name = "Gender")
```

                          Gender                            
     Age Category              f              m          NA_
              0-4   640  (22.8%)   416  (14.8%)  39  (14.0%)
              5-9   641  (22.8%)   412  (14.7%)  42  (15.1%)
            10-14   518  (18.5%)   383  (13.7%)  40  (14.4%)
            15-19   359  (12.8%)   364  (13.0%)  20   (7.2%)
            20-29   468  (16.7%)   575  (20.5%)  30  (10.8%)
            30-49   179   (6.4%)   557  (19.9%)  18   (6.5%)
            50-69     2   (0.1%)    91   (3.2%)   2   (0.7%)
              70+     0   (0.0%)     5   (0.2%)   1   (0.4%)
             <NA>     0   (0.0%)     0   (0.0%)  86  (30.9%)
            Total 2,807 (100.0%) 2,803 (100.0%) 278 (100.0%)

*Toplamlar* dışında özet istatistikleri içeren daha karmaşık ‘sums’ satırları eklemek için [Tanımlayıcı Tablolar sayfasının bu bölümüne](tables_descriptive.llms.md#tbl_dplyr_totals) bakabilirsiniz.

## 13.6 Tarihe göre gruplama

Verileri tarihe göre gruplarken, ilgilenilen tarih birimi için bir sütuna sahip olmalısınız (veya oluşturmalısınız) (örneğin “gün”, “epiweek”, “ay”, vb.) **lubridate**’den ‘floor_date()’ kullanarak bu sütunu oluşturabilirsiniz. \[Tarihlerle çalışma\] sayfasının [Epidemiyolojik haftalar bölümünde](dates.llms.md#dates_epi_wks) açıklandığı gibi. Bu sütuna sahip olduğunuzda, satırları bu benzersiz tarih değerlerine göre gruplandırmak ve toplam sayıları elde etmek için **dplyr**’den `count()` kullanabilirsiniz.

Tarih durumları için ortak bir ek adım, dizide verilerde mevcut olmayan tüm tarihleri ​​“doldurmaktır”. **tidyr**’den ‘complete()’ kullanın, böylece aralık içindeki *tüm olası tarih birimleri* dahil olmak üzere toplu tarih serisi tamamlanır. Bu adım olmadan, hiçbir vakanın bildirilmediği bir hafta verilerinizde görünmeyebilir!

‘complete()’ içinde, tarih sütununuzu minimumdan maksimuma ‘seq.Date()’ tarihlerinin bir *dizisi* olarak *yeniden tanımlarsınız*. Böylece tarihler genişletilir. Varsayılan olarak, herhangi bir yeni “genişletilmiş” satırdaki vaka sayısı değerleri “NA” olacaktır. Adlandırılmış bir liste bekleyen ‘complete()’ öğesinin ‘fill =’ değişkenini kullanarak bunları 0’a ayarlayabilirsiniz (sayımlar sütununuz ‘n’ olarak adlandırılmışsa, ‘fill = list(n = 0)’ sağlayın. Ayrıntılar için ?complete’ komutuna ve örnek için [Tarihlerle çalışma](dates.llms.md#dates_epi_wks) sayfasına bakabilirsiniz.

### Günlere göre satır listesi vakaları

Burada, “complete()” kullanılmadan ​günlere göre gruplandırma örneği verilmiştir. İlk satırların hiçbir durum olmadan tarihleri atladığını unutmayın.

``` r
daily_counts <- linelist %>% 
  drop_na(date_onset) %>%        # date_onset eksik olanları kaldırın
  count(date_onset)              # benzersiz tarih başına satır sayısını say
```

Aşağıda, aralıktaki her günün temsil edilmesini sağlamak için `complete()` komutunu ekliyoruz.

``` r
daily_counts <- linelist %>% 
  drop_na(date_onset) %>%                 # date_onset eksik vakayı kaldır
  count(date_onset) %>%                   # benzersiz tarih başına satır sayısını say
  complete(                               # hiçbir vaka olmasa bile tüm günlerin görünmesini sağlayın
    date_onset = seq.Date(                # tarih sütununu günlük tarih dizisi olarak yeniden tanımlayın
      from = min(date_onset, na.rm=T), 
      to = max(date_onset, na.rm=T),
      by = "day"),
    fill = list(n = 0))                   # yeni doldurulmuş satırları n sütununda 0 gösterecek şekilde ayarla (varsayılan olarak NA değil) 
```

### Haftalara bölünmüş satır listesi vakaları

Aynı prensip haftalarca uygulanabilir. İlk önce, `unit = "week"` ile `floor_date()` kullanarak vakanın haftası olan yeni bir sütun oluşturun. Ardından, haftalık vaka sayılarına ulaşmak için yukarıdaki gibi `count()` kullanın. Hiçbir vaka içermeseler bile tüm haftaların temsil edildiğinden emin olmak için “complete()” ile bitirin.

``` r
# Haftalık vaka sayımlarının veri setini yapın
weekly_counts <- linelist %>% 
  drop_na(date_onset) %>%                 # date_onset eksik vakaları kaldırın
  mutate(week = lubridate::floor_date(date_onset, unit = "week")) %>%  # başlangıç haftasının yeni sütunu
  count(week) %>%                         # verileri haftaya göre gruplandır ve grup başına satırları say
  complete(                               # hiçbir vaka olmasa bile tüm günlerin görünmesini sağlayın
    week = seq.Date(                      # tarih sütununu günlük tarih dizisi olarak yeniden tanımlayın
      from = min(week, na.rm=T), 
      to = max(week, na.rm=T),
      by = "week"),
    fill = list(n = 0))                   # yeni doldurulmuş satırları n sütununda 0 gösterecek şekilde ayarla (varsayılan olarak NA değil)
```

Ortaya çıkan veri çerçevesinin ilk 50 satırı:

### Aylara ayrılmış satır listesi vakaları

Vakaları aylara toplamak için, yine **lubridate** paketinden ‘floor_date()’ kullanın, ancak ‘unit= “months”’ bağımsız değişkeni ile. Bu, her tarihi ayın 1’ine yuvarlar. Çıktı, Date sınıfı olacaktır. `complete()` adımında `by = "month"` ifadesini de kullandığımızı unutmayın.

``` r
# Aylık vaka sayımlarının veri setini yapın
monthly_counts <- linelist %>% 
  drop_na(date_onset) %>% 
  mutate(month = lubridate::floor_date(date_onset, unit = "months")) %>%  # yeni sütun, başlangıcın 1. ayı
  count(month) %>%                          # vakaları aya göre saymak
  complete(
    month = seq.Date(
      min(month, na.rm=T),     # hiçbir vakanın bildirilmediği tüm ayları dahil et
      max(month, na.rm=T),
      by="month"),
    fill = list(n = 0))
```

### Haftalara göre günlük sayım

Günlük sayıları haftalık sayımlarda toplamak için yukarıdaki gibi `floor_date()` kullanın. Ancak, “count()” yerine “group_by()” ve “summarize()” kullanın, çünkü yalnızca haftalık satır sayısını saymak yerine günlük vaka sayılarını “sum()” yapmanız gerekir.

#### Aylara göre günlük sayımlar

Günlük sayıları ay sayılarına toplamak için, yukarıdaki gibi “unit =”month”” ile “floor_date()” kullanın. Ancak, ‘count()’ yerine ‘group_by()’ ve ‘summarize()’ kullanın çünkü sadece aylık satır sayısını saymak yerine günlük vaka sayılarını ‘sum()’ yapmanız gerekir.

## 13.7 Gruplandırılmış verileri düzenleme

Bir veri çerçevesindeki satırları sıralamak için **dplyr** fiilinin “arrange()” kullanılması, “.by_group =TRUE” bağımsız değişkenini ayarlamadığınız sürece, veriler gruplandığında aynı şekilde davranır. Bu durumda, satırlar önce gruplandırma sütunlarına ve ardından ‘arrange()’ için belirttiğiniz diğer sütunlara göre sıralanır.

## 13.8 Gruplandırılmış verilere filtre uygula

### `filter()`

Veri çerçevesini değerlendiren işlevlerle birlikte uygulandığında (‘max()’, ‘min()’, ‘mean()’ gibi), bu fonksiyonlar artık gruplara uygulanacaktır. Örneğin, hastaların medyan yaşın üzerinde olduğu satırları filtrelemek ve tutmak istiyorsanız, bu artık her grup için geçerli olacaktır - satırları *grubun* medyan yaşının üzerinde tutmak için filtreleyin.

### Grup başına satırları dilimleyin

Verilerdeki [satırları konumlarına göre filtreleyen](https://dplyr.tidyverse.org/reference/slice.html) **dplyr** `slice()` fonksiyonu da grup başına uygulanabilir. İstenilen “dilimi” elde etmek için her grup içindeki verileri sıralamayı unutmayın.

Örneğin, her hastaneden yalnızca en son 5 başvuruyu almak için:

1.  Satır listesini “hastane” sütununa göre gruplandırın
2.  Kayıtları en geçten en erken ’hastaneye yatış tarihi’ne *her hastane grubu içinde* düzenleyin
3.  Her hastaneden ilk 5 sırayı almak için dilimleyin

``` r
linelist %>%
  group_by(hospital) %>%
  arrange(hospital, date_hospitalisation) %>%
  slice_head(n = 5) %>% 
  arrange(hospital) %>%                            # for display
  select(case_id, hospital, date_hospitalisation)  # görüntülemek için
```

    # A tibble: 30 × 3
    # Groups:   hospital [6]
       case_id hospital          date_hospitalisation
       <chr>   <chr>             <date>              
     1 20b688  Central Hospital  2014-05-06          
     2 d58402  Central Hospital  2014-05-10          
     3 b8f2fd  Central Hospital  2014-05-13          
     4 acf422  Central Hospital  2014-05-28          
     5 275cc7  Central Hospital  2014-05-28          
     6 d1fafd  Military Hospital 2014-04-17          
     7 974bc1  Military Hospital 2014-05-13          
     8 6a9004  Military Hospital 2014-05-13          
     9 09e386  Military Hospital 2014-05-14          
    10 865581  Military Hospital 2014-05-15          
    # ℹ 20 more rows

`slice_head()` - üstten n satır seçer `slice_tail()` - sondan n satır seçer `slice_sample()` - n satırı rastgele seçer `slice_min()` - `order_by =` sütununda en yüksek değerlere sahip n satırı seçer, bağları korumak için `with_ties = TRUE` kullanın ‘slice_max()’ - ‘order_by =’ sütununda en düşük değerlere sahip n satırı seçer, bağları korumak için ’with_ties = TRUE’yu kullanın

`slice()` hakkında daha fazla örnek ve ayrıntı için \[Tekilleştirme\] sayfasına bakabilirsiniz.

### Grup boyutuna göre filtreleyin

‘add_count()’ fonksiyonu, o satırın grubundaki satır sayısını veren orijinal verilere bir ‘n’ sütunu ekler.

Aşağıda gösterildiği gibi, “hastane” sütununa “add_count()” uygulanır, bu nedenle yeni “n” sütunundaki değerler, o satırın hastane grubundaki satır sayısını yansıtır. ‘n’ sütunundaki değerlerin nasıl tekrarlandığına dikkat edin. Aşağıdaki örnekte, ‘n’ sütun adı ‘add_count()’ içindeki ‘name =’ kullanılarak değiştirilebilir. Gösteri amacıyla sütunları `select()` ile yeniden düzenliyoruz.

``` r
linelist %>% 
  as_tibble() %>% 
  add_count(hospital) %>%          # "bu sıra ile aynı hastaneye kabul edilen sıra sayısı" ekle
  select(hospital, n, everything())
```

    # A tibble: 5,888 × 31
       hospital                       n case_id generation date_infection date_onset
       <chr>                      <int> <chr>        <dbl> <date>         <date>    
     1 Other                        885 5fe599           4 2014-05-08     2014-05-13
     2 Missing                     1469 8689b7           4 NA             2014-05-13
     3 St. Mark's Maternity Hosp…   422 11f8ea           2 NA             2014-05-16
     4 Port Hospital               1762 b8812a           3 2014-05-04     2014-05-18
     5 Military Hospital            896 893f25           3 2014-05-18     2014-05-21
     6 Port Hospital               1762 be99c8           3 2014-05-03     2014-05-22
     7 Missing                     1469 07e3e8           4 2014-05-22     2014-05-27
     8 Missing                     1469 369449           4 2014-05-28     2014-06-02
     9 Missing                     1469 f393b4           4 NA             2014-06-05
    10 Missing                     1469 1389ca           4 NA             2014-06-05
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_hospitalisation <date>, date_outcome <date>,
    #   outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>, age_years <dbl>,
    #   age_cat <fct>, age_cat5 <fct>, lon <dbl>, lat <dbl>, infector <chr>,
    #   source <chr>, wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>,
    #   chills <chr>, cough <chr>, aches <chr>, vomit <chr>, temp <dbl>,
    #   time_admission <chr>, bmi <dbl>, days_onset_hosp <dbl>

Ardından “küçük” bir hastanede, örneğin 500’den az hastayı kabul eden bir hastanede yatan vaka sıralarını filtrelemek kolaylaşıyor:

``` r
linelist %>% 
  add_count(hospital) %>% 
  filter(n < 500)
```

## 13.9 Gruplandırılmış verileri dönüştürün

Tüm sütunları ve satırları (özetleme değil) korumak ve *grup istatistiklerini* içeren yeni bir sütun eklemek için, ‘summarise()’ yerine ‘group_by()’dan sonra ’mutate()’ kullanın.

Bu, orijinal veri kümesinde diğer tüm sütunların mevcut olduğu grup istatistiklerini istiyorsanız yararlıdır - ör. bir satırı kendi grubuyla karşılaştıran hesaplamalar için.

Örneğin, aşağıdaki kod, bir satırın kabul gecikmesi ile hastaneleri için medyan gecikme arasındaki farkı hesaplar. Adımlar:

1.  Verileri hastaneye göre gruplandırın
2.  *o satırın* hastanede ortalama gecikmesini içeren yeni bir sütun oluşturmak için “days_onset_hosp” (hastaneye yatış gecikmesi) sütununu kullanın
3.  İki sütun arasındaki farkı hesaplayın

Gösteri amacıyla yalnızca belirli sütunları “select()” olarak seçiyoruz.

``` r
linelist %>% 
  # hastaneye göre grup verileri (henüz satır listesinde değişiklik yok)
  group_by(hospital) %>% 
  
  # Yeni sütunlar
  mutate(
    # hastaneye kabule kadar geçen ortalama gün sayısı (1 ondalık sayıya yuvarlanır)
    group_delay_admit = round(mean(days_onset_hosp, na.rm=T), 1),
    
    # sıra gecikmesi ile hastanelerindeki ortalama gecikme arasındaki fark (1 ondalık basamağa yuvarlanır)
    diff_to_group     = round(days_onset_hosp - group_delay_admit, 1)) %>%
  
  # yalnızca belirli satırları seçin - gösterim/görüntüleme amaçlı
  select(case_id, hospital, days_onset_hosp, group_delay_admit, diff_to_group)
```

    # A tibble: 5,888 × 5
    # Groups:   hospital [6]
       case_id hospital              days_onset_hosp group_delay_admit diff_to_group
       <chr>   <chr>                           <dbl>             <dbl>         <dbl>
     1 5fe599  Other                               2               2             0  
     2 8689b7  Missing                             1               2.1          -1.1
     3 11f8ea  St. Mark's Maternity…               2               2.1          -0.1
     4 b8812a  Port Hospital                       2               2.1          -0.1
     5 893f25  Military Hospital                   1               2.1          -1.1
     6 be99c8  Port Hospital                       1               2.1          -1.1
     7 07e3e8  Missing                             2               2.1          -0.1
     8 369449  Missing                             1               2.1          -1.1
     9 f393b4  Missing                             1               2.1          -1.1
    10 1389ca  Missing                             2               2.1          -0.1
    # ℹ 5,878 more rows

## 13.10 Gruplandırılmış verileri seçin

‘select()’ fiili gruplandırılmış veriler üzerinde çalışır, ancak gruplandırma sütunları her zaman dahil edilir (‘select()’ içinde belirtilmemiş olsa bile). Bu gruplama sütunlarını istemiyorsanız, önce `ungroup()` kullanın.

## 13.11 Kaynaklar

Daha fazla bilgi için bazı yararlı kaynaklar şunlardır:

Gruplandırılmış veriler üzerinde herhangi bir özet fonksiyonu gerçekleştirebilirsiniz; [RStudio veri dönüştürme bilgi sayfasına](https://github.com/rstudio/cheatsheets/blob/master/data-transformation.pdf) bakabilirsiniz.

[**dplyr**](https://datacarpentry.org/R-genomics/04-dplyr.html) adresindeki Veri Marangozluğu sayfası [group_by()](https://dplyr.tidyverse.org/reference/group_by.html) ve [grouping](https://dplyr.tidyverse.org/articles/grouping.html) üzerindeki **tidyverse** referans sayfaları.

Bu sayfa [Veri manipülasyonu](https://itsalocke.com/files/DataManipulationinR.pdf)

[dplyr’deki koşullarla özetleyin](https://stackoverflow.com/questions/23528862/summarize-with-conditions-in-dplyr)
