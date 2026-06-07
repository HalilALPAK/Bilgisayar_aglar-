# NetProbe: UDP Tabanlı Güvenilir Dosya Aktarım ve Ağ Performans Analiz Platformu

Bursa Teknik Üniversitesi — Bilgisayar Ağları Dönem Projesi

> **GitHub:** [https://github.com/HalilALPAK/aglar-](https://github.com/HalilALPAK/Bilgisayar_aglar-)

## Proje Özeti

Bu proje, UDP üzerinde uygulama katmanında güvenilir dosya aktarımı gerçekleştiren bir istemci-sunucu sistemi sunar. Stop-and-Wait ve Go-Back-N (Kayan Pencere) protokollerinin her ikisi de uygulanmıştır. Aktarım sürecindeki ağ olayları loglanır ve çeşitli performans metrikleri (throughput, goodput, retransmission rate, RTT) analiz edilerek karşılaştırmalı grafikler üretilir.

## Proje Yapısı

| Dosya | Açıklama |
|---|---|
| `packet.py` | Özel protokol paketi: TYPE, SeqNum, Checksum, Payload alanları |
| `server.py` | UDP sunucu; paket alır, dosyayı yeniden birleştirir, MD5 ile bütünlük doğrular |
| `client.py` | Stop-and-Wait istemci; yapay kayıp simülasyonu, maks. 5 yeniden deneme |
| `client_gbn.py` | Go-Back-N istemci; kayan pencere, thread ile eşzamanlı gönderim/alım |
| `logger.py` | CSV tabanlı olay kaydı (SEND, RECV, TIMEOUT, FAILED) |
| `analysis.py` | Log analizi; throughput, goodput, RTT hesaplar; S&W vs GBN karşılaştırma grafikleri üretir |

## Gereksinimler

- Python 3.x
- pandas
- matplotlib

```bash
pip install pandas matplotlib
```

## Nasıl Çalıştırılır

### 1. Sunucuyu Başlat
```bash
python server.py
```

### 2. Stop-and-Wait İstemcisini Çalıştır
```bash
python client.py --file <dosya> --loss 0.1 --timeout 0.5
```
Parametreler:
- `--file` : Gönderilecek dosya (varsayılan: `donem_projesi.pdf`)
- `--loss` : Yapay kayıp oranı, 0.0–1.0 (varsayılan: `0.1`)
- `--timeout` : Zaman aşımı süresi saniye (varsayılan: `0.5`)

### 3. Go-Back-N İstemcisini Çalıştır
```bash
python client_gbn.py --file <dosya> --loss 0.1 --window 5
```
Parametreler:
- `--window` : Kayan pencere boyutu (varsayılan: `5`)

### 4. Performans Analizi ve Grafik Üretimi
```bash
python analysis.py
```
Tüm `log_loss_*.csv` ve `log_gbn_*.csv` dosyalarını okur; aşağıdaki grafikler üretilir:
- `throughput_vs_loss.png` — S&W Throughput vs Kayıp Oranı
- `goodput_vs_loss.png` — S&W Goodput vs Kayıp Oranı
- `retransmission_vs_loss.png` — S&W Yeniden Gönderim Oranı
- `throughput_vs_loss_gbn.png` — GBN Throughput vs Kayıp Oranı
- `goodput_vs_loss_gbn.png` — GBN Goodput vs Kayıp Oranı
- `comparison_throughput.png` — S&W vs GBN Throughput Karşılaştırması
- `comparison_goodput.png` — S&W vs GBN Goodput Karşılaştırması
- `comparison_retransmission.png` — S&W vs GBN Retransmission Karşılaştırması

Tek bir log dosyasını analiz etmek için:
```bash
python analysis.py log_loss_0.1_timeout_0.5.csv
```

## Deney Senaryoları

### Senaryo A — Farklı Kayıp Oranları (Stop-and-Wait)
```bash
python client.py --loss 0.0 --timeout 0.5
python client.py --loss 0.1 --timeout 0.5
python client.py --loss 0.2 --timeout 0.5
python client.py --loss 0.3 --timeout 0.5
```

### Senaryo B — S&W vs Go-Back-N Karşılaştırması
```bash
python client.py     --loss 0.1 --timeout 0.5
python client_gbn.py --loss 0.1 --window 5
```

### Senaryo C — Timeout Değerinin Etkisi
```bash
python client.py --loss 0.1 --timeout 0.2
python client.py --loss 0.1 --timeout 0.5
python client.py --loss 0.1 --timeout 1.0
```

### Senaryo D — Pencere Boyutunun Etkisi (GBN)
```bash
python client_gbn.py --loss 0.1 --window 1
python client_gbn.py --loss 0.1 --window 5
python client_gbn.py --loss 0.1 --window 10
```

## Performans Metrikleri

| Metrik | Açıklama |
|---|---|
| **Throughput** | Gönderilen toplam bit / süre (bps) |
| **Goodput** | Başarıyla iletilen benzersiz bit / süre (bps) |
| **Tamamlanma Süresi** | Aktarım toplam süresi (s) |
| **Retransmission Rate** | Yeniden gönderim / benzersiz paket oranı |
| **Ortalama RTT** | SEND ile eşleşen ACK arasındaki ortalama süre (ms) |

## Protokol Özeti

- **Paket Türleri:** START → DATA → END, karşılıklı ACK
- **Checksum:** Her pakette MD5 (payload başına), aktarım sonunda dosyanın bütün MD5'i
- **Maks. Yeniden Deneme:** Paket başına 5 deneme; aşıldığında `FAILED` loglanır
- **Bütünlük Doğrulaması:** İstemci ve sunucu ayrı ayrı MD5 yazdırır; kullanıcı karşılaştırır

## Yazarlar

- Halil ALPAK
- Hilal KAYA
- İmer İmeri
