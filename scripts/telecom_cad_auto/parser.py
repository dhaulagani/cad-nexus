"""
telecom_cad_auto.parser
Extracts survey metadata, equipment tables, and image fixtures from raw telecom field survey folders.
"""

import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional


def read_xlsx_rows(path: str) -> List[List[str]]:
    """Read rows from an xlsx file using standard library zipfile and XML parser."""
    if not os.path.exists(path):
        return []

    try:
        with zipfile.ZipFile(path) as z:
            strings: List[str] = []
            if "xl/sharedStrings.xml" in z.namelist():
                root = ET.fromstring(z.read("xl/sharedStrings.xml"))
                for si in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                    text = "".join(t.text for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t") if t.text)
                    strings.append(text)

            sheet_xml = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
            rows = []
            for row in sheet_xml.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
                r_vals: List[str] = []
                for c in row.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
                    v = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                    if v is not None and v.text:
                        if c.attrib.get("t") == "s":
                            idx = int(v.text)
                            r_vals.append(strings[idx].strip() if idx < len(strings) else "")
                        else:
                            r_vals.append(v.text.strip())
                    else:
                        t = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}is/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                        if t is not None and t.text:
                            r_vals.append(t.text.strip())
                        else:
                            r_vals.append("")
                # Filter trailing empty strings
                while r_vals and not r_vals[-1]:
                    r_vals.pop()
                if r_vals:
                    rows.append(r_vals)
            return rows
    except Exception as e:
        print(f"[Warning] Failed to parse xlsx {path}: {e}")
        return []


