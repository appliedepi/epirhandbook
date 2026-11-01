# 10  Karakterler ve dizeler

[![](../../images/characters_strings_1500x500.png)](../../images/characters_strings_1500x500.png)

Bu sayfa, karakter değerlerini (“dizeler”) değerlendirmek ve işlemek için **stringr** paketinin kullanımını göstermektedir.

1.  Birleştir, düzenle, ayır, düzenle - `str_c()`, `str_glue()`, `str_order()`, `str_split()`  
2.  Temizle ve standardize et
    - Uzunluğunu ayarla - `str_pad()`, `str_trunc()`, `str_wrap()`  
    - Büyük küçük harfi değiştir - `str_to_upper()`, `str_to_title()`, `str_to_lower()`, `str_to_sentence()`  
3.  Sırasına göre çıkar ve değerlendir - `str_length()`, `str_sub()`, `word()`  
4.  Paternlre
    - Tespit et ve bul - `str_detect()`, `str_subset()`, `str_match()`, `str_extract()`  
    - Modifiye et ve değiştir - `str_sub()`, `str_replace_all()`  
5.  Düzenli ifadeler (“regex”)

Gösterimi kolaylaştırmak için çoğu örnekte kısa tanımlı bir karakter vektörü esas alınmıştır, bu örnekler bir veri çerçevesi içindeki sütuna kolayca uyarlanabilir.

