"""
VisionSpec QC - Dataset Preprocessing Script
Cleans, resizes, and organizes raw PCB images before training.
"""

import os
import shutil
from pathlib import Path
from PIL import Image
from backend.app.config.settings import settings


def clean_dataset(dataset_dir: str = None):
    """
    Walk through the dataset directory and:
    1. Remove corrupted / unreadable images
    2. Resize all images to the target size
    3. Convert all images to RGB (remove alpha channels)
    4. Print a summary report

    Args:
        dataset_dir: Root directory of the dataset.
    """
    if dataset_dir is None:
        dataset_dir = str(settings.DATASETS_DIR)

    target_size = (settings.IMAGE_SIZE, settings.IMAGE_SIZE)
    total_files = 0
    cleaned = 0
    removed = 0
    skipped = 0

    print("=" * 60)
    print("VisionSpec QC - Dataset Preprocessing")
    print("=" * 60)
    print(f"Source      : {dataset_dir}")
    print(f"Target Size : {target_size[0]}x{target_size[1]}")
    print("-" * 60)

    for class_folder in Path(dataset_dir).iterdir():
        if not class_folder.is_dir():
            continue

        print(f"\n📁 Processing class: {class_folder.name}")

        for img_path in class_folder.iterdir():
            total_files += 1

            # Skip non-image files
            if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                print(f"   ⏭️  Skipping non-image: {img_path.name}")
                skipped += 1
                continue

            try:
                img = Image.open(img_path)
                img.verify()  # Verify it's not corrupted
                img = Image.open(img_path)  # Re-open after verify

                # Convert to RGB
                img = img.convert("RGB")

                # Resize
                img = img.resize(target_size, Image.LANCZOS)

                # Save back (overwrite)
                img.save(img_path)
                cleaned += 1

            except Exception as e:
                print(f"   ❌ Corrupted — removing: {img_path.name} ({e})")
                img_path.unlink()
                removed += 1

    print("\n" + "=" * 60)
    print("Preprocessing Summary")
    print("=" * 60)
    print(f"  Total files scanned : {total_files}")
    print(f"  ✅ Cleaned & resized : {cleaned}")
    print(f"  ❌ Corrupted removed : {removed}")
    print(f"  ⏭️  Skipped          : {skipped}")
    print("=" * 60)


if __name__ == "__main__":
    clean_dataset()
