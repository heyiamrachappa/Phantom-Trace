import docx

doc = docx.Document("/home/yi/Downloads/PhantomTrace.docx")

p_texts = [p.text.strip() for p in doc.paragraphs]

rw_idx = -1
meth_idx = -1
res_idx = -1
disc_idx = -1

for i, t in enumerate(p_texts):
    if t == "2.  Related Work":
        rw_idx = i
    elif t == "3.  Methodology":
        meth_idx = i
    elif t == "4.  Results":
        res_idx = i
    elif t == "5.  Discussion":
        disc_idx = i

print(f"Indices: RW={rw_idx}, Meth={meth_idx}, Results={res_idx}, Discussion={disc_idx}")

with open("/home/yi/My-Projects/Stealth-Network-Reconnaissance/revised_sections_ieee_access.md") as f:
    text = f.read()

import re
rw_match = re.search(r"# Section 2\. Related Work\n\n([\s\S]*?)\n\n# Section 4\. Results", text)
res_match = re.search(r"# Section 4\. Results\n\n([\s\S]*?)\n\n## Assumptions", text)

rw_paras = [p.strip() for p in rw_match.group(1).split("\n\n") if p.strip()]
res_content = res_match.group(1).strip()

# Clear old RW paragraphs
for i in range(rw_idx + 1, meth_idx):
    doc.paragraphs[i].text = ""

# Write new continuous prose in RW
doc.paragraphs[rw_idx + 1].text = rw_paras[0]
for p_text in rw_paras[1:]:
    p = doc.paragraphs[meth_idx].insert_paragraph_before(p_text)

# Clean up empty paragraphs in RW range
# In docx, empty paragraphs just have no text.
print("Successfully updated Related Work.")

# Save document
out_path = "/home/yi/My-Projects/Stealth-Network-Reconnaissance/PhantomTrace_Revised_IEEE_Access.docx"
doc.save(out_path)
print(f"Saved update to {out_path}")
