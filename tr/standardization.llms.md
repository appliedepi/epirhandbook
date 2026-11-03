# 21  Standardize edilmiş hızlar

Bu sayfa, hastaneye yatış veya ölüm oranları gibi bir çıktıyı yaş ve cinsiyet gibi özelliklere göre nasıl standardize edeceğinizi gösterecektir.

Bu sayfa **PHEindicatormethods** paketini kullanır.

Birden fazla ülkeden nüfus verileri, standart nüfus verileri, ölümler vb. birleştirilmesi için yaygın kullanımı olduğu için, veri hazırlama/temizleme/birleştirme süreçlerini kapsamlı bir şekilde göstererek başlıyoruz.

## 21.1 Genel bakış

Standardizasyonun iki ana yöntemi vardır: Direkt ve indirekt standardizasyon. A ve B ülkeleri için ölüm hızlarını yaşa ve cinsiyete göre standardize etmek ve bu ülkeler arasındaki standardize edilmiş oranları karşılaştırmak istediğimizi varsayalım.

- Direk standardizasyon için, A ülkesi ve B ülkesi için her yaş ve cinsiyet tabakası için risk altındaki popülasyon büyüklüğüve ölümlerin sayısını bilmeniz gerekecektir. Örneğimizdeki bir katman 15-44 yaş arası kadınlar olabilir.
- İndirekt standardizasyon için, her ülkenin toplam ölüm sayısı, yaş ve cinsiyet yapısını bilmeniz gerekir. Dolayısıyla bu seçenek, yaşa ve cinsiyete özgü ölüm hızları veya nüfus sayıları mevcut değilse uygulanabilir. Direkt standardizasyondaki tahminler örneklem varyasyonundan etkileneceğinden; tabaka başına küçük sayıların olması durumunda indirekt standardizasyon tercih edilir.

## 21.2 Hazırlık

Standardizasyonun nasıl yapıldığını göstermek için, A ve B ülkelerinin yaşa (5 yıllık tabakalar halinde) ve cinsiyete (kadın, erkek) göre kurgusal nüfus büyüklükleri ve ölüm sayımlarını kullanacağız. Veri setlerini kullanıma hazır hale getirmek için aşağıdaki hazırlık adımlarını gerçekleştireceğiz:

1.  Paketlerin yüklenmesi  
2.  Veri tabanlarının yüklenmesi
3.  İki ülkenin nüfus ve ölüm verilerini birleştirilmesi
4.  Yaş-cinsiyet katmanı başına bir satır olacak şekilde daha uzun şekilde pivotlama
5.  Referans popülasyonunu (dünya standart nüfusu) temizleme ve ülke verilerine ekleme

Senaryonuzda, verileriniz farklı bir biçimde gelebilir. Belki verileriniz il, şehir veya başka bir hizmet alanına göre düzenlenmiştir. Her ölüm için bir satır ve bu ölümlerin her biri (veya önemli bir kısmı) için yaş ve cinsiyet bilgileri olabilir. Bu durumda, yaş-cinsiyet katmanlarına göre olay ve nüfus sayıları içeren bir veri tabanı oluşturmak için \[Verileri gruplandırma\], \[Verileri pivotlama\] ve \[Tanımlayıcı tablolar\] sayfalarına bakın.

