from pathlib import Path
import re

p = Path(__file__).resolve().parents[2] / "frontend" / "lib" / "format.ts"
t = p.read_text(encoding="utf-8")
t = t.replace("\u0627\u0644\u0645\u062e\u0627\u0637r", "\u0627\u0644\u0645\u062e\u0627\u0637\u0631")
t = re.sub(
    r"\nexport function mapRiskSourceType\(source: string \| null \| undefined\): string \{[\s\S]*?\n\}\n",
    "\n",
    t,
    count=1,
)
p.write_text(t, encoding="utf-8")
print("fixed format.ts")
