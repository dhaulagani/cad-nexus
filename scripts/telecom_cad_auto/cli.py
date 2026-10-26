r"""
telecom_cad_auto.cli
Command Line Interface to execute automated CAD drawing generation from field survey folders.
Usage:
  python -m telecom_cad_auto.cli --input "O:\...\US1051671_Blue Diamond" --output "C:\...\Output"
"""

import os
import sys
import argparse
import time

# Ensure parent directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from telecom_cad_auto.parser import parse_survey_dataset
from telecom_cad_auto.generator import build_telecom_drawing_set


def main():
    parser = argparse.ArgumentParser(
        description="Automated 2D CAD Drawing Generator for Telecom Site Field Surveys."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to field survey folder containing sitedata.xlsx, equipments.xlsx, and drone captures."
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output directory where .dwg, .dxf, and final 7-sheet .pdf deliverables will be generated."
    )

    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    if not os.path.exists(input_path):
        print(f"[Error] Input survey folder does not exist: {input_path}")
        sys.exit(1)

    print("=" * 70)
    print("TELECOM SURVEY CAD AUTOMATION PIPELINE")
    print("=" * 70)
    print(f"Input Directory : {input_path}")
    print(f"Output Directory: {output_path}")
    print("-" * 70)

    start_time = time.time()

    # Step 1: Parse survey dataset
    print("[1/3] Ingesting survey dataset (Excel tables, coordinates, photos)...")
    survey_data = parse_survey_dataset(input_path)
    site_id = survey_data["site_info"].get("Site ID", "N/A")
    site_name = survey_data["site_info"].get("Site Name", "N/A")
    eq_count = len(survey_data["equipments"])
    img_count = len(survey_data["images"])

    print(f"      -> Identified Site ID  : {site_id}")
    print(f"      -> Identified Site Name: {site_name}")
    print(f"      -> Extracted Equipments: {eq_count} items")
    print(f"      -> Attached Site Images: {img_count} images ({', '.join(survey_data['images'].keys())})")

    # Step 2: Build Drawing Set
    print("\n[2/3] Generating 7-sheet CAD drawing set (.dxf, .dwg) and plotting...")
    deliverables = build_telecom_drawing_set(survey_data, output_path)

    # Step 3: Complete
    elapsed = time.time() - start_time
    print("\n[3/3] Automation Complete!")
    print("-" * 70)
    print("DELIVERABLES GENERATED:")
    for ext, path in deliverables.items():
        size_kb = os.path.getsize(path) / 1024 if os.path.exists(path) else 0
        print(f"  [{ext.upper()}]: {path} ({size_kb:,.1f} KB)")
    print("-" * 70)
    print(f"Total Processing Time: {elapsed:.2f} seconds")
    print("=" * 70)


if __name__ == "__main__":
    main()
