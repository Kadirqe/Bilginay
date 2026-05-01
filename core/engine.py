from abc import ABC, abstractmethod
from core.experts import MasterExpert

class EngineStrategy(ABC):
    @abstractmethod
    def execute(self, data: any) -> str:
        pass

class ChatStrategy(EngineStrategy):
    def __init__(self):
        self.master_expert = MasterExpert()

    def execute(self, data: any) -> str:
        return self.master_expert.process_as_one(data)

class TrainStrategy(EngineStrategy):
    def execute(self, data: any) -> str:
        return f"[Eğitim Modu] {data} dosyası üzerinden eğitim başlatılıyor..."

class InferenceStrategy(EngineStrategy):
    def execute(self, data: any) -> str:
        return f"[Üretim Modu] Modele soruldu: {data}\nModel Yanıtı: (Nano-LLM üretimi burada olacak)"

class AIEngine:
    """Strategy Pattern kullanarak çalışan ana motor."""
    def __init__(self, strategy: EngineStrategy = None):
        if strategy is None:
            self.strategy = ChatStrategy()
        else:
            self.strategy = strategy

    def set_strategy(self, strategy: EngineStrategy):
        self.strategy = strategy

    def process(self, data: any) -> str:
        return self.strategy.execute(data)
