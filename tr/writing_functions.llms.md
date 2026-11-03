# 44  Yazma fonksiyonları

## 44.1 Hazırlık

### Paketleri yüklemek

Bu kod parçası, analizler için gerekli olan paketlerin yüklenmesini gösterir. Bu el kitabında, gerekirse paketi kuran *ve* kullanım için yükleyen **pacman**’dan `p_load()` vurgusu yapıyoruz. R **tabanı**ndan `library()` ile kurulu paketleri de yükleyebilirsiniz. R paketleri hakkında daha fazla bilgi için \[R basics\] sayfasına bakabilirsiniz.

### Verileri içe aktar

Simüle edilmiş bir Ebola salgınından vakaların veri setini içe aktarıyoruz. Adım adım izlenecek verileri indirmek istiyorsanız, \[Kitap ve verileri indir\] sayfasındaki talimatlara bakın. Veri kümesi, **rio** paketinden `import()` fonksiyonuyla kullanılarak içe aktarılır. Verileri içe aktarmanın çeşitli yolları için \[İçe ve dışa aktar\] hakkındaki sayfaya bakabilirsiniz.

Ayrıca bu sayfanın son bölümünde 2013’ten itibaren H7N9 gribiyle ilgili bazı verileri kullanacağız.

## 44.2 Fonksiyonlar

Fonksiyonlar, kodların daha kolay anlaşılmasını, bir şekilde daha kısa olmasını ve hataya daha az meyilli olmasını sağladıklarından (fonksiyonun kendisinde herhangi bir hata olmadığı göz önüne alındığında) programlamada faydalıdır.

Bu el kitabında bu kadar ileri gittiyseniz, R’da her işlem bir fonksiyon çağrısı olduğundan sonsuz fonksiyonlarla karşılaşmışsınız demektir. `+, for, if, [, $, { …`. Örneğin, “x + y”, “+”(x, y)” ile aynıdır

R, fonksiyonlarla en fazla çalışma olanağı sunan ve kullanıcıya bunları kolayca yazabilmesi için yeterli araçları sağlayan dillerden biridir. Fonksiyonları programlama zincirinin en üstünde veya sonunda sabit olarak düşünmemeliyiz, R onları vektörlermiş gibi kullanma ve hatta başka fonksiyonlar, listeler vb. içinde kullanma imkanı sunar.

Fonksiyonel programlama üzerine çok sayıda gelişmiş kaynak mevcuttur ve biz burada yalnızca kısa pratik örneklerle fonksiyonel programlamaya başlamanıza yardımcı olacak bir fikir vereceğiz. Daha sonra bu konuda daha fazla okumak için referanslardaki bağlantıları ziyaret etmeniz önerilir.

## 44.3 Neden bir fonksiyon kullanırsın?

Bu soruyu yanıtlamadan önce, bu el kitabının \[Yineleme, döngüler ve listeler\] sayfasındaki ilk R fonksiyonunuzu yazmak için ipuçlarına zaten sahip olduğunuzu belirtmek önemlidir. Aslında, “if/else” ve döngülerin kullanımı, genellikle birden fazla koşula izin vererek kodumuzun uygulamasını genişletmeye veya görevleri tekrarlamak için kodları yinelemeye kolayca yardımcı olduklarından, çoğu fonksiyonumuzun temel bir parçasıdır.

- Farklı bir değişkene veya verilere uygulamak için aynı kod bloğunu birden çok kez mi tekrarlıyorum?

- Ondan kurtulmak, genel kodumu önemli ölçüde kısaltır ve daha hızlı çalışmasını sağlar mı?

- Yazdığım kodun tekrar kullanılması ancak kodun birçok yerinde farklı bir değerle kullanılması mümkün müdür?

Önceki sorulardan birinin cevabı “EVET” ise, muhtemelen bir fonksiyon yazmanız gerekir.

## 44.4 R, fonksiyonları nasıl oluşturur?

R’daki fonksiyonların üç ana bileşeni vardır:

- fonksiyonu nasıl çağırabileceğimizi kontrol eden değişkenlerin listesi olan `formals()`

- fonksiyonun içindeki kod olan `body()`, yani nasıl yazdığımıza bağlı olarak parantez içinde veya devamında

ve,

- fonksiyonun değişkenlerini bulmaya yardımcı olacak ve fonksiyonun nasıl değer bulacağını belirleyen `environment()`.

Fonksiyonunuzu oluşturduktan sonra, ilişkili fonksiyonu çağırarak bu bileşenlerin her birini doğrulayabilirsiniz.

## 44.5 Temel sözdizimi ve yapı