Ayrıca bir referans popülasyona, standart popülasyona ihtiyacımız vardır. Bu alıştırma için `world_standard_population_by_sex`’i kullanacağız. Dünya standart nüfusu, 46 ülkenin nüfusuna dayanmaktadır ve 1960 yılında geliştirilmiştir. Birçok “standart” popülasyon vardır - bir örnek olarak, [NHS İskoçya’nın web sitesi](https://www.opendata.nhs.scot/dataset/standard-populations) Avrupa Standart Nüfusu, Dünya Standart Nüfusu ve İskoçya Standardı hakkında detaylı bilgi içermektedir. (European Standard Population, World Standard Population and Scotland Standard Population).

### Paketlerin yüklenmesi

Bu kod kümesi, analizler için gereken paketlerin yüklenmesini gösterir. Bu el kitabında, gerekirse paketi kuran ve kullanım için yükleyen **pacman**’ın `p_load()` fonksiyonunu vurguluyoruz. Ayrıca, R tabanından `library()` ile kurulu paketleri yükleyebilirsiniz. R paketleri hakkında daha fazla bilgi için \[R’ın temelleri\] sayfasına bakın.

``` r
pacman::p_load(
     rio,                 # verileri içe/dışa aktar
     here,                # dosyaları bul
     stringr,             # karakterleri ve dizeleri (string) temizleme
     PHEindicatormethods, # hızların  standardizasyonu için alternatif
     tidyverse,           # veri yönetimi ve görselleştirme
     appliedepidata) # bu el kitabında kullanılan örnek veriler
```

### Popülasyon verisinin yüklenmesi

El kitabındaki tüm örnek verilerin nasıl indirileceğine ilişkin talimatlar için \[Verilerin ve el kitabının indirilmesi\] sayfasına bakın. Standardizasyon sayfası verilerini aşağıdaki `appliedepidata::get_data()` çağrılarıyla doğrudan R’a aktarabilirsiniz:

``` r
# A ülkesi için demografik veriyi doğrudan Github'dan içe aktarın
A_demo <- appliedepidata::get_data(name = "country_demographics")

# A ülkesi için ölümleri doğrudan Github'dan içe aktarın
A_deaths <- appliedepidata::get_data(name = "deaths_countryA")

# B ülkesi için demografik veriyi doğrudan Github'dan içe aktarın
B_demo <- appliedepidata::get_data(name = "country_demographics_2")

# B ülkesi için ölümleri doğrudan Github'dan içe aktarın
B_deaths <- appliedepidata::get_data(name = "deaths_countryB")

# B ülkesi için demografik veriyi doğrudan Github'dan içe aktarın
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

İlk önce karşılaştıracağımız iki ülke olan “Ülke A” ve “Ülke B” için demografik verileri (5 yıllık yaş kategorisine göre kadın ve erkek sayıları) yüklüyoruz.

``` r
# A ülkesi
A_demo <- appliedepidata::get_data(name = "country_demographics")
```

``` r
# B ülkesi
B_demo <- appliedepidata::get_data(name = "country_demographics_2")
```

### Ölüm sayılarının yüklenmesi

Elimizde uygun bir şekilde, ilgilenilen zaman dilimindeki yaş ve cinsiyete göre ölüm sayıları da bulunmaktadır. Her ülkenin ölüm sayıları aşağıda gösterilen ayrı bir dosyadadır.

A Ülkesindeki Ölümler

B Ülkesindeki Ölümler

### Nüfus ve ölüm verilerinin temizliği

Bu verileri aşağıdaki şekillerde birleştirmemiz ve dönüştürmemiz gerekiyor:

- Ülke popülasyonlarını tek bir veri tabanında birleştirin ve her bir yaş-cinsiyet katmanının bir satır olması için “uzun” şekilde pivotlayın
- Ülke ölüm sayılarını tek bir veri tabanında birleştirin ve her bir yaş-cinsiyet katmanının bir satır olması için “uzun” şekilde pivotlayın
- Ölümleri nüfusla birleştirin

İlk olarak, ülke popülasyonları veri tabanlarını birleştirip, daha sonra uzun biçimde pivotlar ve temizlik yaparız. Daha fazla ayrıntı için \[Verilerin pivotlanması\] sayfasına bakın.

``` r
pop_countries <- A_demo %>%  # A ülkesi veritabanı ile başla
     bind_rows(B_demo) %>%        # Satırları B veri tabanıyla bağla, çünkü sütunlar aynı şekilde adlandırılır
     pivot_longer(                       # uzun şekilde pivotlama
          cols = c(m, f),                   # birleştirilecek sütunlar
          names_to = "Sex",                 # kategoriyi ("m" veya "f") içeren yeni sütunun adı 
          values_to = "Population") %>%     # özetlenen sayısal değerleri içeren yeni sütunun adı
     mutate(Sex = recode(Sex,            # anlaşılması için değerleri yeniden kodla
          "m" = "Male",
          "f" = "Female"))
```

Birleşik nüfus verileri şimdi şöyle görünür (A ve B ülkelerini görmek için tıklayın):

Şimdi de iki ölüm veri setinde benzer işlemler yapıyoruz.

``` r
deaths_countries <- A_deaths %>%    # A ülkesi ölüm veritabanı ile başlayın
     bind_rows(B_deaths) %>%        # Satırları B veri tabanıyla bağla, çünkü sütunlar aynı şekilde adlandırılır
     pivot_longer(                  # uzun şekilde pivotlama
          cols = c(Male, Female),        # birleştirilecek sütunlar
          names_to = "Sex",              # kategoriyi ("m" veya "f") içeren yeni sütunun adı
          values_to = "Deaths") %>%      # özetlenen sayısal değerleri içeren yeni sütunun adı
     rename(age_cat5 = AgeCat)      # anlaşılması için değerleri yeniden kodla
```

Ölüm verileri şimdi böyle görünüyor ve her iki ülkeden de veriler içermekte:

Şimdi `Country`, `age_cat5` ve `Sex` ortak sütunlarına dayalı ölüm ve nüfus verilerini birleştiriyoruz. Bu işlem, `Deaths` sütununu ekler.

``` r
country_data <- pop_countries %>% 
     left_join(deaths_countries, by = c("Country", "age_cat5", "Sex"))
```

Artık `Sex`, `age_cat5` ve `Country`’yi faktör olarak sınıflandırabilir ve \[Faktörler\] sayfasında açıklandığı gibi **forcats** paketinden `fct_relevel()` fonksiyonunu kullanarak seviye sırasını ayarlayabiliriz. Unutulmamalıdır ki, faktör seviyelerinin sınıflandırılması verileri gözle görülür şekilde değiştirmez, ancak `arrange()` komutu verileri ülkeye, yaş kategorisine ve cinsiyete göre sıralar.

``` r
country_data <- country_data %>% 
  mutate(
    Country = fct_relevel(Country, "A", "B"),
      
    Sex = fct_relevel(Sex, "Male", "Female"),
        
    age_cat5 = fct_relevel(
      age_cat5,
      "0-4", "5-9", "10-14", "15-19",
      "20-24", "25-29",  "30-34", "35-39",
      "40-44", "45-49", "50-54", "55-59",
      "60-64", "65-69", "70-74",
      "75-79", "80-84", "85")) %>% 
          
  arrange(Country, age_cat5, Sex)
```

***DİKKAT:*** Her tabakada az sayıda ölüm varsa, yaşa göre 5 yıllık kategoriler yerine 10 veya 15 yıllık kategorileri kullanmayı düşünün.

### Referans popülasyonun yüklenmesi

Son olarak, direkt standardizasyon için referans popülasyonu (cinsiyete göre dünya “standart nüfusu”) içe aktarıyoruz.

``` r
# Referans popülasyon
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

### Referans popülasyon verisinin temizliği

`country_data` ve `standard_pop_data` veri çerçevelerindeki yaş kategorisi değerlerinin hizalanması gerekir.

Şu anda, `standard_pop_data` veri çerçevesinden `age_cat5` sütununun değerleri “yıllar” ve “artı” kelimelerini içerirken `country_data` veri çerçevesindeki sütun bu kelimeleri içermemektedir. Yaş kategorisi değerlerini eşleştirmemiz gerekecek. Bu kalıpları boşluksuz olarak `""` biçiminde değiştirmek için \[Karakterler ve dizeler\] sayfasında açıklandığı gibi **stringr** paketinden `str_replace_all()` komutunu kullanıyoruz.

`calculate_dsr()` fonksiyonu standart popülasyonu `stdpop =` argümanı ile alır, bu yüzden sütun herhangi bir ada sahip olabilir. Aşağıdaki kod `stdpop = pop` kullandığı için bu sütunu `"pop"` olarak yeniden adlandırıyoruz.

``` r
# Sütun değerlerinden belirli dizeyi kaldır
standard_pop_clean <- standard_pop_data %>%
     mutate(
          age_cat5 = str_replace_all(age_cat5, "years", ""),   # "year"'ı kaldır
          age_cat5 = str_replace_all(age_cat5, "plus", ""),    # "plus"'ı kaldır
          age_cat5 = str_replace_all(age_cat5, " ", "")) %>%   # " " boşluğu kaldır
     
     rename(pop = WorldStandardPopulation)   # sütun adını "pop" olarak değiştir, calculate_dsr() içinde stdpop = ile verilen sütun
```

***DİKKAT:*** Bir artı *sembolünü* kaldırmak için `str_replace_all()` kullanmayı denerseniz, özel bir sembol olduğu için çalışmayacaktır. `str_replace_call(column, "\\+", "")` örneğinde olduğu gibi önüne iki ters eğik çizgi koyarak özel özelliklerden kaçınabilirsiniz.

### Standart popülasyon ile veri tabanının oluşturulması

Son olarak, [aşağıda](#standard_phe) ayrıntıları verilen **PHEindicatormethods** paketi, ülke için gerçekleşen olay (ölüm), nüfus sayıları ve standart popülasyon verilerini istemektedir. Bu amaçla bir `all_data` veri tabanı oluşturacağız.

``` r
all_data <- left_join(country_data, standard_pop_clean, by=c("age_cat5", "Sex"))
```

Tam veri tabanı bu şekilde görülmektedir:

## 21.3 **PHEindicatormethods** paketi

Standardize hızları **PHEindicatormethods** paketi ile hesaplıyoruz. Bu paket, direkt ve indirekt olarak standardize edilmiş hızları hesaplamanıza olanak tanır. İkisini de göstereceğiz.

Bu bölüm, Hazırlık bölümünün sonunda oluşturulan `all_data` veri tabanını kullanacaktır. Bu veri tabanı, ülke popülasyonlarını, ölüm olaylarını ve dünya için standart referans popülasyonu içerir. [Burada](#standard_all) görüntüleyebilirsiniz.

### Direkt standardize edilmiş hızlar

Aşağıda, önce verileri ülkeye göre gruplandırıyoruz ve ardından ülke başına direkt standardize edilmiş hızları elde etmek için `calculate_dsr()` fonksiyonuna aktarıyoruz.

Not: `calculate_dsr()`, referans (standart) popülasyonun **ülkeye özgü veri tabanında bir sütun** olarak verilmesini gerektirir. Bu sütunun adını `stdpop =` argümanında belirtin. Aşağıdaki örneğimizde bu sütun `pop` sütunudur.

Daha fazla bilgi için `?calculate_dsr` ile ilgili yardıma veya Referanslar bölümündeki bağlantılara bakabilirsiniz

``` r
# yaş ve cinsiyet için direkt standardize edilmiş hızları ülke başına hesapla
mortality_ds_rate_phe <- all_data %>%
     group_by(Country) %>%
     PHEindicatormethods::calculate_dsr(
          x = Deaths,                 # gözlemlenen olay sayısını içeren sütun
          n = Population,             # her tabaka için standart olmayan nüfusu içeren sütunlar
          stdpop = pop)               # her tabaka için standart popülasyonlar

# Tabloyu yazdır
knitr::kable(mortality_ds_rate_phe)
```

| Country | total_count | total_pop | value | lowercl | uppercl | confidence | statistic | method |
|:---|---:|---:|---:|---:|---:|:---|:---|:---|
| A | 11344 | 86790567 | 23.56686 | 23.08107 | 24.05944 | 95% | dsr per 100000 | Dobson |
| B | 9955 | 52898281 | 19.32549 | 18.45516 | 20.20882 | 95% | dsr per 100000 | Dobson |

### İndirekt standardize edilmiş hızlar

İnidirekt standardizasyon için, tabaka başına ölüm sayısı, nüfus ve bir referans popülasyona ihtiyacınız vardır. Bu örnekte, `standard_pop_clean` referans popülasyonu tabaka başına ölüm sayısını içermediğinden, *B ülkesini referans popülasyon* olarak kullanarak A ülkesi için hızları hesaplayacağız.

Aşağıda, önce B ülkesinden referans popülasyonu oluşturuyoruz. Ardından, A ülkesi için ölüm ve nüfus verilerini çıkarıyoruz, bu verileri referans popülasyonla birleştiriyoruz ve indirekt standardize edilmiş hızları elde etmek için `calculate_ISRate()` fonksiyonuna aktarıyoruz. Tabii ki, bunun tersini de yapabilirsiniz.

Not: Aşağıdaki örneğimizde, referans popülasyonu ayrı bir veri tabanı olarak verilmiştir. Bu durumda, kayıtlar pozisyona göre eşleştirileceğinden, `x =`, `n =`, `x_ref =` ve `n_ref =` vektörlerinin tümünün, ülkemize özgü veri tabanıyla aynı standardizasyon kategorisi (tabaka) değerlerine göre sıralandığından emin oluruz.

Daha fazla bilgi için `?phr_isr` komutu ile ilgili yardıma veya Referanslar bölümündeki bağlantılara bakın.

``` r
# Referans popülasyonu oluştur
refpopCountryB <- country_data %>% 
  filter(Country == "B") 

# A ülkesi için yaş ve cinsiyete göre indirekt standardize edilmiş hızları hesapla
mortality_is_rate_phe_A <- country_data %>%
     filter(Country == "A") %>%
     PHEindicatormethods::calculate_ISRate(
          x = Deaths,                 # gözlemlenen olay sayısını içeren sütun
          n = Population,             # her tabaka için standardize edilmemiş popülasyonu içeren sütunlar
          x_ref = refpopCountryB$Deaths,  # her tabaka için referans ölüm sayısı
          n_ref = refpopCountryB$Population)  # her tabaka için referans popülasyon

# Tabloyu yazdır
knitr::kable(mortality_is_rate_phe_A)
```

| observed | expected | ref_rate | value | lowercl | uppercl | confidence | statistic | method |
|---:|---:|---:|---:|---:|---:|:---|:---|:---|
| 11344 | 15847.42 | 18.81914 | 13.47123 | 13.22446 | 13.72145 | 95% | indirectly standardised rate per 100000 | Byars |

## 21.4 Kaynaklar

**PHEindicatormethods** paketini kullanan başka bir örnek için lütfen [bu web sitesine](https://mran.microsoft.com/snapshot/2018-10-22/web/packages/PHEindicatormethods/vignettes/IntroductiontoPHEindicatormethods.html) gidin.

**PHEindicatormethods** referans [pdf dosyasına](https://cran.r-project.org/web/packages/PHEindicatormethods/PHEindicatormethods.pdf) bakın.
