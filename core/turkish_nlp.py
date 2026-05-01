from snowballstemmer import TurkishStemmer

class TurkishNLP:
    def __init__(self):
        self.stemmer = TurkishStemmer()

    def get_stems(self, text: str) -> list[str]:
        """Metindeki kelimelerin köklerini bulur."""
        words = text.lower().split()
        return [self.stemmer.stemWord(word) for word in words]

    def analyze_sentiment(self, text: str) -> str:
        """Basit kural tabanlı duygu analizi."""
        text_lower = text.lower()
        positive_words = ["güzel", "iyi", "harika", "muhteşem", "başarılı", "teşekkürler"]
        negative_words = ["kötü", "çirkin", "berbat", "başarısız", "üzücü", "hata"]

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            return "Pozitif"
        elif neg_count > pos_count:
            return "Negatif"
        return "Nötr"

    def detect_intent(self, text: str) -> str:
        """Basit kural tabanlı niyet analizi."""
        text_lower = text.lower()
        if any(word in text_lower for word in ["merhaba", "selam", "günaydın"]):
            return "selamlama"
        elif any(word in text_lower for word in ["nasıl", "nedir", "kimdir", "ne"]):
            return "soru"
        elif any(word in text_lower for word in ["eğit", "öğren", "model"]):
            return "egitim_komutu"
        return "bilinmeyen"