- Bir fonksiyonun adını okuduğumuz anda işinin kolayca anlaşılması için düzgün bir şekilde adlandırılması gerekir. Aslında bu, temel R mimarisinin çoğunda zaten böyledir. ‘mean()’, ‘print()’, ‘summary()’ gibi fonksiyonların çok basit adları vardır.

- Bir fonksiyon, üzerinde çalışılacak veriler ve diğer seçenekler arasında statik değerler olabilen diğer nesneler gibi bağımsız değişkenlere ihtiyaç duyacaktır.

- Ve son olarak bir fonksiyon, temel görevine ve kendisine verilen değişkenlere dayalı olarak bir çıktı verecektir. Genellikle çıktıyı üretmek için yerleşik fonksiyonları `print()`, `return()`… olarak kullanırız. Çıktı, mantıksal bir değer, bir sayı, bir karakter, bir veri çerçevesi… kısacası herhangi bir R nesnesi olabilir.

Temel olarak bu, bir fonksiyonun bileşimidir:

``` r
function_name <- function(argument_1, argument_2, argument_3){
  
           function_task
  
           return(output)
}
```

`contain_covid19()` olarak adlandırılacak ilk fonksiyonumuzu oluşturabiliriz.

``` r
contain_covid19 <- function(barrier_gest, wear_mask, get_vaccine){
  
                            if(barrier_gest == "yes" & wear_mask == "yes" & get_vaccine == "yes" ) 
       
                            return("success")
  
  else("please make sure all are yes, this pandemic has to end!")
}
```

Daha sonra yeni oluşturulan fonksiyonumuzun bileşenlerini doğrulayabiliriz.

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

Şimdi fonksiyonumuzu test edeceğiz. Yazılı fonksiyonumuzu çağırmak için, onu tüm R fonksiyonlarını kullandığınız gibi, yani fonksiyon adını yazıp gerekli değişkenleri ekleyerek kullanabilirsiniz.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "yes")
```

    [1] "success"

Önlem amaçlı olarak her bir değişkenin adını tekrar yazabiliriz. Ancak bunları belirtmeden kod çalışmalıdır çünkü R bellekte her değişkenin konumu vardır. Değişkenlerin değerlerini doğru sıraya koyduğun sürece, fonksiyonları çağırırken değişken isimlerini yazmayı atlayabilirsiniz.

``` r
contain_covid19("yes", "yes", "yes")
```

    [1] "success"

O zaman değerlerden biri `"no"` veya `"yes"` **değil** ise ne olduğuna bakalım.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "no")
```

    [1] "please make sure all are yes, this pandemic has to end!"

Tanınmayan bir değişken sağlarsak bir hata alırız:

``` r
contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", get_vaccine = "no")
```

`Error in contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", : could not find function "contain_covid19"`

***NOT:*** Bazı fonksiyonlar(çoğu zaman çok kısa ve anlaşılır) bir ada ihtiyaç duymayabilir ve hızlı görev yapmak için doğrudan bir kod satırında veya başka bir fonksiyonun içinde kullanılabilir. Bunlara **anonim fonksiyonlar** denir.

Örneğin, aşağıdaki veri kümesinde yalnızca karakter değişkenlerini tutan ilk anonim fonksiyondur.

``` r
linelist %>% 
  dplyr::slice_head(n=10) %>%  #R tabanı "head" fonksiyonuna eşdeğerdir ve bu, veri kümesinin ilk n gözlemini döndürür
  select(function(x) is.character(x)) 
```

Daha sonra, veri setimizin her ikinci gözlemini seçen başka bir fonksiyon (örneğin, tarihe veya ziyarete göre sıralandıktan sonra hasta başına çok sayıda kayıt içeren boylamsal verilerimiz olduğunda alakalı olabilir). Bu durumda, dplyr dışına yazan uygun fonksiyon, tüm satır numaralarını içeren vektöre uygulanacak `function (x) (x%%2 == 0)` olacaktır.

``` r
linelist %>%   
   slice_head(n=20) %>% 
   tibble::rownames_to_column() %>% # son seçimi net bir şekilde görmek için her bir gözlemin indekslerini satır isimleri olarak ekleyin
   filter(row_number() %%2 == 0)
```

Aynı görev için olası bir temel R kodu şöyle olacaktır:

``` r
linelist_firstobs <- head(linelist, 20)

linelist_firstobs[base::Filter(function(x) (x%%2 == 0), seq(nrow(linelist_firstobs))),]
```

