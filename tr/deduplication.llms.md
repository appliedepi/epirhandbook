# 15  Tekilleştirme

[![](../../images/deduplication.png)](../../images/deduplication.png)

Bu sayfa aşağıdaki veri tekilleştirme tekniklerini kapsamaktadır:

1.  Yinelenen satırları belirleme ve kaldırma
2.  Her satır grubundan yalnızca belirli satırları (ör. min veya maks) tutmak için satırları “dilimleme”
3.  “Toplama” veya birden çok satırdaki değerleri tek satırda birleştirme

## 15.1 Hazırlık

### Paketleri yükleme

Bu kod parçası, analizler için gereken paketlerin yüklenmesini göstermektedir. Bu el kitabında, gerekirse paketi kuran *ve* onu kullanım için yükleyen pacman’ın `p_load()` işlevlerini vurgulamaktayız. Ayrıca, **base** R’den `library()` fonksiyonu ile kurulu paketleri yükleyebilirsiniz. R paketleri hakkında daha fazla bilgi için [R’ın Temelleri](basics.llms.md) sayfasına bakabilirsiniz.

``` r
pacman::p_load(
  tidyverse,   # tekilleştirme, gruplama ve dilimleme işlevleri
  janitor,     # kopyaları gözden geçirme işlevi
  stringr)      # dizi aramaları için "toplama" değerleri de kullanılabilir
```

### Verileri içeri aktarma

Aşağıda, R kodu ile oluşturulmuş örnek bir veri seti kullanacağız.

Veriler, temaslı kişiler ve vakalar dahil olmak üzere COVID-19 telefon görüşmelerinin kayıtlarıdır. Sütunlar, kayıt kimliği - `recordID` (bilgisayar tarafından oluşturulan), kişi kimliği - `personID`, ad - `name`, karşılaşma tarihi - `date`, karşılaşma zamanı - `time`, karşılaşmanın amacını - `purpose` (vaka veya temaslı olarak görüşme için) ve semptomları `symptoms_ever` (kayıt zamanında kişinin *hiç* semptom bildirip bildirmediğini) içerir.

`obs` veri kümesini oluşturmak için gereken kod:

``` r
obs <- data.frame(
  recordID  = c(1,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18),
  personID  = c(1,1,2,2,3,2,4,5,6,7,2,1,3,3,4,5,5,7,8),
  name      = c("adam", "adam", "amrish", "amrish", "mariah", "amrish", "nikhil", "brian", "smita", "raquel", "amrish",
                "adam", "mariah", "mariah", "nikhil", "brian", "brian", "raquel", "natalie"),
  date      = c("1/1/2020", "1/1/2020", "2/1/2020", "2/1/2020", "5/1/2020", "5/1/2020", "5/1/2020", "5/1/2020", "5/1/2020","5/1/2020", "2/1/2020",
                "5/1/2020", "6/1/2020", "6/1/2020", "6/1/2020", "6/1/2020", "7/1/2020", "7/1/2020", "7/1/2020"),
  time      = c("09:00", "09:00", "14:20", "14:20", "12:00", "16:10", "13:01", "15:20", "14:20", "12:30", "10:24",
                "09:40", "07:25", "08:32", "15:36", "15:31", "07:59", "11:13", "17:12"),
  encounter = c(1,1,1,1,1,3,1,1,1,1,2,
                2,2,3,2,2,3,2,1),
  purpose   = c("contact", "contact", "contact", "contact", "case", "case", "contact", "contact", "contact", "contact", "contact",
                "case", "contact", "contact", "contact", "contact", "case", "contact", "case"),
  symptoms_ever = c(NA, NA, "No", "No", "No", "Yes", "Yes", "No", "Yes", NA, "Yes",
                    "No", "No", "No", "Yes", "Yes", "No","No", "No")) %>% 
  mutate(date = as.Date(date, format = "%d/%m/%Y"))
```

#### Veri Çerçevesi

Her bir kişi için karşılaşmaları gözden geçirmek için üst kısımdaki filtre kutularını kullanabilirsiniz.

Verileri gözden geçirirken dikkat etmeniz gereken birkaç nokta:

