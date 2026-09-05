"""
extract_manual.py
-----------------
Extracts the Cryocon manual PDF into a clean Markdown file
optimised for AI agent consumption.

Usage:
    python extract_manual.py

Output:
    Cryocon_32_manual.md  (same directory as this script)
"""

import pathlib
import sys
import re

# -- 1. Check dependency -------------------------------------------------------
try:
    import pymupdf4llm
except ImportError:
    print("pymupdf4llm not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf4llm"])
    import pymupdf4llm

# -- 2. Paths ------------------------------------------------------------------
HERE = pathlib.Path(__file__).parent
PDF_PATH = HERE / "Cryocon_32_Temperature_Controller.pdf"
OUT_PATH = HERE / "Cryocon_32_manual.md"

if not PDF_PATH.exists():
    print(f"ERROR: PDF not found at {PDF_PATH}")
    sys.exit(1)

# -- 3. Extract ----------------------------------------------------------------
print(f"Extracting: {PDF_PATH.name}")
print("This may take a few seconds...")

md_text = pymupdf4llm.to_markdown(
    str(PDF_PATH),
    show_progress=True,
)

# -- 4. Light cleanup ----------------------------------------------------------
# Remove excessive blank lines (3+ -> 2)
md_text = re.sub(r'\n{3,}', '\n\n', md_text)

# -- 5. Write output -----------------------------------------------------------
OUT_PATH.write_text(md_text, encoding="utf-8")

size_kb = OUT_PATH.stat().st_size / 1024
print(f"\nDone!")
print(f"   Output : {OUT_PATH.name}")
print(f"   Size   : {size_kb:.1f} KB")
print(f"   Lines  : {md_text.count(chr(10)):,}")
print(f"\nThe manual is now AI-readable at:\n   {OUT_PATH}")
