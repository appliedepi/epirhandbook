# 50  Veri tablosu

El kitabı, verileri temizleme ve gruplama yöntemi olarak **dplyr** “verb” fonksiyonlarına ve **magrittr** tünel operatörü `%>%` üzerine odaklanır, ancak **data.table** paketi kullanabileceğiniz bir alternatif mevcuttur.

## 50.1 Veri tablolarına giriş

Bir veri tablosu, karmaşık gruplama işlemlerinin gerçekleştirilmesine izin veren bir veri çerçevesi gibi 2 boyutlu bir veri yapısıdır. data.table sözdizimi, satırlar, sütunlar ve gruplar üzerinde işlemler gerçekleştirilebilecek şekilde yapılandırılmıştır.

Yapı **DT\[i, j, by\]** şeklindedir ve 3 parça ile ayrılmıştır; **i, j** ve **by** değişkenleri. **i** değişkeni gerekli satırların alt kümelenmesine, **j** değişkeni sütunlar üzerinde işlem yapmanıza ve **by** değişkeni sütunlar üzerinde gruplara göre işlem yapmanıza olanak tanır.

Bu sayfa aşağıdaki konuları ele alacaktır:

- Verileri içe aktarma ve `fread()` ve `fwrite()` kullanımı
- **i** değişkenini kullanarak satırları seçme ve filtreleme
- `%like%`, `%chin%`, `%between%` yardımcı fonksiyonlarını kullanma
- **j** değişkenini kullanarak sütunları seçme ve hesaplama
- **by** değişkenini kullanan gruplara göre hesaplama
- `:=` kullanarak veri tablolarına veri ekleme ve güncelleme

## 50.2 Paketleri yükleyin ve verileri içe aktarın

### Paketleri yükleyin

**pacman**’den `p_load()` fonksiyonunu kullanarak, bu analiz için gerekli paketleri yükleriz (ve gerekirse kurarız).

``` r
pacman::p_load(
  data.table, # verileri gruplamak ve temizlemek için
  tidyverse   # bu bölümde tünelleme (%>%) fonksiyonunun kullanılmasına izin verir
  ) 
```

### Verileri içe aktar

Bu sayfa, el kitabında atıfta bulunulan vaka satır listesini kullanarak **data.table**’ın bazı temel fonksiyonlarını keşfedecektir.

Simüle edilmiş bir Ebola salgınından vakaların veri setini içe aktarıyoruz. Doğrudan `appliedepidata::get_data(name = "linelist_cleaned_excel")` ile yükleyin (ayrıntılar için [El kitabı ve veri indirme](download.llms.md) sayfasına bakın). Buradan veri çerçevesini bir veri tablosuna dönüştürmek için `data.table()` kullanıyoruz.

``` r
linelist <- appliedepidata::get_data(name = "linelist_cleaned_excel") %>% data.table()
```

‘fread()’ fonksiyonu, .csv dosyaları gibi normal sınırlandırılmış dosyaları doğrudan bir veri tablosu biçimine içe aktarmak için kullanılır. Data.tables’ı düzenli sınırlandırılmış dosyalar olarak yazmak için kullanılan bu işlev ve muadili ‘fwrite()’, büyük veritabanları için çok hızlı ve hesaplama açısından verimli seçeneklerdir.

“linelist”in ilk 20 satırı:

Veri çerçeveleri için kullanılan ‘dim()’ gibi R Tabanı komutları, veri tabloları için de kullanılabilir.

``` r
dim(linelist) #veri tablosundaki satır ve sütun sayısını verir
```

    [1] 5888   30

## 50.3 i değişkeni: satırları seçme ve filtreleme

**DT\[i, j, by\]** yapısını hatırlayarak, satır numaralarını veya mantıksal ifadeleri kullanarak satırları filtreleyebiliriz. i değişkeni ilk; bu nedenle, **DT\[i\]** veya **DT\[i,\]** sözdizimi kullanılabilir.

İlk örnek veri tablosunun ilk 5 satırını alır, ikinci örnek alt küme vakaları 18 yaş ve üzeridir ve üçüncü örnek alt kümeler 18 yaş veya üzeri ancak Merkez Hastanede teşhis edilmemiş vakaları içerir:

