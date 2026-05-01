import os
import time
from rich.console import Console
from rich.progress import track

console = Console()

# Eğitim veri setinin oluşturulacağı yer
DATA_FILE = "data/dialogues.txt"

# Mantıksal Akıl Yürütme (Chain-of-Thought) Diyalog şablonları
templates = [
    (
        "Kullanıcı: Yerçekimi nedir?\nBilginay: <düşün>Yerçekimi konusunu basit bir şekilde ele almalıyım. Gezegenlerin kütlesinden dolayı birbirlerini nasıl çektiklerinden ve elmanın yere düşmesi örneğinden bahsedebilirim. Bu kavram Newton tarafından keşfedilmiştir.</düşün> Yerçekimi, kütlesi olan nesnelerin birbirini çekmesini sağlayan doğal bir kuvvettir. Örneğin, bir elmayı bıraktığınızda yere düşmesini sağlayan veya Ay'ı Dünya'nın etrafında tutan güç yerçekimidir.\n",
        "User: What is gravity?\nBilginay: <düşün>I should explain gravity simply. I can mention how planets attract each other due to mass and use the falling apple example. This was discovered by Newton.</düşün> Gravity is a natural force that causes objects with mass to attract each other. For example, it is the force that makes an apple fall to the ground or keeps the Moon orbiting the Earth.\n"
    ),
    (
        "Kullanıcı: Fotosentez nasıl çalışır?\nBilginay: <düşün>Fotosentez biyolojik bir süreçtir. Bitkiler güneş ışığını, suyu ve karbondioksiti alarak oksijen ve enerji üretirler. Bunu kullanıcının anlayacağı sırayla anlatmalıyım.</düşün> Fotosentez, bitkilerin güneş ışığını kullanarak kendi besinlerini üretme sürecidir. Bitkiler, havadan karbondioksit ve topraktan su alarak güneş enerjisi yardımıyla bunları şekere ve atmosfere saldıkları temiz oksijene dönüştürürler.\n",
        "User: How does photosynthesis work?\nBilginay: <düşün>Photosynthesis is a biological process. Plants take sunlight, water, and carbon dioxide to produce oxygen and energy. I must explain this sequentially.</düşün> Photosynthesis is the process by which plants use sunlight to produce their own food. Plants take carbon dioxide from the air and water from the soil, converting them into sugar and fresh oxygen using solar energy.\n"
    ),
    (
        "Kullanıcı: Python'da fonksiyon nasıl yazılır?\nBilginay: <düşün>Programlama dilinde fonksiyonlar 'def' anahtar kelimesi ile tanımlanır. Kullanıcıya net bir sözdizimi (syntax) kuralı göstermem gerekiyor.</düşün> Python'da bir fonksiyon yazmak için `def` anahtar kelimesini kullanırsınız. Örneğin: `def merhaba():` yazıp altına çalıştırmak istediğiniz kodları eklersiniz.\n",
        "User: How to write a function in Python?\nBilginay: <düşün>In programming, functions are defined with the 'def' keyword. I need to show the user a clear syntax rule.</düşün> To write a function in Python, you use the `def` keyword. For example: `def hello():` and then add the code you want to run below it.\n"
    )
]

def generate_massive_dataset(target_gb=3.0):
    os.makedirs("data", exist_ok=True)
    target_bytes = target_gb * 1024 * 1024 * 1024
    
    console.print(f"[bold cyan]Devasa Mantıksal (CoT) Veri Seti Üretiliyor... Hedef: {target_gb} GB[/bold cyan]")
    
    # Chunk (Yığın) mantığı: RAM'i yormadan saniyede yüzlerce MB yazmak için büyük metin blokları oluştur.
    chunk_str = ""
    for _ in range(5000): # 1 bloğun büyüklüğünü artırıyoruz
        for tr, en in templates:
            chunk_str += tr + en
            
    chunk_bytes = chunk_str.encode('utf-8')
    bytes_written = 0
    start_time = time.time()
    
    with open(DATA_FILE, "wb") as f:
        # İlerleme çubuğu için tahmini chunk sayısını hesaplayalım
        total_chunks = int(target_bytes / len(chunk_bytes)) + 1
        
        for _ in track(range(total_chunks), description="[yellow]3GB Veri diske yazılıyor...[/yellow]"):
            f.write(chunk_bytes)
            bytes_written += len(chunk_bytes)
            if bytes_written >= target_bytes:
                break
                
    elapsed = time.time() - start_time
    file_size_gb = bytes_written / (1024**3)
    
    console.print(f"[bold green]Başarılı! {file_size_gb:.2f} GB veri seti {elapsed:.1f} saniyede oluşturuldu.[/bold green]")
    console.print(f"[bold green]Dosya: {DATA_FILE}[/bold green]")

if __name__ == "__main__":
    generate_massive_dataset()
