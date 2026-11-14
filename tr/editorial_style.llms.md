# 1  Önyazı ve teknik notlar

Bu sayfada, el kitabının hazırlanması sırasında belirlediğimiz felsefi yaklaşıma, stile ve belirli editoryal kararlara değineceğiz.

## 1.1 Uygulamalı epidemiyoloji ve halk sağlığı için R

**Hedef:** Yaygın epidemiyolojik sorunlara çözümler üreten, pratik, hedef odaklı ve hızlı bir (çevrimiçi ve [çevrimdışı](download.llms.md)) referans kılavuz olarak rol oynamak.

### Kitabı nasıl kullanabilirim?

- İçindekiler bölümündeki sayfalara göz atabilir veya arama kutusunu kullanabilirsiniz
- Kodu kopyalamak için “kopyala” simgelerine tıklayabilirsiniz
- [örnek verileri](download.llms.md) kullanarak kendiniz de deneyebilirsiniz

**Çevrimdışı versiyonu**

[El Kitabı ve verileri indirme](download.llms.md) sayfasında çevrimdışı versiyonuna nasıl ulaşacağınızı görebilirsiniz.

## 1.2 Yaklaşım ve stil

Bu kitabın potansiyel hedef kitlesinin geniş olmasını istedik. Hem R’a yeni olan kişiler tarafından hem de “R’ın iyi uygulamalarını” ve “R’ın ipuçlarını” öğrenmek isteyen deneyimli kullanıcıların bu kitaptan faydalanabilmesini istedik. Kitap hem kolayca erişilebilir hem de az ve öz olmalıydı. Bu nedenle yaklaşımımızı, R’de çok yeni olan birinin kodu uygulayabileceği ve kodun ne yaptığını takip edebileceği *yeterli* metin açıklamasını sağlamak olarak belirledik.

Bir kaç nokta daha:

- Nispeten kısa örneklerin eşlik ettiği bir kod referans kitabı olarak tasarlanmıştır - R , veri bilimi üzerine kapsamlı bir ders kitabı *değildir*.
- Uygulamalı epidemiyolojide kullanmanız için *R el kitabı* olarak kapsamı sınırlandırılmıştır - uygulamalı epidemiyoloji yöntemleri veya bilimi hakkında bir kılavuz değil.
- Bu el kitabının yaşayan bir belge olması amaçlanmıştır - belirli görevler için hazırlanan R paketleri sıklıkla güncellenir ve değişir. Bu kitapta hangilerine yer vermemiz gerektiğine dair öneri ve eleştirilerinizi memnuniyetle öğrenmek isteriz.

### R paketleri

**Çok fazla seçenek**

R öğrenmenin en zorlu yönlerinden biri de hangi R paketinin kullanılacağını bilmektir. Bir işi çözmeye çalışırken “Hey, bunların hepsini tek bir komut satırında yapan bir R paketi var!” demeniz nadir bir durum olmayacaktır.

Bu el kitabında, her görevi tamamlamanız için size en az iki yol sunmaya çalıştık: ilki denenmiş ve doğrulanmış bir yöntem (muhtemelen **base** R veya **tidyverse** içinde) ve ikincisi o iş için özel olarak tasarlanmış bir R paketi. Belirli bir pakette sorun yaşamanız halinde birden fazla seçeneğe sahip olmanızı istiyoruz.

Paketleri belirlerken, R topluluğu tarafından test edilmiş ve onaylanmış paketlere ve yaklaşımlara öncelik verdik. Rutin bir çalışma oturumunda işinize yarayacak, stabil (çok sık değişmeyen) ve görevi basit ve temiz bir şekilde yerine getirebilecek minimal sayıda paket kullandık.