***UYARI:*** Fonksiyonları kullanmanın kodumuzda bize yardımcı olabileceği doğru olsa da, bazı fonksiyonları yazmak, iyice düşünülmemiş, yeterince yazılmamış ve sonuç olarak hatalar döndürüyorsa, o fonksiyonu düzeltmek zaman alıcı olabilir. Bu nedenle genellikle önce R kodunun yazılması, yapmak istediğimizi yaptığından emin olunması ve ardından yukarıda listelendiği gibi üç ana bileşeni ile bir fonksiyona dönüştürülmesi önerilir.

## 44.6 Örnekler

### Birkaç sütun için orantı tablolarını döndürmek

Evet, zaten birçok pakette bilgileri çok kolay ve güzel bir şekilde özetlememizi sağlayan güzel fonksiyonlarımız var. Ama yine de yazma fonksiyonlarına alışmak için ilk adımlarımızda kendimizinkini yapmaya çalışacağız.

Bu örnekte, basit bir fonksiyon yazmanın, aynı kodu defalarca kopyalayıp yapıştırmanızı nasıl önleyeceğini göstermek istiyoruz.

``` r
proptab_multiple <- function(my_data, var_to_tab){
  
  #tablolamayı yapmadan önce ilgilenilen her değişkenin adını yazdırın
  print(var_to_tab)

  with(my_data,
       rbind( #aşağıdaki iki fonksiyonun sonuçlarını satıra bağla
        #ilgilenilen değişkeni tablo haline getirin: sadece sayıları verir
          table(my_data[[var_to_tab]], useNA = "no"),
          #ilgilenilen her değişken için oranları hesaplayın ve değeri 2 ondalık basamağa yuvarlayın
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

***İPUCU:*** Yukarıda gösterildiği gibi, genel programlama için yaptığınız fonksiyonlarınızı yorumlamanız çok önemlidir. Bir fonksiyonun amacının bir kodu okunmaya hazır, daha kısa ve daha verimli hale getirmek olduğunu unutmayın. O zaman sadece adını okuyarak fonksiyonun ne yaptığını anlayabilmeli ve yorumları okuyarak daha fazla ayrıntıya sahip olmalıyız.

İkinci bir seçenek, işlemi bir kerede yapmak için bu fonksiyonu bir döngü aracılığıyla başka bir fonksiyonda kullanmaktır:

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

Daha basit bir yol, aşağıda ifade edildiği gibi “for loop” yerine R “apply” tabanını kullanmak olabilir:

***İPUCU:***R genellikle işlevsel bir programlama dili olarak tanımlanır ve neredeyse her zaman bir kod satırı çalıştırdığınızda bazı yerleşik fonksiyonları kullanırsınız. Yazma fonksiyonları konusunda daha rahat olmak için iyi bir alışkanlık, günlük olarak kullandığınız temel fonksiyonların nasıl oluşturulduğunu sık sık içsel olarak incelemektir. Bunu yapmanın kısayolu, fonksiyonun adını seçmek ve ardından `Ctrl+F2` veya `fn+F2` veya `Cmd+F2` (bilgisayarınıza bağlı olarak) üzerine tıklamaktır.

## 44.7 **purrr** kullanımı: yinelemeli olarak uygulanabilen yazma fonksiyonları

### Bir veri kümesindeki birden çok sütunun sınıfını değiştirin

Orijinal ‘satır listesi’ verilerindeki birçok karakter değişkeninin analiz ve çizim amaçları için “faktör” olarak değiştirilmesi gerektiğini varsayalım. Adımı birkaç kez tekrarlamak yerine, ilgili tüm değişkenlerin dönüşümünü tek bir kod satırında yapmak için sadece `lapply()` kullanabiliriz.

***UYARI:*** `lapply()` bir liste döndürür, bu nedenle kullanımı son adım olarak ek bir değişiklik gerektirebilir.

Aynı adım, **purrr** paketindeki `map_if()` fonksiyonu kullanılarak da yapılabilir.

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

### Değişkeninin farklı seviyeleri için yinelemeli olarak grafikler üretin

Her eyalet için H7N9 salgını sırasında Çin’de hastaların sonucunun dağılımına bakmak için burada pasta grafiği üreteceğiz. Her biri için kodu tekrarlamak yerine sadece oluşturacağımız bir fonksiyonu uygulayacağız.

``` r
#highchart kullanımı için kusursuz seçenekler
options(highcharter.theme =   highcharter::hc_theme_smpl(tooltip = list(valueDecimals = 2)))


#"chart_outcome_province" adında, veri kümesini ve sonucun dağılımını çizeceği ilin adını değişken olarak alan bir fonksiyon oluşturun.

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

