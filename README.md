# 🧠 Bilginay — Çok Uzman Akıl Yürütme Sistemi

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-CPU%20Only-orange?style=for-the-badge&logo=pytorch)
![License](https://img.shields.io/badge/Lisans-MIT-green?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Mimari-MoE%20%2B%20CoT-purple?style=for-the-badge)
![Languages](https://img.shields.io/badge/Dil-TR%20%2F%20EN-red?style=for-the-badge)

**Türkçe ve İngilizce destekli, CPU üzerinde çalışan,  
Mixture of Experts + Chain-of-Thought mimarisine sahip deneysel Micro-LLM sistemi.**

[Özellikler](#-özellikler) · [Mimari](#-mimari) · [Kurulum](#-kurulum) · [Kullanım](#-kullanım) · [Veri Seti](#-veri-seti) · [Katkı](#-katkı)

</div>

---

## 📖 Nedir?

**Bilginay**, harici bir API anahtarına ya da GPU'ya ihtiyaç duymadan, tamamen kendi bilgisayarınızın işlemcisi (CPU) üzerinde çalışan, modüler bir yapay zeka araştırma platformudur.

Sıradan bir chatbot'tan farkı şudur: Bilginay bir soruyu aldığında önce **sorunun köküne iner**, ardından üç farklı uzmanlık seviyesinde (İlkokul, Ortaokul, Akademik) ayrı ayrı cevap üretir ve bu cevapları bir **Master Uzman** aracılığıyla tek bir tutarlı senteze dönüştürür.

> "Cevabı ezberden vermek yerine, önce **neden** ve **nasıl** sorularını sor; sonra konuş."
> — Bilginay'ın tasarım felsefesi

---

## ✨ Özellikler

| Özellik | Açıklama |
|---|---|
| 🔗 **Mixture of Experts (MoE)** | 3 seviyede uzman (Primary / Middle / High), bir Master tarafından yönetilir |
| 🤔 **Chain-of-Thought (CoT)** | Her cevap önce `Neden → Nasıl → Sonuç` zinciri kurarak üretilir |
| 🇹🇷🇬🇧 **İki Dil Desteği** | Türkçe ve İngilizce soruları otomatik algılar ve cevaplar |
| 🧩 **Genişletilebilir Bilgi Tabanı** | `KNOWLEDGE_BASE` sözlüğüne konu ekleyerek sistemi büyütebilirsiniz |
| 🔌 **Ollama / Yerel LLM Desteği** | Bilgisayarınızda Ollama çalışıyorsa sistemi gerçek bir LLM'e bağlar |
| 🧠 **NanoLLM (PyTorch)** | Sıfırdan yazılmış CPU-only Transformer mimarisi; üzerinde eğitim yapılabilir |
| 💾 **Memory Mapped Eğitim** | 3 GB+ veri setini RAM'e yüklemeden `mmap` ile diskten canlı okuyarak eğitir |
| 📦 **Sıfır Bulut Bağımlılığı** | API anahtarı, internet bağlantısı veya GPU gerekmez |

---

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                        KULLANICI                            │
└───────────────────────────┬─────────────────────────────────┘
                            │ Soru (TR / EN)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    main.py  (CLI Arayüzü)                   │
│                  Rich · Panel · Markdown                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     AIEngine  (Strategy Pattern)            │
│          ChatStrategy / TrainStrategy / InferenceStrategy   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    MasterExpert  (MoE Router)               │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│   │PrimaryExpert │  │MiddleExpert  │  │  HighExpert  │     │
│   │  (İlkokul)   │  │  (Ortaokul)  │  │  (Akademik)  │     │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└──────────┼─────────────────┼─────────────────┼─────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │ (Her uzman aynı motoru kullanır)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  reasoning_engine.py                        │
│  ┌────────────────┐  ┌──────────────────┐  ┌────────────┐  │
│  │  QueryAnalyzer │→ │  ReasoningChain  │→ │ResponseSyn │  │
│  │  (Dil/Niyet/   │  │  Neden→Nasıl→    │  │ th (Seviye │  │
│  │   Konu Tespit) │  │  Sonuç Zinciri)  │  │ Dil Tonu)  │  │
│  └────────────────┘  └──────────────────┘  └────────────┘  │
│                         │                                   │
│                         ▼                                   │
│                   KNOWLEDGE_BASE                            │
│   (Yerçekimi, Fotosentez, DNA, Python, YZ, Atatürk...)      │
└─────────────────────────────────────────────────────────────┘
           │
           │ (PyTorch varsa)
           ▼
┌─────────────────────────────────────────────────────────────┐
│                 NanoLLM  (nano_llm.py)                      │
│       Decoder-only Transformer  ·  CPU  ·  PyTorch          │
│   n_embd=64  ·  n_head=4  ·  n_layer=4  ·  block_size=128  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Proje Yapısı

```
bilginay/
├── main.py                  # CLI giriş noktası (Rich arayüzü)
├── generate_data.py         # 3 GB+ ikidilli CoT veri seti üreticisi
├── test_reasoning.py        # Mantık motoru birim testi
├── requirements.txt         # Python bağımlılıkları
├── .env                     # Ortam değişkenleri (Ollama URL vb.)
│
├── core/
│   ├── reasoning_engine.py  # ⭐ Asıl akıl yürütme motoru (CoT + KB)
│   ├── experts.py           # MoE uzman sınıfları + MasterExpert
│   ├── engine.py            # Strategy Pattern — AIEngine
│   ├── nano_llm.py          # PyTorch Transformer (CPU-only NanoLLM)
│   ├── trainer.py           # Memory-mapped PyTorch eğitim döngüsü
│   ├── api_client.py        # Yerel LLM (Ollama) HTTP istemcisi
│   ├── turkish_nlp.py       # Türkçe kök bulma + duygu/niyet analizi
│   ├── memory.py            # SQLite + NumPy vektör belleği
│   └── culture.py           # Türk kültürü bağlam modülü
│
└── data/
    ├── dataset.txt          # Küçük ölçekli test verisi
    └── dialogues.txt        # 3 GB ikidilli CoT eğitim veri seti
```

---

## 🚀 Kurulum

### Gereksinimler

- Python **3.11+**
- Windows / Linux / macOS
- GPU **gerekmez** — tamamen CPU üzerinde çalışır

### 1. Depoyu klonlayın

```bash
git clone https://github.com/Kadirqe/bilginay.git
cd bilginay
```

### 2. Sanal ortam oluşturun (önerilir)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

### 4. Ortam değişkenlerini ayarlayın

`.env` dosyasını düzenleyin (Ollama kullanmak isteyenler için):

```env
LOCAL_LLM_URL=http://localhost:11434/api/generate
LOCAL_MODEL_NAME=llama3
```

> **Not:** Ollama kurulu değilse sistem otomatik olarak yerleşik mantık motoruna (ReasoningEngine) geçer.

---

## 🖥️ Kullanım

### Sistemı Başlatın

```bash
python main.py
```

### Kullanılabilir Komutlar

```
Bilginay> merhaba
Bilginay> nasılsın
Bilginay> yerçekimi nedir
Bilginay> fotosentez nasıl çalışır
Bilginay> yapay zeka nedir
Bilginay> bilinç nedir
Bilginay> What is gravity?
Bilginay> konular          ← Bilinen tüm konuları listeler
Bilginay> modeli eğit      ← PyTorch eğitimini başlatır
Bilginay> çıkış            ← Programı kapatır
```

### Örnek Çıktı

```
╔══════════════════════════════════════════════════════╗
║      Bilginay — Çok Uzman Akıl Yürütme Sistemi       ║
║   Türkçe & İngilizce · Chain-of-Thought · MoE        ║
╚══════════════════════════════════════════════════════╝

Bilginay> yerçekimi nedir

┌──────────────────────────────────────────────────────────────┐
│ Bilginay — Master Uzman Sentezi                              │
│ Konu: yercekimi                                              │
│                                                              │
│ [Ilkokul Uzmani]                                             │
│ >> Yerçekimi, kütlesi olan her cismin diğer cisimleri        │
│    kendine çektiği evrensel bir kuvvettir.                   │
│ Hatirla: Bu kuvvet sayesinde gezegenler yörüngede kalır...   │
│                                                              │
│ [Ortaokul Uzmani]                                            │
│ Yerçekimi, kütlesi olan her cismin diğer cisimleri...        │
│ Neden Onemli: Newton, elmanın ağaçtan düşerken neden yere    │
│               doğru gittiğini sorguladı.                     │
│                                                              │
│ [Akademik Uzman]                                             │
│ Yerçekimi, kütlesi olan her cismin...                        │
│ Gerekce: Newton, elmanın ağaçtan düşerken...                 │
│ Mekanizma: F = G × (m₁ × m₂) / r²                          │
│ Cikarim: Bu kuvvet sayesinde gezegenler yörüngede kalır...   │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Veri Seti

Bilginay, **3 GB+** büyüklüğünde, Türkçe ve İngilizce diyaloglardan oluşan bir eğitim veri seti üzerinde eğitilmek üzere tasarlanmıştır.

### Veri Seti Üretimi

```bash
python generate_data.py
```

Bu komut `data/dialogues.txt` dosyasını oluşturur (yaklaşık 3 GB).

### Veri Formatı (Chain-of-Thought)

```
Kullanıcı: Yerçekimi nedir?
Bilginay: <düşün>Yerçekimi konusunu basit bir şekilde ele almalıyım.
Gezegenlerin kütlesinden dolayı birbirlerini nasıl çektiklerinden
ve elmanın yere düşmesi örneğinden bahsedebilirim.</düşün>
Yerçekimi, kütlesi olan nesnelerin birbirini çektiği doğal bir kuvvettir.

User: What is gravity?
Bilginay: <think>I should explain gravity simply...</think>
Gravity is a natural force that causes objects with mass to attract each other.
```

---

## 🤖 NanoLLM ile Eğitim

PyTorch kurulu ve çalışıyor ise gerçek bir model eğitimi başlatabilirsiniz:

```bash
# Arayüzden
python main.py
Bilginay> modeli eğit
```

veya doğrudan:

```python
from core.trainer import NanoTrainer

trainer = NanoTrainer("data/dialogues.txt")
trainer.train_expert("primary", iterations=3000)
trainer.train_expert("middle",  iterations=3000)
trainer.train_expert("high",    iterations=3000)
```

Eğitilen ağırlıklar `models/` klasörüne `.pt` uzantısıyla kaydedilir.

### Model Mimarisi

| Parametre | Değer |
|---|---|
| Katman Sayısı (`n_layer`) | 4 |
| Gömme Boyutu (`n_embd`) | 64 |
| Attention Kafası (`n_head`) | 4 |
| Bağlam Penceresi (`block_size`) | 128 |
| Tokenizasyon | Kelime-Bazlı (Word-Level) |
| Hedef Donanım | CPU (GPU'suz) |
| Eğitim Algoritması | AdamW |

---

## 🧩 Bilgi Tabanını Genişletme

`core/reasoning_engine.py` dosyasındaki `KNOWLEDGE_BASE` sözlüğüne yeni konular ekleyerek sistemi büyütebilirsiniz:

```python
KNOWLEDGE_BASE["kara_delikler"] = {
    "tr": "Kara delikler, kütleçekiminin o kadar güçlü olduğu uzay bölgeleridir ki...",
    "en": "Black holes are regions of space where gravity is so strong that...",
    "neden": "Çok büyük yıldızlar ömürlerini tükettiklerinde çökerek kara delik oluştururlar.",
    "nasil": "Schwarzschild yarıçapı ile tanımlanır: r = 2GM/c²",
    "sonuc": "Işık bile bu bölgeden kaçamaz; bu yüzden 'kara' olarak adlandırılırlar.",
    "keywords": ["kara delik", "black hole", "hawking", "olay ufku", "singülarite"]
}
```

---

## 📦 Bağımlılıklar

```
torch             # NanoLLM ve PyTorch eğitim döngüsü (opsiyonel)
rich              # Terminal arayüzü (Panel, Markdown, Progress)
requests          # Yerel LLM (Ollama) HTTP istemcisi
python-dotenv     # .env dosyası okuma
numpy             # Vektör belleği hesaplamaları
snowballstemmer   # Türkçe kelime kök bulma
pybreaker         # Circuit Breaker (API güvenlik deseni)
```

> **PyTorch hatası alıyorsanız:** Windows'ta `[WinError 1114]` hatası Microsoft Visual C++ Redistributable eksikliğinden kaynaklanır. Sistem otomatik olarak Python tabanlı simülasyon moduna geçer.

---

## 🛣️ Yol Haritası

- [x] Strategy Pattern + MoE mimarisi
- [x] Chain-of-Thought (CoT) akıl yürütme motoru
- [x] İkidilli (TR/EN) destek ve otomatik dil tespiti
- [x] Memory-mapped 3 GB+ veri seti eğitimi
- [x] Genişletilebilir bilgi tabanı
- [x] SQLite vektör belleği
- [ ] Alan uzmanları (Tıp, Hukuk, Tarih, Mühendislik)
- [ ] RAG (Retrieval-Augmented Generation) entegrasyonu
- [ ] Eğitilmiş NanoLLM ağırlıklarının uzmanlarla entegrasyonu
- [ ] Web arayüzü (FastAPI + minimal UI)
- [ ] Model ağırlıklarının Hugging Face'e yüklenmesi

---

## 🤝 Katkı

Katkılarınızı memnuniyetle karşılıyoruz!

1. Depoyu fork edin
2. Yeni bir dal oluşturun: `git checkout -b ozellik/yeni-uzman`
3. Değişikliklerinizi yapın ve commit edin: `git commit -m 'feat: tıp uzmanı eklendi'`
4. Dalı gönderin: `git push origin ozellik/yeni-uzman`
5. Pull Request açın

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında lisanslanmıştır.

---

## 👨‍💻 Yazar

**Huseyin** — Yapay Zeka Araştırmacısı & Geliştirici  
Bilginay, tamamen CPU üzerinde çalışan, erişilebilir ve şeffaf bir yapay zeka sistemi inşa etme vizyonuyla geliştirilmektedir.

---

<div align="center">
<sub>Bilginay — Bilgi + İnay (İncelik, Zariflik)</sub><br>
<sub>Yapay zekanın gücünü herkesin erişebileceği bir seviyeye taşımak için.</sub>
</div>
