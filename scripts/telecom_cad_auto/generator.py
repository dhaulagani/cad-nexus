"""
telecom_cad_auto.generator
Generates telecommunication CAD packages (.dxf, .dwg, .pdf)
from parsed survey data using ezdxf and AutoCAD accoreconsole.
"""

import os
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
import ezdxf
import fitz  # PyMuPDF
from PIL import Image


ACCORE_EXE = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"
MODULE_DIR = os.path.dirname(__file__)
DEFAULT_TEMPLATE_DXF = os.path.join(MODULE_DIR, "template_site.dxf")
DEFAULT_TEMPLATE_SITEDATA = os.path.join(MODULE_DIR, "template_sitedata.xlsx")
DEFAULT_TEMPLATE_EQUIPMENTS = os.path.join(MODULE_DIR, "template_equipments.xlsx")

LAYOUT_ORDER = [
    "SITE ID&IMAGE",
    "LOCATION",
    "COMPOUND_1",
    "COMPOUND_2",
    "TOWER ELEVATION",
    "EQUIPMENT",
    "LINE DIAGRAM"
]


def create_sitedata_file(template_xlsx: str, output_xlsx: str, site_info: Dict[str, str]) -> str:
    """
    Creates site-specific sitedata.xlsx from template by updating shared strings and worksheet values.
    """
    with zipfile.ZipFile(template_xlsx, 'r') as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    # String replacements in sharedStrings.xml
    sst_xml = files['xl/sharedStrings.xml'].decode('utf-8')
    
    agl_val = site_info.get('Overall Height AGL (Ft)', "65.13'")
    appurt_val = site_info.get('Structure Height + Appurtenances (Ft)', "64.22'")
    gl_val = site_info.get('Ground Level (Ft)', "-0.91'")
    flight_date_val = site_info.get('Drone flight date', '29/07/2026')
    site_id_val = site_info.get('Site ID', 'US1051600')
    site_name_val = site_info.get('Site Name', 'Site')
    site_addr_val = site_info.get('Site Address', site_name_val)

    rep_map = {
        'US1051519': site_id_val,
        'Eagle Creek': site_name_val,
        '4760 Martin Road, Platora, Nevada, 89825': site_addr_val,
        ' 07/27/2026': f" {flight_date_val}",
        " 63.21'": f" {agl_val}",
        " 63.20'": f" {appurt_val}",
        "    -0.01'": f"    {gl_val}",
        "5552.56'": site_info.get('AMSL (Ground Finish)', "6959.43'"),
    }
    
    for old_val, new_val in rep_map.items():
        sst_xml = sst_xml.replace(old_val, new_val)
    files['xl/sharedStrings.xml'] = sst_xml.encode('utf-8')

    # Update sheet1 numeric values (lat/long)
    sheet_xml = files['xl/worksheets/sheet1.xml'].decode('utf-8')
    lat = site_info.get('Latitude', '34.343600') or '34.343600'
    long_val = site_info.get('Longitude', '-108.497500') or '-108.497500'
    sheet_xml = sheet_xml.replace('41.632137999999998', lat)
    sheet_xml = sheet_xml.replace('-117.741979', long_val)
    files['xl/worksheets/sheet1.xml'] = sheet_xml.encode('utf-8')

    with zipfile.ZipFile(output_xlsx, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)

    print(f"[Generator] Created local sitedata: {output_xlsx}")
    return output_xlsx


def prepare_dxf_package(
    template_dxf: str,
    output_dxf: str,
    site_info: Dict[str, str],
    sitedata_path: str
) -> str:
    """
    Performs global replacement of Eagle Creek data links and text,
    and removes old hardcoded OLE photos from modelspace.
    """
    with open(template_dxf, 'r', encoding='latin-1') as f:
        content = f.read()

    site_id = site_info.get("Site ID", "US1051600")
    site_name = site_info.get("Site Name", "Quemado")
    address = site_info.get("Site Address", f"{site_name}, Catron County, NM")
    flight_date = site_info.get("Drone flight date", "29/07/2026")
    agl = site_info.get("Overall Height AGL (Ft)", "65.13'")
    appurt = site_info.get("Structure Height + Appurtenances (Ft)", "64.22'")
    str_h = site_info.get("Structure Height (Ft)", "60.00'")
    gl = site_info.get("Ground Level (Ft)", "-0.91'")
    amsl = site_info.get("AMSL (Ground Finish)", "6959.43'")
    lat = site_info.get("Latitude", "34.343600") or "34.343600"
    lon = site_info.get("Longitude", "-108.497500") or "-108.497500"

    replacements = [
        (r"O:\Documents\Document Gani\Project\Uirtus\Works\US1051519 Eagle Creek\Designer Data\CAD File\sitedata.xlsx", sitedata_path),
        ("US1051519", site_id),
        ("Eagle Creek", site_name),
        ("4760 Martin Road, Platora, Nevada, 89825", address),
        ("4760 Martin Road, Platora,\nNevada, 89825", address),
        ("4760 Martin Road, Platora,\\PNevada, 89825", address),
        ("63.21'", agl),
        ("63.20'", appurt),
        ("5552.56'", amsl),
        ("-0.01'", gl),
        ("07/27/2026", flight_date),
        ("41.632138", lat),
        ("-117.741979", lon),
    ]

    for src, dst in replacements:
        content = content.replace(src, dst)

    with open(output_dxf, 'w', encoding='latin-1') as f:
        f.write(content)

    # Remove old OLE photos
    doc = ezdxf.readfile(output_dxf)
    msp = doc.modelspace()
    for e in list(msp.query('OLE2FRAME')):
        if e.dxf.handle.upper() in ['DF994', 'DF995']:
            msp.delete_entity(e)
    doc.saveas(output_dxf)

    print(f"[Generator] Saved cleaned DXF to: {output_dxf}")
    return output_dxf