``` r
linelist[1:5] #1.ila 5. satır arasını getirir
linelist[age >= 18] #alt küme vakaları 18 yaşa eşit veya daha büyük
linelist[age >= 18 & hospital != "Central Hospital"] #18 yaşına eşit veya daha büyük ancak Merkez Hastanede teşhis edilmemiş alt kümeler
```

i bağımsız değişkeninde .N kullanılması, veri tablosundaki toplam satır sayısını temsil eder. Bu, satır numaralarını alt kümelemek için kullanılabilir:

``` r
linelist[.N] #son satırı getirir
linelist[15:.N] #15. satırdan son satıra kadar getirir
```

### Filtreleme için yardımcı fonksiyonları kullanma

Veri tablosu, alt küme satırlarını kolaylaştıran yardımcı fonksiyonları kullanır. ‘%like%’ bir sütundaki kalıbı eşleştirmek için kullanılır, ‘%chin%’ belirli bir karakteri eşleştirmek için kullanılır ve ‘%between%’ önceden belirlenmiş bir aralıktaki sayısal sütunları eşleştirmek için kullanılır.

Aşağıdaki örneklerde: \* hastane değişkeninin “Hastane” içerdiği satırları filtreleyin \* sonucun “İyileşme” veya “Ölüm” olduğu satırları filtreleyin \* 40-60 yaş aralığındaki satırları filtreleyin

``` r
linelist[hospital %like% "Hospital"] #hastane değişkeninin "Hastane" içerdiği satırları filtreleyin
linelist[outcome %chin% c("Recover", "Death")] #sonucun "İyileşme" veya "Ölüm" olduğu satırları filtreleyin
linelist[age %between% c(40, 60)] #40-60 yaş aralığındaki satırları filtreleyin

#%between% 2 uzunlukta bir vektör almalıdır, oysa %chin% >= 1 uzunlukta vektörler alabilir
```

## 50.4 j değişkeni: sütunları seçme ve hesaplama

**DT\[i, j, by\]** yapısını kullanarak sayıları veya isimleri kullanarak sütunları seçebiliriz. **j** değişkeni ikinci sıradadır; bu nedenle **DT\[, j\]** sözdizimi kullanılır. **j** değişkenindeki hesaplamaları kolaylaştırmak için, ‘list()’ ya da ‘.()’ kullanılarak sütun sarılır.

### Sütunları seçme

İlk örnek, veri tablosunun birinci, üçüncü ve beşinci sütunlarını alır; ikinci örnek, boy, ağırlık ve cinsiyet sütunları dışındaki tüm sütunları seçer. Üçüncü örnek, **case_id** ve **outcome** sütunlarını seçmek için `.()` sarmasını kullanır.

``` r
linelist[ , c(1,3,5)]
linelist[ , -c("gender", "age", "wt_kg", "ht_cm")]
linelist[ , list(case_id, outcome)] #linelist[ , .(case_id, outcome)] aynı şekilde çalışır
```

### Sütunlarda hesaplama

**i** ve **j** değikenlerini birleştirerek, satırları filtrelemek ve sütunlarda hesaplama yapmak mümkündür. **j** değişkeninde **.N** kullanılması ayrıca veri tablosundaki toplam satır sayısını temsil eder ve satır filtrelemeden sonra satır sayısını döndürmek için yararlı olabilir.

Aşağıdaki örneklerde: \* Hastanede 7 günden fazla kalan vaka sayısını sayın \* Askeri hastanede ölen vakaların yaş ortalamasını hesaplayın \* Merkez hastanede iyileşen vakaların standart sapma, ortanca, yaş ortalamasını hesaplayın

``` r
linelist[days_onset_hosp > 7 , .N]
```

    [1] 189

``` r
linelist[hospital %like% "Military" & outcome %chin% "Death", .(mean(age, na.rm = T))] #na.rm = T siler N/A değerleri
```

            V1
         <num>
    1: 15.9084

