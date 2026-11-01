# 1  Önyazı ve teknik notlar

Bu sayfada, el kitabının hazırlanması sırasında belirlediğimiz felsefi yaklaşıma, stile ve belirli editoryal kararlara değineceğiz.

## 1.1 Uygulamalı epidemiyoloji ve halk sağlığı için R

**Hedef:** Yaygın epidemiyolojik sorunlara çözümler üreten, pratik, hedef odaklı ve hızlı bir (çevrimiçi ve **[çevrimdışı](download.llms.md)**) referans kılavuz olarak rol oynamak.

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
  group_by(hospital) %>%  # satırları hastane (hospital) olarak gruplandır
  slice_max(date, n = 1, with_ties = F) # eğer tarih (date) ile eşleşirse ilk satırı al
```

…şu şekilde yazılır:

``` r
linelist %>% 
  group_by(hospital) %>% # satırları hastane (hospital) olarak gruplandır
  slice_max(
    date,                # maksimum tarih değerine grubu sırala
    n = 1,               # gruptaki satırlardan sadece ilkini al 
    with_ties = F)       # eğer tarih (date) ile eşleşirse ilk satırı al
```

R kodu genel olarak yeni satır veya girintilerden etkilenmez. Kodu yazarken, virgülden sonra yeni bir satır başlatırsanız, program yeni satıra otomatik girinti uygular.

Ayrıca, okunması daha kolay olduğu için kodu yazarken birçok boşluk kullandık (örneğin, ‘n=1’ yerine ‘n = 1’). Siz de kodunuzu yazarken onu okuyabilecek insanları düşünerek yazmalısınız!

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
| Epiweeks | **lubridate**, **aweek**, **tsibble**, **zoo** | genelde **lubridate**, özel durumlarda diğer paketler | **lubridate**’in esnekliği, tutarlılığı ve paket bakımının sürdürülme olasılığı |
| ggplot etiketleri | `labs()`, `ggtitle()`/`ylab()`/`xlab()` | `labs()` | tüm etiketler tek bir yerde, kullanımı basittir. |
| Faktöre çevir | `factor()`, **forcats** | **forcats** | çeşitli fonksiyonları da aynı komutta faktöre dönüşür. |
| Epidemi eğrileri | **incidence**, **ggplot2**, **EpiCurve** | hızlı seçenek olarak **incidence2**, ayrıntılı seçenek olarak **ggplot2** | güvenilirlik |
| Birleştirme | `paste()`, `paste0()`, `str_glue()`, `glue()` | `str_glue()` | **stringr** paketinin içindedir; yapıştır fonksiyonlarından daha basit bir sentaks (sözdizimi) vardır. |

## 1.4 Büyük güncellemeler

| Tarih       | Açıklama                       |
|-------------|--------------------------------|
| 10 May 2021 | Versiyon 1.0.0’ın yayınlanması |
| 20 Kas 2022 | Versiyon 1.0.1’in yayınlanması |

**NEWS** Versiyon 1.0.1 ile aşağıdaki değişiklikler uygulanmıştır:

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

Bu el kitabı, belirli bir kuruluşun onaylanmış bir ürünü **değildir**. En doğru bilgiyi sizinle paylaşmak için çabalasak da, bu kitaptaki içerikle ilgili hiçbir garanti veremeyiz.

### Katkıda Bulunanlar

**Editör:** [Neale Batra](https://www.linkedin.com/in/neale-batra/)

**Yazarlar**: [Neale Batra](https://www.linkedin.com/in/neale-batra/), [Alex Spina](https://github.com/aspina7), [Paula Blomquist](https://www.linkedin.com/in/paula-bianca-blomquist-53188186/), [Finlay Campbell](https://github.com/finlaycampbell), [Henry Laurenson-Schafer](https://github.com/henryls1), [Isaac Florence](https://www.Twitter.com/isaacatflorence), [Natalie Fischer](https://www.linkedin.com/in/nataliefischer211/), [Aminata Ndiaye](https://twitter.com/aminata_fadl), [Liza Coyer](https://www.linkedin.com/in/liza-coyer-86022040/), [Jonathan Polonsky](https://twitter.com/jonny_polonsky), [Yurie Izawa](https://ch.linkedin.com/in/yurie-izawa-a1590319), [Chris Bailey](https://twitter.com/cbailey_58?lang=en), [Daniel Molling](https://www.linkedin.com/in/daniel-molling-4005716a/), [Isha Berry](https://twitter.com/ishaberry2), [Emma Buajitti](https://twitter.com/buajitti), [Mathilde Mousset](https://mathildemousset.wordpress.com/research/), [Sara Hollis](https://www.linkedin.com/in/saramhollis/), Wen Lin

**Katkıda bulunanlar**: Pat Keating, [Amrish Baidjoe](https://twitter.com/Ammer_B), Annick Lenglet, Margot Charette, Danielly Xavier, Marie-Amélie Degail Chabrat, Esther Kukielka, Michelle Sloan, Aybüke Koyuncu, Rachel Burke, Kate Kelsey, [Berhe Etsay](https://www.linkedin.com/in/berhe-etsay-5752b1154/), John Rossow, Mackenzie Zendt, James Wright, Laura Haskins, [Flavio Finger](https://ffinger.github.io), Tim Taylor, [Jae Hyoung Tim Lee](https://www.linkedin.com/in/jaehyoungtlee/), [Brianna Bradley](https://www.linkedin.com/in/brianna-bradley-bb8658155), [Wayne Enanoria](https://www.linkedin.com/in/wenanoria), Manual Albela Miranda, [Molly Mantus](https://www.linkedin.com/in/molly-mantus-174550150/), Pattama Ulrich, Joseph Timothy, Adam Vaughan, Olivia Varsaneux, Lionel Monteiro, Joao Muianga

**İllüstrasyonlar**: Calder Fong

**Çevirmenler**: Çağrı Emin Şahin, Abdullah Ömer Şeker, Can Ilgin, Ömer Özer, Yasemin Denizli

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

Akademik kurslarda ve epidemiyoloji eğitim programlarında bu el kitabı eğitim amaçlı kullanılıp çoğaltılabilir. Böyle bir durum söz konusu olduğunda bize e-posta ile haber vermenizi rica ediyoruz. Kullanım amacınızla ilgili sorularınız varsa **contact@appliedepi.org** adresine e-posta gönderebilirsiniz.

### Alıntı

Batra, Neale, et al. The Epidemiologist R Handbook. 2021. [![DOI](https://zenodo.org/badge/231610102.svg)](https://zenodo.org/badge/231610102.svg)  

### Katkı

İçerik katkısı yapmak istiyorsanız, lütfen önce Github veya e-posta yoluyla bizimle iletişime geçin. Güncellemeler için bir kapsamlı bir program uyguluyor ve bu amaçla destek rehberi hazırlıyoruz.

Lütfen destek vermeden önce epiRhandbook projesi [Davranış Kuralları](https://contributor-covenant.org/version/2/0/CODE_OF_CONDUCT.html) kılavuzunu inceleyin. Bu projeye katkıda bulunarak, kılavuzda belirlenen şartlara uymayı kabul etmiş olursunuz.

## 1.7 Oturum bilgisi (R, RStudio, packages)

Aşağıda, bu el Kitabının hazırlanması sırasında kullanılan R, RStudio, R paketleri ve sürümlerine ilişkin bilgiler yer almaktadır.

``` r
sessioninfo::session_info()
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
     date     2026-11-01
     pandoc   3.7.0.2 @ /usr/bin/ (via rmarkdown)
     quarto   1.9.38 @ /usr/local/bin/quarto

    ─ Packages ───────────────────────────────────────────────────────────────────
     package     * version date (UTC) lib source
     cli           3.6.6   2026-04-09 [1] RSPM
     digest        0.6.39  2025-11-19 [1] RSPM
     evaluate      1.0.5   2025-08-27 [1] RSPM
     fastmap       1.2.0   2024-05-15 [1] RSPM
     htmltools     0.5.9   2025-12-04 [1] RSPM
     htmlwidgets   1.6.4   2023-12-06 [1] RSPM
     jsonlite      2.0.0   2025-03-27 [1] RSPM
     knitr         1.51    2025-12-20 [1] RSPM
     otel          0.2.0   2025-08-29 [1] RSPM
     rlang         1.2.0   2026-04-06 [1] RSPM
     rmarkdown     2.31    2026-03-26 [1] RSPM
     sessioninfo   1.2.4   2026-06-04 [1] RSPM
     xfun          0.59    2026-06-19 [1] RSPM
     yaml          2.3.12  2025-12-10 [1] RSPM

     [1] /opt/R/4.6.0/lib/R/library

    ──────────────────────────────────────────────────────────────────────────────