Bu el kitabı **tidyverse**’de bulunan R paket ve işlevlerine öncelik verir. Tidyverse, temel dilbilgisi ve veri yapılarını paylaşan veri bilimi için tasarlanmış bir R paketi koleksiyonudur. Tüm tidyverse paketleri, **tidyverse** paketi aracılığıyla kurulabilir veya yüklenebilir. [Tidyverse’n web sitesinde](https://www.tidyverse.org/) daha fazlasını okuyabilirsiniz.

Uygun yerlerde, kurulum sırasında R ile birlikte yüklenen **base** paket ve fonksiyonlarıyla ilişkili kod seçeneklerini de ekledik. Bunu, bu kitabın okuyucularından bazılarının ekstra paketleri indirmek için güvenilir bir internete sahip ol(a)mama ihtimaline karşılık yaptık.

**Fonksiyonları paketlerle ilişkilendirme**

R eğitim ve rehberlerinde bir fonksiyona ilişkin kodun anlatılıp, kullanılan paketin hiç değinilmemesine şahit olmuşsunuzdur. Bu durum sinir bozucudur! İşte biz bunu size yaşatmaktan kaçınmaya çalıştık.

Açıklama metinlerinde paket adları kalın harflerle (örn. **dplyr**) ve fonksiyonları `mutate()` şeklinde yazılır. Bir fonksiyonun hangi paketten geldiğini, ya en yakındaki metinde referanslayarak ya da kodu `dplyr::mutate()` şeklinde yazarak size açıklamaya çalıştık. Başta gereksiz görünebilir ancak bunu yukarıda bahsettiğimiz amaç doğrultusunda, bilerek yapıyoruz.

Paketler ve fonksiyonları hakkında daha fazla bilgi edinmek için [R basics](basics.llms.md) sayfasına bakabilirsiniz.

### Kodlama stili

El kitabında sık sık “yeni satırlar” kullanıyoruz, bu da kodumuzun “uzun” görünmesine neden olabiliyor. Bunun birkaç sebebi var:

- Kodun her küçük parçasına bitişik `#` ile açıklayıcı yorumlar yazabiliriz.
- Genellikle daha uzun (dikey) kodun okunması daha kolaydır.
- Kodların dar bir ekranda okunması daha kolaydır (ekranı yana kaydırmanıza gerek kalmaz).
- Girintiler sayesinde hangi argümanların hangi fonksiyona ait olduğunu daha kolay anlayabilirsiniz.

Sonuç olarak, *aşağıdaki gibi* yazılabilecek kod:

``` r
linelist %>% 
  group_by(hospital) %>%  # satırları hastane (hospital) olarak gruplandırır
  slice_max(date, n = 1, with_ties = F) # eğer tarih (date) ile eşleşirse ilk satırı alır
```

…şu şekilde yazılır:

``` r
linelist %>% 
  group_by(hospital) %>% # satırları hastane (hospital) olarak gruplandırır
  slice_max(
    date,                # maksimum tarih değerine göre grubu sıralar
    n = 1,               # gruptaki satırlardan sadece ilkini alır 
    with_ties = F)       # eğer tarih (date) ile eşleşirse ilk satırı alır
```

R kodu genel olarak yeni satır veya girintilerden etkilenmez. Kodu yazarken, virgülden sonra yeni bir satır başlatırsanız, program yeni satıra otomatik girinti uygular.

Ayrıca, okunması daha kolay olduğu için kodu yazarken birçok boşluk kullandık (örneğin, `n=1` yerine `n = 1`). Siz de kodunuzu yazarken onu okuyabilecek insanları düşünerek yazmalısınız!

### Terminoloji

Bu el kitabında, genellikle “değişkenler” ve “gözlemler” yerine “sütunlar” ve “satırlar”a atıfta bulunuyoruz. [“Tidy verileri”](https://tidyr.tidyverse.org/articles/tidy-data.html) ile ilgili bu makalede açıklandığı gibi, epidemiyolojik istatistiksel veri setlerinin çoğu yapısal olarak satır, sütun ve değerlerden oluşur.

*Değişkenler* aynı temel özelliği ölçen değerleri içerir (yaş grubu, çıktı veya başlangıç tarihi gibi). *Gözlemler* aynı birimde ölçülen tüm değerleri içerir (örneğin bir kişi, alan veya laboratuvar numunesi vb.). Dolayısıyla bu yönleri somut olarak tanımlamak daha zor olabilmektedir.

“Tidy” veri kümelerinde her sütun bir değişken, her satır bir gözlem ve her hücre de tek bir değeri ifade etmektedir. Ancak karşılaştığınız bazı veri kümeleri bu kalıba sığmaz - “geniş” biçimli bir veri kümesinin birkaç sütuna bölünebilen değişkenleri olabilir ([Pivoting data](pivoting.llms.md) sayfasındaki bir örneğe bakın). Benzer şekilde, gözlemler de birkaç satıra bölünebilir.

Bu el kitabı çoğunlukla, verileri yönetmek ve işlemek üzerine odaklanmıştır. O nedenle satır ve sütunlarda somut verilere atıfta bulunmayı, daha soyut olan “gözlem” ve “değişkenler”e tercih ettik. Bu yaklaşımımızın istisnası, daha fazla değişken ve gözlem referansıyla karşılaşacağınız veri analizi sayfalarıdır.

### Notlar

El kitabında karşılaşabileceğiniz not türleri şunlardır:

***NOT:*** Bu bir nottur.  
***İPUCU:*** Bu bir ipucudur.  
***DİKKAT:*** Bu dikkatli yaklaşmanızı tavsiye eden bir nottur.  
***TEHLİKE:*** Bu bir uyarıdır.

## 1.3 Editöryal Kararlar

Aşağıda, paket ve işlev seçimiyle ilgili önemli editoryal kararları sizinle paylaşıyoruz. Bizimle aynı fikirde değilseniz veya değerlendirilmesi için yeni bir araç önermek isterseniz, lütfen [Github sayfamıza](https://github.com/appliedepi/epirhandbook_eng) katılın ve yeni bir sohbet başlatın.

**Paket, fonksiyon ve diğer editoryal kararlar tablosu**

| Konu | Değerlendirilenler | Çıktı | Rasyoneli |
|----|----|----|----|
| Genel kodlama yaklaşımı | **tidyverse**, **data.table**, **base** | **tidyverse**, **data.table** üzerinde bir sayfa ve interneti olmayan okuyucular için **base** alternatifleri | **tidyverse** okunabilir, evrensel, en çok öğretilen pakettir. |
| Paket yükleme | `library()`,`install.packages()`, `require()`, **pacman** | **pacman** | Çoklu paket indirme/yükleme süreçlerini kısaltır ve basitleştirir. |
| İçe ve dışa aktarma | **rio**, ve diğer pek çok paketler | **rio** | birçok dosya türü için kolaylık sağlar. |
| İstatistik özetleri için gruplandırma | **dplyr** `group_by()`, **stats** `aggregate()` | **dplyr** `group_by()` | **tidyverse** vurgusu ile tutarlıdır. |
| Pivotlama | **tidyr** (pivot fonksiyonları), **reshape2** (melt/cast), **tidyr** (spread/gather) | **tidyr** (pivot fonksiyonları) | **reshape2** artık kullanımda değil, **tidyr** v1.0.0 itibariyle pivot fonksiyonlarını kullanmaktadır. |
| Sütun adlarını temizleme | **linelist**, **janitor** | **janitor** | Paketlerin birleştirilmesi vurgulanmaktadır. |
| Epiweeks | lubridate, **aweek**, **tsibble**, **zoo** | genelde **lubridate**, özel durumlarda diğer paketler | **lubridate**’in esnekliği, tutarlılığı ve paket bakımının sürdürülme olasılığı |
| ggplot etiketleri | `labs()`, `ggtitle()`/`ylab()`/`xlab()` | `labs()` | tüm etiketler tek bir yerde, kullanımı basittir. |
| Faktöre çevirme | `factor()`, **forcats** | **forcats** | çeşitli fonksiyonları da aynı komutta faktöre dönüşür. |
| Epidemi eğrileri | **incidence**, **ggplot2**, **EpiCurve** | hızlı seçenek olarak **incidence2**, ayrıntılı seçenek olarak **ggplot2** | güvenilirlik |
| Birleştirme | `paste()`, `paste0()`, `str_glue()`, `glue()` | `str_glue()` | **stringr** paketinin içindedir; yapıştır fonksiyonlarından daha basit bir sentaks (sözdizimi) vardır. |

## 1.4 Büyük güncellemeler

| Tarih       | Açıklama                       |
|-------------|--------------------------------|
| 10 May 2021 | Versiyon 1.0.0’ın yayınlanması |
| 20 Kas 2022 | Versiyon 1.0.1’in yayınlanması |

NEWS Versiyon 1.0.1 ile aşağıdaki değişiklikler uygulanmıştır:

- R sürüm 4.2’ye güncelleme
- Veri temizliği: {linelist} yerine {matchmaker} kullanıldı, `case_when()` örneğinden gereksiz satır kaldırıldı
- Tarihler: {linelist} `guess_date()` yerine {parsedate} `parse_date()` kullanıldı
- Verilerin pivotlanması: `pivot_wider()` `id_cols=` argümanında küçük bir güncelleme
- Anket analizi: `plot_age_pyramid()` yerine `age_pyramid()` kullanıldı, alüvyon grafiği kodunda küçük bir değişiklik
- Isı grafikleri: `agg_weeks` kod parçasına `ungroup()` eklendi
- İnteraktif grafikler: `expand()` amaçlandığı gibi çalışsın diye `agg_weeks` oluşturan kod parçasına `ungroup()` eklendi
- Zaman serileri: tüm `trending::fit()` ve `predict()` komutlarındaki nesnelerin etrafına `data.frame()` eklendi
- Kombinasyon analizi: `case_when()` yerine `ifelse()` kullanıldı ve verilerin hazırlanması için isteğe bağlı `across()` kodu eklendi
- İletim zincirleri: {epicontacts} paketinin daha yeni bir sürümüne güncelleme

## 1.5 Teşekkür

Bu el kitabı, Dünya Sağlık Örgütü (WHO), Médecins Sans Frontières / Sınır Tanımayan Doktorlar (MSF), bölgesel ve ulusal sağlık örgütleri, akademik kurumlar ve hastaneler dahil olmak üzere pek çok kuruluşun deneyimlerinden faydalanılarak dünyanın dört bir yanından epidemiyologların işbirliğiyle hazırlanmıştır.

Bu el kitabı, belirli bir kuruluşun onaylanmış bir ürünü değildir. En doğru bilgiyi sizinle paylaşmak için çabalasak da, bu kitaptaki içerikle ilgili hiçbir garanti veremeyiz.

### Katkıda Bulunanlar

**Editör:** [Neale Batra](https://www.linkedin.com/in/neale-batra/)

**Yazarlar:** [Neale Batra](https://www.linkedin.com/in/neale-batra/), [Alex Spina](https://github.com/aspina7), [Paula Blomquist](https://www.linkedin.com/in/paula-bianca-blomquist-53188186/), [Finlay Campbell](https://github.com/finlaycampbell), [Henry Laurenson-Schafer](https://github.com/henryls1), [Isaac Florence](https://www.Twitter.com/isaacatflorence), [Natalie Fischer](https://www.linkedin.com/in/nataliefischer211/), [Aminata Ndiaye](https://twitter.com/aminata_fadl), [Liza Coyer](https://www.linkedin.com/in/liza-coyer-86022040/), [Jonathan Polonsky](https://twitter.com/jonny_polonsky), [Yurie Izawa](https://ch.linkedin.com/in/yurie-izawa-a1590319), [Chris Bailey](https://twitter.com/cbailey_58?lang=en), [Daniel Molling](https://www.linkedin.com/in/daniel-molling-4005716a/), [Isha Berry](https://twitter.com/ishaberry2), [Emma Buajitti](https://twitter.com/buajitti), [Mathilde Mousset](https://mathildemousset.wordpress.com/research/), [Sara Hollis](https://www.linkedin.com/in/saramhollis/), Wen Lin

**Katkıda bulunanlar:** Pat Keating, [Amrish Baidjoe](https://twitter.com/Ammer_B), Annick Lenglet, Margot Charette, Danielly Xavier, Marie-Amélie Degail Chabrat, Esther Kukielka, Michelle Sloan, Aybüke Koyuncu, Rachel Burke, Kate Kelsey, [Berhe Etsay](https://www.linkedin.com/in/berhe-etsay-5752b1154/), John Rossow, Mackenzie Zendt, James Wright, Laura Haskins, [Flavio Finger](https://ffinger.github.io), Tim Taylor, [Jae Hyoung Tim Lee](https://www.linkedin.com/in/jaehyoungtlee/), [Brianna Bradley](https://www.linkedin.com/in/brianna-bradley-bb8658155), [Wayne Enanoria](https://www.linkedin.com/in/wenanoria), Manual Albela Miranda, [Molly Mantus](https://www.linkedin.com/in/molly-mantus-174550150/), Pattama Ulrich, Joseph Timothy, Adam Vaughan, Olivia Varsaneux, Lionel Monteiro, Joao Muianga

**İllüstrasyonlar:** Calder Fong

Çevirmenler: Çağrı Emin Şahin, Abdullah Ömer Şeker, Can Ilgin, Ömer Özer, Yasemin Denizli

### Fonlama ve destek

Bu kitap binlerce saat süren gönüllü bir çabanın sonunda ortaya çıktı.

El kitabı, Saha Epidemiyolojisi küresel ağı olan [TEPHINET’in](https://www.tephinet.org/) COVID-19 acil durum kapasite geliştirme hibesinden destek fonu aldı.

Ayrıca El kitabı Annika Wendland’ın destekleriyle EPIET Mezunlar Ağı’ndan ([EAN](https://epietalumni.net/)) idari destek aldı. EPIET, girişimsel epidemiyoloji eğitimi veren bir Avrupa programıdır.

Bu el kitabının geliştirilmesi sırasındaki destekleri için Médecins Sans Frontières (MSF) Amsterdam Operasyon Merkezi’ne (OCA) özellikle teşekkür ederiz.

*Bu yayın, NU2GGH001873 numaralı İşbirliği Anlaşması ile Hastalık Kontrol ve Önleme Merkezi tarafından Küresel Sağlık Kurulu’nun bir programı olan TEPHINET aracılığıyla finanse edilmiştir. İçeriğin oluşturulması yalnızca yazarların sorumluluğundadır ve Hastalık Kontrol ve Önleme Merkezi, Sağlık ve İnsan Hizmetleri Departmanı, Küresel Sağlık Kurulu veya TEPHINET’in resmi görüşlerini temsil etmemektedir.*

### İlham

El kitabı içeriğinin geliştirilmesi için, bilgi amaçlı, çok sayıda öğretici ve kısa hikaye, ilgili sayfalarında paylaşılmıştır.

Daha genel olarak, aşağıdaki kaynaklar bu el kitabı için ilham kaynağı olmuştur: [“R4Epis” projesi](https://r4epis.netlify.app/) (MSF ve RECON işbirliği)  
[R Salgın Konsorsiyumu (RECON)](https://www.repidemicsconsortium.org/)  
[Veri Bilimi için R kitabı (R4DS)](https://r4ds.had.co.nz/)  
[bookdown: R Markdown ile Kitap ve Teknik Belge Yazma](https://bookdown.org/yihui/bookdown/)  
[Netlify](https://www.netlify.com) (website sunucusu)

## 1.6 Kullanım ve Katkı Koşulları

### Lisans

[![Creative Commons License](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/4.0/) Applied Epi Anonim Şirketi, 2021  
Bu yayın, Applied Epi Anonim Şirketi tarafından [“Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License”ı ile lisanslanmıştır.](http://creativecommons.org/licenses/by-nc-sa/4.0/).

Akademik kurslarda ve epidemiyoloji eğitim programlarında bu el kitabı eğitim amaçlı kullanılıp çoğaltılabilir. Böyle bir durum söz konusu olduğunda bize e-posta ile haber vermenizi rica ediyoruz. Kullanım amacınızla ilgili sorularınız varsa contact@appliedepi.org adresine e-posta gönderebilirsiniz.

### Alıntı

Batra, Neale, et al. The Epidemiologist R Handbook. 2021. [![DOI](https://zenodo.org/badge/231610102.svg)](https://zenodo.org/badge/231610102.svg)  

### Katkı

İçerik katkısı yapmak istiyorsanız, lütfen önce Github veya e-posta yoluyla bizimle iletişime geçin. Güncellemeler için bir kapsamlı bir program uyguluyor ve bu amaçla destek rehberi hazırlıyoruz.

Lütfen destek vermeden önce epiRhandbook projesi [Davranış Kuralları](https://contributor-covenant.org/version/2/0/CODE_OF_CONDUCT.html) kılavuzunu inceleyin. Bu projeye katkıda bulunarak, kılavuzda belirlenen şartlara uymayı kabul etmiş olursunuz.

## 1.7 Oturum bilgisi (R, packages)

Aşağıda, bu El Kitabının kullandığı tüm paketleri içeren Docker imajındaki R ve tüm R paketlerinin sürümleri yer almaktadır.

``` r
sessioninfo::session_info(pkgs = "installed", include_base = TRUE)
```

    ─ Session info ───────────────────────────────────────────────────────────────
     setting  value
     version  R version 4.6.0 (2026-04-24)
     os       Ubuntu 26.04 LTS
     system   x86_64, linux-gnu
     ui       X11
     language en_US:en
     collate  en_US.UTF-8
     ctype    en_US.UTF-8
     tz       Etc/UTC
     date     2026-11-14
     pandoc   3.7.0.2 @ /usr/bin/ (via rmarkdown)
     quarto   1.9.38 @ /usr/local/bin/quarto

    ─ Packages ───────────────────────────────────────────────────────────────────
     package              * version    date (UTC) lib source
     abind                  1.4-8      2024-09-12 [1] RSPM
     adagio                 0.9.2      2023-10-26 [1] RSPM
     anytime                0.3.13     2026-04-14 [1] RSPM
     ape                    5.8-1      2024-12-16 [1] RSPM
     aplot                  0.3.0      2026-06-23 [1] RSPM
     appliedepidata         0.0.0.9013 2026-11-02 [1] Github (appliedepi/appliedepidata@77036b1)
     apyramid               0.1.3      2023-02-14 [1] RSPM
     arm                    1.15-3     2026-04-15 [1] RSPM
     askpass                1.2.1      2024-10-04 [1] RSPM
     assertthat             0.2.1      2019-03-21 [1] RSPM
     aweek                  1.0.3      2022-10-06 [1] RSPM
     backports              1.5.1      2026-04-03 [1] RSPM
     base                 * 4.6.0      2026-04-24 [1] local
     base64enc              0.1-6      2026-02-02 [1] RSPM
     bayestestR             0.18.1     2026-05-24 [1] RSPM
     bigD                   0.3.1      2025-04-03 [1] RSPM
     binom                  1.1-1.1    2022-05-02 [1] RSPM
     BiocManager            1.30.27    2025-11-14 [1] RSPM
     bit                    4.6.0      2025-03-06 [1] RSPM
     bit64                  4.8.2      2026-05-19 [1] RSPM
     bitops                 1.0-9      2024-10-03 [1] RSPM
     blob                   1.3.0      2026-01-14 [1] RSPM
     boot                   1.3-32     2025-08-29 [1] CRAN (R 4.6.0)
     broom                  1.0.13     2026-05-14 [1] RSPM
     broom.helpers          1.22.0     2025-09-17 [1] RSPM
     bslib                  0.11.0     2026-05-16 [1] RSPM
     ca                     0.71.1     2020-01-24 [1] RSPM
     cachem                 1.1.0      2024-05-16 [1] RSPM
     callr                  3.8.0      2026-06-05 [1] RSPM
     car                    3.1-5      2026-02-03 [1] RSPM
     carData                3.0-6      2026-01-30 [1] RSPM
     cards                  0.8.0      2026-05-28 [1] RSPM
     cardx                  0.3.3      2026-05-29 [1] RSPM
     cellranger             1.1.0      2016-07-27 [1] RSPM
     CFtime                 1.7.3      2026-04-02 [1] RSPM
     checkmate              2.3.4      2026-02-03 [1] RSPM
     ciTools                0.6.1      2020-10-25 [1] RSPM
     class                  7.3-23     2025-01-01 [1] CRAN (R 4.6.0)
     classInt               0.4-11     2025-01-08 [1] RSPM
     cli                    3.6.6      2026-04-09 [1] RSPM
     clipr                  0.8.1      2026-05-25 [1] RSPM
     clock                  0.7.4      2026-01-13 [1] RSPM
     cluster                2.1.8.2    2026-02-05 [1] CRAN (R 4.6.0)
     cmprsk                 2.2-12     2024-05-19 [1] RSPM
     coarseDataTools        0.7.2      2025-04-11 [1] RSPM
     coda                   0.19-4.1   2024-01-31 [1] RSPM
     codetools              0.2-20     2024-03-31 [1] CRAN (R 4.6.0)
     colorspace             2.1-2      2025-09-22 [1] RSPM
     colourpicker           1.3.0      2023-08-21 [1] RSPM
     cols4all               0.10       2025-10-27 [1] RSPM
     commonmark             2.0.0      2025-07-07 [1] RSPM
     compiler               4.6.0      2026-04-24 [1] local
     conflicted             1.2.0      2023-02-01 [1] RSPM
     correlation            0.8.8      2025-07-08 [1] RSPM
     corrplot               0.95       2024-10-14 [1] RSPM
     corrr                  0.4.5      2025-08-18 [1] RSPM
     cowplot                1.2.0      2025-07-07 [1] RSPM
     crayon                 1.5.3      2024-06-20 [1] RSPM
     crosstalk              1.2.2      2025-08-26 [1] RSPM
     curl                   7.1.0      2026-04-22 [1] RSPM
     data.table             1.18.4     2026-05-06 [1] RSPM
     data.tree              1.2.0      2025-08-25 [1] RSPM
     datasets             * 4.6.0      2026-04-24 [1] local
     datawizard             1.3.1      2026-04-26 [1] RSPM
     DBI                    1.3.0      2026-02-25 [1] RSPM
     dbplyr                 2.6.0      2026-06-17 [1] RSPM
     deldir                 2.0-4      2024-02-28 [1] RSPM
     DEoptimR               1.2-0      2026-06-07 [1] RSPM
     Deriv                  4.2.0      2025-06-20 [1] RSPM
     desc                   1.4.3      2023-12-10 [1] RSPM
     diagram                1.6.5      2020-09-30 [1] RSPM
     DiagrammeR             1.0.12     2026-04-27 [1] RSPM
     dichromat              2.0-0.1    2022-05-02 [1] RSPM
     digest                 0.6.39     2025-11-19 [1] RSPM
     distcrete              1.0.3      2017-11-23 [1] RSPM
     distributional         0.8.1      2026-06-27 [1] RSPM
     doBy                   4.7.1      2025-12-02 [1] RSPM
     doParallel             1.0.17     2022-02-07 [1] RSPM
     dplyr                  1.2.1      2026-04-03 [1] RSPM
     DT                     0.34.0     2025-09-02 [1] RSPM
     dtplyr                 1.3.3      2026-02-11 [1] RSPM
     e1071                  1.7-17     2025-12-18 [1] RSPM
     easystats              0.7.6      2026-05-24 [1] RSPM
     ecmwfr                 2.0.3      2025-02-10 [1] RSPM
     effectsize             1.0.2      2026-03-11 [1] RSPM
     Epi                    2.65       2026-04-15 [1] RSPM
     epicontacts            1.2.0      2026-11-02 [1] Github (reconhub/epicontacts@e68f228)
     epidict                0.3.0      2026-11-02 [1] Github (R4EPI/epidict@af29299)
     EpiEstim               2.2-5      2025-06-27 [1] RSPM
     epikit                 0.2.0      2025-11-05 [1] RSPM
     EpiNow2                1.9.0      2026-06-16 [1] RSPM
     epitabulate            0.1.0      2026-11-02 [1] Github (R4EPI/epitabulate@6f5539d)
     epitrix                0.4.1      2025-07-25 [1] RSPM
     etm                    1.1.2      2025-04-12 [1] RSPM
     evaluate               1.0.5      2025-08-27 [1] RSPM
     evd                    2.3-7.1    2024-09-21 [1] RSPM
     exactRankTests         0.8-37     2026-05-04 [1] RSPM
     fabletools             0.8.0      2026-06-28 [1] RSPM
     fansi                  1.0.7      2025-11-19 [1] RSPM
     farver                 2.1.2      2024-05-13 [1] RSPM
     fastLink               0.6.1      2023-11-17 [1] RSPM
     fastmap                1.2.0      2024-05-15 [1] RSPM
     fastymd                0.1.5      2026-02-27 [1] RSPM
     feasts                 0.5.0      2026-02-09 [1] RSPM
     ff                     4.5.2      2025-01-13 [1] RSPM
     filelock               1.0.3      2023-12-11 [1] RSPM
     fitdistrplus           1.2-6      2026-01-24 [1] RSPM
     flexdashboard          0.6.3      2026-01-28 [1] RSPM
     flextable              0.9.12     2026-06-02 [1] RSPM
     fontawesome            0.5.3      2024-11-16 [1] RSPM
     fontBitstreamVera      0.1.1      2017-02-01 [1] RSPM
     fontLiberation         0.1.0      2016-10-15 [1] RSPM
     fontquiver             0.2.1      2017-02-01 [1] RSPM
     forcats                1.0.1      2025-09-25 [1] RSPM
     foreach                1.5.2      2022-02-02 [1] RSPM
     forecast               9.0.2      2026-03-18 [1] RSPM
     foreign                0.8-91     2026-01-29 [1] CRAN (R 4.6.0)
     formatR                1.14       2023-01-17 [1] RSPM
     formattable            0.2.1      2021-01-07 [1] RSPM
     Formula                1.2-5      2023-02-24 [1] RSPM
     fracdiff               1.5-4      2026-04-28 [1] RSPM
     fs                     2.1.0      2026-04-18 [1] RSPM
     furrr                  0.4.0      2026-03-31 [1] RSPM
     futile.logger          1.4.9      2025-12-29 [1] RSPM
     futile.options         1.0.1      2018-04-20 [1] RSPM
     future                 1.70.0     2026-03-14 [1] RSPM
     future.apply           1.20.2     2026-02-20 [1] RSPM
     gargle                 1.6.1      2026-01-29 [1] RSPM
     gclus                  1.3.3      2025-03-28 [1] RSPM
     gdtools                0.5.1      2026-05-25 [1] RSPM
     generics               0.1.4      2025-05-09 [1] RSPM
     geojsonsf              2.0.5      2025-11-26 [1] RSPM
     getPass                0.2-4      2023-12-10 [1] RSPM
     ggdist                 3.3.3      2025-04-23 [1] RSPM
     ggExtra                0.11.0     2025-09-01 [1] RSPM
     ggforce                0.5.0      2025-06-18 [1] RSPM
     ggfun                  0.2.0      2025-07-15 [1] RSPM
     gghighlight            0.5.0      2025-06-14 [1] RSPM
     ggiraph                0.9.6      2026-02-21 [1] RSPM
     ggnewscale             0.5.2      2025-06-20 [1] RSPM
     ggplot2                4.0.3      2026-04-22 [1] RSPM
     ggplotify              0.1.3      2025-09-20 [1] RSPM
     ggpubr                 0.6.3      2026-02-24 [1] RSPM
     ggrepel                0.9.8      2026-03-17 [1] RSPM
     ggsci                  5.1.0      2026-06-26 [1] RSPM
     ggsignif               0.6.4      2022-10-13 [1] RSPM
     ggtext                 0.1.2      2022-09-16 [1] RSPM
     ggtime                 0.2.0      2026-02-09 [1] RSPM
     ggtree                 4.2.1      2026-10-29 [1] Bioconduc~
     ggupset                0.4.1      2025-02-11 [1] RSPM
     glmnet                 5.0        2026-05-04 [1] RSPM
     globals                0.19.1     2026-03-13 [1] RSPM
     glue                   1.8.1      2026-04-17 [1] RSPM
     googledrive            2.1.2      2025-09-10 [1] RSPM
     googlesheets4          1.1.2.9000 2026-11-02 [1] Github (tidyverse/googlesheets4@55cd9fd)
     gower                  1.0.2      2024-12-17 [1] RSPM
     graphics             * 4.6.0      2026-04-24 [1] local
     grates                 1.8.0      2026-03-25 [1] RSPM
     grDevices            * 4.6.0      2026-04-24 [1] local
     grid                   4.6.0      2026-04-24 [1] local
     gridExtra              2.3.1      2026-06-25 [1] RSPM
     gridGraphics           0.5-1      2020-12-13 [1] RSPM
     gridtext               0.1.6      2026-02-19 [1] RSPM
     gt                     1.3.0      2026-01-22 [1] RSPM
     gtable                 0.3.6      2024-10-25 [1] RSPM
     gtools                 3.9.5      2023-11-20 [1] RSPM
     gtsummary              2.5.1      2026-05-30 [1] RSPM
     hardhat                1.4.3      2026-04-04 [1] RSPM
     haven                  2.5.5      2025-05-30 [1] RSPM
     here                   1.0.2      2025-09-15 [1] RSPM
     highcharter            0.9.5      2026-04-22 [1] RSPM
     highr                  0.12       2026-03-06 [1] RSPM
     hms                    1.1.4      2025-10-17 [1] RSPM
     htmltools              0.5.9      2025-12-04 [1] RSPM
     htmlwidgets            1.6.4      2023-12-06 [1] RSPM
     httpuv                 1.6.17     2026-03-18 [1] RSPM
     httr                   1.4.8      2026-02-13 [1] RSPM
     httr2                  1.2.3      2026-06-23 [1] RSPM
     i2extras               0.2.1.9000 2026-11-02 [1] Github (reconverse/i2extras@10fea67)
     ids                    1.0.1      2017-05-31 [1] RSPM
     igraph                 2.3.3      2026-06-26 [1] RSPM
     imputeTS               3.4        2025-08-25 [1] RSPM
     incidence              1.7.6      2025-06-19 [1] RSPM
     incidence2             2.6.4      2026-03-02 [1] RSPM
     inline                 0.3.21     2025-01-09 [1] RSPM
     insight                1.5.2      2026-06-28 [1] RSPM
     ipred                  0.9-15     2024-07-18 [1] RSPM
     isoband                0.3.0      2025-12-07 [1] RSPM
     iterators              1.0.14     2022-02-05 [1] RSPM
     janitor                2.2.1      2024-12-22 [1] RSPM
     jomo                   2.7-6      2023-04-15 [1] RSPM
     jpeg                   0.1-11     2025-03-21 [1] RSPM
     jquerylib              0.1.4      2021-04-26 [1] RSPM
     jsonlite               2.0.0      2025-03-27 [1] RSPM
     juicyjuice             0.1.0      2022-11-10 [1] RSPM
     kableExtra             1.4.0      2024-01-24 [1] RSPM
     KernSmooth             2.23-26    2025-01-01 [1] CRAN (R 4.6.0)
     keyring                1.4.1      2025-06-15 [1] RSPM
     knitr                  1.51       2025-12-20 [1] RSPM
     labeling               0.4.3      2023-08-29 [1] RSPM
     labelled               2.16.0     2025-10-22 [1] RSPM
     lambda.r               1.2.4      2019-09-18 [1] RSPM
     later                  1.4.8      2026-03-05 [1] RSPM
     lattice                0.22-9     2026-02-09 [1] CRAN (R 4.6.0)
     lava                   1.9.2      2026-06-30 [1] RSPM
     lazyeval               0.2.3      2026-04-04 [1] RSPM
     leafem                 0.2.5      2025-08-28 [1] RSPM
     leafgl                 0.2.4      2026-04-15 [1] RSPM
     leaflegend             1.2.8      2026-05-16 [1] RSPM
     leaflet                2.2.3      2025-09-04 [1] RSPM
     leaflet.providers      3.0.0      2026-03-18 [1] RSPM
     leafsync               0.1.0      2019-03-05 [1] RSPM
     lifecycle              1.0.5      2026-01-08 [1] RSPM
     listenv                1.0.0      2026-06-22 [1] RSPM
     litedown               0.9        2025-12-18 [1] RSPM
     lme4                   2.0-1      2026-03-05 [1] RSPM
     lmtest                 0.9-40     2022-03-21 [1] RSPM
     logger                 0.4.2      2026-05-10 [1] RSPM
     loo                    2.10.0     2026-06-26 [1] RSPM
     lpSolve                5.6.23     2024-12-14 [1] RSPM
     lubridate              1.9.5      2026-02-04 [1] RSPM
     lwgeom                 0.2-16     2026-05-03 [1] RSPM
     magrittr               2.0.5      2026-04-04 [1] RSPM
     maptiles               0.11.0     2025-12-12 [1] RSPM
     markdown               2.0        2025-03-23 [1] RSPM
     MASS                   7.3-65     2025-02-28 [1] CRAN (R 4.6.0)
     matchmaker             0.1.1      2020-02-21 [1] RSPM
     Matrix                 1.7-5      2026-03-21 [1] CRAN (R 4.6.0)
     MatrixModels           0.5-4      2025-03-26 [1] RSPM
     matrixStats            1.5.0      2025-01-07 [1] RSPM
     maxstat                0.7-26     2025-05-02 [1] RSPM
     mcmc                   0.9-8      2023-11-16 [1] RSPM
     MCMCpack               1.7-1      2024-08-27 [1] RSPM
     memoise                2.0.1      2021-11-26 [1] RSPM
     methods              * 4.6.0      2026-04-24 [1] local
     mgcv                   1.9-4      2025-11-07 [1] CRAN (R 4.6.0)
     mice                   3.19.0     2025-12-10 [1] RSPM
     microbenchmark         1.5.0      2024-09-04 [1] RSPM
     mime                   0.13       2025-03-17 [1] RSPM
     miniUI                 0.1.2      2025-04-17 [1] RSPM
     minqa                  1.2.8      2024-08-17 [1] RSPM
     mitml                  0.4-5      2023-03-08 [1] RSPM
     mitools                2.4        2019-04-26 [1] RSPM
     modelbased             0.16.0     2026-06-30 [1] RSPM
     modelr                 0.1.11     2023-03-22 [1] RSPM
     munsell                0.5.1      2024-04-01 [1] RSPM
     mvtnorm                1.4-1      2026-06-06 [1] RSPM
     naniar                 1.1.0      2024-03-05 [1] RSPM
     ncmeta                 0.4.0      2024-03-25 [1] RSPM
     networkD3              0.4.1      2025-04-14 [1] RSPM
     nlme                   3.1-169    2026-03-27 [1] CRAN (R 4.6.0)
     nloptr                 2.2.1      2025-03-17 [1] RSPM
     nnet                   7.3-20     2025-01-01 [1] CRAN (R 4.6.0)
     norm                   1.0-11.1   2023-06-18 [1] RSPM
     numDeriv               2016.8-1.1 2019-06-06 [1] RSPM
     officer                0.7.5      2026-05-15 [1] RSPM
     openssl                2.4.2      2026-06-09 [1] RSPM
     OpenStreetMap          0.4.1      2025-09-29 [1] RSPM
     ordinal                2025.12-29 2026-01-10 [1] RSPM
     otel                   0.2.0      2025-08-29 [1] RSPM
     pacman                 0.5.1      2019-03-11 [1] RSPM
     padr                   0.6.3      2024-11-21 [1] RSPM
     pak                    0.10.0     2026-06-07 [1] RSPM (R 4.6.0)
     pan                    2.0        2026-06-30 [1] RSPM
     parallel               4.6.0      2026-04-24 [1] local
     parallelly             1.48.0     2026-06-29 [1] RSPM
     parameters             0.29.2     2026-06-28 [1] RSPM
     parsedate              1.3.2      2024-12-09 [1] RSPM
     patchwork              1.3.2      2025-08-25 [1] RSPM
     pbkrtest               0.5.5      2025-07-18 [1] RSPM
     pcaPP                  2.0-5      2024-08-19 [1] RSPM
     performance            0.17.1     2026-06-30 [1] RSPM
     PerformanceAnalytics   2.1.0      2026-04-11 [1] RSPM
     permute                0.9-10     2026-02-06 [1] RSPM
     PHEindicatormethods    2.1.1      2025-11-18 [1] RSPM
     pillar                 1.11.1     2025-09-17 [1] RSPM
     pkgbuild               1.4.8      2025-05-26 [1] RSPM
     pkgconfig              2.0.3      2019-09-22 [1] RSPM
     plotly                 4.12.0     2026-01-24 [1] RSPM
     plotrix                3.8-14     2026-02-13 [1] RSPM
     plyr                   1.8.9      2023-10-02 [1] RSPM
     png                    0.1-9      2026-03-15 [1] RSPM
     polyclip               1.10-7     2024-07-23 [1] RSPM
     polyCub                0.9.4      2026-04-24 [1] RSPM
     polynom                1.4-1      2022-04-11 [1] RSPM
     posterior              1.7.0      2026-04-01 [1] RSPM
     primarycensored        1.5.1      2026-06-15 [1] RSPM
     processx               3.9.0      2026-04-22 [1] RSPM
     prodlim                2026.03.11 2026-03-11 [1] RSPM
     progressr              0.19.0     2026-03-31 [1] RSPM
     projections            0.6.1      2024-12-06 [1] RSPM
     promises               1.5.0      2025-11-01 [1] RSPM
     proxy                  0.4-29     2025-12-29 [1] RSPM
     ps                     1.9.3      2026-04-20 [1] RSPM
     purrr                  1.2.2      2026-04-10 [1] RSPM
     pyinit                 1.1.5      2026-01-08 [1] RSPM
     qap                    0.1-2      2022-06-27 [1] RSPM
     quadprog               1.5-8      2019-11-20 [1] RSPM
     quantmod               0.4.29     2026-06-28 [1] RSPM
     quantreg               6.1        2025-03-10 [1] RSPM
     QuickJSR               1.10.0     2026-05-17 [1] RSPM
     R.methodsS3            1.8.2      2022-06-13 [1] RSPM
     R.oo                   1.27.1     2025-05-02 [1] RSPM
     R.utils                2.13.0     2025-02-24 [1] RSPM
     R6                     2.6.1      2025-02-15 [1] RSPM
     ragg                   1.5.2      2026-03-23 [1] RSPM
     rappdirs               0.3.4      2026-01-17 [1] RSPM
     raster                 3.6-32     2025-03-28 [1] RSPM
     rbibutils              2.4.1      2026-01-21 [1] RSPM
     RColorBrewer           1.1-3      2022-04-03 [1] RSPM
     Rcpp                   1.1.1-1.1  2026-04-24 [1] RSPM
     RcppParallel           5.1.11-2   2026-03-05 [1] RSPM
     RcppRoll               0.3.2      2026-03-28 [1] RSPM
     Rdpack                 2.6.6      2026-02-08 [1] RSPM
     reactable              0.4.5      2025-12-01 [1] RSPM
     reactR                 0.6.1      2024-09-14 [1] RSPM
     readr                  2.2.0      2026-02-19 [1] RSPM
     readxl                 1.5.0      2026-05-16 [1] RSPM
     recipes                1.3.3      2026-05-30 [1] RSPM
     RecordLinkage          0.4-12.6   2026-01-25 [1] RSPM
     reformulas             0.4.4      2026-02-02 [1] RSPM
     registry               0.5-1      2019-03-05 [1] RSPM
     rematch                2.0.0      2023-08-30 [1] RSPM
     rematch2               2.1.2      2020-05-01 [1] RSPM
     remotes                2.5.0      2024-03-17 [1] RSPM
     report                 0.6.4      2026-05-04 [1] RSPM
     repr                   1.1.7      2024-03-22 [1] RSPM
     reprex                 2.1.1      2024-07-06 [1] RSPM
     reshape2               1.4.5      2025-11-12 [1] RSPM
     rio                    1.3.0      2026-04-02 [1] RSPM
     rJava                  1.0-18     2026-04-08 [1] RSPM
     rjson                  0.2.23     2024-09-16 [1] RSPM
     rlang                  1.2.0      2026-04-06 [1] RSPM
     rlist                  0.4.6.2    2021-09-03 [1] RSPM
     rmarkdown              2.31       2026-03-26 [1] RSPM
     RNetCDF                2.11-1     2025-04-30 [1] RSPM
     RobStatTM              1.0.11     2024-10-17 [1] RSPM
     robustbase             0.99-7     2026-02-05 [1] RSPM
     rpart                  4.1.27     2026-03-27 [1] CRAN (R 4.6.0)
     rprojroot              2.1.1      2025-08-26 [1] RSPM
     rrcov                  1.7-7      2025-04-21 [1] RSPM
     rsample                1.3.2      2026-01-30 [1] RSPM
     RSQLite                3.53.3     2026-06-30 [1] RSPM
     rstan                  2.32.7     2025-03-10 [1] RSPM
     rstantools             2.6.0      2026-01-10 [1] RSPM
     rstatix                0.7.3      2025-10-18 [1] RSPM
     rstudioapi             0.19.0     2026-06-11 [1] RSPM
     runner                 0.4.6      2026-01-31 [1] RSPM
     rvest                  1.0.5      2025-08-29 [1] RSPM
     s2                     1.1.11     2026-06-01 [1] RSPM
     S7                     0.2.2      2026-04-22 [1] RSPM
     sass                   0.4.10     2025-04-11 [1] RSPM
     scales                 1.4.0      2025-04-24 [1] RSPM
     see                    0.14.1     2026-06-29 [1] RSPM
     selectr                0.6-0      2026-06-23 [1] RSPM
     SemiCompRisks          3.4        2021-02-03 [1] RSPM
     seriation              1.5.8      2025-08-20 [1] RSPM
     servr                  0.33       2026-06-16 [1] RSPM
     sessioninfo            1.2.4      2026-06-04 [1] RSPM
     sf                     1.1-1      2026-05-06 [1] RSPM
     shape                  1.4.6.1    2024-02-23 [1] RSPM
     shiny                  1.14.0     2026-06-21 [1] RSPM
     shinyjs                2.1.1      2026-01-15 [1] RSPM
     sitrep                 0.4.1      2026-11-02 [1] Github (R4EPI/sitrep@72c205f)
     skimr                  2.2.2      2026-01-10 [1] RSPM
     slider                 0.3.3      2025-11-14 [1] RSPM
     snakecase              0.11.1     2023-08-27 [1] RSPM
     sodium                 1.4.0      2024-12-16 [1] RSPM
     sourcetools            0.1.7-2    2026-03-28 [1] RSPM
     sp                     2.2-1      2026-02-13 [1] RSPM
     spacesXYZ              1.6-0      2025-06-06 [1] RSPM
     SparseM                1.84-2     2024-07-17 [1] RSPM
     sparsevctrs            0.3.6      2026-01-27 [1] RSPM
     spatial                7.3-18     2025-01-01 [1] CRAN (R 4.6.0)
     spatstat.data          3.1-9      2025-10-18 [1] RSPM
     spatstat.geom          3.8-1      2026-05-23 [1] RSPM
     spatstat.univar        3.2-0      2026-05-18 [1] RSPM
     spatstat.utils         3.2-3      2026-05-10 [1] RSPM
     spData                 2.3.5      2026-05-04 [1] RSPM
     spdep                  1.4-2      2026-02-13 [1] RSPM
     splines                4.6.0      2026-04-24 [1] local
     SQUAREM                2026.1     2026-03-12 [1] RSPM
     srvyr                  1.3.1      2026-02-02 [1] RSPM
     StanHeaders            2.32.10    2024-07-15 [1] RSPM
     stars                  0.7-2      2026-04-03 [1] RSPM
     stats                * 4.6.0      2026-04-24 [1] local
     stats4                 4.6.0      2026-04-24 [1] local
     stinepack              1.5        2024-03-07 [1] RSPM
     stringdist             0.9.17     2026-01-16 [1] RSPM
     stringi                1.8.7      2025-03-27 [1] RSPM
     stringr                1.6.0      2025-11-04 [1] RSPM
     surveillance           1.25.0     2025-06-25 [1] RSPM
     survey                 4.5        2026-02-24 [1] RSPM
     survival               3.8-6      2026-01-16 [1] CRAN (R 4.6.0)
     survminer              0.5.2      2026-02-25 [1] RSPM
     svglite                2.2.2      2025-10-21 [1] RSPM
     sys                    3.4.3      2024-10-04 [1] RSPM
     systemfonts            1.3.2      2026-03-05 [1] RSPM
     tcltk                  4.6.0      2026-04-24 [1] local
     tensorA                0.36.2.1   2023-12-13 [1] RSPM
     terra                  1.9-34     2026-06-19 [1] RSPM
     textshaping            1.0.5      2026-03-06 [1] RSPM
     threejs                0.3.4      2025-04-21 [1] RSPM
     tibble                 3.3.1      2026-01-11 [1] RSPM
     tidyquant              1.0.12     2026-03-16 [1] RSPM
     tidyr                  1.3.2      2025-12-19 [1] RSPM
     tidyselect             1.2.1      2024-03-11 [1] RSPM
     tidytree               0.4.7      2026-01-08 [1] RSPM
     tidyverse              2.0.0      2023-02-22 [1] RSPM
     timechange             0.4.0      2026-01-29 [1] RSPM
     timeDate               4052.112   2026-01-28 [1] RSPM
     timetk                 2.9.1      2025-08-29 [1] RSPM
     tinytex                0.60       2026-06-16 [1] RSPM
     tmap                   4.4-1      2026-06-26 [1] RSPM
     tmaptools              3.3        2025-07-24 [1] RSPM
     tools                  4.6.0      2026-04-24 [1] local
     treeio                 1.36.1     2026-04-30 [1] Bioconduc~
     trending               0.1.0      2023-04-03 [1] RSPM
     truncnorm              1.0-9      2023-03-20 [1] RSPM
     tseries                0.10-61    2026-03-26 [1] RSPM
     tsfeatures             1.1.1      2023-08-28 [1] RSPM
     tsibble                1.2.0      2026-02-09 [1] RSPM
     TSP                    1.2.7      2026-03-23 [1] RSPM
     TTR                    0.24.4     2023-11-28 [1] RSPM
     tweenr                 2.0.3      2024-02-26 [1] RSPM
     tzdb                   0.5.0      2025-03-15 [1] RSPM
     ucminf                 1.2.3      2026-04-02 [1] RSPM
     units                  1.0-1      2026-03-11 [1] RSPM
     UpSetR                 1.4.1      2026-05-25 [1] RSPM
     urca                   1.3-4      2024-05-27 [1] RSPM
     utf8                   1.2.6      2025-06-08 [1] RSPM
     utils                * 4.6.0      2026-04-24 [1] local
     uuid                   1.2-2      2026-01-23 [1] RSPM
     V8                     8.2.0      2026-04-21 [1] RSPM
     vctrs                  0.7.3      2026-04-11 [1] RSPM
     vegan                  2.7-5      2026-05-25 [1] RSPM
     viridis                0.6.5      2024-01-29 [1] RSPM
     viridisLite            0.4.3      2026-02-04 [1] RSPM
     visdat                 0.6.0      2023-02-02 [1] RSPM
     visNetwork             2.1.4      2025-09-04 [1] RSPM
     vistime                1.3.0      2026-03-28 [1] RSPM
     vroom                  1.7.1      2026-03-31 [1] RSPM
     warp                   0.2.3      2026-01-13 [1] RSPM
     webshot                0.5.5      2023-06-26 [1] RSPM
     withr                  3.0.3      2026-06-19 [1] RSPM
     wk                     0.9.5      2025-12-18 [1] RSPM
     writexl                1.5.4      2025-04-15 [1] RSPM
     xfun                   0.59       2026-06-19 [1] RSPM
     XML                    3.99-0.23  2026-03-20 [1] RSPM
     xml2                   1.6.0      2026-06-22 [1] RSPM
     xtable                 1.8-8      2026-02-22 [1] RSPM
     xts                    0.14.2     2026-02-28 [1] RSPM
     yaml                   2.3.12     2025-12-10 [1] RSPM
     yardstick              1.4.0      2026-04-07 [1] RSPM
     ympes                  1.9.0      2025-04-14 [1] RSPM
     yulab.utils            0.2.4      2026-02-02 [1] RSPM
     yyjsonr                0.1.22     2026-04-05 [1] RSPM
     zip                    3.0.0      2026-06-10 [1] RSPM
     zoo                    1.8-15     2025-12-15 [1] RSPM

     [1] /opt/R/4.6.0/lib/R/library
     * ── Packages attached to the search path.

    ──────────────────────────────────────────────────────────────────────────────
