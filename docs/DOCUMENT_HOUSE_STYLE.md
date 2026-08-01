# Document House Style — P3MAI Method Map

Applies to every Word and PowerPoint deliverable in this set. Modelled on the
*Microsoft Ecosystem – PMO Project* house style, re-branded to P3MAI (this is a
P3MAI product, not a Microsoft-stack solution).

## 1. Shared identity

| Element | Value |
|---|---|
| Primary colour | `#0B2545` (P3MAI navy) |
| Primary light | `#1B3F6E` |
| Accent | `#C9A227` (P3MAI gold) · dark `#A8841C` |
| Practice / success | `#2E7D5B` |
| Product / alert | `#C0392B` |
| Approach | `#8E5BE0` |
| Neutral text | `#1C2B3A` · muted `#5B6675` |
| Heading font | Segoe UI Semibold |
| Body font | Segoe UI, 11pt |
| Code font | Consolas, 10pt |

Entity-type colours are used consistently in diagrams and text: process = navy,
activity = steel blue `#3D5A80`, role = gold, practice = green, approach = purple,
product = red.

## 2. Word structure (`.docx`)

1. **Title page** — doc ID, title, version, date, author, classification.
2. **Document control** — version history table.
3. **Table of contents** — auto field, 3 levels.
4. Numbered body sections (`1.`, `1.1`, `1.1.1` — never deeper than three).
5. Appendices.

**Formatting**
- Footer: `P3MAI Method Map | version | Page N | CLASSIFICATION`.
- Tables: navy header row, white bold text, banded body rows.
- Figures captioned below (*Figure 1 — …*); tables captioned above.
- Callout boxes (single-cell shaded tables), at least one Tip and one Pitfall per
  major section where relevant:

| Type | Fill | Left border | Opens with |
|---|---|---|---|
| Pitfall | `#FDEEEE` | `#C0392B` | ⚠ |
| Key tip | `#FFF9E0` | `#A8841C` | ★ |
| Note / security | `#EAF2FB` | `#0B2545` | 🔒 |

## 3. PowerPoint structure (`.pptx`)

Widescreen 16:9. ~10 slides (title + ~9 content).

- Navy title slide with gold rule; content slides have a navy title and a short
  gold rule beneath.
- **One message per slide.** Max ~6 bullets, short.
- Diagrams get their own slide, sized to fill.
- Footer: classification bottom-left, `DOC-ID · slide` bottom-right.
- No clip art or stock photos — diagrams and tables only.

## 4. Classification

Default **OFFICIAL**. Raise to **OFFICIAL-SENSITIVE** when content includes
deployment specifics, secrets (admin password), or anything that eases attack.
The Operation Manual is OFFICIAL-SENSITIVE.

## 5. Versioning

`v0.x` draft, `v1.0` first issue, `v1.1` corrections, `v2.0` material redesign.
Version appears in the footer and the document-control table.