- İlk iki kayıt, yineleyen kayıt kimliği - `recordID` de dahil olmak üzere %100 birbirinin tam kopyalarıdır (bir bilgisayar arızası olmalı!)
- İkinci iki satır, kayıt kimliği - `recordID` dışındaki tüm sütunlarda birbirinin kopyalarıdır.
- Birkaç kişi, çeşitli tarih ve saatlerde ve temaslılar ve/veya vakalar olarak birden fazla telefon görüşmesi yaptı.
- Her vizitte, kişiye **daha öncesinde** semptomları olup olmadığı soruldu ve bu bilgilerin bir kısmı eksik.

Ve işte **janitor** paketinden `tabyl()` fonksiyonu kullanılarak insanların ve karşılaşmalarının amaçlarının kısa bir özeti:

``` r
obs %>% 
  tabyl(name, purpose)
```

        name case contact
        adam    1       2
      amrish    1       3
       brian    1       2
      mariah    1       2
     natalie    1       0
      nikhil    0       2
      raquel    0       2
       smita    0       1

## 15.2 Tekilleştirme

Bu bölüm, bir veri çerçevesindeki yinelenen satırların nasıl gözden geçirileceğini ve kaldırılacağını açıklamakta ve bir vektörde yinelenen öğelerin nasıl ele alınacağını göstermektedir.

### Yinelenen satırları inceleme

Yinelenen satırları hızlı bir şekilde gözden geçirmek için **janitor** paketinden `get_dupes()` öğesini kullanabilirsiniz. *Varsayılan olarak*, yinelemeler değerlendirilirken tüm sütunlar dikkate alınır - fonksiyon tarafından döndürülen satırlar, **bütün** sütunlardaki değerler dikkate alındığında %100 yinelemedir.

`obs` veri çerçevesinde, ilk iki satır *%100 kopyadır* - her sütunda aynı değere sahiptirler (*benzersiz olması gereken* kayıt kimliği - `recordID` sütunu dahil - bir bilgisayar arızası olmalı). Döndürülen veri çerçevesi, sağ tarafta otomatik olarak yeni bir `dupe_count` sütunu içerir ve bu yinelenen değerler kombinasyonuna sahip satır sayısını gösterir.

``` r
# Tüm sütunlarda %100 kopyalar
obs %>% 
  janitor::get_dupes()
```

