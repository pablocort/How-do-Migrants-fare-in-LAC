# Skill: Presentation Aesthetics

## Purpose

Define the standard visual conventions for all HDMF PowerPoint presentations built by the `document_builder` agent. Apply these rules whenever creating or updating a `.pptx` file for the project.

---

## Slide layout

| Property | Value |
|----------|-------|
| Dimensions | 16:9 widescreen — 33.87 cm × 19.05 cm |
| Background | White (no decorative fills or gradients) |
| Layout base | Blank slide layout (index 6 in python-pptx) |
| Margins | Left/right: 1 cm; Top (after title): 2 cm; Bottom (before footer): 1 cm |

---

## Typography

| Element | Font | Size | Style | Color |
|---------|------|------|-------|-------|
| Slide title | Calibri | 18 pt | Bold | IDB Blue `#1F497D` |
| Title slide — main title | Calibri | 32 pt | Bold | IDB Blue `#1F497D` |
| Title slide — subtitle | Calibri | 20 pt | Normal | Dark grey `#595959` |
| Title slide — date/institution | Calibri | 12 pt | Normal | Light grey `#787878` |
| Body text | Calibri | 11 pt | Normal | Black |
| Footer | Calibri | 8 pt | Normal | Light grey `#787878` |
| Table header | Calibri | 10 pt | Bold | White `#FFFFFF` |
| Table body | Calibri | 10 pt | Normal | Black |

---

## Color palette

| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| IDB Blue | `#1F497D` | (31, 73, 125) | Titles, table headers |
| IDB Light Blue | `#DCE6F1` | (220, 230, 241) | Alternating table rows |
| Dark Grey | `#595959` | (89, 89, 89) | Subtitles |
| Light Grey | `#787878` | (120, 120, 120) | Footer, secondary text |

No other colors should be introduced. Charts use their own `Blues` palette from matplotlib.

---

## Image slides

### Placement rule

Images must be **horizontally and vertically centered** within the available content area — the space between the bottom of the title box and the top of the footer.

```
Available top    = 1.9 cm  (bottom edge of title text box)
Available bottom = slide_h - 0.8 cm  (top edge of footer)
Available height = slide_h - 0.8 - 1.9  =  16.35 cm  (for 19.05 cm slide)
Available width  = slide_w - 2.0 cm    =  31.87 cm  (with 1 cm side margins)
```

### Sizing rule

- Default image width: **22 cm**
- Preserve aspect ratio: `img_h = img_w * (px_h / px_w)`
- If `img_h > available_h`: scale down to fit height, recompute width
- If `img_w > available_w`: scale down to fit width, recompute height

### Centering formula (python-pptx)

```python
TITLE_BOTTOM_CM  = 1.9
FOOTER_TOP_CM    = SLIDE_H_CM - 0.8
available_h_cm   = FOOTER_TOP_CM - TITLE_BOTTOM_CM
available_w_cm   = SLIDE_W_CM - 2.0

# Scale to fit
if img_h_cm > available_h_cm:
    img_h_cm = available_h_cm
    img_w_cm = img_h_cm / ratio

if img_w_cm > available_w_cm:
    img_w_cm = available_w_cm
    img_h_cm = img_w_cm * ratio

# Center
img_left_cm = (SLIDE_W_CM - img_w_cm) / 2
img_top_cm  = TITLE_BOTTOM_CM + (available_h_cm - img_h_cm) / 2

slide.shapes.add_picture(path, Cm(img_left_cm), Cm(img_top_cm), Cm(img_w_cm), Cm(img_h_cm))
```

---

## Table slides

- Header row: IDB Blue background, white bold text
- Body rows: alternating white / IDB Light Blue
- All cells: borders on all sides (default pptx table border)
- Cell padding: default (no manual adjustment needed)
- Word wrap: enabled on all cells
- Alignment: LEFT for text, RIGHT for numbers
- Number format: percentages shown as `XX.X%`, counts with thousands separator

### Column width guidance

Design columns proportionally to content:
- ID / number columns: ~5% of table width
- Short label columns: ~15–20%
- Long description columns: ~40–55%
- Numeric value columns: ~12–15% each

---

## Footer

Every slide except the title slide must have a footer text box:

```python
# Position: bottom-right, 8pt grey
left   = Cm(1)
top    = Cm(SLIDE_H_CM - 0.8)
width  = Cm(SLIDE_W_CM - 2)
height = Cm(0.6)
alignment = PP_ALIGN.RIGHT
text  = 'HDMF — How do Migrants Fare in LAC | IDB'
font  = Calibri 8pt, color #787878
```

---

## Slide order convention (standard labor deck)

1. Title slide
2. Chart slides (one per indicator, labor group first)
3. Summary table slides (2 slides minimum for labor data)
4. Pipeline timing table