``` r
linelist[hospital == "Central Hospital" & outcome == "Recover", 
                 .(mean_age = mean(age, na.rm = T),
                   median_age = median(age, na.rm = T),
                   sd_age = sd(age, na.rm = T))] #bu sözdizimi yardımcı fonksiyonları kullanmaz ancak aynı şekilde çalışır
```

       mean_age median_age   sd_age
          <num>      <num>    <num>
    1: 16.85185         14 12.93857

j değişkeninde .() sarma kullanmanın hesaplamayı kolaylaştırdığını, bir veri tablosu döndürdüğünü ve sütun adlandırmasına izin verdiğini unutmayın.

## 50.5 Değişkene göre: gruplara göre hesaplama

**by** değişkeni, **DT\[i, j, by\]** yapısındaki üçüncü değişkendir. **by** değişkeni hem bir karakter vektörünü hem de ‘list()’ veya ‘.()’ sözdizimini kabul eder. **by** değişkeninde `.()` sözdizimini kullanmak, anında sütun yeniden adlandırılmasına izin verir.

Aşağıdaki örneklerde: \* vaka sayısını hastaneye göre gruplandırın \* 18 yaş ve üzeri vakalarda cinsiyete göre vakaların ortalama boy ve kilolarını, iyileşip ölmediklerini hesaplayın \* 7 günü aşan başvurularda, vaka sayısını yattığı aya ve yattığı hastaneye göre sayısını hesaplayın

``` r
linelist[, .N, .(hospital)] #hastaneye göre vaka sayıları
```

                                   hospital     N
                                     <char> <int>
    1:                                Other   885
    2:                              Missing  1469
    3: St. Mark's Maternity Hospital (SMMH)   422
    4:                        Port Hospital  1762
    5:                    Military Hospital   896
    6:                     Central Hospital   454

``` r
linelist[age > 18, .(mean_wt = mean(wt_kg, na.rm = T),
                             mean_ht = mean(ht_cm, na.rm = T)), .(gender, outcome)] #NAs, verilerin eksik olduğu kategorileri temsil eder
```

       gender outcome  mean_wt  mean_ht
       <char>  <char>    <num>    <num>
    1:      m Recover 71.90227 178.1977
    2:      f   Death 63.27273 159.9448
    3:      m   Death 71.61770 175.4726
    4:      f    <NA> 64.49375 162.7875
    5:      m    <NA> 72.65505 176.9686
    6:      f Recover 62.86498 159.2996
    7:   <NA> Recover 67.21429 175.2143
    8:   <NA>   Death 69.16667 170.7917
    9:   <NA>    <NA> 70.25000 175.5000

``` r
linelist[days_onset_hosp > 7, .N, .(month = month(date_hospitalisation), hospital)]
```

        month                             hospital     N
        <num>                               <char> <int>
     1:     5                    Military Hospital     3
     2:     6                        Port Hospital     4
     3:     7                        Port Hospital     8
     4:     8 St. Mark's Maternity Hospital (SMMH)     5
     5:     8                    Military Hospital     9
     6:     8                                Other    10
     7:     8                        Port Hospital    10
     8:     9                        Port Hospital    28
     9:     9                              Missing    27
    10:     9                     Central Hospital    10
    11:     9 St. Mark's Maternity Hospital (SMMH)     6
    12:    10                              Missing     2
    13:    10                    Military Hospital     3
    14:     3                        Port Hospital     1
    15:     4                    Military Hospital     1
    16:     5                                Other     2
    17:     5                     Central Hospital     1
    18:     5                              Missing     1
    19:     6                              Missing     7
    20:     6 St. Mark's Maternity Hospital (SMMH)     2
    21:     6                    Military Hospital     1
    22:     7                    Military Hospital     3
    23:     7                                Other     1
    24:     7                              Missing     2
    25:     7 St. Mark's Maternity Hospital (SMMH)     1
    26:     8                     Central Hospital     2
    27:     8                              Missing     6
    28:     9                                Other     9
    29:     9                    Military Hospital    11
    30:    10                        Port Hospital     3
    31:    10                                Other     4
    32:    10 St. Mark's Maternity Hospital (SMMH)     1
    33:    10                     Central Hospital     1
    34:    11                              Missing     2
    35:    11                        Port Hospital     1
    36:    12                        Port Hospital     1
        month                             hospital     N
        <num>                               <char> <int>

