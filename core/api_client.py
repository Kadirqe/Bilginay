import requests
import pybreaker
import os
from dotenv import load_dotenv

load_dotenv()

# Devre Kesici: 3 hatadan sonra 60 saniye boyunca devreyi aç (istek atma)
circuit_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)

class APIClient:
    """Güvenli Yerel API istemcisi. Dış servisler yerine yerel (Ollama, LM Studio) LLM sunucularına bağlanır."""
    def __init__(self):
        # API anahtarı kullanmak yerine tamamen yerel (local) adresi alıyoruz.
        self.local_url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
        self.model_name = os.getenv("LOCAL_MODEL_NAME", "llama3")
        
    @circuit_breaker
    def fetch_local_llm(self, prompt: str) -> dict:
        """API Key gerektirmeyen yerel bir LLM'e (ör. Ollama) istek atar."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        try:
            # Localhost'a gittiği için API anahtarına (Authorization header'a) gerek yoktur.
            response = requests.post(self.local_url, json=payload, timeout=2)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Hata ekrana yazdırılmıyor, doğrudan üst katmana aktarılıyor ki simülasyon sessizce devreye girsin.
            raise
