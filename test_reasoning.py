import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from core.reasoning_engine import QueryAnalyzer, ReasoningChain, ResponseSynth

analyzer = QueryAnalyzer()
chain    = ReasoningChain()
synth    = ResponseSynth()

tests = [
    ("nasılsın",                  "hal_hatir bekl."),
    ("yerçekimi nedir",           "bilim - fizik"),
    ("fotosentez nasıl çalışır",  "bilim - biyoloji"),
    ("python nedir",              "bilgisayar"),
    ("yapay zeka nedir",          "AI"),
    ("bilinç nedir",              "felsefe"),
    ("merhaba",                   "selamlama"),
    ("uçan domuzlar nerede?",     "bilgi yok"),
]

for query, hint in tests:
    print("=" * 65)
    print(f"SORU   : {query}  ({hint})")
    a = analyzer.analyze(query)
    r = chain.reason(a)
    topic  = r.get("topic", "?")
    conf   = r.get("confidence", 0.0)
    print(f"Konu   : {topic}  |  Guven: {conf:.2f}  |  Dil: {a.lang}  |  Niyet: {a.intent}")
    print("--- Ilkokul ---")
    print(synth.synthesize(r, "primary", query))
    print("--- Ortaokul ---")
    print(synth.synthesize(r, "middle", query))
    print("--- Akademik ---")
    print(synth.synthesize(r, "high", query))
    print()