Data.table ayrıca zincirleme ifadelere aşağıdaki gibi izin verir:

``` r
linelist[, .N, .(hospital)][order(-N)][1:3] #1. tüm vakaları hastaneye göre seçer, 2. vakaları azalan sırayla sıralar, 3. en büyük vaka yüküne sahip 3 hastaneyi alt kümeler
```

                hospital     N
                  <char> <int>
    1:     Port Hospital  1762
    2:           Missing  1469
    3: Military Hospital   896

Bu örneklerde, veri tablosundaki bir satırın yeni bir duruma eşit olduğu varsayımını izliyoruz ve bu nedenle veri tablosundaki satır sayısını temsil etmek için **.N**’yi kullanabiliriz. Benzersiz durumların sayısını temsil eden başka bir yararlı fonksiyon, belirli bir girdideki benzersiz değerlerin sayısını döndüren “uniqueN()” dir. Aşağıda gösterilmektedir:

``` r
linelist[, .(uniqueN(gender))] #hatırlayın .() j değişkeninde bir veri tablosu döndürür
```

          V1
       <int>
    1:     3

Cinsiyet sütunundaki benzersiz değerler m, f ve N/A olduğundan cevap 3’tür. Belirli bir girdideki tüm benzersiz değerleri döndüren temel R fonksiyonu “unique()” ile karşılaştırın:

``` r
linelist[, .(unique(gender))]
```

           V1
       <char>
    1:      m
    2:      f
    3:   <NA>

Belirli bir aydaki benzersiz vakaların sayısını bulmak için aşağıdakileri yazarız:

``` r
linelist[, .(uniqueN(case_id)), .(month = month(date_hospitalisation))]
```

        month    V1
        <num> <int>
     1:     5    62
     2:     6   100
     3:     7   198
     4:     8   509
     5:     9  1170
     6:    10  1228
     7:    11   813
     8:    12   576
     9:     1   434
    10:     2   310
    11:     3   290
    12:     4   198

## 50.6 Veri tablolarına ekleme ve güncelleme

`:=` operatörü, bir veri tablosuna veri eklemek veya bu tabloya veri güncellemek için kullanılır. Veri tablonuza sütun eklemek aşağıdaki şekillerde yapılabilir:

``` r
linelist[, adult := age >= 18] #bir sütun ekler
linelist[, c("child", "wt_lbs") := .(age < 18, wt_kg*2.204)] #birden çok sütun eklemek için c("") ve list() veya .() sözdizimi gerekir
linelist[, `:=` (bmi_in_range = (bmi > 16 & bmi < 40),
                         no_infector_source_data = is.na(infector) | is.na(source))] #bu yöntem :='yi fonksiyonel operatör olarak `:=` kullanır
linelist[, adult := NULL] #sütunu siler
```

Daha karmaşık toplamalar bu giriş bölümünün kapsamı dışındadır, ancak buradaki fikir, verileri gruplama ve temizleme için **dplyr**’e popüler ve uygulanabilir bir alternatif sağlamaktır. **data.table** paketi, düzgün ve okunabilir koda izin veren harika bir pakettir.

## 50.7 Kaynaklar

Daha fazla bilgi için bazı yararlı kaynaklar şunlardır: \* https://cran.r-project.org/web/packages/data.table/vignettes/datatable-intro.html \* https://github.com/Rdatatable/data.table \* https://s3.amazonaws.com/assets.datacamp.com/img/blog/data+table+cheat+sheet.pdf \* https://www.machinelearningplus.com/data-manipulation/datatable-in-r-complete-guide/ \* https://www.datacamp.com/community/tutorials/data-table-r-tutorial

Gruplandırılmış veriler üzerinde herhangi bir özet fonksiyonu gerçekleştirebilirsiniz; Daha fazla bilgi için buradaki pratik belgeye bakın: https://s3.amazonaws.com/assets.datacamp.com/blog_assets/datatable_Cheat_Sheet_R.pdf
