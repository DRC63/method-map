"""Generate P3MAI-branded architecture diagrams (PNG) for the Method Map docs."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(ASSETS, exist_ok=True)

NAVY = "#0B2545"; NAVYL = "#1B3F6E"; GOLD = "#C9A227"; GOLDD = "#A8841C"
GREEN = "#2E7D5B"; RED = "#C0392B"; PURPLE = "#8E5BE0"; GREY = "#5B6675"
BG = "#F6F7F9"; STEEL = "#3D5A80"


def box(ax, x, y, w, h, text, fill=NAVY, fg="white", fs=11, bold=True, edge=None, sub=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                linewidth=1.4, edgecolor=edge or fill, facecolor=fill, zorder=2))
    ax.text(x + w / 2, y + h / 2 + (0.12 if sub else 0), text, ha="center", va="center",
            color=fg, fontsize=fs, fontweight="bold" if bold else "normal", zorder=3)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.22, sub, ha="center", va="center",
                color=fg, fontsize=fs - 2.5, zorder=3)


def arrow(ax, x1, y1, x2, y2, color=GREY, text=None, style="-|>", lw=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=14,
                                 color=color, linewidth=lw, zorder=1))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.14, text, ha="center", va="bottom",
                color=color, fontsize=8.5, fontstyle="italic")


def fig(w=11, h=6.5):
    f, ax = plt.subplots(figsize=(w, h), dpi=150)
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis("off")
    f.patch.set_facecolor("white")
    return f, ax


def save(f, name):
    path = os.path.join(ASSETS, name)
    f.savefig(path, bbox_inches="tight", facecolor="white", pad_inches=0.15)
    plt.close(f)
    print("wrote", os.path.abspath(path))


# ---------- 1. Deployment architecture ----------
f, ax = fig(11, 6.8)
ax.text(6, 7.6, "Method Map — Deployment Architecture", ha="center", fontsize=15,
        fontweight="bold", color=NAVY)
box(ax, 0.4, 4.2, 2.2, 1.1, "User", fill="white", fg=NAVY, edge=NAVY, sub="web browser")
# Render service container
ax.add_patch(FancyBboxPatch((4.1, 2.2), 6.4, 3.6, boxstyle="round,pad=0.02,rounding_size=0.1",
             linewidth=1.6, edgecolor=NAVY, facecolor=BG, zorder=1))
ax.text(7.3, 5.5, "Render — Docker Web Service  (single origin)", ha="center",
        fontsize=11, fontweight="bold", color=NAVY)
box(ax, 4.5, 4.35, 2.7, 0.95, "uvicorn + FastAPI", fill=NAVY, sub="/api/* routes")
box(ax, 7.5, 4.35, 2.7, 0.95, "React SPA", fill=STEEL, sub="served from frontend/dist")
box(ax, 4.5, 2.55, 2.7, 0.95, "SQLite", fill=GREEN, sub="methodmap.db (auto-seeded)")
box(ax, 7.5, 2.55, 2.7, 0.95, "Seed JSON", fill=GOLDD, sub="prince2-7.json")
arrow(ax, 7.5, 3.02, 7.2, 3.02, color=NAVY, style="-|>")
ax.text(7.35, 3.5, "seeds DB\non boot", ha="center", va="bottom", color=GREY, fontsize=7.5, fontstyle="italic")
arrow(ax, 2.6, 4.75, 4.1, 4.75, color=NAVYL, text="HTTPS", style="-|>")
ax.text(3.35, 4.35, "prince2.p3mai.com", ha="center", fontsize=8, color=GOLDD, fontstyle="italic")
# github
box(ax, 4.1, 0.5, 6.4, 0.95, "GitHub  ·  DRC63/method-map", fill="white", fg=NAVY, edge=GREY)
arrow(ax, 7.3, 1.45, 7.3, 2.2, color=GOLD, text="push → autoDeploy (Docker build)", style="-|>")
ax.text(6, 0.05, "Render disk is ephemeral — DB re-seeds from the bundled JSON on every deploy/restart.",
        ha="center", fontsize=8.5, color=GREY, fontstyle="italic")
save(f, "arch_deployment.png")


# ---------- 2. Data model ----------
f, ax = fig(11, 6.2)
ax.text(6, 7.6, "Method Map — Data Model", ha="center", fontsize=15, fontweight="bold", color=NAVY)
box(ax, 0.5, 5.6, 3.0, 1.2, "Framework", fill=NAVY, sub="PRINCE2 7  (MSP-ready)")
box(ax, 4.5, 5.6, 3.0, 1.2, "Entity", fill=STEEL, sub="typed node")
box(ax, 8.5, 5.6, 3.0, 1.2, "Relationship", fill=GOLDD, sub="coded edge")
arrow(ax, 3.5, 6.2, 4.5, 6.2, color=GREY, text="1 → many", style="-|>")
arrow(ax, 7.5, 6.2, 8.5, 6.2, color=GREY, text="from / to", style="-|>")
# entity types
ax.text(6, 4.7, "entities.type", ha="center", fontsize=10, color=NAVY, fontweight="bold")
types = [("Process", NAVY), ("Activity", STEEL), ("Role", GOLD), ("Practice", GREEN),
         ("Approach", PURPLE), ("Product", RED)]
for i, (t, c) in enumerate(types):
    box(ax, 0.5 + i * 1.95, 3.7, 1.75, 0.8, t, fill=c, fs=10)
ax.text(6, 3.1, "Activities point at their Process via parent_id · Processes carry "
        "lifecycle metadata (level / phase / sequence)", ha="center", fontsize=8.5,
        color=GREY, fontstyle="italic")
# codes
box(ax, 1.0, 1.2, 4.6, 1.3, "Role / Practice / Approach codes", fill="white", fg=NAVY, edge=NAVY,
    sub="C = Responsible · P = Participates · N = Assists")
box(ax, 6.4, 1.2, 4.6, 1.3, "Product codes", fill="white", fg=RED, edge=RED,
    sub="I = Input · O = Output · U = Update · A = Authorise")
save(f, "arch_datamodel.png")


# ---------- 3. Graph link model ----------
f, ax = fig(11, 6.0)
ax.text(6, 7.6, "Method Map — Graph Link Model", ha="center", fontsize=15, fontweight="bold", color=NAVY)
box(ax, 4.7, 6.2, 2.6, 1.0, "Process", fill=NAVY)
box(ax, 4.7, 3.9, 2.6, 1.0, "Activity", fill=STEEL)
arrow(ax, 6.0, 6.2, 6.0, 4.9, color=NAVYL, text="contains", style="-|>")
targets = [("Role", GOLD, 0.6), ("Practice", GREEN, 3.2), ("Approach", PURPLE, 6.2), ("Product", RED, 8.8)]
for name, c, x in targets:
    box(ax, x, 1.7, 2.2, 0.9, name, fill=c, fs=10)
    arrow(ax, 6.0, 3.9, x + 1.1, 2.6, color=STEEL, style="-|>")
ax.text(1.9, 3.5, "direct links\n(carry the code)", ha="left", va="center", fontsize=8.5,
        color=STEEL, fontstyle="italic")
# derived (below the boxes so nothing overlaps)
arrow(ax, 1.7, 1.35, 4.3, 1.35, color=GREY, style="<|-|>", lw=1.3)
arrow(ax, 6.5, 1.35, 8.8, 1.35, color=GREY, style="<|-|>", lw=1.3)
ax.text(6, 0.85, "derived (co-occurrence) links", ha="center", fontsize=8.5, color=GREY, fontstyle="italic")
ax.text(6, 0.3, "Two non-activity entities are linked when they share an activity — "
        "drives the 'hide Activities' view and node-size weighting.",
        ha="center", fontsize=8, color=GREY, fontstyle="italic")
save(f, "arch_graph_model.png")

# ---------- 4. Explorer interface wireframe ----------
f, ax = fig(11, 6.2)
ax.text(6, 7.6, "Method Explorer — Interface", ha="center", fontsize=15, fontweight="bold", color=NAVY)
box(ax, 0.4, 0.6, 1.7, 6.4, "Sidebar", fill=NAVY, fs=10, sub="views")
box(ax, 2.3, 0.6, 2.7, 6.4, "Control panel", fill="white", fg=NAVY, edge=NAVY, fs=10,
    sub="search · layout\nlayers · legend\nexport")
box(ax, 5.2, 0.6, 4.0, 6.4, "Graph stage", fill=BG, fg=NAVY, edge=NAVYL, fs=11,
    sub="the network\n(pan · zoom · click)")
box(ax, 9.4, 0.6, 2.2, 6.4, "Detail panel", fill="white", fg=NAVY, edge=GOLD, fs=10,
    sub="selected node:\nrelationships,\nexports")
ax.text(7.2, 0.15, "Timeline layout adds a scrubber along the bottom of the graph stage.",
        ha="center", fontsize=8.5, color=GREY, fontstyle="italic")
save(f, "ui_explorer.png")

print("done")
