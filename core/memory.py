import sqlite3
import numpy as np
import json
import os

class VectorMemory:
    """SQLite kullanarak vektör gömmelerini (embeddings) saklayan ve sorgulayan hafıza sınıfı."""
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                vector TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add_memory(self, text: str, vector: np.ndarray):
        """Metni ve vektör karşılığını veritabanına ekler."""
        vector_json = json.dumps(vector.tolist())
        self.cursor.execute('INSERT INTO embeddings (text, vector) VALUES (?, ?)', (text, vector_json))
        self.conn.commit()

    def cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """İki vektör arasındaki kosinüs benzerliğini hesaplar."""
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        return dot_product / (norm_v1 * norm_v2)

    def search_similar(self, query_vector: np.ndarray, top_k: int = 3) -> list[tuple[str, float]]:
        """Verilen vektöre en benzer k adet kaydı getirir."""
        self.cursor.execute('SELECT text, vector FROM embeddings')
        rows = self.cursor.fetchall()
        
        results = []
        for text, vector_str in rows:
            vec = np.array(json.loads(vector_str))
            sim = self.cosine_similarity(query_vector, vec)
            results.append((text, sim))
            
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def close(self):
        self.conn.close()