Bu [stringr skeci](https://cran.r-project.org/web/packages/stringr/vignettes/stringr.html) bu sayfa için ilham vermiştir.

## 10.1 Hazırlık

### Paketleri yükleme

**stringr** ve diğer **tidyverse** paketlerini kurun veya yükleyin.

``` r
# paketleri indir/yükle
pacman::p_load(
  stringr,    # dizeleri işlemek için birçok fonksiyon
  tidyverse,  # ek veri işleme fonksiyonları
  tools,      # başlıkları dönüştürmek için alternatif
  appliedepidata) # bu el kitabında kullanılan örnek veriler
```

### Verileri yükleme

Bu sayfada, simüle edilmiş bir Ebola salgını vakalarının temizlenmiş “satır listesine” ara sıra atıfta bulunulacaktır. Doğrudan `appliedepidata::get_data(name = "linelist_cleaned_rds")` ile yükleyin (ayrıntılar için [El kitabı ve veri indirme](download.llms.md) sayfasına bakın).

``` r
# Satır listesini indir
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

The first 50 rows of the linelist are displayed below.

## 10.2 Birleştir, böl ve düzenle

Bu bölüm aşağıdaki başlıkları içermektedir:

- `str_c()`, `str_glue()`, ve `unite()` komutlarıyla dizeleri birleştirmek  
- `str_order()` komutuyla dizeleri sıralamak
- `str_split()` ve `separate()` komutuyla dizeleri ayırmak

### Dizeleri Birleştirme

Birden çok dizeyi tek bir dizede birleştirmek için, **stringr**’dan `str_c` fonksiyonu kullanılır. Birleştirilecek farklı karakterler mevcutsa, bunları virgülle ayırarak benzersiz argümanlar olarak eklemeniz yeterlidir.

``` r
str_c("String1", "String2", "String3")
```

    [1] "String1String2String3"

`sep =` argümanı, eklediğiniz bağımsız değişkenlerin her birinin arasına bir karakter değeri ekler (ör. virgül, boşluk veya yeni satır `"\n"` ekleme)

``` r
str_c("String1", "String2", "String3", sep = ", ")
```

    [1] "String1, String2, String3"

`collapse =` argümanı, `str_c()` argümanıyla birden çok *vektör* kullanılıldığı durumlarda işe yarar. Çıktı vektörünün öğelerini, çıktı vektörü tek bir uzun karakter öğesinden oluşacak şekilde ayırmak için kullanılır.

Aşağıdaki örnek, iki vektörün tek bir vektörde (adlar ve soyadlar) birleşimini göstermektedir. Bir başka benzer örnek, yargı yetkileri ve dava sayıları olabilir. Bu örnekte:

- `sep =` değeri ad ve soyad arasını belirler  
- `collapse =` değeri her bir kişiyi bir diğerinden ayırır

``` r
first_names <- c("abdul", "fahruk", "janice") 
last_names  <- c("hussein", "akinleye", "okeke")

# ilgili giriş dizeleri arasını sep belirler, her bir öğenin arasını ise collapse belirler
str_c(first_names, last_names, sep = " ", collapse = ";  ")
```

    [1] "abdul hussein;  fahruk akinleye;  janice okeke"

Not: İstenilen görüntüleme şekline göre, birleşik dize yazdırırken, yeni satırların düzgün yazdırılması için tüm ifadeyi `cat()` fonksiyonu içine sarmanız gerekebilir:

``` r
# Yeni satırların doğru yazdırılması için ifadenin cat() içine sarılması gerekir
cat(str_c(first_names, last_names, sep = " ", collapse = ";\n"))
```

    abdul hussein;
    fahruk akinleye;
    janice okeke

### Dinamik dizeler

Bir dizeye dinamik R kodu eklemek için `str_glue()` fonksiyonunu kullanın. Bu, aşağıda gösterildiği gibi dinamik grafik başlıkları oluşturmak için çok kullanışlı bir fonksiyondur

- Tüm içerik çift tırnak işaretleri arasında girilir `str_glue("")`  
- Herhangi bir dinamik kod veya önceden tanımlanmış değerlere yapılan referanslar, çift tırnak işareti içerisinde `{}` küme parantezleri içine yerleştirilir. Aynı `str_glue()` komutunda birçok küme parantezleri olabilir.  
- `''` tek tırnak işaretlerini görüntülemek için, çevreleyen çift tırnak içinde *tek* tırnak kullanılabilir (ör. tarih formatı sağlarken - aşağıdaki örneğe bakın)  
- İpucu: Satır atlamak için `\n`i kullanabilirsiniz
- İpucu: Tarih gösterimini ayarlamak için `format()` ve geçerli tarihi görüntülemek için `Sys.Date()` fonksiyonlarını kullanabilirsiniz

Dinamik bir grafik başlığının basit bir örneği:

``` r
str_glue("Data include {nrow(linelist)} cases and are current to {format(Sys.Date(), '%d %b %Y')}.")
```

    Data include 5888 cases and are current to 01 Nov 2026.

Alternatif bir format, parantez içinde yer tutucuları kullanmak ve kodu, aşağıdaki gibi `str_glue()` fonksiyonunun sonunda ayrı argümanlarda tanımlamaktır. Bu, metin uzunsa kodun okunabilirliğini artırabilir.

``` r
str_glue("Linelist as of {current_date}.\nLast case hospitalized on {last_hospital}.\n{n_missing_onset} cases are missing date of onset and not shown",
         current_date = format(Sys.Date(), '%d %b %Y'),
         last_hospital = format(as.Date(max(linelist$date_hospitalisation, na.rm=T)), '%d %b %Y'),
         n_missing_onset = nrow(linelist %>% filter(is.na(date_onset)))
         )
```

    Linelist as of 01 Nov 2026.
    Last case hospitalized on 30 Apr 2015.
    256 cases are missing date of onset and not shown

**Bir veri çerçevesinden dizi alımı**

Bazen, bir veri çerçevesinden veri çekmek ve peşpeşe eklemek istenebilir. Aşağıda örnek bir veri çerçevesi bulunmaktadır. Bu veri çerçevesi, yetki alanları; yeni ve toplam dava sayıları hakkında özet bir açıklama yapmak için kullanılabilir.

``` r
# vaka veri çerçevesini hazırla
case_table <- data.frame(
  zone        = c("Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5"),
  new_cases   = c(3, 0, 7, 0, 15),
  total_cases = c(40, 4, 25, 10, 103)
  )
```

Veri çerçevesi satırlarından veri almak için özel olarak yapılmış `str_glue_data()` kullanılır:

``` r
case_table %>% 
  str_glue_data("{zone}: {new_cases} ({total_cases} total cases)")
```

    Zone 1: 3 (40 total cases)
    Zone 2: 0 (4 total cases)
    Zone 3: 7 (25 total cases)
    Zone 4: 0 (10 total cases)
    Zone 5: 15 (103 total cases)

**Dizeleri satırlarda birleştirme**

Bir veri çerçevesi sütunundaki değerleri “birleştirmeye” çalışıyorsanız; örneğin, birden çok satırdaki değerleri bir ayırıcıyla birbirine yapıştırarak tek bir satırda birleştirme, [Tekilleştirme](deduplication.llms.md) sayfasının [“toplama” değerleri](deduplication.llms.md#str_rollup) bölümüne bakabilirsiniz.

**Veri çerçevesini bir satıra çevirme**

`str_c()` fonksiyonu (veri çerçevesini ve sütun adlarını da belirterek), `sep =` ve `collapse =` argümanlarını kullanarak verilerin tek satırda görünmesini sağlayabilirsiniz.

``` r
str_c(case_table$zone, case_table$new_cases, sep = " = ", collapse = ";  ")
```

    [1] "Zone 1 = 3;  Zone 2 = 0;  Zone 3 = 7;  Zone 4 = 0;  Zone 5 = 15"

Verileri ayrı bir `str_c()` komutu ile sarmalayarak ifadenin başına “New Cases:” ön metnini ekleyebilirsiniz (“New Cases:” orijinal `str_c()` içindeyse, birden çok kez görünecektir).

``` r
str_c("New Cases: ", str_c(case_table$zone, case_table$new_cases, sep = " = ", collapse = ";  "))
```

    [1] "New Cases: Zone 1 = 3;  Zone 2 = 0;  Zone 3 = 7;  Zone 4 = 0;  Zone 5 = 15"

### Sütunları birleştirme

Bir veri çerçevesinde, birden çok sütundaki karakter değerlerini bir araya getirmek, **tidyr**’den `unite()` fonksiyonu ile gerçekleştirilebilir. Bu, `separate()`in tam tersidir.

Yeni birleşik sütunun adı girilir. Ardından, birleştirmek istenen sütunların adları girilir.

- Varsayılan olarak, birleşik sütunda kullanılan ayırıcı `_` alt çizgidir, ancak bu, `sep =` argümanı ile değiştirilebilir.
- `remove =` veri çerçevesinden giriş sütunlarını kaldırır (varsayılan olarak TRUE)
- `na.rm =` birleştirirken eksik değerleri kaldırır (varsayılan olarak FALSE)

Aşağıda, göstermek için bir mini veri çerçevesi tanımlanmaktadır:

``` r
df <- data.frame(
  case_ID = c(1:6),
  symptoms  = c("jaundice, fever, chills",     # hasta 1
                "chills, aches, pains",        # hasta 2 
                "fever",                       # hasta 3
                "vomiting, diarrhoea",         # hasta 4
                "bleeding from gums, fever",   # hasta 5
                "rapid pulse, headache"),      # hasta 6
  outcome = c("Recover", "Death", "Death", "Recover", "Recover", "Recover"))
```

``` r
df_split <- separate(df, symptoms, into = c("sym_1", "sym_2", "sym_3"), extra = "merge", fill = "right")
```

Örnek bir veri çerçevesi:

Aşağıda, üç semptom sütununu birleştirilmiştir:

``` r
df_split %>% 
  unite(
    col = "all_symptoms",         # yeni birleşik sütunun adı
    c("sym_1", "sym_2", "sym_3"), # birleştirilecek için sütunlar
    sep = ", ",                   # birleşik sütunda kullanılacak ayırıcı
    remove = TRUE,                # TRUE ise, veri çerçevesinden girdi sütunlarını kaldırır
    na.rm = TRUE                  # DOĞRU ise, birleştirmeden önce eksik değerler kaldırılır
  )
```

      case_ID                all_symptoms outcome
    1       1     jaundice, fever, chills Recover
    2       2        chills, aches, pains   Death
    3       3                       fever   Death
    4       4         vomiting, diarrhoea Recover
    5       5 bleeding, from, gums, fever Recover
    6       6      rapid, pulse, headache Recover

### Ayırma

Bir dizgiyi belli bir paterne göre bölmek için `str_split()` kullanılabilir. Bu komut dize(ler)i uygun paternde böler ve yeni değerlerden oluşan karakter vektörleri `list` olarak döndürür.

Aşağıdaki basit örnek, verilen dizeyi değerlendirir ve onu üçe böler. Varsayılan olarak, her dizin her bir bölümü (bir karakter vektörü) `list` sınıfının bir nesnesine dönüştürülür. Eğer argüman `simplify = TRUE` ise, sonuç bir karakter matrisi olacaktır.

Bu örnekte, dize fonksiyon ile, listeye dönüştürülür - üç değer içeren bir karakter vektörü.

``` r
str_split(string = "jaundice, fever, chills",
          pattern = ",")
```

    [[1]]
    [1] "jaundice" " fever"   " chills" 

Çıktı kaydedilirse, parantez sözdizimi ile n’inci değerine erişebilirsiniz. Belirli bir değere erişmek için `the_returned_object[[1]][2]` argümanı kullanılır. Bu fonksiyonla listedeki (“fever”) ikinci değere erişir. Değerlere erişim hakkında daha fazla ayrıntı için [R temelleri](basics.llms.md) sayfasına bakabilirsiniz.

``` r
pt1_symptoms <- str_split("jaundice, fever, chills", ",")

pt1_symptoms[[1]][2]  # listeden 2. değeri çıkarır
```

    [1] " fever"

`str_split()` fonksiyonuyla listede birden fazla karakter dizisi mevcutsa, döndürülen listede de birden fazla eleman olacaktır.

``` r
symptoms <- c("jaundice, fever, chills",     # hasta 1
              "chills, aches, pains",        # hasta 2 
              "fever",                       # hasta 3
              "vomiting, diarrhoea",         # hasta 4
              "bleeding from gums, fever",   # hasta 5
              "rapid pulse, headache")       # hasta 6

str_split(symptoms, ",")                     # her hastanın semptomlarını ayırır
```

    [[1]]
    [1] "jaundice" " fever"   " chills" 

    [[2]]
    [1] "chills" " aches" " pains"

    [[3]]
    [1] "fever"

    [[4]]
    [1] "vomiting"   " diarrhoea"

    [[5]]
    [1] "bleeding from gums" " fever"            

    [[6]]
    [1] "rapid pulse" " headache"  

Veri çerçevesi sütununa dönüştürebileceğiniz bir “karakter matrisi” çıktısını almak için, `simplify = TRUE` bağımsız değişkenini aşağıda gösterildiği gibi ayarlamalısınız:

``` r
str_split(symptoms, ",", simplify = TRUE)
```

         [,1]                 [,2]         [,3]     
    [1,] "jaundice"           " fever"     " chills"
    [2,] "chills"             " aches"     " pains" 
    [3,] "fever"              ""           ""       
    [4,] "vomiting"           " diarrhoea" ""       
    [5,] "bleeding from gums" " fever"     ""       
    [6,] "rapid pulse"        " headache"  ""       

Ayrıca `n =` argümanıyla oluşturulacak bölmelerin sayısını da ayarlayabilirsiniz. Aşağıdaki örnekte bölme sayısı 2 ile sınırlandırılmıştır. Diğer virgül ve dizeler ikinci değer içinde kalır.

``` r
str_split(symptoms, ",", simplify = TRUE, n = 2)
```

         [,1]                 [,2]            
    [1,] "jaundice"           " fever, chills"
    [2,] "chills"             " aches, pains" 
    [3,] "fever"              ""              
    [4,] "vomiting"           " diarrhoea"    
    [5,] "bleeding from gums" " fever"        
    [6,] "rapid pulse"        " headache"     

*Not - aynı çıktıları, “simplify” argümanını kullanmadığınız, bunun yerine sütun sayısını (`n`) belirtmeniz gereken `str_split_fixed()` fonksiyonu ile de elde edilebilirsiniz.*

``` r
str_split_fixed(symptoms, ",", n = 2)
```

### Sütunları ayırma

Veri çerçevesine ait bir sütunu bölmeye çalışıyorsanız, **dplyr** paketinden `separate()` fonksiyonu en iyi seçenektir. Bu fonksiyon var olan bir karakter sütununu diğer sütunlara bölmek için kullanılır.

Diyelim ki bir `case_ID` sütunu, birçok semptom içeren bir karakter sütunu ve bir sonuç sütunu içeren basit bir “df” ([Sütunları birleştirme bölümünde](#str_unite) içinde tanımlanmış ve birleştirilmiş) veri çerçevemiz var. Bu örnekte amacımız, `symptoms` sütununu her biri bir semptom içeren birçok sütuna ayırmaktır.

Verileri `separate()` fonksiyonuna aktarıldığını varsayarsak, önce ayrılacak sütunu fonksiyona tanımlamalısınız. Ardından, aşağıda gösterildiği gibi *yeni* sütun adlarını içeren bir `c( )` vektörünü olarak `into =` argümanına aktarabilirsiniz.

- `sep =` ayırıcı, bir karakter veya bir sayı olabilir (bölünecek karakter konumu olarak yorumlanır)
- `remove =` Varsayılan olarak TRUE, giriş sütununu kaldırır  
- `convert =` Varsayılan olarak FALSE, “NA” dizelerinin “NA” (eksik veri) formatına dönüştürür
- `extra =` bu, ayırılan yeni sütunlarda daha fazla değer varsa bunların ne olacağını kontrol eder.
  - `extra = "warn"` sizi uyarır, ancak aşırı değerlerin kaybolacağı anlamına gelir (**the default**)  
  - `extra = "drop"` aşırı değerlerin uyarı yapılmadan kaybolacağı anlamına gelir
  - **`extra = "merge"` yalnızca “into” argümanında tanımlanan sütun sayısına bölünür - *bu ayar tüm verilerinizi korur***

Aşağıda `extra = "merge"` içeren bir örnek verilmiştir - burada hiçbir veri kaybolmaz. İki yeni sütun tanımlanır, ancak ikinci yeni sütunda üçüncü semptomlar kalmaya devam eder:

``` r
# ikinci ve üçüncü semptomlar ikinci sütunda birleştirildi
df %>% 
  separate(symptoms, into = c("sym_1", "sym_2"), sep=",", extra = "merge", fill = "right")
```

      case_ID              sym_1          sym_2 outcome
    1       1           jaundice  fever, chills Recover
    2       2             chills   aches, pains   Death
    3       3              fever           <NA>   Death
    4       4           vomiting      diarrhoea Recover
    5       5 bleeding from gums          fever Recover
    6       6        rapid pulse       headache Recover

Aşağıda `extra = "drop"` kullanıldığında üçüncü semptomlar kaybolur:

``` r
# üçüncü semptomlar kaybolur
df %>% 
  separate(symptoms, into = c("sym_1", "sym_2"), sep=",", extra = "drop", fill = "right")
```

      case_ID              sym_1      sym_2 outcome
    1       1           jaundice      fever Recover
    2       2             chills      aches   Death
    3       3              fever       <NA>   Death
    4       4           vomiting  diarrhoea Recover
    5       5 bleeding from gums      fever Recover
    6       6        rapid pulse   headache Recover

***DİKKAT:*** Yeni sütunlar için yeterli `into` değeri sağlamazsanız verileriniz kaybolabilir.

### Alfabetik olarak düzenle

Birkaç dize alfabetik sıraya göre sıralanabilir. `str_order()` dizelerin alfabetik olarak sırasını verirken, `str_sort()` dizeleri alfabetik olarak sıralar.

``` r
# dizeler
health_zones <- c("Alba", "Takota", "Delta")

# alfabetik sırasını döndürür
str_order(health_zones)
```

    [1] 1 3 2

``` r
# dizeleri alfabetik olarak sıralar
str_sort(health_zones)
```

    [1] "Alba"   "Delta"  "Takota"

Farklı bir alfabe kullanmak için `locale =` argümanını ekleyebilirsiniz. R konsoluna `stringi::stri_locale_list()` girerek yerel ayarların tam listesine bakabınız.

### R tabanı fonksiyonları

Tüm parçaları karaktere dönüştürdükten sonra vektörleri birleştiren R tabanındaki `paste()` ve `paste0()` fonksiyonları yaygın bir şekilde kullanılmaktadır. Bunlar `str_c()` fonksiyonuna benzer şekilde hareket ederler, ancak sözdizimi daha karmaşıktır - parantez içinde her bölüm bir virgülle ayrılır. Parçalar ya karakter metnidir (tırnak içinde) ya da önceden tanımlanmış kod nesneleridir (tırnak işaretleri olmadan). Örnek olarak:

``` r
n_beds <- 10
n_masks <- 20

paste0("Regional hospital needs ", n_beds, " beds and ", n_masks, " masks.")
```

    [1] "Regional hospital needs 10 beds and 20 masks."

`sep =` ve `collapse =` argümanları özelleştirilebilir. `paste()` basitçe `paste0()` fonksiyonunun varsayılan `sep = " "` (bir boşluk) argümanlı halidir.

## 10.3 Temizleme ve standartlaştırma

### Karakterleri değiştirme

Çoğu zaman, bir dize değerinin büyük/küçük harf kullanımı değiştirilmelidir, örneğin şehir adları. Aşağıda **stringr** paketinden `str_to_upper()`, `str_to_lower()` ve `str_to_title()` fonksiyonlarına ait örnekler verilmiştir:

``` r
str_to_upper("California")
```

    [1] "CALIFORNIA"

``` r
str_to_lower("California")
```

    [1] "california"

Yukarıdaki örnekler R tabanındaki `toupper()`, `tolower()` fonksiyonlarıyla da yapılabilir.

**İlk karakter**

Her kelimenin ilk harfini büyütmek için `str_to_title()` fonksiyonu kullanılır:

``` r
str_to_title("go to the US state of california ")
```

    [1] "Go To The Us State Of California "

Daha hassas bir büyük harf kullanımı elde etmek için **tools** paketinden `toTitleCase()` fonksiyonunu kullanabilirsiniz (“to”, “the” ve “of” gibi sözcükler büyük harfle yazılmaz).

``` r
tools::toTitleCase("This is the US state of california")
```

    [1] "This is the US State of California"

Ayrıca cümlenin yalnızca ilk harfini büyük harf yapan `str_to_sentence()` kullanabilirsiniz.

``` r
str_to_sentence("the patient must be transported")
```

    [1] "The patient must be transported"

### Karakter uzunluğu

Bir dizeye minimum uzunlukta karakter eklemek için `str_pad()` fonksiyonunu kullanabilirsiniz. Varsayılan olarak boşluklar eklenir, ancak `pad =` argümanını kullanarak diğer karakterlerle de doldurabilirsiniz.

``` r
# Farklı uzunluktaki ICD kodları
ICD_codes <- c("R10.13",
               "R10.819",
               "R17")

# Sağ tarafta 7 karaktere kadar doldurulmuş ICD kodları
str_pad(ICD_codes, 7, "right")
```

    [1] "R10.13 " "R10.819" "R17    "

``` r
# Boşluk yerine nokta içeren karakter alanı
str_pad(ICD_codes, 7, "right", pad = ".")
```

    [1] "R10.13." "R10.819" "R17...."

Örneğin, sayıların başını sıfırlarla doldurmak için (saat veya dakika gibi), sayıyı `pad = "0"` ile minimum 2 uzunluğa kadar doldurabilirsiniz.

``` r
# İki basamağın başına sıfır ekle (ör. dakika/saat zamanları için)
str_pad("4", 2, pad = "0") 
```

    [1] "04"

``` r
# example using a numeric column named "hours"
# hours <- str_pad(hours, 2, pad = "0")
```

### Kesme

`str_trunc()` her dize için bir maksimum bir uzunluk belirler. Bir dize bu uzunluğu aşarsa, kısaltılır (kısaltılır) ve dizenin öncesinde daha uzun olduğunu belirtmek için bir üç nokta (…) eklenir. Üç noktanın *uzunluk* olarak sayıldığına dikkat etmelisiniz. Üç nokta karakterleri `ellipsis =` argümanı ile değiştirilebilir. İsteğe bağlı `side =` argümanı, üç noktanın kesilen dize (“left”, “right” veya “center”) içinde nerede görüneceğini belirtir.

``` r
original <- "Symptom onset on 4/3/2020 with vomiting"
str_trunc(original, 10, "center")
```

    [1] "Symp...ing"

### Standart uzunluk

Standart uzunluğu belirlemek için `str_trunc()` fonksiyonunu kullanabilirsiniz. Standart uzunluğa göre kısa olan dizeleri genişletmek için `str_pad()` fonksiyonu kullanılır. Aşağıdaki örnekte, maksimum uzunluk olarak 6 ayarlanmıştır. Burada daha uzun değerler kesilir ve kısa olan değerler genişler.

``` r
# Farklı uzunluktaki ICD kodları
ICD_codes   <- c("R10.13",
                 "R10.819",
                 "R17")

# en fazla 6 karakterle sınırla
ICD_codes_2 <- str_trunc(ICD_codes, 6)
ICD_codes_2
```

    [1] "R10.13" "R10..." "R17"   

``` r
# en az 6 karakter uzunluğunda tut
ICD_codes_3 <- str_pad(ICD_codes_2, 6, "right")
ICD_codes_3
```

    [1] "R10.13" "R10..." "R17   "

### Baştaki/sondaki boşlukları kaldırma

Bir dize girişinin kenarlarındaki boşlukları, yeni satırları (`\n`) veya sekmeleri (`\t`) kaldırmak için `str_trim()` kullanın. Hangi tarafın kırpılacağını belirtmek için komuta `"right"` `"left"` veya `"both"` ekleyin (ör. `str_trim(x, "right")`).

``` r
# Sağda fazla boşluk bulunan kimlik numaraları
IDs <- c("provA_1852  ", # iki fazla boşluk
         "provA_2345",   # fazla boşluk yok
         "provA_9460 ")  # bir fazla boşluk

# Kimlik numaraların yalnızca sağ taraftaki fazla boşlukları kaldırılır
str_trim(IDs)
```

    [1] "provA_1852" "provA_2345" "provA_9460"

### Tekrarlanan boşlukları kaldırma

Bir dizenin *içindeki* yinelenen boşlukları kaldırmak için `str_squish()` fonksiyonunu kullanabilirsiniz. Örneğin, çift boşlukları tek boşluklara dönüştürmek için. Ayrıca `str_trim()` fonksiyonu gibi dizenin dışındaki boşlukları, yeni satırları veya sekmeleri de kaldırır.

``` r
# orijinal, dize içinde fazla boşluk içeriyor
str_squish("  Pt requires   IV saline\n") 
```

    [1] "Pt requires IV saline"

Daha fazla ayrıntı görmek için R konsolunuza `?str_trim`, `?str_pad` komutunu giriniz.

### Paragrafa sığdırma

Uzun bir yapılandırılmamış metni sabit satır uzunluğuna sahip yapılandırılmış bir paragrafa sığdırmak için `str_wrap()` fonksiyonunu kullanabilirsiniz. Her satır için ideal karakter uzunluğunu tanımladığınızda, fonksiyon, aşağıdaki örnekte görüldüğü gibi paragraf içine yeni satırlar (`\n`) eklemek için bir algoritma uygular.

``` r
pt_course <- "Symptom onset 1/4/2020 vomiting chills fever. Pt saw traditional healer in home village on 2/4/2020. On 5/4/2020 pt symptoms worsened and was admitted to Lumta clinic. Sample was taken and pt was transported to regional hospital on 6/4/2020. Pt died at regional hospital on 7/4/2020."

str_wrap(pt_course, 40)
```

    [1] "Symptom onset 1/4/2020 vomiting chills\nfever. Pt saw traditional healer in\nhome village on 2/4/2020. On 5/4/2020\npt symptoms worsened and was admitted\nto Lumta clinic. Sample was taken and pt\nwas transported to regional hospital on\n6/4/2020. Pt died at regional hospital\non 7/4/2020."

R tabanındaki `cat()` fonksiyonu ile yapılandırılmış bu yeni paragrafın çıktısı alınabilir.

``` r
cat(str_wrap(pt_course, 40))
```

    Symptom onset 1/4/2020 vomiting chills
    fever. Pt saw traditional healer in
    home village on 2/4/2020. On 5/4/2020
    pt symptoms worsened and was admitted
    to Lumta clinic. Sample was taken and pt
    was transported to regional hospital on
    6/4/2020. Pt died at regional hospital
    on 7/4/2020.

## 10.4 Pozisyona göre düzenleme

### Karakter pozisyonuna göre çıkarma

Bir dizenin yalnızca bir kısmını döndürmek için `str_sub()` kullanın. Fonksiyon üç ana argüman alır:

1.  karakter vektör(leri)  
2.  başlangıç pozisyonu
3.  bitiş pozisyonu

Pozisyon değeri hakkında bir kaç:

- Bir pozisyon değeri pozitifse, pozisyon dizenin sol ucundan başlayarak sayılır.  
- Bir pozisyon değeri negatifse, pozisyon dizenin sağ ucundan başlayarak sayılır.
- Pozisyon numaraları dahildir.  
- Dizinin ötesine uzanan konumlar kesilir (kaldırılır).

Aşağıda “pneumonia” dizesine uygulanan bazı örnekler verilmiştir.:

``` r
# soldan üçüncü başlar ve biter (soldan üçüncü harf)
str_sub("pneumonia", 3, 3)
```

    [1] "e"

``` r
# 0 mevcut değil
str_sub("pneumonia", 0, 0)
```

    [1] ""

``` r
# soldan 6., sağdan 1. arasındaki
str_sub("pneumonia", 6, -1)
```

    [1] "onia"

``` r
# Sağdan 5., sağdan 2. arasındaki
str_sub("pneumonia", -5, -2)
```

    [1] "moni"

``` r
# 4. soldan dizenin dışındaki bir pozisyona
str_sub("pneumonia", 4, 15)
```

    [1] "umonia"

### Kelime pozisyonuna göre çıkarma

n’inci ’kelime’yi çıkarmak için, yine **stringr** paketinden `word()` fonksiyonunu kullanabilirsiniz. Fonksiyonu kullanabilmek için dizeyi, ardından ayıklanacak ilk sözcük konumunu ve ayıklanacak son sözcük konumunu tanımlamanız gerekmektedir.

Varsayılan olarak, `sep =` ile aksi belirtilmedikçe ‘kelimeler’ arasındaki ayırıcının bir boşluk olduğu varsayılır (örneğin, kelimeler alt çizgilerle ayrıldığında `sep = "_"`.

``` r
# dizeleri değerlendirme
chief_complaints <- c("I just got out of the hospital 2 days ago, but still can barely breathe.",
                      "My stomach hurts",
                      "Severe ear pain")

# her dizenin 1. ila 3. kelimelerin arasını ayır
word(chief_complaints, start = 1, end = 3, sep = " ")
```

    [1] "I just got"       "My stomach hurts" "Severe ear pain" 

### Karakteri pozisyonuna göre değiştirme

Atama operatörüyle (`<-`) eşleştirilen `str_sub()` fonksiyonu, bir dizenin bir bölümünü değiştirmek için kullanılabilir:

``` r
word <- "pneumonia"

# üçüncü ve dördüncü karakterleri X'e dönüştür
str_sub(word, 3, 4) <- "XX"

# print
word
```

    [1] "pnXXmonia"

Birden çok dizeye uygulanan bir örnek (örneğin bir sütun). “HIV” uzunluğundaki genişlemeye dikkat edin.

``` r
words <- c("pneumonia", "tubercolosis", "HIV")

# üçüncü ve dördüncü karakterleri X'e dönüştür
str_sub(words, 3, 4) <- "XX"

words
```

    [1] "pnXXmonia"    "tuXXrcolosis" "HIXX"        

### Uzunluğu değerlendirme

``` r
str_length("abc")
```

    [1] 3

Alternatif olarak, R tabanından `nchar()` fonksiyonu kullanabilirsiniz.

## 10.5 Paternler

Birçok **stringr** fonksiyonu, belirli bir *paterne* göre algılamak, bulmak, ayıklamak, eşleştirmek, değiştirmek ve bölmek için kullanılabilir.

### Patern bulma

Bir dize içindeki bir kalıbın varlığını/yokluğunu algılamak için aşağıdaki gibi `str_detect()` fonksiyonunu kullanabilirsiniz. Önce aranacak dizeyi veya vektörü (`string =`) ve sonra aranacak modeli (`pattern =`) belirlemeniz gerekmektedir. Varsayılan olarak aramanın *büyük/küçük harf duyarlı olduğunu* unutmayın!

``` r
str_detect(string = "primary school teacher", pattern = "teach")
```

    [1] TRUE

Desenin mevcut OLMADIĞINI bilmek istiyorsanız, `negate =` argümanı eklenebilir ve `TRUE` olarak ayarlanabilir.

``` r
str_detect(string = "primary school teacher", pattern = "teach", negate = TRUE)
```

    [1] FALSE

Büyük/küçük harf kullanımını yok saymak için, kalıbı `regex()` içine sarın ve `regex()` komutu *içinde*, `ignore_case = TRUE` (veya `T`) argümanını ekleyin.

``` r
str_detect(string = "Teacher", pattern = regex("teach", ignore_case = T))
```

    [1] TRUE

Bir karakter vektörüne veya bir veri çerçevesi sütununa `str_detect()` uygulandığında, değerlerin her biri için DOĞRU veya YANLIŞ sonucunu döndürür.

``` r
# bir meslek vektörü/sütunu 
occupations <- c("field laborer",
                 "university professor",
                 "primary school teacher & tutor",
                 "tutor",
                 "nurse at regional hospital",
                 "lineworker at Amberdeen Fish Factory",
                 "physican",
                 "cardiologist",
                 "office worker",
                 "food service")

# Her dizede "teach" kalıbının varlığını tespit et - çıktı DOĞRU/YANLIŞ vektörüdür
str_detect(occupations, "teach")
```

     [1] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE

“DOĞRU”ları saymanız gerekiyorsa, çıktıyı `sum()` fonksiyonu içine almanız yeterlidir. Bu, “DOĞRU” çıktıların sayısını verir.

``` r
sum(str_detect(occupations, "teach"))
```

    [1] 1

Birden çok terimi aramak için, bunları aşağıda gösterildiği gibi ‘pattern =’ bağımsız değişkenine VEYA çubukları (`|`) ile ayırarak ekleyin:

``` r
sum(str_detect(string = occupations, pattern = "teach|professor|tutor"))
```

    [1] 3

Uzun bir arama terimleri listesi oluşturmanız gerekiyorsa, bunları `str_c()` ve `sep = |` kullanarak birleştirebilir ardından bunun bir karakter nesnesi olarak tanımlayabilir ve daha sonrasında vektör formatında arayabilirsiniz. Aşağıdaki örnek, birinci basamak sağlık çalışanları için olası meslek arama terimlerini içermektedir.

``` r
# search terms
occupation_med_frontline <- str_c("medical", "medicine", "hcw", "healthcare", "home care", "home health",
                                "surgeon", "doctor", "doc", "physician", "surgery", "peds", "pediatrician",
                               "intensivist", "cardiologist", "coroner", "nurse", "nursing", "rn", "lpn",
                               "cna", "pa", "physician assistant", "mental health",
                               "emergency department technician", "resp therapist", "respiratory",
                                "phlebotomist", "pharmacy", "pharmacist", "hospital", "snf", "rehabilitation",
                               "rehab", "activity", "elderly", "subacute", "sub acute",
                                "clinic", "post acute", "therapist", "extended care",
                                "dental", "dential", "dentist", sep = "|")

occupation_med_frontline
```

    [1] "medical|medicine|hcw|healthcare|home care|home health|surgeon|doctor|doc|physician|surgery|peds|pediatrician|intensivist|cardiologist|coroner|nurse|nursing|rn|lpn|cna|pa|physician assistant|mental health|emergency department technician|resp therapist|respiratory|phlebotomist|pharmacy|pharmacist|hospital|snf|rehabilitation|rehab|activity|elderly|subacute|sub acute|clinic|post acute|therapist|extended care|dental|dential|dentist"

Aşağıdaki komut, birinci basamak sağlık çalışanları (`occupation_med_frontline`) için arama terimlerinden herhangi birini içeren mesleklerin sayısını döndürür:

``` r
sum(str_detect(string = occupations, pattern = occupation_med_frontline))
```

    [1] 2

**R tabanı dizin arama işlevleri**

R tabanı fonksiyonu olan `grepl()`, `str_detect()` fonksiyonuna benzer bir şekilde çalışır. Çünkü o da bir modelle eşleşmeleri arar ve mantıksal bir vektör döndürür. Temel sözdizimi `grepl(pattern, strings_to_search, ignore.case = FALSE, ...)` şeklindedir. Avantajlardan biri, `ignore.case` argümanını yazmanın daha kolay olmasıdır (`regex()` fonksiyonunu dahil etmeye gerek yoktur).

Benzer şekilde, R tabanı fonksiyonları olan `sub()` ve `gsub()`, `str_replace()`a benzer şekilde hareket eder. Temel sözdizimleri şöyledir: `gsub(pattern, replacement, strings_to_search, ignore.case = FALSE)`. `sub()` kalıbın ilk örneğini değiştirirken, `gsub()` kalıbın tüm örneklerini değiştirir.

#### Virgülleri noktalara dönüştürme

Burada, bir sayı vektöründe virgülleri noktalara dönüştürmek için `gsub()` kullanımına örnek verilmiştir. Bu durum özellikle verileriniz Amerika Birleşik Devletleri veya İngiltere dışındaki ülkelerden geliyorsa faydalı olabilir.

İlk olarak “lengths” üzerinde etkili olan komutun içindeki `gsub()` fonksiyonu, herhangi bir noktayı boşluksuz “” değerine dönüştürmektedir (silmektedir). Noktayı doğru tanımlamak için başına iki eğik çizgi “eklenmesi” gerekir çünkü normal “.” ifadesi “herhangi bir karakter” anlamına gelir. Ardından, sonuç (yalnızca virgülle), virgüllerin noktalarla değiştirildiği dış `gsub()` komutuna iletilir.

``` r
lengths <- c("2.454,56", "1,2", "6.096,5")

as.numeric(gsub(pattern = ",",                # virgülleri bul     
                replacement = ".",            # nokta ile değiştir
                x = gsub("\\.", "", lengths)  # binlik değerlerdeki noktaları kaldır
                )
           )                                  # çıktıyı sayısal bir değer olarak tanımla
```

### Tamamını değiştirme

“Bul ve değiştir” aracı olarak `str_replace_all()` kullanabilirsiniz. İlk Önce, `string =` olarak değerlendirilecek dizeleri, sonra değiştirilecek kalıbı `pattern =` olarak ve ardından değiştirme değerini `replacement =` olarak tanımlamanız gerekmektedir. Aşağıdaki örnek, tüm “dead” örneklerini “deceased” ile değiştirmektedir. Bu komuttaki argümanların büyük/küçük harfe duyarlı olduğunu unutmayın.

``` r
outcome <- c("Karl: dead",
            "Samantha: dead",
            "Marco: not dead")

str_replace_all(string = outcome, pattern = "dead", replacement = "deceased")
```

    [1] "Karl: deceased"      "Samantha: deceased"  "Marco: not deceased"

Notlar:

- Paternleri `NA` olarak değiştirmek için `str_replace_na()` fonksiyonunu kullanın.  
- `str_replace()` fonksiyonu her bir dizedeki sadece ilk paterni değiştirir, diğerlerini değiştirmez.

### Mantığa göre arama

**`case_when()` fonksiyonuyla**

`str_detect()` genellikle `case_when()` içinde kullanılır (**dplyr** paketinden). `occupations`ın satır listesindeki bir sütun olduğunu varsayalım. Aşağıda `mutate()`, `case_when()` fonksiyonları aracılığıyla koşullu mantığı kullanarak `is_educator` adında yeni bir sütun oluşturmaktayız. `case_when()` hakkında daha fazla bilgi edinmek için veri temizleme sayfasına bakabilirsiniz.

``` r
df <- df %>% 
  mutate(is_educator = case_when(
    # meslek içinde terim arama, büyük/küçük harfe duyarlı değil
    str_detect(occupations,
               regex("teach|prof|tutor|university",
                     ignore_case = TRUE))              ~ "Educator",
    # diğerleri
    TRUE                                               ~ "Not an educator"))
```

Bir hatırlatma olarak, koşullu mantığa dışlama kriterlerini(`negate = F`) eklemeniz işinizi kolaylaştırabilir:

``` r
df <- df %>% 
  # is_educator yeni sütunundaki değer koşullu mantığa dayalıdır
  mutate(is_educator = case_when(
    
    # Meslek sütununun "Educator" olarak atanabilmesi için 2 kriteri karşılaması gerekir:
    # bir arama terimine sahip olmalı VE herhangi bir dışlama terimi olmamalı
    
    # Bir arama terimi içermeli
    str_detect(occupations,
               regex("teach|prof|tutor|university", ignore_case = T)) &              
    
    # VE bir dışlama terimi İÇERMEMELİDİR
    str_detect(occupations,
               regex("admin", ignore_case = T),
               negate = TRUE)                       ~ "Educator",
    
    # Yukarıdaki kriterlere uymayan tüm satırlar
    TRUE                                            ~ "Not an educator"))
```

### Patern konumunu bulma

Bir paternin *ilk* konumunu bulmak için `str_locate()` kullanabilirsiniz. Fonksiyon çıktı olarak bir başlangıç ve bitiş konumu verir.

``` r
str_locate("I wish", "sh")
```

         start end
    [1,]     5   6

Diğer `str` fonksiyonları gibi, her dizede paterni karşılayan *bütün* örneklerin konumlarını döndürecek bir “\_all” versiyonu (`str_locate_all()`) mevcuttur. Bu fonksiyon bir liste çıktısı verir.

``` r
phrases <- c("I wish", "I hope", "he hopes", "He hopes")

str_locate(phrases, "h" )     # paternin *ilk* örneğinin konumu
```

         start end
    [1,]     6   6
    [2,]     3   3
    [3,]     1   1
    [4,]     4   4

``` r
str_locate_all(phrases, "h" ) # paternin *her* örneğinin konumu
```

    [[1]]
         start end
    [1,]     6   6

    [[2]]
         start end
    [1,]     3   3

    [[3]]
         start end
    [1,]     1   1
    [2,]     4   4

    [[4]]
         start end
    [1,]     4   4

### Eşleşeni çıkarma

`str_extract_all()` eşleşen kalıpların kendisini döndürür; bu fonksiyon, “VEYA” koşulları aracılığıyla birkaç kalıp önerdiğinizde en kullanışlı seçenektir. Örnek olarak, “teach”, “prof” *veya* “tutor” paternleri için meslekler vektörünü (önceki sekmeye bakın) inceleyebilirsiniz.

`str_extract_all()`, değerlendirilen her dize için *tüm eşleşmeleri* içeren bir “liste” döndürür. Aşağıda, 3. mesleğin içinde iki paternin nasıl eşleştiğini görebilirsiniz.

``` r
str_extract_all(occupations, "teach|prof|tutor")
```

    [[1]]
    character(0)

    [[2]]
    [1] "prof"

    [[3]]
    [1] "teach" "tutor"

    [[4]]
    [1] "tutor"

    [[5]]
    character(0)

    [[6]]
    character(0)

    [[7]]
    character(0)

    [[8]]
    character(0)

    [[9]]
    character(0)

    [[10]]
    character(0)

`str_extract()`, değerlendirilen her dizede *yalnızca ilk eşleşmeyi* ortaya çıkararak, değerlendirilen her dize için bir elemanlı bir karakter vektörü üretir. Eşleşmenin olmadığı yerde `NA` sonucunu döndürür. `NA`lar, döndürülen vektör `na.exclude()` fonksiyonu ile sarılarak kaldırılabilir. Çıkan sonuçta ikincisinin nasıl gösterilmediğine dikkat ediniz.

``` r
str_extract(occupations, "teach|prof|tutor")
```

     [1] NA      "prof"  "teach" "tutor" NA      NA      NA      NA      NA     
    [10] NA     

### Alt küme ve sayı

Bu başlıktaki fonksiyonlar arasında `str_subset()` ve `str_count()` bulunmaktadır.

`str_subset()` fonksiyonu paterni içeren gerçek değerleri döndürür:

``` r
str_subset(occupations, "teach|prof|tutor")
```

    [1] "university professor"           "primary school teacher & tutor"
    [3] "tutor"                         

`str_count()` bir sayı vektörü döndürür: Değerlendirilen her değerde bir arama teriminin göründüğü **miktar**.

``` r
str_count(occupations, regex("teach|prof|tutor", ignore_case = TRUE))
```

     [1] 0 1 2 1 0 0 0 0 0 0

### Regex grupları

HAZIRLANIYOR

## 10.6 Özel karakterler

**Ters eğik çizgi `\`**

Ters eğik çizgi `\` sonrasındaki karakteri “yok saymak” için kullanılır. Bu şekilde, diğer tırnak işaretleri (`\"`) *içinde* olan bir alıntı işaretini görüntülemek için bir ters eğik çizgi kullanılabilir - ortadaki alıntı işareti, çevreleyen alıntı işaretlerini “iptal etmez”.

Not - bu nedenle, bir ters eğik çizgi *görüntülemek* istiyorsanız için iki ters eğik çizgi `\\` yazmalısınız.

**Özel Karakterler**

| Özel Karakter | Anlamı |
|----|----|
| `"\\"` | ters eğik çizgi |
| `"\n"` | yeni satır |
| `"\""` | çift tırnak *içinde* çift tırnak |
| `'\''` | tek tırnak *içinde* tek tırnak |
| `"\`“`| ters tırnak (gravis) işareti`”`| satır başı`“`| sekme`”`| dikey sekme`“\` | geri alma |

Bu özel karakterlerin tam listesini görüntülemek için R Konsolunda `?"'"` komutunu çalıştırabilirsiniz (RStudio Yardım bölmesinde görünecektir).

## 10.7 Düzenli ifadeler (regex)

## 10.8 Regex ve özel karakterler

Düzenli ifadeler veya “regex”, dizelerdeki kalıpları açıklamak için kısa bir dildir. Eğer aşina değilseniz, düzenli ifadeler yabancı bir dil gibi görünebilir. Burada bu dili biraz gizeminden arındırmaya çalışacağız.

*[Bölümün çocuğu bu rehberden alınmıştır](https://towardsdatascience.com/a-gentle-introduction-to-regular-expressions-with-r-df5e897ca432) and [this cheatsheet](https://evoldyn.gitlab.io/evomics-2018/ref-sheets/R_strings.pdf)*. Bu el kitabının internet erişimi olmayan kişiler tarafından da görüntülenebileceğini ön görülerek burada önemli olanları paylaşıyoruz.

“Yapılandırılmamış” metinden belirli kalıplarını çıkarmak için genellikle düzenli bir ifade uygulanır - örneğin tıbbi notlar, hasta şikayetleri, geçmişi veya bir veri çerçevesindeki diğer serbest metin sütunları.

Temel bir düzenli ifade oluşturmak için kullanılabilecek dört araç vardır:

1.  Karakter setleri  
2.  Meta karakterler  
3.  Niceleyiciler  
4.  Grouplar

**Karakter setleri**

Karakter setleri, bir karakter eşleşmesi için köşeli parantez içinde listeleme seçeneklerini ifade etmenin bir yoludur. Bu nedenle, köşeli parantez içindeki karakterlerden herhangi biri dizede bulunursa eşleşme tetiklenir. Örneğin, sesli harfleri aramak için şu karakter seti kullanılabilir: “\[aeiou\]”. Diğer bazı yaygın karakter setleri şunlardır:

| Karakter Seti | Anlamı                                    |
|---------------|-------------------------------------------|
| `"[A-Z]"`     | herhangi bir tek büyük harf               |
| `"[a-z]"`     | herhangi bir tek küçük harf               |
| `"[0-9]"`     | herhangi bir rakam                        |
| `[:alnum:]`   | herhangi bir alfanümerik karakter         |
| `[:digit:]`   | herhangi bir sayısal rakam                |
| `[:alpha:]`   | herhangi bir harf (büyük veya küçük harf) |
| `[:upper:]`   | herhangi bir büyük harf                   |
| `[:lower:]`   | herhangi bir küçük harf                   |

Karakter setleri, `"[A-Za-z]"` (herhangi bir büyük veya küçük harf) veya başka bir örnek `"[t-z0-5]"` gibi tek bir parantez içinde (boşluksuz!) birleştirilebilir ( t’den z’ye kadar küçük harf VEYA 0’dan 5’e kadar sayılar).

**Meta karakterler**

Meta karakterler, karakter setlerinin kısaltmasıdır. Önemli olanlardan bazıları aşağıda listelenmiştir:

| Meta karakter | Anlamı                                                   |
|---------------|----------------------------------------------------------|
| `"\\s"`       | tek bir boşluk                                           |
| `"\\w"`       | herhangi bir tek alfanümerik karakter (A-Z, a-z, or 0-9) |
| `"\\d"`       | herhangi bir tek sayısal rakam (0-9)                     |

**Niceleyiciler**

Genellikle tek bir karakterde eşleşme aramak istemezsiniz. Niceleyiciler, eşleşmeye izin vermek için harflerin/sayıların uzunluğunu belirlemenize olanak tanır.

Niceleyiciler, nicelleştirdikleri karakterin *sonrasında* olan `{ }` küme parantezleri içinde yazılan sayılardır, örneğin,

- `"A{2}"` **iki** büyük A harfinin örneklerini döndürür.  
- `"A{2,4}"` **iki ile dört** arasında büyük A harfi *(boşluk koymayın!)* örneklerini döndürür.
- `"A{2,}"` **iki veya daha fazla** büyük A harfinin örneklerini döndürür.
- `"A+"` **bir veya daha fazla** büyük A harfinin örneklerini döndürür (farklı bir karakterle karşılaşılıncaya kadar uzatılan grup).  
- **Sıfır veya daha fazla** eşleşme döndürmek için bir `*` yıldız işareti ile başlayın (paternin mevcut olduğundan emin değilseniz kullanışlıdır)

Nicelik belirteci olarak ‘+’ artı sembolü kullanıldığında, farklı bir karakterle karşılaşılıncaya kadar eşleşme gerçekleşir. Örneğin, bu ifade tüm *kelimeleri* (alfa karakterleri: `"[A-Za-z]+"`) döndürür.

``` r
# niceleyiciler için test dizisi
test <- "A-AA-AAA-AAAA"
```

{2} niceleyicisi kullanıldığında, yalnızca ardışık A çiftleri döndürülür. “AAAA” içinde iki çift tanımlanmıştır.

``` r
str_extract_all(test, "A{2}")
```

    [[1]]
    [1] "AA" "AA" "AA" "AA"

{2,4} niceleyicisi kullanıldığında, uzunluğu iki ila dört olan ardışık A grupları döndürülebilir.

``` r
str_extract_all(test, "A{2,4}")
```

    [[1]]
    [1] "AA"   "AAA"  "AAAA"

“+” niceleyicisiyle, **bir veya daha fazla** gruplar döndürülebilir:

``` r
str_extract_all(test, "A+")
```

    [[1]]
    [1] "A"    "AA"   "AAA"  "AAAA"

**Relatif pozisyon**

Relatif pozisyon, bir kalıptan önce gelen veya onu izleyen bir kalıba göre konumu ifade eder. Örneğin, cümleleri çıkarmak için “sonunda bir nokta bulunan iki sayı” (`""`). (?\<=\\)\s(?=\[A-Z\])

``` r
str_extract_all(test, "")
```

    [[1]]
     [1] "A" "-" "A" "A" "-" "A" "A" "A" "-" "A" "A" "A" "A"

| Pozisyon Tanımı | Anlamı                            |
|-----------------|-----------------------------------|
| `"(?<=b)a"`     | **öncesinde** bir “b” bulunan “a” |
| `"(?<!b)a"`     | **Öncesinde** bir “b” olmayan “a” |
| `"a(?=b)"`      | **ardından** bir “b” gelen “a”    |
| `"a(?!b)"`      | **ardından** bir “b” gelmeyen “a” |

**Gruplar**

Düzenli ifadelerinizde grupları yakalamak, çıkarma işlemi sonrasında daha organize bir çıktı elde etmenin bir yoludur.

**Regex örnekleri**

Aşağıda örnekler için serbest bir metin bulunmaktadır. Bir düzenli ifade arama terimi kullanarak ondan faydalı bilgiler çıkarmaya çalışacağız.

``` r
pt_note <- "Patient arrived at Broward Hospital emergency ward at 18:00 on 6/12/2005. Patient presented with radiating abdominal pain from LR quadrant. Patient skin was pale, cool, and clammy. Patient temperature was 99.8 degrees farinheit. Patient pulse rate was 100 bpm and thready. Respiratory rate was 29 per minute."
```

Bu ifade tüm kelimelerle (boşluk gibi karakter olmayan bir karaktere ulaşana kadar herhangi bir karakter) eşleşir:

``` r
str_extract_all(pt_note, "[A-Za-z]+")
```

    [[1]]
     [1] "Patient"     "arrived"     "at"          "Broward"     "Hospital"   
     [6] "emergency"   "ward"        "at"          "on"          "Patient"    
    [11] "presented"   "with"        "radiating"   "abdominal"   "pain"       
    [16] "from"        "LR"          "quadrant"    "Patient"     "skin"       
    [21] "was"         "pale"        "cool"        "and"         "clammy"     
    [26] "Patient"     "temperature" "was"         "degrees"     "farinheit"  
    [31] "Patient"     "pulse"       "rate"        "was"         "bpm"        
    [36] "and"         "thready"     "Respiratory" "rate"        "was"        
    [41] "per"         "minute"     

`"[0-9]{1,2}"` ifadesi, 1 veya 2 basamak uzunluğunda ardışık sayılarla eşleşir. Ayrıca `"\\d{1,2}"` veya `"[:digit:]{1,2}"` şeklinde de yazılabilir.

``` r
str_extract_all(pt_note, "[0-9]{1,2}")
```

    [[1]]
     [1] "18" "00" "6"  "12" "20" "05" "99" "8"  "10" "0"  "29"

[Bu kopya kağıdının 2. sayfasında, normal ifadelerin ve ipuçlarının faydalı bir listesini görüntüleyebilirsiniz.](https://evoldyn.gitlab.io/evomics-2018/ref-sheets/R_strings.pdf)

[Ayrıca bu rehbere bakabilirsiniz](https://towardsdatascience.com/a-gentle-introduction-to-regular-expressions-with-r-df5e897ca432).

## 10.9 Kaynaklar

[**stringr** işlevleri için bir referans sayfası burada bulunabilir](https://evoldyn.gitlab.io/evomics-2018/ref-sheets/R_strings.pdf)

[**stringr** ile ilgili bir gösterim burada bulunabilir](https://cran.r-project.org/web/packages/stringr/vignettes/stringr.html)