### Bir değişkenin farklı seviyeleri için yinelemeli olarak tablolar üretin

Burada bir tablo halinde özetlemek için üç gösterge oluşturacağız ve bu tabloyu her il için üretmek istiyoruz. Göstergelerimiz, başlangıç ile hastaneye yatış arasındaki gecikme, iyileşme yüzdesi ve vakaların medyan yaşıdır.

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

#üç gösterge veri kümesine katılın

table_indic_all <- indic_1 %>% 
  dplyr::left_join(indic_2, by = "province") %>% 
        left_join(indic_3, by = "province")


#göstergeleri esnek bir tabloda yazdırın


print_indic_prov <-  function(table_used, prov){
  
  #önce yazdırma kolaylığı için veri çerçevesini biraz dönüştürün
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

## 44.8 İyi işleyen fonksiyonlar için ipuçları ve en iyi Uygulamalar

Fonksiyonel programlama, kodu kolaylaştırmak içindir ve okunmasını kolaylaştırır. Aşağıdaki ipuçları, temiz bir koda ve okunması kolay bir koda sahip olmanıza yardımcı olacaktır.

### Adlandırma ve sözdizimi

- Ortamınızda zaten mevcut olan diğer fonksiyonlar tarafından kolayca alınmış olabilecek karakterleri kullanmaktan kaçının

- Fonksiyon adının başka bir okuyucu için kısa ve anlaşılır olması önerilir.

- Fonksiyon adı olarak fiiller, değişken adları için isimler kullanılması tercih edilir.

### Sütun adları ve düzenli değerlendirme

Değişken olarak kodunuza sağlanan *sütun adlarına* nasıl başvuracağınızı öğrenmek istiyorsanız, bu [tidyverse programlama kılavuzunu](https://dplyr.tidyverse.org/articles/programming.html) okuyabilirsiniz. Kapsanan konular arasında *tidy evaluation* ve *embrace* `{ }` “çift ayraç” kullanımı yer alır.

Örneğin, hemen yukarıda bahsedilen sayfa eğitiminden hızlı bir iskelet şablon kodu:

``` r
var_summary <- function(data, var) {
  data %>%
    summarise(n = n(), min = min({{ var }}), max = max({{ var }}))
}
mtcars %>% 
  group_by(cyl) %>% 
  var_summary(mpg)
```

### Test ve Hata işleme

Bir fonksiyonun görevi ne kadar karmaşıksa, hata olasılığı da o kadar yüksek olur. Bu nedenle, bazen hatanın nereden geldiğini hızlı bir şekilde anlamaya ve düzeltmenin bir yolunu bulmaya yardımcı olmak için fonksiyona bazı doğrulamalar eklemek gerekir.

- `missing(değişken)` kullanarak bir değişkenin eksikliğini kontrol etmek şiddetle tavsiye edilmektedir. Bu basit kontrol, “TRUE” veya “FALSE” değerini döndürebilir.

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

- Daha fazla algılanabilir hata için `stop()` kullanın.

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

- Yerleşik fonksiyonların çoğunu çalıştırdığımızda gördüğümüz gibi, belirli koşullarda açılabilen mesajlar ve uyarılar vardır. Bunları yazılı fonksiyonlarımıza `message()` ve `warning()` fonksiyonlarını kullanarak entegre edebiliriz.

- Bir fonksiyonu değişken olarak alan ve onu güvenli bir şekilde yürüten `safely()` kullanarak da hataları halledebiliriz. Aslında, bir hatayla karşılaşırsa fonksiyon durmadan yürütülür. `safely()` çıktı olarak, sonuçlar ve “atladığı” hata olan iki nesne içeren bir **liste** döndürür.

Önce `mean()` fonksiyonunu fonksiyon olarak çalıştırıp sonra `safely()` ile çalıştırarak doğrulayabiliriz.

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

Daha önce de belirtildiği gibi, kodlarımızı iyi yorumlamak, çalışmalarımızda dokümantasyona sahip olmak için zaten iyi bir yoldur.

## 44.9 Kaynaklar

[Veri Bilimi için R](https://r4ds.had.co.nz/functions.html)

[İleri R Programlama Pratik Kılavuzu](https://www.rstudio.com/wp-content/uploads/2016/02/advancedR.pdf)

[purr Paket Pratik Kılavuzu](https://purrr.tidyverse.org/)

[Hadley Wickham’dan Video-ACM konuşması: Fonksiyonel programlamanın keyfi (map_dbl nasıl çalışır?)](https://youtube.videoken.com/embed/bzUmK0Y07ck)
