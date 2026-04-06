import os
src = r"C:\Marcus-Henri\CGS Contact Manager\CGS_FINAL_V7.html"
dst = r"C:\CGS\index.html"
out = r"C:\Marcus-Henri\CGS Contact Manager\CGS_FINAL_V9.html"
f=open(src,encoding="utf-8"); html=f.read(); f.close()
print(f"Loaded {len(html):,} bytes")
