with open(r"c:\Projekty\Blyskawica_V8\scratch\faza_anywhere.txt", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.finditer(r"FAZA 4", content, re.IGNORECASE)
with open(r"c:\Projekty\Blyskawica_V8\scratch\extract_faza4_output.txt", "w", encoding="utf-8") as out:
    for m in matches:
        start = max(0, m.start() - 200)
        end = min(len(content), m.end() + 1500)
        out.write(f"Match found at position {m.start()}:\n")
        out.write(content[start:end])
        out.write("\n" + "-" * 80 + "\n\n")

print("Done extracting matches to scratch/extract_faza4_output.txt")
