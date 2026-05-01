"""
reasoning_engine.py
─────────────────────────────────────────────────────────────────────────────
Bilginay'ın gerçek "düşünme" katmanı.

Mimari:
  1. QueryAnalyzer   — soruyu dilbilgisel/semantik olarak parçalar
  2. KnowledgeBase   — bilgi veri tabanı (genişletilebilir dict/JSON)
  3. ReasoningChain  — "neden → nasıl → sonuç" zinciri kurar
  4. ResponseSynth   — seviyeye göre dil tonunu ayarlayıp cevabı üretir
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────
# 1. Bilgi Tabanı (Genişletilebilir)
# ──────────────────────────────────────────────────────────────────────────

KNOWLEDGE_BASE: dict[str, dict] = {
    # ── Genel Sohbet ──────────────────────────────────────────────────────
    "selamlama": {
        "tr": "Merhaba! Ben Bilginay. Size nasıl yardımcı olabilirim?",
        "en": "Hello! I'm Bilginay. How can I help you?",
        "neden": "İnsanlar sosyal bir canlıdır; karşılıklı selamlama güveni ve iletişimi başlatır.",
        "nasil": "Gülümseyerek, samimi ve sıcak bir dille karşılık veririm.",
        "sonuc": "Konuşmanın temelini sevgi ve saygıyla atarız.",
        "keywords": ["merhaba", "selam", "günaydın", "iyi günler", "hey", "hi", "hello"]
    },
    "hal_hatir": {
        "tr": "Teşekkür ederim, çok iyiyim! Siz nasılsınız?",
        "en": "Thank you, I'm doing great! How about you?",
        "neden": "Hal hatır sormak, karşıdaki kişiye değer verdiğini göstermenin en doğal yoludur.",
        "nasil": "Samimi bir ilgiyle, hem kendi durumumu paylaşır hem de sizi sorarım.",
        "sonuc": "İki taraflı bir sıcaklık ve güven ortamı oluşur.",
        "keywords": ["nasılsın", "nasıl gidiyor", "ne haber", "iyi misin", "how are you", "how are u"]
    },
    # ── Bilim ─────────────────────────────────────────────────────────────
    "yercekimi": {
        "tr": "Yerçekimi, kütlesi olan her cismin diğer cisimleri kendine çektiği evrensel bir kuvvettir.",
        "en": "Gravity is a universal force by which all objects with mass attract each other.",
        "neden": "Newton, elmanın ağaçtan düşerken neden yere doğru gittiğini sorguladı. Cevap: kütleler arası çekim.",
        "nasil": "F = G × (m₁ × m₂) / r² formülüyle hesaplanır. G evrensel çekim sabitidir (6.674×10⁻¹¹ Nm²/kg²).",
        "sonuc": "Bu kuvvet sayesinde gezegenler yörüngede kalır, Ay Dünya'nın etrafında döner, siz koltuğunuzda otururken yere saplanmaz kalmazsınız.",
        "keywords": ["yerçekimi", "yer çekimi", "çekim", "gravity", "newton", "kütle", "düşme"]
    },
    "fotosentez": {
        "tr": "Fotosentez, bitkilerin güneş enerjisini kullanarak CO₂ ve H₂O'dan organik madde (glikoz) ve O₂ ürettiği biyokimyasal süreçtir.",
        "en": "Photosynthesis is the biochemical process where plants use sunlight to convert CO₂ and H₂O into glucose and O₂.",
        "neden": "Bitkiler kendi besinlerini üretemezse yaşayamaz; güneş enerjisini kimyasal enerjiye çevirmek için bu mekanizmayı geliştirdiler.",
        "nasil": "6CO₂ + 6H₂O + ışık enerjisi → C₆H₁₂O₆ + 6O₂. Kloroplast içindeki klorofil pigmenti ışığı emerek reaksiyonu tetikler.",
        "sonuc": "Atmosferdeki oksijen büyük ölçüde fotosentez sayesinde vardır. Tüm besin zinciri bitkilere dayanır.",
        "keywords": ["fotosentez", "photosynthesis", "bitki", "oksijen", "klorofil", "güneş enerjisi", "co2"]
    },
    "dna": {
        "tr": "DNA (Deoksiribonükleik Asit), canlıların genetik bilgisini taşıyan çift sarmal yapıdaki moleküldür.",
        "en": "DNA (Deoxyribonucleic Acid) is the double-helix molecule that carries the genetic information of living organisms.",
        "neden": "Kalıtımın nasıl gerçekleştiğini açıklamak için genetik bilginin bir molekülde kodlanmış olması gerekiyordu.",
        "nasil": "Adenin-Timin ve Guanin-Sitozin baz çiftleri arasındaki hidrojen bağları çift sarmalı birbirine bağlar. Baz dizisi genleri oluşturur.",
        "sonuc": "Hücreler bölündüğünde DNA kopyalanır; bu sayede genetik bilgi nesilden nesile aktarılır.",
        "keywords": ["dna", "gen", "genetik", "kalıtım", "kromozom", "rna", "protein", "double helix"]
    },
    "evrim": {
        "tr": "Evrim, canlı türlerinin doğal seçilim ve mutasyon aracılığıyla nesiller boyunca değiştiği biyolojik süreçtir.",
        "en": "Evolution is the biological process by which species change over generations through natural selection and mutation.",
        "neden": "Çevre koşullarına en iyi uyum sağlayan bireyler hayatta kalır ve genlerini aktarır; bu kümülatif değişim türleşmeye yol açar.",
        "nasil": "Mutasyon → Genetik çeşitlilik → Doğal seçilim → Uyumlu bireylerin hayatta kalması → Nesiller boyu birikim.",
        "sonuc": "Bugün Dünya'daki tüm canlı çeşitliliği bu mekanizma ile açıklanır. Darwin bu teoriyi 1859'da 'Türlerin Kökeni' kitabıyla ortaya koydu.",
        "keywords": ["evrim", "evolution", "darwin", "doğal seçilim", "mutasyon", "tür", "species"]
    },
    # ── Fizik ─────────────────────────────────────────────────────────────
    "enerji": {
        "tr": "Enerji, iş yapabilme kapasitesidir. Türleri arasında kinetik, potansiyel, ısı, ışık ve elektrik enerjisi sayılabilir.",
        "en": "Energy is the capacity to do work. Its types include kinetic, potential, thermal, light, and electrical energy.",
        "neden": "Enerji olmadan hiçbir fiziksel ya da kimyasal değişim mümkün değildir.",
        "nasil": "Enerji dönüşüm yoluyla bir formdan diğerine geçer; toplam enerji her zaman korunur (Termodinamiğin 1. Yasası).",
        "sonuc": "Elektrik santralleri kimyasal veya nükleer enerjiyi elektriğe çevirir; bu da evlerinizi aydınlatır.",
        "keywords": ["enerji", "energy", "kinetik", "potansiyel", "ısı", "güç", "watt", "joule"]
    },
    "isik": {
        "tr": "Işık, hem dalga hem de parçacık özelliği gösteren elektromanyetik radyasyondur. Vakumda hızı ~3×10⁸ m/s'dir.",
        "en": "Light is electromagnetic radiation that exhibits both wave and particle properties. Its speed in vacuum is ~3×10⁸ m/s.",
        "neden": "Maxwell elektromanyetik dalgaları keşfetti; Einstein ise foton teorisiyle ışığın parçacık boyutunu açıkladı.",
        "nasil": "Fotonlar titreşen elektrik ve manyetik alanlardan oluşur. Dalga boyu rengi belirler (400-700 nm görünür ışık).",
        "sonuc": "Güneş enerjisi, lazerler, fotoğraf makineleri, fiber optik iletişim — hepsinin temelinde ışık fiziği yatar.",
        "keywords": ["ışık", "light", "foton", "dalga", "hız", "laser", "renk", "spektrum"]
    },
    # ── Matematik ─────────────────────────────────────────────────────────
    "pi": {
        "tr": "Pi (π), bir çemberin çevresinin çapına oranıdır; yaklaşık 3.14159... değerinde irrasyonel ve aşkın bir sayıdır.",
        "en": "Pi (π) is the ratio of a circle's circumference to its diameter; approximately 3.14159..., an irrational and transcendental number.",
        "neden": "Çemberlerin geometrisi incelenirken bu sabitin varlığı kaçınılmaz hale geldi.",
        "nasil": "Archimedes çokgenlerle yaklaşık değerini hesapladı. Modern bilgisayarlar trilyon basamağa kadar hesaplamıştır.",
        "sonuc": "Trigonometri, sinyal işleme, fizik ve mühendisliğin her alanında π kullanılır.",
        "keywords": ["pi", "π", "çember", "çevre", "çap", "trigonometri", "matematk"]
    },
    "asal_sayi": {
        "tr": "Asal sayı, 1'den büyük olan ve yalnızca 1 ile kendisine bölünebilen tam sayıdır. Örn: 2, 3, 5, 7, 11...",
        "en": "A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself. E.g.: 2, 3, 5, 7, 11...",
        "neden": "Asal sayılar, matematiğin 'yapı taşları'dır; her tam sayı asal çarpanlarına ayrılabilir.",
        "nasil": "Bir sayının asal olup olmadığını test etmek için karekökünden küçük asal sayılara bölünüp bölünmediği kontrol edilir.",
        "sonuc": "RSA şifreleme (internet güvenliğinin temeli) büyük asal sayıları çarpmak kolay ama çarpanlarına ayırmak zor olduğu gerçeğine dayanır.",
        "keywords": ["asal", "prime", "sayı", "bölen", "mathematics"]
    },
    # ── Yapay Zeka / Bilgisayar ────────────────────────────────────────────
    "yapay_zeka": {
        "tr": "Yapay Zeka (YZ), makinelerin insan benzeri düşünme, öğrenme ve karar verme süreçlerini gerçekleştirmesini sağlayan bilgisayar bilimleri dalıdır.",
        "en": "Artificial Intelligence (AI) is the branch of computer science enabling machines to perform human-like thinking, learning and decision making.",
        "neden": "İnsanların yapabileceği karmaşık bilişsel görevleri otomatize etmek için YZ geliştirilmiştir.",
        "nasil": "Makine öğrenmesi, derin öğrenme ve sinir ağları aracılığıyla büyük veri setlerinden örüntüler öğrenilir.",
        "sonuc": "Bugün YZ; tıp, hukuk, finans, otonom araçlar ve dil modellerinde (GPT, Bilginay gibi!) kullanılmaktadır.",
        "keywords": ["yapay zeka", "ai", "artificial intelligence", "makine öğrenmesi", "deep learning", "neural", "model", "llm"]
    },
    "python": {
        "tr": "Python, okunması kolay sözdizimi olan, yüksek seviyeli, genel amaçlı bir programlama dilidir.",
        "en": "Python is a high-level, general-purpose programming language known for its clean and readable syntax.",
        "neden": "Öğrenmesi kolay, kütüphane ekosistemi geniş ve hızlı prototipleme imkânı tanıdığı için popülerdir.",
        "nasil": "def ile fonksiyon tanımlanır, class ile nesne oluşturulur, import ile kütüphaneler yüklenir.",
        "sonuc": "Data science, web geliştirme, otomasyon ve yapay zekada en yaygın kullanılan dillerden biridir.",
        "keywords": ["python", "programlama", "kod", "fonksiyon", "class", "script", "def", "import"]
    },
    # ── Tarih / Kültür ─────────────────────────────────────────────────────
    "ataturk": {
        "tr": "Mustafa Kemal Atatürk, Türkiye Cumhuriyeti'nin kurucusu ve ilk cumhurbaşkanıdır (1923-1938).",
        "en": "Mustafa Kemal Atatürk is the founder and first president of the Republic of Turkey (1923-1938).",
        "neden": "Osmanlı İmparatorluğu'nun çöküşünün ardından yeni, laik ve modern bir devlet kurmak için harekete geçti.",
        "nasil": "Kurtuluş Savaşı'nı örgütledi, ardından harf, hukuk, eğitim ve kıyafet reformlarıyla modernleşmeyi hızlandırdı.",
        "sonuc": "Bugünkü Türkiye Cumhuriyeti'nin demokratik, laik ve üniter yapısı onun vizyon ve reformlarına dayanmaktadır.",
        "keywords": ["atatürk", "mustafa kemal", "cumhuriyet", "türkiye", "kurtuluş savaşı", "cumhurbaşkanı"]
    },
    # ── Felsefe ────────────────────────────────────────────────────────────
    "bilinc": {
        "tr": "Bilinç, öznel deneyimin ve iç gözlemin toplamıdır; felsefenin ve nörobilimin en zor sorularından birini oluşturur.",
        "en": "Consciousness is the totality of subjective experience and introspection; it poses one of the hardest questions in philosophy and neuroscience.",
        "neden": "Beynin neden öznel deneyim (qualia) yarattığı henüz tam olarak açıklanamamıştır — bu 'zor problem' olarak bilinir.",
        "nasil": "Nörobilimciler beyin aktivitelerini fMRI ile inceler; filozoflar fenomenoloji, fonksiyonalizm gibi teoriler geliştirir.",
        "sonuc": "Bilinç araştırmaları yapay zeka bilincinin mümkün olup olmadığı sorusunu da doğrudan etkiler.",
        "keywords": ["bilinç", "consciousness", "felsefe", "philosophy", "qualia", "zihin", "mind", "beyin"]
    },
}

# ──────────────────────────────────────────────────────────────────────────
# 2. Soru Analiz Motoru
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class QueryAnalysis:
    raw: str
    lang: str = "tr"               # "tr" veya "en"
    intent: str = "soru"           # soru / selamlama / hal_hatir / bilinmeyen
    matched_topic: Optional[str] = None
    confidence: float = 0.0
    keywords_found: list[str] = field(default_factory=list)


class QueryAnalyzer:
    """Soruyu dil, niyet ve konu açısından parçalar."""

    EN_MARKERS = {"what","who","where","when","how","why","is","are","can","do","does",
                  "hello","hi","hey","how are you","how are u"}

    def analyze(self, text: str) -> QueryAnalysis:
        result = QueryAnalysis(raw=text)
        result.lang = self._detect_lang(text)
        result.intent = self._detect_intent(text)
        result.matched_topic, result.confidence, result.keywords_found = self._match_topic(text)
        return result

    def _detect_lang(self, text: str) -> str:
        lower = text.lower()
        # Türkçe karakterler varsa TR
        if re.search(r'[çğışöüÇĞİŞÖÜ]', text):
            return "tr"
        en_count = sum(1 for w in self.EN_MARKERS if w in lower.split())
        return "en" if en_count > 0 else "tr"

    def _detect_intent(self, text: str) -> str:
        lower = text.lower()
        greeting_tr = {"merhaba", "selam", "günaydın", "iyi günler", "iyi akşamlar", "iyi geceler"}
        greeting_en = {"hello", "hi", "hey", "good morning", "good evening"}
        halhatir_tr = {"nasılsın", "nasılsınız", "ne haber", "ne var ne yok", "iyi misin"}
        halhatir_en = {"how are you", "how are u", "how r u", "sup", "what's up"}

        for g in greeting_tr | greeting_en:
            if g in lower:
                return "selamlama"
        for g in halhatir_tr | halhatir_en:
            if g in lower:
                return "hal_hatir"
        if any(q in lower for q in ["nedir","neden","nasıl","nerede","ne zaman","kim","what","why","how","where","who"]):
            return "soru"
        return "genel"

    def _match_topic(self, text: str) -> tuple[Optional[str], float, list[str]]:
        lower = text.lower()
        best_topic = None
        best_score = 0
        best_kw: list[str] = []

        for topic, data in KNOWLEDGE_BASE.items():
            kws: list[str] = data.get("keywords", [])
            found = [kw for kw in kws if kw in lower]
            score = len(found) / max(len(kws), 1)
            if score > best_score:
                best_score = score
                best_topic = topic
                best_kw = found

        return (best_topic, best_score, best_kw) if best_score > 0 else (None, 0.0, [])


# ──────────────────────────────────────────────────────────────────────────
# 3. Akıl Yürütme Zinciri (Chain-of-Thought)
# ──────────────────────────────────────────────────────────────────────────

class ReasoningChain:
    """
    Bir soruyu 'Neden → Nasıl → Sonuç' adımlarıyla işleyerek
    yapılandırılmış bir düşünce zinciri üretir.
    """

    def reason(self, analysis: QueryAnalysis) -> dict:
        topic = analysis.matched_topic
        lang = analysis.lang

        if topic and topic in KNOWLEDGE_BASE:
            kb = KNOWLEDGE_BASE[topic]
            return {
                "cevap": kb.get("en" if lang == "en" else "tr", ""),
                "neden": kb.get("neden", ""),
                "nasil": kb.get("nasil", ""),
                "sonuc": kb.get("sonuc", ""),
                "topic": topic,
                "confidence": analysis.confidence,
            }

        # Konu bulunamadıysa: intent'e göre jenerik mantık
        if analysis.intent == "selamlama":
            return self.reason(QueryAnalysis(raw=analysis.raw, intent="selamlama", matched_topic="selamlama"))
        if analysis.intent == "hal_hatir":
            return self.reason(QueryAnalysis(raw=analysis.raw, intent="hal_hatir", matched_topic="hal_hatir"))

        # Tamamen bilinmeyen
        return {
            "cevap": "" if lang == "tr" else "",
            "neden": "",
            "nasil": "",
            "sonuc": "",
            "topic": None,
            "confidence": 0.0,
        }


# ──────────────────────────────────────────────────────────────────────────
# 4. Cevap Sentezleyici (Seviye-Duyarlı Dil Tonu)
# ──────────────────────────────────────────────────────────────────────────

class ResponseSynth:
    """Akıl yürütme çıktısını belirtilen eğitim seviyesinde dile getirir."""

    def synthesize(self, reasoning: dict, level: str, query: str) -> str:
        cevap = reasoning["cevap"]
        neden = reasoning["neden"]
        nasil = reasoning["nasil"]
        sonuc = reasoning["sonuc"]
        confidence = reasoning["confidence"]

        # Konu bulunamadıysa dürüst bir yanıt ver
        if not cevap and confidence == 0.0:
            return self._unknown_response(query, level)

        if level == "primary":
            return self._primary(query, cevap, sonuc)
        elif level == "middle":
            return self._middle(query, cevap, neden, sonuc)
        else:
            return self._high(query, cevap, neden, nasil, sonuc)

    def _primary(self, query: str, cevap: str, sonuc: str) -> str:
        return (
            f"[Ilkokul Uzmani]\n"
            f">> {cevap}\n"
            f"Hatirla: {sonuc.split('.')[0]}." if sonuc else f">> {cevap}"
        )

    def _middle(self, query: str, cevap: str, neden: str, sonuc: str) -> str:
        parts = [f"[Ortaokul Uzmani]\n{cevap}"]
        if neden:
            parts.append(f"Neden Onemli: {neden}")
        if sonuc:
            parts.append(f"Sonuc: {sonuc}")
        return "\n".join(parts)

    def _high(self, query: str, cevap: str, neden: str, nasil: str, sonuc: str) -> str:
        parts = [f"[Akademik Uzman]\n{cevap}"]
        if neden:
            parts.append(f"Gerekce: {neden}")
        if nasil:
            parts.append(f"Mekanizma: {nasil}")
        if sonuc:
            parts.append(f"Cikarim: {sonuc}")
        return "\n".join(parts)

    def _unknown_response(self, query: str, level: str) -> str:
        base = (
            f"'{query}' konusunda su an yeterli bilgiye sahip degilim. "
            "Bilgi tabanim genisleyince bu soruya daha iyi yanit verebilecegim."
        )
        if level == "primary":
            return f"[Ilkokul Uzmani]\nHmm, bunu tam bilmiyorum ama ogrenmeye devam ediyorum! {base}"
        elif level == "middle":
            return f"[Ortaokul Uzmani]\nDurust olmak gerekirse: {base}"
        else:
            return f"[Akademik Uzman]\nBu soruyu bilgi tabanımda bulamadım. {base}"
