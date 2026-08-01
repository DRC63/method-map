# P3MAI Method Map — Documentation Set

Formal documentation for the **P3MAI Method Map** (PRINCE2 7 interdependency +
lifecycle explorer). Organised in the same manner as the *Microsoft Ecosystem –
PMO Project*: a numbered document set, each Word document paired with a
PowerPoint summary, plus a house style and generated diagram assets.

## Documents

| ID | Document | Word | PowerPoint summary |
|----|----------|------|--------------------|
| DOC-01 | **Architecture & Design** — stack, data model, graph/layout algorithms, deployment, design decisions | [01_Architecture_and_Design.docx](01_Architecture_and_Design.docx) | [01_…_Summary.pptx](01_Architecture_and_Design_Summary.pptx) |
| DOC-02 | **User Manual** — using the Explorer (Matrix/Timeline), Lifecycle, detail panel, exports, codes | [02_User_Manual.docx](02_User_Manual.docx) | [02_…_Summary.pptx](02_User_Manual_Summary.pptx) |
| DOC-03 | **Operation Manual** — configuration, data management, deployment, DNS, monitoring, troubleshooting, runbooks | [03_Operation_Manual.docx](03_Operation_Manual.docx) | [03_…_Summary.pptx](03_Operation_Manual_Summary.pptx) |

All three are **v1.0, 1 August 2026**. DOC-03 is marked **OFFICIAL-SENSITIVE**
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