def parse_survey_dataset(survey_dir: str) -> Dict[str, Any]:
    """
    Scans a site survey folder and extracts:
    - site_info: dict with Site ID, Site Name, Address, Coordinates, Heights, Flight Date
    - equipments: list of equipment dictionaries
    - images: dict of found images (compound, elevation, map/location)
    """
    site_info: Dict[str, str] = {
        "Site ID": "",
        "Site Name": "",
        "Site Address": "",
        "Latitude": "",
        "Longitude": "",
        "Overall Height AGL (Ft)": "",
        "Structure Height + Appurtenances (Ft)": "",
        "Structure Height (Ft)": "",
        "Foundation Height (Ft)": "0.00'",
        "Ground Level (Ft)": "0.00'",
        "AMSL (Ground Finish)": "",
        "Drone flight date": "",
        "Revision": "A",
        "Revision Description": "Issue for review"
    }

    equipments: List[Dict[str, Any]] = []
    images: Dict[str, str] = {}

    sitedata_file: Optional[str] = None
    sitedata_file_addr: Optional[str] = None
    equipments_file: Optional[str] = None

    # Step 1: Scan files
    for root, dirs, files in os.walk(survey_dir):
        for f in files:
            low = f.lower()
            full_path = os.path.join(root, f)

            # Sitedata / Elevation Table matching
            if ("sitedata" in low or "elevation table" in low or "elevation_table" in low) and low.endswith(".xlsx"):
                if not sitedata_file or "final" in full_path.lower():
                    sitedata_file = full_path

            # Address matching
            elif "address" in low and low.endswith(".xlsx"):
                sitedata_file_addr = full_path

            # Equipments matching
            elif ("equipment" in low or "equipments" in low) and low.endswith(".xlsx"):
                if not equipments_file or "rev_a" in low or "final" in full_path.lower():
                    equipments_file = full_path

            # Images matching
            elif low.endswith((".jpg", ".jpeg", ".png")):
                if "compound" in low and "compound" not in images:
                    images["compound"] = full_path
                elif "elevation" in low and "elevation" not in images:
                    images["elevation"] = full_path
                elif "home" in low:
                    images["map"] = full_path
                elif "map" not in images and any(k in low for k in ["map_location", "location", "aerial", "gateway"]):
                    images["map"] = full_path

    # Step 2: Parse Site Data
    if sitedata_file:
        rows = read_xlsx_rows(sitedata_file)
        def clean_key(s: str) -> str:
            return re.sub(r"[^a-zA-Z0-9]", "", s).lower()

        target_map = {clean_key(k): k for k in site_info.keys()}

        for r in rows:
            if len(r) >= 2:
                raw_k = r[0].strip().rstrip(":")
                val = r[1].strip()
                ck = clean_key(raw_k)
                if ck in ["siteidandname", "siteidname", "siteidandnam", "siteid"]:
                    parts = re.split(r"[_\-]+|\s{2,}", val, maxsplit=1)
                    if len(parts) >= 2:
                        site_info["Site ID"] = parts[0].strip()
                        site_info["Site Name"] = parts[1].strip()
                    else:
                        site_info["Site ID"] = val
                elif ck in target_map:
                    site_info[target_map[ck]] = val
                else:
                    for target_ck, target_k in target_map.items():
                        if target_ck == ck:
                            site_info[target_k] = val
                            break

    # Parse Address File if available
    if sitedata_file_addr:
        addr_rows = read_xlsx_rows(sitedata_file_addr)
        if len(addr_rows) >= 2:
            headers = [clean_key(h) for h in addr_rows[0]]
            vals = addr_rows[1]
            hdr_dict = dict(zip(headers, vals))
            if "sitecellid" in hdr_dict and hdr_dict["sitecellid"]:
                site_info["Site ID"] = hdr_dict["sitecellid"].strip()
            if "sitename" in hdr_dict and hdr_dict["sitename"]:
                site_info["Site Name"] = hdr_dict["sitename"].strip()
            
            addr_parts = [hdr_dict.get(k, "").strip() for k in ["siteaddress", "city", "state", "zip"] if hdr_dict.get(k, "").strip()]
            if addr_parts:
                site_info["Site Address"] = ", ".join(addr_parts)
            if "latitude" in hdr_dict:
                site_info["Latitude"] = hdr_dict["latitude"].strip()
            if "longitude" in hdr_dict:
                site_info["Longitude"] = hdr_dict["longitude"].strip()

    # Fallback: Infer Site ID and Site Name from folder name if not yet found
    folder_name = os.path.basename(survey_dir.rstrip("\\/"))
    m = re.search(r"(US\d+)[_\s]+(.*)", folder_name)
    if m:
        if not site_info["Site ID"]:
            site_info["Site ID"] = m.group(1).strip()
        if not site_info["Site Name"]:
            site_info["Site Name"] = m.group(2).strip()

    if not site_info["Site Address"] and site_info["Site Name"]:
        site_info["Site Address"] = f"{site_info['Site Name']}"

    # Format numeric coordinates
    try:
        if site_info["Latitude"]:
            site_info["Latitude"] = f"{float(site_info['Latitude']):.6f}"
        if site_info["Longitude"]:
            site_info["Longitude"] = f"{float(site_info['Longitude']):.6f}"
    except ValueError:
        pass

    # Step 3: Parse Equipments
    if equipments_file:
        rows = read_xlsx_rows(equipments_file)
        
        detected_headers = None
        for r in rows:
            lower_r = [c.lower() for c in r]
            if "tenant" in lower_r and any("equipment" in c for c in lower_r):
                detected_headers = [c.strip() for c in r]
                break

        eq_patterns = re.compile(r"^(antenna|rru|combiner|mw|odu|gps|tma|junction|diplexer)", re.IGNORECASE)
        for r in rows:
            has_eq = any(eq_patterns.search(c) for c in r)
            if has_eq and len(r) >= 3:
                eq_dict: Dict[str, str] = {}
                if detected_headers:
                    for i, hdr in enumerate(detected_headers):
                        if hdr and i < len(r):
                            eq_dict[hdr] = r[i].strip()
                else:
                    for i, val in enumerate(r):
                        eq_dict[f"Col_{i}"] = val.strip()
                equipments.append(eq_dict)

    return {
        "survey_dir": survey_dir,
        "site_info": site_info,
        "equipments": equipments,
        "images": images
    }


if __name__ == "__main__":
    import sys
    test_dir = sys.argv[1] if len(sys.argv) > 1 else r"O:\Documents\Document Gani\Project\Uirtus\Works\US1051519 Eagle Creek"
    data = parse_survey_dataset(test_dir)
    print(json.dumps(data, indent=2))