def generate_page1_deliverable(survey_data: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Dedicated generator for Page 1 (Sheet 1: SITE ID&IMAGE):
    1. Creates local sitedata.xlsx.
    2. Rewires template DXF datalinks and deletes old OLE photos.
    3. Attaches site elevation and drone aerial photos at precise WCS bounds.
    4. Plots Sheet 1 to high-resolution A3 PDF and renders verification PNG.
    """
    os.makedirs(output_dir, exist_ok=True)
    site_info = survey_data.get("site_info", {})
    images = survey_data.get("images", {})

    site_id = site_info.get("Site ID", "US1051600").replace(" ", "")
    site_name = site_info.get("Site Name", "Quemado").replace(" ", "_")
    base_name = f"{site_id}_{site_name}_Rev_A"

    out_dxf = os.path.join(output_dir, f"{base_name}_Page1.dxf")
    dwg_path = os.path.join(output_dir, f"{base_name}_Page1.dwg")
    pdf_path = os.path.join(output_dir, f"{base_name}_Page1.pdf")
    png_path = os.path.join(output_dir, f"{base_name}_Page1.png")
    scr_path = os.path.join(output_dir, "plot_page1.scr")
    local_sitedata = os.path.join(output_dir, "sitedata.xlsx")

    # 1. Create local sitedata.xlsx
    create_sitedata_file(DEFAULT_TEMPLATE_SITEDATA, local_sitedata, site_info)

    # 2. Prepare DXF
    prepare_dxf_package(DEFAULT_TEMPLATE_DXF, out_dxf, site_info, local_sitedata)

    # 3. Copy images to non-spaced local paths for AutoCAD script compatibility
    elev_src = images.get("elevation", "")
    home_src = images.get("map", "")

    elev_local = os.path.join(output_dir, "elev.jpg")
    home_local = os.path.join(output_dir, "home.jpg")

    if elev_src and os.path.exists(elev_src):
        shutil.copyfile(elev_src, elev_local)
    if home_src and os.path.exists(home_src):
        shutil.copyfile(home_src, home_local)

    # 4. Generate AutoCAD plot script
    # Left VP: (24.54, 2564.49, 0), scale 408.65
    # Right VP: (470.51, 2379.30, 0), scale 648.82
    scr_lines = [
        '(setvar "EXPERT" 2)',
        '(setvar "CTAB" "Model")',
        '-IMAGE', 'A', elev_local, '24.54,2564.49,0', '408.65', '0',
        '-IMAGE', 'A', home_local, '470.51,2379.30,0', '648.82', '0',
        '(setvar "CTAB" "SITE ID&IMAGE")',
        'DATALINKUPDATE', 'U', 'K',
        '-PLOT', 'Y', '', 'AutoCAD PDF (General Documentation).pc3',
        'ISO full bleed A3 (420.00 x 297.00 MM)',
        'I', 'L', 'N', 'Layout', 'Fit', '0.0,0.0', 'Y', 'acad.ctb', 'Y', 'N', 'N', 'N',
        pdf_path, 'N', 'Y',
        f'SAVEAS\n2018\n"{dwg_path}"',
        'QUIT Y\n'
    ]

    with open(scr_path, "w", encoding="ascii") as f:
        f.write('\n'.join(scr_lines))

    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    # 5. Run AutoCAD accoreconsole
    print(f"[Page1 Generator] Running AutoCAD headless engine for Page 1...")
    cmd = [ACCORE_EXE, "/i", out_dxf, "/s", scr_path]
    res = subprocess.run(cmd, capture_output=True, timeout=120)

    if not os.path.exists(pdf_path):
        raise RuntimeError(f"Failed to generate Page 1 PDF: {res.stdout.decode('latin-1', errors='ignore')}")

    # 6. Render high-res PNG for validation
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    pix.save(png_path)
    text_content = page.get_text()
    image_count = len(page.get_images())
    doc.close()

    print(f"[Page1 Generator] Page 1 generated successfully: {pdf_path}")
    print(f"[Page1 Generator] Images detected in PDF: {image_count}")

    return {
        "dxf": out_dxf,
        "dwg": dwg_path,
        "pdf": pdf_path,
        "png": png_path,
        "images_count": image_count,
        "text": text_content
    }


def build_telecom_drawing_set(survey_data: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Builds the telecommunication drawing deliverables.
    Currently delegates to Page 1 generator for single-page milestone validation.
    """
    return generate_page1_deliverable(survey_data, output_dir)

