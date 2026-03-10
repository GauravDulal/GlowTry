from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


StyleName = Literal["natural-glow", "soft-glam", "bold-lips", "bridal-touch", "party-look"]


@dataclass(frozen=True)
class MakeupStyle:
    name: StyleName
    label: str
    description: str
    # Colors are in BGR (OpenCV) for convenience.
    lip_bgr: tuple[int, int, int]
    lip_alpha: float
    blush_bgr: tuple[int, int, int]
    blush_alpha: float
    eye_bgr: tuple[int, int, int]
    eye_alpha: float
    liner_strength: float
    feather_px: int


STYLES: dict[StyleName, MakeupStyle] = {
    "natural-glow": MakeupStyle(
        name="natural-glow",
        label="Natural Glow",
        description="Soft pink lips, subtle blush, barely-there eyes.",
        lip_bgr=(150, 120, 210),
        lip_alpha=0.22,
        blush_bgr=(140, 160, 230),
        blush_alpha=0.16,
        eye_bgr=(120, 125, 170),
        eye_alpha=0.08,
        liner_strength=0.10,
        feather_px=25,
    ),
    "soft-glam": MakeupStyle(
        name="soft-glam",
        label="Soft Glam",
        description="Nude-rose lips, warm blush, soft eye tint.",
        lip_bgr=(120, 130, 190),
        lip_alpha=0.28,
        blush_bgr=(120, 170, 235),
        blush_alpha=0.20,
        eye_bgr=(90, 120, 160),
        eye_alpha=0.12,
        liner_strength=0.14,
        feather_px=28,
    ),
    "bold-lips": MakeupStyle(
        name="bold-lips",
        label="Bold Lips",
        description="Strong red lips, minimal blush.",
        lip_bgr=(40, 60, 220),
        lip_alpha=0.42,
        blush_bgr=(120, 160, 210),
        blush_alpha=0.08,
        eye_bgr=(95, 110, 140),
        eye_alpha=0.06,
        liner_strength=0.10,
        feather_px=24,
    ),
    "bridal-touch": MakeupStyle(
        name="bridal-touch",
        label="Bridal Touch",
        description="Rosy lips, soft blush, elegant eye enhancement.",
        lip_bgr=(90, 95, 205),
        lip_alpha=0.34,
        blush_bgr=(110, 160, 235),
        blush_alpha=0.20,
        eye_bgr=(80, 110, 155),
        eye_alpha=0.14,
        liner_strength=0.18,
        feather_px=30,
    ),
    "party-look": MakeupStyle(
        name="party-look",
        label="Party Look",
        description="Deeper lips, visible eyes, stronger blush.",
        lip_bgr=(70, 55, 200),
        lip_alpha=0.40,
        blush_bgr=(95, 150, 240),
        blush_alpha=0.26,
        eye_bgr=(70, 95, 170),
        eye_alpha=0.18,
        liner_strength=0.22,
        feather_px=32,
    ),
}


def list_styles():
    return [
        {"name": s.name, "label": s.label, "description": s.description}
        for s in STYLES.values()
    ]


def normalize_style_name(style: str) -> StyleName | None:
    s = (style or "").strip().lower()
    s = s.replace("_", "-")
    # Accept labels too (lightly).
    label_map = {v.label.lower().replace(" ", "-"): k for k, v in STYLES.items()}
    if s in STYLES:
        return s  # type: ignore[return-value]
    if s in label_map:
        return label_map[s]
    return None

