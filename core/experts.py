"""
experts.py — Bilginay Uzman Modülleri
─────────────────────────────────────
Her uzman artık:
  1. Önce yerel LLM'e (Ollama) bağlanmayı dener.
  2. LLM yoksa → ReasoningEngine üzerinden GERÇEK mantık kurar.
  3. Bilinmeyen sorularda dürüstçe "bilmiyorum" der.
"""
from core.api_client import APIClient
from core.reasoning_engine import QueryAnalyzer, ReasoningChain, ResponseSynth


# Paylaşılan tek instance (performans)
_analyzer = QueryAnalyzer()
_chain    = ReasoningChain()
_synth    = ResponseSynth()


class _BaseExpert:
    def __init__(self, level: str, system_prompt: str):
        self.level         = level          # "primary" | "middle" | "high"
        self.system_prompt = system_prompt
        self.api_client    = APIClient()

    def process(self, query: str) -> str:
        """Önce yerel LLM dener, yoksa reasoning engine devreye girer."""
        full_prompt = f"Sistem: {self.system_prompt}\nKullanıcı: {query}\nUzman Yanıtı:"
        try:
            resp = self.api_client.fetch_local_llm(full_prompt)
            return resp.get("response", "").strip() or self._reason(query)
        except Exception:
            return self._reason(query)

    def _reason(self, query: str) -> str:
        """Chain-of-Thought mantık motoru."""
        analysis  = _analyzer.analyze(query)
        reasoning = _chain.reason(analysis)
        return _synth.synthesize(reasoning, self.level, query)


class PrimaryExpert(_BaseExpert):
    def __init__(self):
        super().__init__(
            level="primary",
            system_prompt=(
                "Sen bir ilkokul öğretmenisin. "
                "Kavramları 7-10 yaş arası bir çocuğun anlayacağı şekilde, "
                "çok basit, eğlenceli ve günlük hayattan örneklerle anlatırsın."
            )
        )


class MiddleSchoolExpert(_BaseExpert):
    def __init__(self):
        super().__init__(
            level="middle",
            system_prompt=(
                "Sen bir ortaokul öğretmenisin. "
                "Konuları 11-14 yaş arası çocuklara, bilimsel temellere dayandırarak "
                "ama çok sıkmadan, mantıklı nedensellik kurarak anlatırsın."
            )
        )


class HighSchoolExpert(_BaseExpert):
    def __init__(self):
        super().__init__(
            level="high",
            system_prompt=(
                "Sen bir lise ve üniversite profesörüsün. "
                "Konuları derinlemesine, akademik terimlerle, formüller ve "
                "kompleks felsefi/bilimsel altyapılarla analiz edersin."
            )
        )


class MasterExpert:
    """
    MoE (Mixture of Experts) Birleştirici.
    Üç uzmanı çalıştırır, analizlerini sentezler ve
    tutarlı, çok boyutlu bir cevap üretir.
    """
    def __init__(self):
        self.primary = PrimaryExpert()
        self.middle  = MiddleSchoolExpert()
        self.high    = HighSchoolExpert()

    def process_as_one(self, query: str) -> str:
        # Ortak analiz — aynı soruyu 3x parse etmemek için bir kez çalıştır
        analysis  = _analyzer.analyze(query)
        reasoning = _chain.reason(analysis)

        p = _synth.synthesize(reasoning, "primary", query)
        m = _synth.synthesize(reasoning, "middle",  query)
        h = _synth.synthesize(reasoning, "high",    query)

        # Ollama varsa bireysel uzman yanıtlarını tercih et
        p_live = self.primary.process(query)
        m_live = self.middle.process(query)
        h_live = self.high.process(query)

        # Eğer Ollama cevabı boş değilse onu al, yoksa reasoning sonucunu kullan
        p_final = p_live if len(p_live) > len(p) else p
        m_final = m_live if len(m_live) > len(m) else m
        h_final = h_live if len(h_live) > len(h) else h

        header = "🎓 **Bilginay — Master Uzman Sentezi**"
        topic_str = f"📚 Konu: `{reasoning.get('topic', 'Genel')}`" if reasoning.get("topic") else ""

        return "\n".join(filter(None, [
            header,
            topic_str,
            "",
            "🌱 **Temel Düzey (İlkokul):**",
            p_final,
            "",
            "🔍 **Gelişim Düzeyi (Ortaokul):**",
            m_final,
            "",
            "🔬 **Akademik Düzey (Lise/Üniversite):**",
            h_final,
        ]))