Orijinal veriyi incelemek için [linke](#dedup_data) tıklayınız.

Ancak kayıt kimliğini- `recordID` yok saymayı seçersek 3. ve 4. satırlar da birbirinin kopyasıdır. Yani, `recordID` *dışındaki* tüm sütunlarda aynı değerlere sahiptirler. Bir `-` eksi sembolü kullanarak fonksiyonda yok sayılacak belirli sütunları belirtebilirsiniz.

``` r
# Sütun kayıt kimliği/recordID dikkate alınmadığında yinelenir
obs %>% 
  janitor::get_dupes(-recordID)         # if multiple columns, wrap them in c()
```

Ayrıca dikkate alınacak sütunları pozitif olarak belirleyebilirsiniz. Aşağıda, yalnızca ad- `name` ve amaç - `purpose` sütunlarında aynı değerlere sahip satırlar döndürülür. “amrish”in, üç “temas” karşılaşmasını yansıtmak için nasıl `dupe_count`’un 3’e eşit olduğuna dikkat edin.

**Daha fazla satır görmek için sola kaydırın.**

``` r
# YALNIZCA ad ve amaç sütunlarına dayalı olarak kopyalar
obs %>% 
  janitor::get_dupes(name, purpose)
```

Orijinal veriyi incelemek için [linke](#dedup_data) tıklayınız.

Daha fazla ayrıntı için `?get_dupes` fonksiyonunu kullanabilir veya bu [çevrimiçi referansa](https://cran.r-project.org/web/packages/janitor/vignettes/janitor.html#explore-records-with-duplicated-values-for-specific-combinations-of-variables-with-get_dupes) bakabilirsiniz.

### Yalnızca benzersiz satırları tutma

Bir veri çerçevesinin yalnızca benzersiz satırlarını tutmak için **dplyr** paketinden `distinct()` fonksiyonunu kullanabilirsiniz ([Veri ve temel işlevleri temizleme](cleaning.llms.md) sayfasında gösterildiği gibi). Yinelenen satırlar, bu tür satırlardan yalnızca ilki tutulacak şekilde kaldırılır. Varsayılan olarak, “ilk” en yüksek satır sayısı - `rownumber` anlamına gelir (yukarıdan aşağıya sırasında). Yalnızca benzersiz satırlar kalır.

Aşağıdaki örnekte, kayıt kimliği - `recordID` sütununun dikkate alınmaması için `distinct()` fonksiyonunu çalıştırıyoruz - bu nedenle *iki yinelenen satır* kaldırılmaktadır. İlk satır (“adam” için) %100 kopyalandı ve kaldırıldı. Ayrıca 3. satır (“amrish” için) `recordID` (değerlendirilmemiştir) *dışındaki* her sütunda bir kopyaydı ve bu nedenle de kaldırıldı. `obs` veri kümesinin n’i `nrow(obs)-2`dir, `nrow(obs)` satırı değil.

*Tüm veri çerçevesini görmek için sola kaydırın.*

``` r
# veri zincirine eklendi (ör. veri temizleme)
obs %>% 
  distinct(across(-recordID), # veri çerçevesini yalnızca benzersiz satırlara indirger (herhangi bir kopyadan ilkini tutar)
           .keep_all = TRUE) 

# eğer veri zincirinin dışındaysa, verileri ilk argüman olarak dahil et 
# distinct(obs)
```

***UYARI:*** Gruplandırılmış verilerde `distinct()` kullanılıyorsa, fonksiyon her gruba uygulanacaktır.

**Belirli sütunlara dayalı olarak tekilleştirme**

Ayrıca tekilleştirme için temel olacak sütunları da belirtebilirsiniz. Bu şekilde, tekilleştirme yalnızca belirtilen sütunlar içinde yinelenen satırlar için geçerlidir. `.keep_all = TRUE`, olarak ayarlamadığınız sürece, belirtilmeyen tüm sütunlar kaldırılacaktır.

Aşağıdaki örnekte, tekilleştirme yalnızca ad - `name` ve amaç - `purpose` sütunları için aynı değerlere sahip satırlar için geçerlidir. Böylece, “brian”ın 3 yerine sadece 2 satırı vardır - *ilk* “temas” karşılaşması ve tek “vaka” karşılaşması. Brian’ın her bir amaç için *en son* karşılaşmasını koruyacak şekilde ayarlamak için, Gruplar içinde Dilimleme sekmesine bakın.

*Tüm veri çerçevesini görmek için sola kaydırın.*

``` r
# veri zincirine eklendi (ör. veri temizleme)
obs %>% 
  distinct(name, purpose, .keep_all = TRUE) %>%  # satırları ada ve amaca göre benzersiz tut ve tüm sütunları koru
  arrange(name)                                  # daha kolay görüntüleme için düzenle
```

Orijinal veriyi incelemek için [linke](#dedup_data) tıklayınız.

### Bir vektörde yinelenen öğeler

**base** R’dan `duplicated()` fonksiyonu, bir vektörü (sütun) değerlendirecek ve aynı uzunlukta (DOĞRU/YANLIŞ) bir mantıksal vektöre döndürecektir. Bir değer ilk göründüğünde, YANLIŞ’a (yinelenen değil) döndürür ve bu değerin sonraki görüntülerinde DOĞRU’ya döndürür. `NA`’nın diğer herhangi bir değerle nasıl aynı şekilde ele alındığına dikkat edin.

``` r
x <- c(1, 1, 2, NA, NA, 4, 5, 4, 4, 1, 2)
duplicated(x)
```

     [1] FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE

Yalnızca yinelenen öğeleri döndürmek için, orijinal vektörün alt kümesini oluşturmak için köşeli parantezleri kullanabilirsiniz:

``` r
x[duplicated(x)]
```

    [1]  1 NA  4  4  1  2

Yalnızca benzersiz öğeleri döndürmek için, **base** R’dan `unique()` kullanın. `NA`’ları sonuçtan çıkarmak için na.omit() öğesini `unique()` içine yerleştirin.

``` r
unique(x)           # alternatif olarak, x[!duplicated(x)]kullanın
```

    [1]  1  2 NA  4  5

``` r
unique(na.omit(x))  # NA’ları kaldırın
```

    [1] 1 2 4 5

### **base** R’ı kullanma

**Yinelenen satırları döndürmek için**

**base** R’da, `duplicated(df)` komutuyla `df` veri çerçevesinde hangi satırların %100 kopya olduğunu da görebilirsiniz (satırların mantıksal vektörünü döndürür).

Bu nedenle, `df[duplicated(df),]` ile *yineleyen* satırları görmek için veri çerçevesindeki `[ ]` temel alt kümesini de kullanabilirsiniz (virgülü unutmayın, bu tüm sütunları görmek istediğiniz anlamına gelir!).

**Benzersiz satırları döndürmek için**

Yukarıdaki notlara bakın. *Benzersiz* satırları görmek için `duplicated()` işlevinin önünde mantıksal olumsuzlayıcıyı/logical negator `!v eklersiniz:`df\[!duplicated(df),\]\`

**Yalnızca belirli sütunların kopyası olan satırları döndürmek için**

*`duplicated()` parantez içindeki* `df`’yi alt kümeye alın, böylece bu işlev df’nin yalnızca belirli sütunlarında çalışacaktır.

Sütunları belirtmek için, virgülden sonra sütun numaralarını veya adlarını girin (tüm bunların `duplicated()` fonksiyonu *içinde* olduğunu unutmayın).

`duplicated()` fonksiyonundan sonra da virgülü `,` *dışarıda* tuttuğunuzdan emin olun!

Örneğin, kopyalar için yalnızca 2 ila 5 arasındaki sütunları değerlendirmek için: `df[!duplicated(df[, 2:5]),]`  
Kopyalar için yalnızca `name` ve `purpose` sütununu değerlendirmek için: `df[!duplicated(df[, c("name", "purpose)]),]`

## 15.3 Dilimleme

Satır numarasına/konumuna göre satırlara filtre uygulamak için bir veri çerçevesini “dilimlemek”. Bu, özellikle işlevsel grup başına (örneğin, “kişi” başına) birden çok satırınız varsa ve bunlardan yalnızca birini veya birkaçını tutmak istiyorsanız yararlı olur.

Temel `slice()` işlevi sayıları kabul eder ve bu konumlardaki satırları döndürür. Sağlanan sayılar pozitifse, yalnızca döndürülür. Negatifse, bu satırlar *döndürülmez*. Sayıların tümü pozitif veya tümü negatif olmalıdır.

``` r
obs %>% slice(4)  # 4. satırı döndür
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        3        2 amrish 2020-01-02 14:20         1 contact            No

``` r
obs %>% slice(c(2,4))  # 2. ve 4. satırları döndür
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        1        1   adam 2020-01-01 09:00         1 contact          <NA>
    2        3        2 amrish 2020-01-02 14:20         1 contact            No

``` r
#obs %>% slice(c(2:4))  # 2'den 4'e kadar olan satırları döndür
```

Orijinal veriyi incelemek için [linke](#dedup_data) tıklayınız.

Birkaç varyasyon mevcuttur: Bunlara bir sütun ve döndürülecek birkaç satır verilmelidir ( n =’ye).

- `slice_min()` ve `slice_max()` yalnızca belirtilen sütunun minimum veya maksimum değer(ler)ine sahip satır(lar)ı tutar. Bu aynı zamanda sıralı faktörlerin “min” ve “maks” değerlerini döndürmek için de işe yarar.
- `slice_head()` ve `slice_tail()` - sadece *ilk* veya *son* satır(lar)ı tutar.
- `slice_sample()` - satırların yalnızca rastgele bir örneğini tutar.

``` r
obs %>% slice_max(encounter, n = 1)  # en büyük karşılaşma numarasına sahip satırları döndür
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        5        2 amrish 2020-01-05 16:10         3    case           Yes
    2       13        3 mariah 2020-01-06 08:32         3 contact            No
    3       16        5  brian 2020-01-07 07:59         3    case            No

Saklanacak satırların sayısını veya oranını belirtmek için `n =` veya `prop =` argümanlarını kullanın. İşlev bir boru zincirinde kullanılmıyorsa, önce veri bağımsız değişkenini sağlayın (ör. `slice(data, n = 2)`). Daha fazla bilgi için `?slice` bölümüne bakın.

Diğer argümanlar:

`.order_by =` `slice_min()` ve `slice_max()` içinde kullanılır ve bu, dilimlemeden önce sıralanması gereken bir sütundur. `with_ties =` Varsayılan olarak DOĞRU, yani bağlar korunur. `.preserve =` Varsayılan olarak YANLIŞ. DOĞRU ise, dilimlemeden sonra gruplama yapısı yeniden hesaplanır.  
`weight_by =` Ağırlıklandırmaya göre isteğe bağlı, sayısal sütun (daha büyük sayının örneklenmesi daha olasıdır). Ayrıca `replace =` Örneklemenin değiştirilerek/değiştirilmeden yapılıp yapılmadığı için.

***İPUCU:*** `slice_max()` ve `slice_min()` kullanırken, n =’yi belirttiğinizden/yazdığınızdan emin olun (ör. `n = 2`, sadece `2` değil). Aksi takdirde bir hata alabilirsiniz. `Error:` … `is not empty.`

***NOT:*** yerini `slice` işlevlerine bırakmış olan [`top_n()`](https://dplyr.tidyverse.org/reference/top_n.html) fonksiyonuyla karşılaşabilirsiniz.

### Gruplarla dilimleme

`slice_*()` fonksiyonları, gruplanmış bir veri çerçevesine uygulandığında çok yararlı olabilir, çünkü dilim işlemi her grup üzerinde ayrı ayrı gerçekleştirilir. Her gruptan bir dilim almak üzere verileri gruplamak için `group_by()` **fonksiyonunu** `slice()` ile birlikte kullanın.

Bu, kişi başına birden fazla satırınız varsa ancak bunlardan yalnızca birini tutmak istiyorsanız, tekilleştirme için yararlıdır. Önce `group_by()` fonksiyonunu kişi başına aynı olan anahtar sütunlarla kullanırsınız ve ardından gruplanmış satırlar arasında farklılık gösterecek bir sütun üzerinde bir `slice` fonksiyonunu kullanırsınız.

Aşağıdaki örnekte, *kişi başına* yalnızca *en son* karşılaşmayı tutmak için satırları ada - `name` göre grupladık ve ardından tarih - `date` sütununda `n = 1` ile `slice_max()`’ı kullandık. Haberin olsun! Tarihlere `slice_max()` gibi bir işlevi uygulamak için tarih sütunu Date sınıfı olmalıdır.

Varsayılan olarak, “bağlar” (ör. bu senaryoda aynı tarih) korunur ve yine de bazı insanlar için (ör. adam) birden çok satır alırız. Bunu önlemek için `with_ties = FALSE` olarak ayarladık. Böylece kişi başına yalnızca tek bir satır elde ederiz.

***UYARI:*** Eğer `arrange()` fonksiyonu kullanılıyorsa, verilerin her bir grup içinde düzenlenmesi için `.by_group = TRUE` olarak belirtin.

***TEHLİKE:*** Eğer `with_ties = FALSE` ise, bir bağın ilk satırı tutulur. Bu aldatıcı olabilir. Mariah’nın son randevusunda (6 Ocak) iki karşılaşması var ve ilki (en erken) tutuluyor. Muhtemelen, o gün daha sonraki karşılaşmasını sürdürmek istiyoruz. Bir sonraki örnekte bu bağların nasıl “kırılacağını” görebilirsiniz.

``` r
obs %>% 
  group_by(name) %>%       # satırları 'ad'a göre gruplandır
  slice_max(date,          # maksimum tarih değerine sahip grup başına satır tut 
            n = 1,         # sadece tek en yüksek satırı tut
            with_ties = F) # (tarihin) bir bağı varsa, ilk sırayı alın
```

Yukarıda, örneğin sadece Amrish’in 5 Ocak’taki satırının tutulduğunu ve sadece Brian’ın 7 Ocak’taki satırının tutulduğunu görebiliriz. Orijinal veriyi incelemek için [linke](#dedup_data) tıklayınız.

**“Bağları” kırmak**

“Bağları kırmak” için birden çok dilim ifadesi çalıştırılabilir. Bu durumda, bir kişinin en son *tarihinde* birden fazla karşılaşması varsa, en son *zamanlı* olan karşılaşma tutulur (karakter zamanlarını sıralanabilir bir zaman sınıfına dönüştürmek için `lubridate::hm()` kullanılır). Şimdi, 6 Ocak’ta “Mariah” için tutulan bir satırın, 07:25’teki 2. karşılaşma değil, 08:32’deki 3. karşılaşma olduğuna dikkat edin.

``` r
# "Bağları kırmak" için çoklu dilim ifadesi örneği
obs %>%
  group_by(name) %>%
  
  # İLK - en son tarihe göre dilimleyin
  slice_max(date, n = 1, with_ties = TRUE) %>% 
  
  # İKİNCİ - bir bağ varsa, en son zamana sahip satırı seçin; bağlar yasak
  slice_max(lubridate::hm(time), n = 1, with_ties = FALSE)
```

*ScriptIn yukarıdaki örnekte karşılaşma - `encounter` sayısına göre dilimleme yapmak da mümkün olabilirdi ama biz örnek amaçlı olarak tarih - `date` ve saat - `time` üzerinde dilimi gösterdik.*

***İPUCU:*** Bir “karakter” sütununda `slice_max()` veya `slice_min()` kullanmak için, onu sıralı bir faktör sınıfına dönüştürün!

Orijinal veriyi incelemek için [linke](#dedup_data) tıklayınız.

### Hepsini sakla ama işaretle

Tüm kayıtları tutmak, ancak yalnızca bazılarını analiz için işaretlemek istiyorsanız, benzersiz bir recordID/encounter number kullanan iki adımlı bir yaklaşımı değerlendirin:

1.  Orijinal veri çerçevesini analiz için yalnızca satırlara küçültün/dilimleyin. Bu azaltılmış veri çerçevesini kaydedin/saklayın.
2.  Orijinal veri çerçevesinde, satırları, kayıtlı benzersiz tanımlayıcısının (bu örnekte recordID) indirgenmiş veri çerçevesinde bulunup bulunmadığına bağlı olarak `case_when()` ile uygun şekilde işaretleyin.

``` r
# 1. Analiz için saklanacak satırların veri çerçevesini tanımlayın
obs_keep <- obs %>%
  group_by(name) %>%
  slice_max(encounter, n = 1, with_ties = FALSE) # her kişi başına yalnızca en son karşılaşmayı tutun


# 2. Orijinal veri çerçevesini işaretleyin
obs_marked <- obs %>%

  # yeni dup_record sütunu oluşturun
  mutate(dup_record = case_when(
    
    # kayıt obs_keep veri çerçevesindeyse
    recordID %in% obs_keep$recordID ~ "For analysis", 
    
    # analiz amacıyla "Yoksay" olarak işaretlenen diğer her şey
    TRUE                            ~ "Ignore"))

# yazdır
obs_marked
```

       recordID personID    name       date  time encounter purpose symptoms_ever
    1         1        1    adam 2020-01-01 09:00         1 contact          <NA>
    2         1        1    adam 2020-01-01 09:00         1 contact          <NA>
    3         2        2  amrish 2020-01-02 14:20         1 contact            No
    4         3        2  amrish 2020-01-02 14:20         1 contact            No
    5         4        3  mariah 2020-01-05 12:00         1    case            No
    6         5        2  amrish 2020-01-05 16:10         3    case           Yes
    7         6        4  nikhil 2020-01-05 13:01         1 contact           Yes
    8         7        5   brian 2020-01-05 15:20         1 contact            No
    9         8        6   smita 2020-01-05 14:20         1 contact           Yes
    10        9        7  raquel 2020-01-05 12:30         1 contact          <NA>
    11       10        2  amrish 2020-01-02 10:24         2 contact           Yes
    12       11        1    adam 2020-01-05 09:40         2    case            No
    13       12        3  mariah 2020-01-06 07:25         2 contact            No
    14       13        3  mariah 2020-01-06 08:32         3 contact            No
    15       14        4  nikhil 2020-01-06 15:36         2 contact           Yes
    16       15        5   brian 2020-01-06 15:31         2 contact           Yes
    17       16        5   brian 2020-01-07 07:59         3    case            No
    18       17        7  raquel 2020-01-07 11:13         2 contact            No
    19       18        8 natalie 2020-01-07 17:12         1    case            No
         dup_record
    1        Ignore
    2        Ignore
    3        Ignore
    4        Ignore
    5        Ignore
    6  For analysis
    7        Ignore
    8        Ignore
    9  For analysis
    10       Ignore
    11       Ignore
    12 For analysis
    13       Ignore
    14 For analysis
    15 For analysis
    16       Ignore
    17 For analysis
    18 For analysis
    19 For analysis

Orijinal veriyi incelemek için [linke](#dedup_data) tıklayınız.

### Satır tamlığını hesapla

Satırın tamlığı (eksik olmaması) için bir metrik içeren bir sütun oluşturun. Bu, tekilleştirme/dilimleme sırasında hangi satırların diğerlerine göre önceliklendirileceğine karar verirken yardımcı olabilir.

Bu örnekte, tamlığını ölçmek istediğiniz “anahtar” sütunlar, bir sütun adları vektörüne kaydedilir.

Daha sonra `mutate()` ile yeni `key_completeness` sütunu oluşturulur. Her satırdaki yeni değer, hesaplanmış bir kesir olarak tanımlanır: o satırda anahtar sütunlar arasında eksik olmayan değerlerin sayısı, anahtar sütunların sayısına bölünür.

Bu işlem, base R’daki `rowSums()` fonksiyonunu içermektedir. Ayrıca, tünellemede, tünelin o noktasındaki veri çerçevesine atıfta bulunan `.` kullanılır (bu durumda, köşeli parantez `[]` ile alt kümelenmektedir).

\*Daha fazla satır görmek için sağa kaydırın\*\*

``` r
# bir "değişken tamlığı" sütunu oluşturun
# bu, eksik olmayan değerlere sahip "key_cols" olarak belirlenmiş sütunların *oranıdır*

key_cols = c("personID", "name", "symptoms_ever")

obs %>% 
  mutate(key_completeness = rowSums(!is.na(.[,key_cols]))/length(key_cols)) 
```

Orijinal veriyi incelemek için [linke](#dedup_data) tıklayınız.

## 15.4 Toplama değerleri

Bu bölüm şunları açıklar:

1.  Bazı varyasyonlarla birden çok satırdaki değerleri tek bir satıra “toplama”
2.  “Toplanmış” değerlere sahip olduğunuzda, her hücredeki değerlerin üzerine nasıl yazılır/öncelik verilir

Bu sekme, Hazırlık sekmesindeki örnek veri kümesini kullanır.

### Değerleri bir satıra topla

Aşağıdaki kod örneği, satırları kişiye göre gruplandırmak için `group_by()` ve `summarise()` öğelerini kullanır ve ardından gruplanmış satırlardaki tüm benzersiz değerleri birbirine yapıştırır. Böylece kişi başına bir özet satırı elde edersiniz.

- Tüm yeni sütunlara bir son ek eklenir (bu örnekte “\_roll”).
- Hücre başına yalnızca benzersiz değerleri göstermek istiyorsanız, `na.omit()` öğesini `unique()` ile sarın.
- `na.omit()` `NA` değerlerini kaldırır, ancak bu istenmiyorsa `paste0(.x)`… kaldırılabilir.

``` r
# "Toplama" değerlerini grup başına bir satırda toplar ("personID" başına) 
cases_rolled <- obs %>% 
  
  # Ada göre grup oluşturur
  group_by(personID) %>% 
  
  # Her gruptaki satırları sıralar (ör. tarihe göre)
  arrange(date, .by_group = TRUE) %>% 
  
  # Her sütun için, gruplandırılmış satırlardaki tüm değerleri ";" ile ayırarak birbirine yapıştır
  summarise(
    across(everything(),                           # Tüm sütunlara uygula
           ~paste0(na.omit(.x), collapse = "; "))) # NA olmayan değerleri birleştiren işlev tanımlanır
```

Fonksiyonun çıktısı, girişlerin tarihe göre düzenlendiği ve birbirine yapıştırıldığı, grup başına bir satırdır (“ID”). *Daha fazla satır görmek için sola kaydırın.*

Orijinal veriyi incelemek için [linke](#dedup_data) tıklayınız.

**Bu varyasyon yalnızca benzersiz değerleri gösterir:**

``` r
# Varyasyon - yalnızca benzersiz değerleri göster
cases_rolled <- obs %>% 
  group_by(personID) %>% 
  arrange(date, .by_group = TRUE) %>% 
  summarise(
    across(everything(),                                   # Tüm sütunlara uygular
           ~paste0(unique(na.omit(.x)), collapse = "; "))) # NA olmayan benzersiz değerleri birleştiren işlev tanımlanır
```

**Bu varyasyon, her sütuna bir son ek ekler.**  
Bu durumda, yuvarlandığını belirtmek için “\_roll”:

``` r
# Varyasyon - sütun adlarına eklenen sonek 
cases_rolled <- obs %>% 
  group_by(personID) %>% 
  arrange(date, .by_group = TRUE) %>% 
  summarise(
    across(everything(),                
           list(roll = ~paste0(na.omit(.x), collapse = "; ")))) # _roll sütun adlarına eklenir
```

### Değerlerin/hiyerarşinin üzerine yaz

Daha sonra tüm yuvarlanan değerleri değerlendirmek ve yalnızca belirli bir değeri (örneğin, “en iyi” veya “maksimum” değer) tutmak istiyorsanız, dize kalıplarını sırayla aramak ve hücre içeriğinin üzerine yazmak için **stringr** paketinden `str_detect()` kullanan `case_when()` öğesini uygulamak için istenen sütunlarda `mutate()` öğesini kullanabilirsiniz.

``` r
# TEMİZ VAKALAR
#############
cases_clean <- cases_rolled %>% 
    
    # Temiz Evet-Hayır-Bilinmeyen değişkenler: metni dizede bulunan "en yüksek" değerle değiştir
    mutate(across(c(contains("symptoms_ever")),                     # belirtilen sütunlarda çalışır (E/H/B)
             list(mod = ~case_when(                                 # yeni sütunlara "_mod" son ekini ekler; case_when() öğesini uygular
               
               str_detect(.x, "Yes")       ~ "Yes",                 # "Evet" algılanırsa, hücre değeri evet'e dönüşür
               str_detect(.x, "No")        ~ "No",                  # daha sonra, "Hayır" algılanırsa, hücre değeri hayır'a dönüşür
               str_detect(.x, "Unknown")   ~ "Unknown",             # daha sonra, "Bilinmeyen" algılanırsa, hücre değeri bilinmeyen'e dönüşür
               TRUE                        ~ as.character(.x)))),   # sonra, başka bir şey varsa olduğu gibi tutulursa
      .keep = "unused")                                             # eski sütunlar kaldırıldı, yalnızca _mod sütunları kaldı
```

Şimdi, `symptoms_ever` sütununda görebilirsiniz, eğer kişi HEP semptomlara “Evet” dediyse, o zaman sadece “Evet” görüntülenir.

Orijinal veriyi incelemek için [linke](#dedup_data) tıklayınız.

## 15.5 Probabilistic de-duplication

Bazen, ad, yaş, cinsiyet, doğum tarihi vb. gibi çeşitli sütunlarda benzerliğe (ör. dize “mesafe”) dayalı olarak “olası” yinelemeleri belirlemek isteyebilirsiniz. Olası yinelemeleri belirlemek için olasılıklı bir eşleştirme algoritması uygulayabilirsiniz.

Bu yöntemle ilgili bir açıklama için [Verileri birleştirme](joining_matching.llms.md) sayfasına bakın. Olasılıksal Eşleştirme bölümü, bir veri çerçevesini *kendisiyle* karşılaştırmak için bu algoritmaları uygulamanın bir örneğini içerir, böylece olasılıksal tekilleştirme gerçekleştirir.

## 15.6 Kaynaklar

Bu sayfadaki bilgilerin çoğu şu kaynaklardan ve çevrimiçi vinyetlerden uyarlanmıştır:

[datanovia](https://www.datanovia.com/en/lessons/identify-and-remove-duplicate-data-in-r/)

[dplyr tidyverse reference](https://dplyr.tidyverse.org/reference/slice.html)

[cran janitor vignette](https://cran.r-project.org/web/packages/janitor/vignettes/janitor.html#explore-records-with-duplicated-values-for-specific-combinations-of-variables-with-get_dupes)
