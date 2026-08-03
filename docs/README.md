# P3MAI Method Map — Documentation Set

Formal documentation for the **P3MAI Method Map** — a multi-framework
interdependency + lifecycle explorer now hosting **PRINCE2 7**, **MSP 5th
edition**, **SAFe 6.0 Essential** and **PMBOK 6th edition**, each as its own
deployment behind the shared front door `apps.p3mai.com`. Organised in the same manner as the
*Microsoft Ecosystem – PMO Project*: a numbered document set, each Word document
paired with a PowerPoint summary, plus a house style and generated diagram assets.

## Documents

| ID | Document | Word | PowerPoint summary |
|----|----------|------|--------------------|
| DOC-01 | **Architecture & Design** — stack, data model, graph/layout algorithms, deployment, design decisions | [01_Architecture_and_Design.docx](01_Architecture_and_Design.docx) | [01_…_Summary.pptx](01_Architecture_and_Design_Summary.pptx) |
| DOC-02 | **User Manual** — using the Explorer (Matrix/Timeline), Lifecycle, detail panel, exports, codes | [02_User_Manual.docx](02_User_Manual.docx) | [02_…_Summary.pptx](02_User_Manual_Summary.pptx) |
| DOC-03 | **Operation Manual** — configuration, data management, per-framework deployment, the front door, monitoring, troubleshooting, runbooks | [03_Operation_Manual.docx](03_Operation_Manual.docx) | [03_…_Summary.pptx](03_Operation_Manual_Summary.pptx) |

DOC-01 & DOC-02 are **v1.3**, DOC-03 is **v1.2** (2 August 2026) — multi-framework
(MSP, SAFe and PMBOK 6th ed added as the second, third and fourth live frameworks;
v1.3 adds the Timeline Reset control and the `label_below` Matrix option). DOC-03 is marked **OFFICIAL-SENSITIVE**
(it references deployment specifics and the admin secret); the others are **OFFICIAL**.

## Folder layout

```
docs/
  README.md                     this index
  DOCUMENT_HOUSE_STYLE.md        brand + formatting rules
  01_Architecture_and_Design.docx / _Summary.pptx
  02_User_Manual.docx            / _Summary.pptx
  03_Operation_Manual.docx       / _Summary.pptx
  assets/                        generated diagrams (PNG)
  _source/                       the generator scripts (the reproducible source)
```

## Regenerating

The Office files are generated from Python so they can be rebuilt after any change.
From `docs/_source/` (with `python-docx`, `python-pptx`, `matplotlib`, `Pillow`):

```bash
python gen_diagrams.py   # (re)build the PNG diagrams in ../assets
python gen_arch.py       # 01_Architecture_and_Design.docx
python gen_user.py       # 02_User_Manual.docx
python gen_ops.py        # 03_Operation_Manual.docx
python gen_decks.py      # the three *_Summary.pptx
```

`docstyle.py` / `deckstyle.py` hold the shared P3MAI-branded helpers.

> Note: the Word documents contain an auto Table of Contents field. When first
> opened, click the contents list and press **F9** to populate it.
