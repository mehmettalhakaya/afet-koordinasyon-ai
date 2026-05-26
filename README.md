# AfetKoordinasyonAI

> Afet anında gelen yardım çağrılarını analiz eden, önem sırasına göre değerlendiren ve harita üzerinde görselleştiren yapay zekâ destekli afet koordinasyon demo projesi.

<p align="center">
  <a href="https://afet-koordinasyon-ai.vercel.app/"><strong>Canlı Demo</strong></a>
  ·
  <a href="https://github.com/mehmettalhakaya/afet-koordinasyon-ai"><strong>GitHub Repo</strong></a>
</p>

<p align="center">
  <img alt="AfetKoordinasyonAI" src="images/1.png">
</p>

---

## Projenin Amacı

**AfetKoordinasyonAI**, afet ve kriz anlarında farklı kişilerden gelen yardım çağrılarını daha anlaşılır, önceliklendirilebilir ve takip edilebilir hale getirmek amacıyla geliştirilmiş bir web uygulamasıdır.

Proje; yardım çağrısı metinlerini analiz eder, çağrının hangi ihtiyaç kategorisine ait olabileceğini tahmin eder, aciliyet seviyesini hesaplar, benzer çağrıları tespit eder ve kayıtları harita üzerinde gösterir.

Bu çalışma; afet teknolojileri, kriz bilişimi, Türkçe doğal dil işleme ve karar destek sistemleri üzerine geliştirilmiş **eğitim/demo amaçlı** bir projedir.

---

## Proje Ne Yapar?

- Yardım çağrısı metinlerini analiz eder.
- Çağrıları ihtiyaç kategorilerine ayırır.
- Her çağrı için 0-100 arası aciliyet skoru üretir.
- Benzer veya tekrar olabilecek çağrıları işaretler.
- Çağrıları şehir, ilçe, kategori ve aciliyet bilgileriyle listeler.
- Çağrıları Türkiye haritası üzerinde marker, cluster ve heatmap görünümleriyle gösterir.
- Operasyon panelinde genel durum özetini sunar.
- Demo analiz ekranı ile çağrıyı kaydetmeden model çıktısını gösterir.

---

## Önemli Uyarı

Bu proje **resmi bir afet koordinasyon sistemi değildir**.

- Gerçek acil durumlarda kullanılmak üzere geliştirilmemiştir.
- İçerikte kullanılan veriler demo/sentetik veri niteliğindedir.
- Gerçek kişi, gerçek adres, gerçek olay veya resmi vaka bilgisi içermez.
- Gerçek afet ve acil durumlarda **112**, **AFAD**, **Kızılay** ve ilgili resmi kurumlar takip edilmelidir.

Bu proje yalnızca teknik demo, portföy ve eğitim amacıyla değerlendirilmelidir.

---

## Ekran Görüntüleri

### 1. Operasyon Paneli

Operasyon paneli, sistemdeki çağrıların genel durumunu tek ekranda özetler. Toplam çağrı sayısı, ortalama aciliyet, şüpheli tekrar sayısı, kategori dağılımı ve son eklenen çağrılar bu ekranda görüntülenir.

![Operasyon Paneli](images/1.png)

---

### 2. Kategori ve Şehir Dağılımları

Bu bölümde yardım çağrıları kategori ve şehir bazında görselleştirilir. Böylece hangi ihtiyaçların öne çıktığı ve hangi şehirlerde yoğunluk oluştuğu hızlıca anlaşılabilir.

![Kategori ve Şehir Dağılımları](images/2.png)

---

### 3. Harita Görünümü

Harita ekranı, çağrıların coğrafi konumlarını görsel olarak takip etmeyi sağlar. Marker, marker cluster ve heatmap görünümleriyle çağrı yoğunlukları incelenebilir.

![Harita Görünümü](images/3.png)

---

### 4. Çağrı Listesi

Çağrı listesi ekranında kayıtlı yardım çağrıları tablo halinde gösterilir. Çağrılar şehir, ilçe, kategori, aciliyet skoru ve tekrar şüphesi gibi bilgilerle birlikte incelenebilir.

![Çağrı Listesi](images/4.png)

---

### 5. Yeni Çağrı Oluşturma

Bu ekranda yeni yardım çağrısı oluşturulur. Kullanıcı çağrı metnini, şehir/ilçe bilgisini, etkilenen kişi sayısını ve varsa kategori bilgisini girer. Kategori boş bırakılırsa sistem çağrının kategorisini otomatik tahmin eder.

![Yeni Çağrı Oluşturma](images/5.png)

---

### 6. Analiz Demo

Analiz demo ekranı, yardım çağrısını veritabanına kaydetmeden test etmeyi sağlar. Girilen metin üzerinden kategori tahmini, aciliyet skoru ve benzer çağrı kontrolü yapılır.

![Analiz Demo](images/6.png)

---

## Kısa Tanıtım

AfetKoordinasyonAI, afet anında gelen dağınık yardım çağrılarını daha düzenli ve anlamlı hale getirmeyi hedefleyen bir karar destek demosudur.

Uygulama, bir çağrının yalnızca metnini saklamakla kalmaz; çağrının neyle ilgili olduğunu, ne kadar acil olabileceğini ve daha önce gelen çağrılarla benzerlik taşıyıp taşımadığını da analiz eder. Böylece operatörlerin ve koordinasyon ekiplerinin çağrıları daha hızlı değerlendirebilmesine yönelik bir örnek sistem sunar.

Proje; Türkçe metin analizi, çağrı önceliklendirme, harita tabanlı görselleştirme ve afet yönetimi senaryosunu bir araya getiren uçtan uca bir web uygulaması olarak hazırlanmıştır.

---

## Canlı Demo

Projeyi buradan inceleyebilirsiniz:

**https://afet-koordinasyon-ai.vercel.app/**

---

## Geliştirici

**Mehmet Talha Kaya**

- GitHub: [@mehmettalhakaya](https://github.com/mehmettalhakaya)
- Proje: [afet-koordinasyon-ai](https://github.com/mehmettalhakaya/afet-koordinasyon-ai)
- Demo: [afet-koordinasyon-ai.vercel.app](https://afet-koordinasyon-ai.vercel.app/)
