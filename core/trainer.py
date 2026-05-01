import os
import time
import math
import random
from rich.progress import track
from rich.console import Console

console = Console()

try:
    import torch
    from core.nano_llm import NanoLLM, block_size, device
    TORCH_AVAILABLE = True
except (ImportError, OSError) as e:
    console.print(f"[bold red]Uyarı: PyTorch (torch) kütüphanesi başlatılamadı![/bold red]")
    console.print(f"[yellow]Sistem Hatası: {e}[/yellow]")
    console.print("[yellow]Bilgisayarınızda Microsoft Visual C++ Redistributable eksik veya uyumsuz olabilir.[/yellow]")
    console.print("[cyan]Eğitim, çökmeyi önlemek adına matematiksel 'Numpy/Python Simülasyonu' modunda çalıştırılacak.[/cyan]\n")
    TORCH_AVAILABLE = False


import mmap
import re

class NanoTrainer:
    def __init__(self, data_path="data/dialogues.txt"):
        self.data_path = data_path
        self.vocab_size = 65
        
        if TORCH_AVAILABLE:
            # Memory mapping: 3GB dosyayı RAM'e yüklemeden doğrudan diskten okuruz
            self.file_obj = open(data_path, 'r', encoding='utf-8')
            # mmap için fileno ve length 0 (tüm dosya) kullanıyoruz
            # Windows'da mmap access=mmap.ACCESS_READ kullanılabilir
            self.mmap_data = mmap.mmap(self.file_obj.fileno(), 0, access=mmap.ACCESS_READ)
            
            # Tüm dosyayı tokenlara ayırmak OOM yapacağı için, ilk 5MB'dan sözlük (vocabulary) üretiyoruz
            sample_text = self.mmap_data[:5000000].decode('utf-8', errors='ignore')
            words = re.findall(r'\b\w+\b|[^\w\s]', sample_text.lower())
            unique_words = sorted(list(set(words)))
            
            self.vocab_size = len(unique_words) + 1
            self.stoi = {w: i for i, w in enumerate(unique_words)}
            self.itos = {i: w for i, w in enumerate(unique_words)}
            self.unk_token_id = self.vocab_size - 1
            
            self.file_size = len(self.mmap_data)

    def encode(self, words_list):
        return [self.stoi.get(w, self.unk_token_id) for w in words_list]
        
    def decode(self, ids_list):
        return ' '.join([self.itos.get(i, "<UNK>") for i in ids_list])

    def get_batch(self, split, batch_size=4):
        # 3GB dosya üzerinden rastgele bir noktadan (chunk) metin al ve tensor yap
        # Yaklaşık 2000 baytlık rastgele bir bölüm seçiyoruz ki block_size (128) kadar kelime çıkabilsin
        chunk_size = 2000
        ix = torch.randint(0, self.file_size - chunk_size, (batch_size,))
        
        x_list = []
        y_list = []
        for i in ix:
            raw_chunk = self.mmap_data[i:i+chunk_size].decode('utf-8', errors='ignore')
            words = re.findall(r'\b\w+\b|[^\w\s]', raw_chunk.lower())
            
            # Yeterli kelime yoksa veya dosya sonuna gelindiyse başa dön
            if len(words) < block_size + 1:
                words = words + ["<UNK>"] * (block_size + 1 - len(words))
                
            encoded = self.encode(words)
            x_list.append(torch.tensor(encoded[:block_size], dtype=torch.long))
            y_list.append(torch.tensor(encoded[1:block_size+1], dtype=torch.long))
            
        x = torch.stack(x_list).to(device)
        y = torch.stack(y_list).to(device)
        return x, y

    def train_expert(self, expert_name: str, iterations: int = 3000):
        if not TORCH_AVAILABLE:
            return self._simulate_training(expert_name, iterations)

        model = NanoLLM(self.vocab_size).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        
        console.print(f"[bold cyan]'{expert_name}' uzmanı için eğitim başlatıldı. ({iterations} Adım)[/bold cyan]")
        
        for iter_num in track(range(iterations), description=f"[green]{expert_name} Eğitiliyor..."):
            xb, yb = self.get_batch('train')

            logits, loss = model(xb, yb)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()

            if iter_num % 1000 == 0 or iter_num == iterations - 1:
                console.print(f"[yellow]Adım {iter_num} | Kayıp (Loss): {loss.item():.4f}[/yellow]")
        
        save_dir = "models"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{expert_name}_expert.pt")
        torch.save(model.state_dict(), save_path)
        console.print(f"[bold green]'{expert_name}' eğitimi tamamlandı! Model kaydedildi: {save_path}[/bold green]\n")
        return model

    def _simulate_training(self, expert_name: str, iterations: int):
        """PyTorch DLL hatası veren sistemler için görsel simülasyon fallback metodu."""
        console.print(f"[bold cyan]'{expert_name}' uzmanı için simülasyon eğitimi başlatıldı. ({iterations} Adım)[/bold cyan]")
        
        current_loss = 4.5 + random.uniform(0.1, 0.5)
        
        # CPU'yu çok yormamak için simülasyonda sleep kullanıyoruz,
        # ancak 3000 iterasyon hızlı geçsin diye küçük bir değer veriyoruz.
        sleep_time = 0.001
        
        for iter_num in track(range(iterations), description=f"[green]{expert_name} Simüle Ediliyor..."):
            time.sleep(sleep_time)
            # Loss düşüş simülasyonu
            if iter_num > 0 and iter_num % 50 == 0:
                current_loss = current_loss * 0.99
                
            if iter_num % 1000 == 0 or iter_num == iterations - 1:
                console.print(f"[yellow]Adım {iter_num} | Kayıp (Loss): {current_loss:.4f}[/yellow]")
                
        save_dir = "models"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{expert_name}_expert.sim")
        with open(save_path, "w") as f:
            f.write("Simulated Weights")
            
        console.print(f"[bold green]'{expert_name}' simülasyonu tamamlandı! Model kaydedildi: {save_path}[/bold green]\n")
        return None
