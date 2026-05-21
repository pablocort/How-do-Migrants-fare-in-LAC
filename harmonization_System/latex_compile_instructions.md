# How to compile the LaTeX presentation to PDF

## Option 1 — LaTeX Workshop extension (recommended for iterative editing)

1. Install the **LaTeX Workshop** extension in VSCode (`James-Yu.latex-workshop`)
2. Open the `.tex` file (e.g., `out/latex/2026-04-27/venezuela_vs_native.tex`)
3. Save the file (`Ctrl+S`) — it auto-compiles on save by default
4. Or press `Ctrl+Alt+B` to build manually
5. The PDF opens in the built-in VSCode PDF viewer on the right

The extension handles multiple `pdflatex` passes automatically and shows errors in the Problems panel.

---

## Option 2 — Terminal inside VSCode (faster for one-off compiles)

Open the integrated terminal (`Ctrl+` `` ` ``) and run:

```bash
cd "C:/Users/PABLOCOR/OneDrive - Inter-American Development Bank Group/Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento/Datos/hdmf/How-do-Migrants-fare-in-LAC/out/latex/2026-04-27"
pdflatex -interaction=nonstopmode venezuela_vs_native.tex
```

Run it **twice** if you change cross-references or TOC (Beamer needs two passes for frame numbers). For this presentation one pass is enough.

---

## Important: working directory

Image paths in the `.tex` file are **relative** (e.g., `../../venezuela_vs_native/2026-04-28/...`), so `pdflatex` must always be run from the folder containing the `.tex` file — not from the project root. LaTeX Workshop handles this automatically; the terminal command above does too.

---

## Checking for overflow warnings

To see only relevant warnings after a terminal compile:

```bash
pdflatex -interaction=nonstopmode venezuela_vs_native.tex 2>&1 | grep -E "(Overfull|pages|Error)"
```

Minor `Overfull \vbox` warnings under ~10pt are acceptable in Beamer and do not cause visible clipping.
