"""
fix_encoding.py — Reescribe reporte_investigacion.tex con UTF-8 limpio (sin BOM).
Ejecutar una sola vez desde la raiz del proyecto.
"""
import pathlib, re

TEX = pathlib.Path("Documentacion/reporte_investigacion.tex")

# Tabla de reparacion: secuencias mal codificadas -> caracter correcto
FIXES = [
    # doble-codificacion tipica (utf-8 leido como latin-1 y re-codificado)
    ("Ã\x83\xc2\xb3",  "ó"),  # ó
    ("Ã\x83\xc2\xa9",  "é"),  # é
    ("Ã\x83\xc2\xa1",  "á"),  # á
    ("Ã\x83\xc2\xad",  "í"),  # í
    ("Ã\x83\xc2\xba",  "ú"),  # ú
    ("Ã\x83\xc2\xb1",  "ñ"),  # ñ
    ("Ã\x83\xc2\x9a",  "Ú"),  # Ú
    ("Ã\x83\xc2\x93",  "Ó"),  # Ó
    ("Ã\x83\xc2\x89",  "É"),  # É
    ("Ã\x83\xc2\x81",  "Á"),  # Á
    ("Ã\x83\xc2\x8d",  "Í"),  # Í
    # secuencias simples (un solo nivel de error)
    ("Ã³",  "ó"),
    ("Ã©",  "é"),
    ("Ã¡",  "á"),
    ("Ã­",  "í"),
    ("Ãº",  "ú"),
    ("Ã±",  "ñ"),
    ("Ã"",  "Ó"),
    ("Ã‰",  "É"),
    ("Ã",   "Á"),
    ("Ã",   "Í"),
    ("\xc3\xb3", "ó"),
    ("\xc3\xa9", "é"),
    ("\xc3\xa1", "á"),
    ("\xc3\xad", "í"),
    ("\xc3\xba", "ú"),
    ("\xc3\xb1", "ñ"),
    ("\xc3\x93", "Ó"),
    ("\xc3\x89", "É"),
    ("\xc3\x81", "Á"),
    ("\xc3\x8d", "Í"),
    # guiones y apostrofes mal codificados
    ("\xe2\x80\x94", "---"),   # em dash
    ("\xe2\x80\x93", "--"),    # en dash
    ("\xe2\x80\x9c", "``"),    # comilla doble izq
    ("\xe2\x80\x9d", "''"),    # comilla doble der
    ("\xe2\x80\x99", "'"),     # apostrofe
]

# Leer raw bytes
raw = TEX.read_bytes()

# Quitar BOM si existe
if raw[:3] == b"\xef\xbb\xbf":
    raw = raw[3:]

# Decodificar en latin-1 para ver todos los bytes como caracteres
text = raw.decode("latin-1")

# Aplicar reparaciones
for bad, good in FIXES:
    text = text.replace(bad, good)

# Escribir en UTF-8 sin BOM
TEX.write_text(text, encoding="utf-8")
print(f"[OK] {TEX} reescrito ({TEX.stat().st_size} bytes, UTF-8 sin BOM)")

# Verificacion rapida
sample = TEX.read_text(encoding="utf-8")
idx = sample.find("Universidad")
print("Muestra portada:", repr(sample[idx:idx+80]))
