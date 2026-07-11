from pathlib import Path
p = Path("experts_data.json")
data = p.read_bytes()
# On décode en cp1252 (Windows) et on réencode en utf-8
text = data.decode("cp1252")
p.write_text(text, encoding="utf-8")
print("Conversion vers UTF-8 réussie !")