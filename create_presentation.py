"""
Generates a PDF presentation for the NetProbe project.
Run: python create_presentation.py
Output: sunum.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

W, H = A4

# ── Register Unicode-aware fonts (Arial supports Turkish characters) ─────────
FONT_DIR = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Arial",    os.path.join(FONT_DIR, "Arial.ttf")))
pdfmetrics.registerFont(TTFont("ArialBD",  os.path.join(FONT_DIR, "ArialBD.ttf")))
pdfmetrics.registerFont(TTFont("ArialI",   os.path.join(FONT_DIR, "ArialI.ttf")))
pdfmetrics.registerFont(TTFont("ArialBI",  os.path.join(FONT_DIR, "ArialBI.ttf")))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Arial", normal="Arial", bold="ArialBD", italic="ArialI", boldItalic="ArialBI")

# ── Colour palette ──────────────────────────────────────────────────────────
BLUE_DARK  = colors.HexColor("#1a3a5c")
BLUE_MID   = colors.HexColor("#2563a8")
BLUE_LIGHT = colors.HexColor("#dbeafe")
ORANGE     = colors.HexColor("#f97316")
GRAY_LIGHT = colors.HexColor("#f1f5f9")
GRAY_TEXT  = colors.HexColor("#374151")

# ── Style helpers ────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def style(name, **kw):
    s = ParagraphStyle(name, parent=base["Normal"], **kw)
    return s

S_SLIDE_TITLE = style("SlideTitle",
    fontSize=28, leading=34, textColor=BLUE_DARK,
    fontName="ArialBD", alignment=TA_CENTER, spaceAfter=6)

S_SUBTITLE = style("Subtitle",
    fontSize=14, leading=18, textColor=BLUE_MID,
    fontName="Arial", alignment=TA_CENTER, spaceAfter=4)

S_SECTION = style("Section",
    fontSize=16, leading=20, textColor=BLUE_DARK,
    fontName="ArialBD", spaceAfter=6, spaceBefore=4)

S_BODY = style("Body",
    fontSize=11, leading=16, textColor=GRAY_TEXT,
    fontName="Arial", spaceAfter=4, alignment=TA_JUSTIFY)

S_BULLET = style("Bullet",
    fontSize=11, leading=16, textColor=GRAY_TEXT,
    fontName="Arial", leftIndent=16, spaceAfter=3,
    bulletIndent=4)

S_CODE = style("Code",
    fontSize=9, leading=13, textColor=colors.HexColor("#1e293b"),
    fontName="Courier", backColor=GRAY_LIGHT,
    leftIndent=12, rightIndent=12, spaceAfter=4, spaceBefore=4)

S_TABLE_HDR = style("TblHdr",
    fontSize=10, fontName="ArialBD",
    textColor=colors.white, alignment=TA_CENTER)

S_TABLE_CELL = style("TblCell",
    fontSize=10, fontName="Arial",
    textColor=GRAY_TEXT, alignment=TA_LEFT)

S_CAPTION = style("Caption",
    fontSize=9, fontName="ArialI",
    textColor=colors.HexColor("#6b7280"), alignment=TA_CENTER)

def hline():
    return HRFlowable(width="100%", thickness=1.5, color=BLUE_MID, spaceAfter=8)

def bullet(text):
    return Paragraph(f"• &nbsp; {text}", S_BULLET)

def sp(h=0.3):
    return Spacer(1, h * cm)

# ── Slide factory ────────────────────────────────────────────────────────────
def slide_title(story, title, subtitle="", info=""):
    story.append(sp(3))
    story.append(Paragraph(title, S_SLIDE_TITLE))
    if subtitle:
        story.append(Paragraph(subtitle, S_SUBTITLE))
    story.append(hline())
    if info:
        story.append(Paragraph(info, S_BODY))
    story.append(PageBreak())

def slide(story, title, content_fn):
    story.append(Paragraph(title, S_SECTION))
    story.append(hline())
    content_fn(story)
    story.append(PageBreak())

# ── Content ──────────────────────────────────────────────────────────────────
def build_story():
    story = []

    # ── SLIDE 1 — Cover ──────────────────────────────────────────────────────
    story.append(sp(2))
    story.append(Paragraph(
        "NetProbe", style("CoverMain", fontSize=42, leading=50,
                          textColor=BLUE_DARK, fontName="ArialBD",
                          alignment=TA_CENTER)))
    story.append(sp(0.4))
    story.append(Paragraph(
        "UDP Tabanlı Güvenilir Dosya Aktarım ve<br/>Ağ Performans Analiz Platformu",
        style("CoverSub", fontSize=16, leading=22, textColor=BLUE_MID,
              fontName="Arial", alignment=TA_CENTER)))
    story.append(sp(0.8))
    story.append(hline())
    story.append(sp(0.5))
    for line in [
        "Bursa Teknik Üniversitesi",
        "Bilgisayar Mühendisliği Bölümü",
        "Bilgisayar Ağları Dersi — Dönem Projesi",
        "<br/>Halil ALPAK",
        "2025-2026",
    ]:
        story.append(Paragraph(line, S_SUBTITLE))
    story.append(PageBreak())

    # ── SLIDE 2 — Outline ────────────────────────────────────────────────────
    def s2(s):
        items = [
            "1. Projenin Amacı ve Kapsamı",
            "2. Sistem Mimarisi",
            "3. Protokol Tasarımı",
            "4. Stop-and-Wait Gerçeklemesi",
            "5. Go-Back-N (Kayan Pencere) Gerçeklemesi",
            "6. Trafik İzleme ve Loglama",
            "7. Performans Analizi ve Deney Sonuçları",
            "8. Karşılaştırmalı Değerlendirme",
            "9. Zorluklar ve Çözümler",
            "10. Sonuç ve Gelecek Çalışmalar",
        ]
        for it in items:
            s.append(bullet(it))
    slide(story, "İçindekiler", s2)

    # ── SLIDE 3 — Amaç ──────────────────────────────────────────────────────
    def s3(s):
        s.append(Paragraph(
            "Bu projenin amacı, bilgisayar ağları dersinde ele alınan temel kavramları "
            "uygulamalı olarak pekiştirmektir. UDP protokolü üzerinde uygulama katmanında "
            "güvenilirlik mekanizmaları tasarlanmış; ağ performansı ölçülmüş ve görselleştirilmiştir.",
            S_BODY))
        s.append(sp())
        for it in [
            "UDP ve TCP arasındaki temel farkların uygulamalı incelenmesi",
            "Sequence number, ACK, timeout ve retransmission mekanizmalarının sıfırdan tasarımı",
            "Stop-and-Wait ve Go-Back-N protokollerinin karşılaştırılması",
            "Throughput, goodput, RTT ve retransmission rate metriklerinin ölçülmesi",
            "Teknik rapor ve sunum hazırlama becerisi kazanımı",
        ]:
            s.append(bullet(it))
    slide(story, "Projenin Amacı", s3)

    # ── SLIDE 4 — Mimari ─────────────────────────────────────────────────────
    def s4(s):
        s.append(Paragraph(
            "Sistem istemci-sunucu mimarisinde çalışmakta olup tüm iletişim UDP soket "
            "programlama ile gerçekleştirilmektedir. Üç ana katman mevcuttur:",
            S_BODY))
        s.append(sp(0.4))
        data = [
            [Paragraph("Katman", S_TABLE_HDR),
             Paragraph("Bileşen", S_TABLE_HDR),
             Paragraph("Görev", S_TABLE_HDR)],
            [Paragraph("Paket Katmanı", S_TABLE_CELL),
             Paragraph("packet.py", S_TABLE_CELL),
             Paragraph("Serileştirme, MD5 checksum, paket türleri", S_TABLE_CELL)],
            [Paragraph("Aktarım Katmanı", S_TABLE_CELL),
             Paragraph("client.py / client_gbn.py", S_TABLE_CELL),
             Paragraph("S&W ve GBN protokol mantığı, kayıp simülasyonu", S_TABLE_CELL)],
            [Paragraph("Alıcı Katman", S_TABLE_CELL),
             Paragraph("server.py", S_TABLE_CELL),
             Paragraph("Paket kabulü, sıralama, MD5 bütünlük doğrulama", S_TABLE_CELL)],
            [Paragraph("Loglama Katmanı", S_TABLE_CELL),
             Paragraph("logger.py", S_TABLE_CELL),
             Paragraph("CSV olay kaydı: SEND, RECV, TIMEOUT, FAILED", S_TABLE_CELL)],
            [Paragraph("Analiz Katmanı", S_TABLE_CELL),
             Paragraph("analysis.py", S_TABLE_CELL),
             Paragraph("Metrik hesaplama, karşılaştırmalı grafik üretimi", S_TABLE_CELL)],
        ]
        tbl = Table(data, colWidths=[3.5*cm, 4.5*cm, 8.5*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), BLUE_DARK),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [GRAY_LIGHT, colors.white]),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        s.append(tbl)
    slide(story, "Sistem Mimarisi", s4)

    # ── SLIDE 5 — Protokol ───────────────────────────────────────────────────
    def s5(s):
        s.append(Paragraph("<b>Paket Türleri:</b>", S_BODY))
        data = [
            [Paragraph("Tür", S_TABLE_HDR),
             Paragraph("Alanlar", S_TABLE_HDR),
             Paragraph("Boyut", S_TABLE_HDR)],
            [Paragraph("DATA", S_TABLE_CELL),
             Paragraph("Type(1B), SeqNum(4B), TotalPkts(4B), PayloadLen(2B), Checksum(16B) + Payload", S_TABLE_CELL),
             Paragraph("27 B + payload", S_TABLE_CELL)],
            [Paragraph("ACK", S_TABLE_CELL),
             Paragraph("Type(1B), AckNum(4B), Checksum(16B)", S_TABLE_CELL),
             Paragraph("21 B", S_TABLE_CELL)],
            [Paragraph("START", S_TABLE_CELL),
             Paragraph("Type(1B), SeqNum=0, TotalPkts(4B), Checksum(16B)", S_TABLE_CELL),
             Paragraph("27 B", S_TABLE_CELL)],
            [Paragraph("END", S_TABLE_CELL),
             Paragraph("Type(1B), SeqNum=N, Checksum(16B)", S_TABLE_CELL),
             Paragraph("27 B", S_TABLE_CELL)],
        ]
        tbl = Table(data, colWidths=[2*cm, 11.5*cm, 3*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), BLUE_MID),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [GRAY_LIGHT, colors.white]),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        s.append(tbl)
        s.append(sp(0.5))
        s.append(Paragraph("<b>Aktarım Akışı:</b>", S_BODY))
        for it in [
            "Handshake: İstemci START gönderir → Sunucu ACK(0) yanıtlar",
            "Veri: Her chunk ayrı DATA paketi olarak gönderilir → Sunucu ACK(seq) yanıtlar",
            "Kapanış: İstemci END gönderir → Sunucu ACK(N) yanıtlar, dosyayı kaydeder",
            "Bütünlük: Her pakette MD5 checksum; aktarım sonunda dosyanın tamamı için MD5 karşılaştırması",
        ]:
            s.append(bullet(it))
    slide(story, "Protokol Tasarımı", s5)

    # ── SLIDE 6 — Stop-and-Wait ──────────────────────────────────────────────
    def s6(s):
        s.append(Paragraph(
            "Stop-and-Wait protokolünde istemci her paketi gönderir ve ACK gelmeden "
            "bir sonraki pakete geçmez. Kayıp veya timeout durumunda paket yeniden gönderilir.",
            S_BODY))
        s.append(sp(0.4))
        for it in [
            "Chunk boyutu: 1024 bayt",
            "Varsayılan timeout: 0.5 saniye (yapılandırılabilir)",
            "Maks. yeniden deneme: <b>5 deneme/paket</b> (PDF zorunluluğu)",
            "5 denemeden sonra başarısız paket FAILED olarak loglanır ve geçilir",
            "Aktarım sonunda kayıp paket sayısı ekrana yazdırılır",
            "İstemci ve sunucu ayrı ayrı MD5 yazdırır — manuel karşılaştırma imkânı",
        ]:
            s.append(bullet(it))
        s.append(sp(0.4))
        s.append(Paragraph("Çalıştırma örneği:", S_BODY))
        s.append(Paragraph(
            "python server.py<br/>"
            "python client.py --file donem_projesi.pdf --loss 0.1 --timeout 0.5",
            S_CODE))
    slide(story, "Stop-and-Wait Gerçeklemesi", s6)

    # ── SLIDE 7 — GBN ───────────────────────────────────────────────────────
    def s7(s):
        s.append(Paragraph(
            "Go-Back-N protokolünde istemci, ACK beklenmeksizin pencere boyutu kadar "
            "paketi art arda gönderir. Ayrı bir alıcı thread ACK'leri eşzamanlı işler.",
            S_BODY))
        s.append(sp(0.4))
        for it in [
            "Kayan pencere boyutu: yapılandırılabilir (varsayılan: 5)",
            "Alıcı thread ayrı çalışır; gönderici thread ile lock ile senkronize edilir",
            "Kümülatif ACK: ACK(n) alınırsa base n+1'e ilerler, timer yeniden başlar",
            "Timeout: base pencereden geri gönderim başlatılır",
            "Maks. yeniden deneme: <b>5 deneme/paket</b>; aşılırsa base ilerletilir",
            "Başarısız paket sayısı loglanır ve kullanıcıya raporlanır",
        ]:
            s.append(bullet(it))
        s.append(sp(0.4))
        s.append(Paragraph("Çalıştırma örneği:", S_BODY))
        s.append(Paragraph(
            "python client_gbn.py --file donem_projesi.pdf --loss 0.1 --window 5",
            S_CODE))
    slide(story, "Go-Back-N Gerçeklemesi", s7)

    # ── SLIDE 8 — Loglama ───────────────────────────────────────────────────
    def s8(s):
        s.append(Paragraph(
            "Her aktarım başlatıldığında otomatik olarak CSV log dosyası oluşturulur. "
            "Tüm ağ olayları zaman damgasıyla kaydedilir.",
            S_BODY))
        s.append(sp(0.4))
        data = [
            [Paragraph("Olay", S_TABLE_HDR),
             Paragraph("Açıklama", S_TABLE_HDR)],
            [Paragraph("SEND", S_TABLE_CELL),
             Paragraph("Paket gönderim zamanı, seq_num, payload_size", S_TABLE_CELL)],
            [Paragraph("RECV", S_TABLE_CELL),
             Paragraph("ACK alım zamanı ve ack_num", S_TABLE_CELL)],
            [Paragraph("TIMEOUT", S_TABLE_CELL),
             Paragraph("Zaman aşımı oluştuğunda seq_num kaydı", S_TABLE_CELL)],
            [Paragraph("FAILED", S_TABLE_CELL),
             Paragraph("5 denemede iletilememiş paketin seq_num kaydı", S_TABLE_CELL)],
        ]
        tbl = Table(data, colWidths=[3*cm, 13.5*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), BLUE_MID),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [GRAY_LIGHT, colors.white]),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        s.append(tbl)
        s.append(sp(0.4))
        s.append(Paragraph("Log dosyası adlandırma şeması:", S_BODY))
        s.append(Paragraph(
            "S&W : log_loss_&lt;kayıp&gt;_timeout_&lt;timeout&gt;.csv<br/>"
            "GBN : log_gbn_loss_&lt;kayıp&gt;_win_&lt;pencere&gt;.csv",
            S_CODE))
    slide(story, "Trafik İzleme ve Loglama", s8)

    # ── SLIDE 9 — Metrikler ──────────────────────────────────────────────────
    def s9(s):
        data = [
            [Paragraph("Metrik", S_TABLE_HDR),
             Paragraph("Formül", S_TABLE_HDR),
             Paragraph("Birim", S_TABLE_HDR)],
            [Paragraph("Throughput", S_TABLE_CELL),
             Paragraph("(Toplam gönderilen bit) / süre", S_TABLE_CELL),
             Paragraph("bps / kbps", S_TABLE_CELL)],
            [Paragraph("Goodput", S_TABLE_CELL),
             Paragraph("(Benzersiz iletilen bit) / süre", S_TABLE_CELL),
             Paragraph("bps / kbps", S_TABLE_CELL)],
            [Paragraph("Retransmission Rate", S_TABLE_CELL),
             Paragraph("(Toplam SEND − Benzersiz paket) / Benzersiz paket", S_TABLE_CELL),
             Paragraph("%", S_TABLE_CELL)],
            [Paragraph("Ortalama RTT", S_TABLE_CELL),
             Paragraph("Ort(ACK zamanı − SEND zamanı), her paket için", S_TABLE_CELL),
             Paragraph("ms", S_TABLE_CELL)],
            [Paragraph("Tamamlanma Süresi", S_TABLE_CELL),
             Paragraph("max(timestamp) − min(timestamp)", S_TABLE_CELL),
             Paragraph("s", S_TABLE_CELL)],
        ]
        tbl = Table(data, colWidths=[4*cm, 9*cm, 3.5*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), BLUE_DARK),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [GRAY_LIGHT, colors.white]),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        s.append(tbl)
    slide(story, "Performans Metrikleri", s9)

    # ── SLIDE 10 — Deney Senaryoları ─────────────────────────────────────────
    def s10(s):
        for title, items in [
            ("Senaryo A — Farklı Kayıp Oranları (S&W)", [
                "Kayıp: %0, %10, %20, %30",
                "Beklenti: Kayıp arttıkça throughput/goodput düşer, retransmission rate artar",
            ]),
            ("Senaryo B — S&W vs Go-Back-N Karşılaştırması", [
                "Aynı kayıp oranında (%10) iki protokol test edilir",
                "Beklenti: GBN yüksek throughput, S&W daha basit ama daha yavaş",
            ]),
            ("Senaryo C — Timeout Değerinin Etkisi", [
                "Timeout: 0.2 s, 0.5 s, 1.0 s",
                "Beklenti: Çok kısa timeout gereksiz retransmission üretir",
            ]),
            ("Senaryo D — Pencere Boyutunun Etkisi (GBN)", [
                "Pencere: 1, 5, 10",
                "Beklenti: Büyük pencere throughput'u artırır, hata maliyetini de artırır",
            ]),
        ]:
            s.append(Paragraph(f"<b>{title}</b>", S_BODY))
            for it in items:
                s.append(bullet(it))
            s.append(sp(0.3))
    slide(story, "Deney Senaryoları", s10)

    # ── SLIDE 11 — Grafik Sonuçları ──────────────────────────────────────────
    def s11(s):
        s.append(Paragraph(
            "analysis.py çalıştırıldığında log dosyalarından otomatik olarak aşağıdaki "
            "grafikler üretilmektedir. Tüm grafikler .png formatında projeye eklenir.",
            S_BODY))
        s.append(sp(0.4))

        img_files = [
            ("throughput_vs_loss.png", "Throughput vs Kayıp Oranı (S&W)"),
            ("goodput_vs_loss.png", "Goodput vs Kayıp Oranı (S&W)"),
            ("retransmission_vs_loss.png", "Retransmission Rate vs Kayıp Oranı (S&W)"),
            ("comparison_throughput.png", "Throughput: S&W vs GBN Karşılaştırması"),
        ]
        added = False
        for fname, caption in img_files:
            fpath = os.path.join(os.path.dirname(__file__), fname)
            if os.path.exists(fpath):
                try:
                    img = Image(fpath, width=7*cm, height=4.5*cm)
                    s.append(img)
                    s.append(Paragraph(caption, S_CAPTION))
                    s.append(sp(0.3))
                    added = True
                except Exception:
                    pass

        if not added:
            for fname, caption in img_files:
                s.append(bullet(f"<b>{fname}</b> — {caption}"))
            s.append(sp(0.3))
            s.append(Paragraph(
                "Grafikleri üretmek için: <font name='Courier'>python analysis.py</font>",
                S_BODY))
    slide(story, "Deney Sonuçları — Grafikler", s11)

    # ── SLIDE 12 — Karşılaştırmalı Değerlendirme ────────────────────────────
    def s12(s):
        data = [
            [Paragraph("Kriter", S_TABLE_HDR),
             Paragraph("Stop-and-Wait", S_TABLE_HDR),
             Paragraph("Go-Back-N", S_TABLE_HDR)],
            [Paragraph("Throughput", S_TABLE_CELL),
             Paragraph("Düşük (tek paket bekler)", S_TABLE_CELL),
             Paragraph("Yüksek (pencere dolu gönderir)", S_TABLE_CELL)],
            [Paragraph("Kayıp durumu", S_TABLE_CELL),
             Paragraph("Sadece kayıp paketi yeniden gönderir", S_TABLE_CELL),
             Paragraph("Tüm pencereyi geri gönderir", S_TABLE_CELL)],
            [Paragraph("Karmaşıklık", S_TABLE_CELL),
             Paragraph("Basit (tek thread)", S_TABLE_CELL),
             Paragraph("Karmaşık (çoklu thread, lock)", S_TABLE_CELL)],
            [Paragraph("Gecikme etkisi", S_TABLE_CELL),
             Paragraph("RTT her pakette hissedilir", S_TABLE_CELL),
             Paragraph("RTT pencere boyutuyla örtüşür", S_TABLE_CELL)],
            [Paragraph("Düşük kayıp (%0–5)", S_TABLE_CELL),
             Paragraph("Kabul edilebilir performans", S_TABLE_CELL),
             Paragraph("Belirgin avantaj", S_TABLE_CELL)],
            [Paragraph("Yüksek kayıp (>%20)", S_TABLE_CELL),
             Paragraph("Çok yavaş", S_TABLE_CELL),
             Paragraph("GBN de ciddi düşüş gösterir", S_TABLE_CELL)],
        ]
        tbl = Table(data, colWidths=[4*cm, 6.5*cm, 6*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), BLUE_DARK),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [GRAY_LIGHT, colors.white]),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        s.append(tbl)
    slide(story, "S&W vs GBN Karşılaştırmalı Değerlendirme", s12)

    # ── SLIDE 13 — Zorluklar ─────────────────────────────────────────────────
    def s13(s):
        for prob, sol in [
            ("GBN'de kümülatif ACK yönetimi",
             "base ve next_seq değişkenleri lock ile korunarak güncellendi"),
            ("Thread senkronizasyonu (gönderici-alıcı)",
             "threading.Lock() ile kritik bölgeler izole edildi"),
            ("Per-paket maks. yeniden deneme sayısı",
             "retry_counts dict'i ile her paketin deneme sayısı izlendi"),
            ("Dosya bütünlüğü doğrulaması",
             "Per-paket MD5 + tüm dosya MD5 karşılaştırması eklendi"),
            ("GBN loglarının analiz edilememesi",
             "analysis.py log_gbn_*.csv dosyalarını da tarayacak şekilde güncellendi"),
        ]:
            s.append(Paragraph(f"<b>Problem:</b> {prob}", S_BODY))
            s.append(Paragraph(f"<b>Çözüm:</b> {sol}", S_BODY))
            s.append(sp(0.3))
    slide(story, "Karşılaşılan Zorluklar ve Çözümler", s13)

    # ── SLIDE 14 — Bonus ─────────────────────────────────────────────────────
    def s14(s):
        s.append(Paragraph("<b>Uygulanan Bonus Özellikler:</b>", S_BODY))
        for it in [
            "✓  Go-Back-N kayan pencere protokolü gerçeklendi",
            "✓  Yapay kayıp ve gecikme simülasyon modülü",
            "✓  S&W ve GBN karşılaştırmalı analiz grafikleri",
            "✓  RTT ölçümü (SEND-ACK zaman farkı istatistiği)",
            "✓  Başarısız paket takibi ve raporlama (FAILED event)",
        ]:
            s.append(bullet(it))
        s.append(sp(0.5))
        s.append(Paragraph("<b>Gelecekte Yapılabilecek Geliştirmeler:</b>", S_BODY))
        for it in [
            "Selective Repeat — sadece kayıp paketi yeniden gönder",
            "Congestion control (AIMD) ile TCP benzeri tıkanıklık yönetimi",
            "Gerçek zamanlı görselleştirme paneli",
            "Wireshark / pcap tabanlı analiz desteği",
            "Çoklu istemci desteği",
        ]:
            s.append(bullet(it))
    slide(story, "Bonus Özellikler ve Gelecek Çalışmalar", s14)

    # ── SLIDE 15 — Sonuç ─────────────────────────────────────────────────────
    def s15(s):
        s.append(Paragraph(
            "Bu proje kapsamında UDP üzerinde tam işlevsel, güvenilir bir dosya aktarım "
            "sistemi başarıyla geliştirilmiştir. Temel zorunlu gereksinimler eksiksiz "
            "karşılanmıştır; Go-Back-N ve karşılaştırmalı analiz ise bonus özellik olarak "
            "sisteme dahil edilmiştir.",
            S_BODY))
        s.append(sp(0.5))
        for it in [
            "Stop-and-Wait: basit, güvenilir; yüksek RTT'de verimsiz",
            "Go-Back-N: yüksek throughput; ancak pencere geri gönderimi ek yük getirir",
            "Kayıp oranı %10 üzerine çıktığında her iki protokolde ciddi performans düşüşü gözlemlendi",
            "Timeout süresi çok kısa tutulursa gereksiz retransmission oluştuğu doğrulandı",
            "MD5 bütünlük doğrulaması ile veri güvenilirliği garanti altına alındı",
        ]:
            s.append(bullet(it))
        s.append(sp(1.5))
        s.append(Paragraph("Teşekkürler / Sorular?", style("Thanks",
            fontSize=20, fontName="ArialBD", textColor=BLUE_DARK,
            alignment=TA_CENTER)))
    slide(story, "Sonuç", s15)

    return story

# ── Build PDF ────────────────────────────────────────────────────────────────
def main():
    out = os.path.join(os.path.dirname(__file__), "sunum.pdf")
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="NetProbe Sunum",
        author="Halil ALPAK",
        subject="Bilgisayar Ağları Dönem Projesi",
    )
    doc.build(build_story())
    print(f"Sunum oluşturuldu: {out}")

if __name__ == "__main__":
    main()
