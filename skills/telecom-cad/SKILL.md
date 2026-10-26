---
name: telecom-cad
description: Automated parametric generation of telecom site drawings (Page-01 Site Layout, Page-04 Compound Plan, Page-07 Tower Elevation). Produces production DWG 2018, vector PDF, and high-resolution hairline PNG with strict decimal feet dimensions, non-touching fence post 'X' symbols, equipment foundation pads, and automated AutoCAD Core Console batch plotting.
license: MIT
---

# Telecom CAD Automation

Provenance: maintained in [dhaulagani/text-to-cad](https://github.com/dhaulagani/text-to-cad).

`telecom-cad` provides automated, survey-accurate procedural generation of telecom infrastructure drawings:

- **Page-01 (Site Location & Key Map)**: Maps, satellite orthophotos, coordinate frames, and project notes.
- **Page-04 (Compound Plan)**: Compound perimeter fences with non-touching 'X' post symbols (gap 1.25"), double-swing and pedestrian gates with swing arcs, equipment foundation pads (shelters, generators, fuel tanks, transformer diamond pads, ACUs, ice bridges), bubble callouts (A through Z), and modular equipment & foundation legend tables.
- **Page-07 (Tower Elevation & Monopole)**: Precise linear taper pole diameter calculations, equipment attachment racks, coax/feedline routing, benchmark elevation levels, and antenna tables.

## Plotting & Lineweight Invariants

All automated exports follow strict AutoCAD drafting standards:
1. **Plot Style**: `acad.ctb`
2. **Lineweights**: `Plot with lineweights = NO` (enforcing crisp hairlines, zero thick/bloated ink).
3. **Dimensions**: Strict decimal feet (`137.33'`, `73.68'`) with architectural ticks.
4. **Deliverables**: Triple export (`.dwg`, `.pdf`, 300 DPI `.png` with auto-crop).

## Scripts

- `scripts/build_quemado_page04.py`: Compound Plan Page-04 for US1051600 Quemado.
- `scripts/build_quemado_page07.py`: Monopole Elevation Page-07 for US1051600 Quemado.
- `scripts/build_us1051510_page07.py`: Monopole Elevation Page-07 for US1051510 Denio.
- `scripts/build_us1051627_page07.py`: Monopole Elevation Page-07 for US1051627 Top Gun.
