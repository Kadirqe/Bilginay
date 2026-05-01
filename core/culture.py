class TurkishCulture:
    """Türk kültürüne özgü bilgileri barındıran zenginleştirilmiş veri modülü."""
    def __init__(self):
        self.proverbs = [
            "Damlaya damlaya göl olur.",
            "Sakla samanı gelir zamanı.",
            "Ağaç yaşken eğilir.",
            "İşleyen demir ışıldar."
        ]
        
        self.idioms = [
            "Etekleri zil çalmak",
            "Göze girmek",
            "Küplere binmek",
            "Saman altından su yürütmek"
        ]
        
        self.cultural_contexts = {
            "selamlama": "Türk kültüründe selamlaşma samimi ve sıcaktır. Büyüklerin ellerinden öpülür.",
            "misafirperverlik": "Misafire çay ikramı şarttır ve aç gönderilmez.",
        }

    def get_random_proverb(self) -> str:
        import random
        return random.choice(self.proverbs)

    def get_context(self, topic: str) -> str:
        return self.cultural_contexts.get(topic, "Bu konuda özel bir kültürel bağlam bulunamadı.")
