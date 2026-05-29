"""
VisionSpec QC — Synthetic PCB Dataset Generator
Generates realistic synthetic PCB images for training the defect detection model.

Creates two classes:
  - Pass:   Clean PCB boards with circuit traces and components
  - Defect: PCB boards with scratches, burns, missing traces, corrosion

Usage:
    python backend/scripts/generate_dataset.py
    python backend/scripts/generate_dataset.py --count 500 --size 224
"""

import os
import sys
import argparse
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

# ── Resolve project paths ──────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
DATASETS_DIR = BACKEND_DIR / "datasets"

# ── PCB Color Palettes ─────────────────────────────────────
PCB_GREENS = [
    (0, 100, 0), (0, 120, 30), (10, 90, 20), (5, 110, 25),
    (0, 80, 15), (20, 105, 10), (15, 95, 30),
]
COPPER_COLORS = [
    (180, 140, 60), (200, 160, 80), (170, 130, 50), (190, 150, 70),
    (210, 170, 90), (160, 120, 40),
]
SOLDER_COLORS = [
    (192, 192, 192), (180, 180, 180), (200, 200, 200), (170, 170, 170),
]
COMPONENT_COLORS = [
    (30, 30, 30), (40, 40, 40), (50, 50, 60), (20, 20, 25),  # IC chips
    (100, 80, 60), (80, 60, 40),  # Resistors
    (60, 60, 80), (70, 70, 90),   # Capacitors
]


def generate_base_pcb(size: int = 224) -> Image.Image:
    """Create a base PCB board image with green substrate and subtle texture."""
    base_color = random.choice(PCB_GREENS)
    img = Image.new("RGB", (size, size), base_color)
    pixels = np.array(img, dtype=np.float32)

    # Add noise/texture to simulate PCB surface
    noise = np.random.normal(0, 8, pixels.shape).astype(np.float32)
    pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)

    return Image.fromarray(pixels)


def draw_traces(draw: ImageDraw.Draw, size: int):
    """Draw copper traces (circuit paths) on the PCB."""
    num_horizontal = random.randint(5, 15)
    num_vertical = random.randint(5, 15)
    num_diagonal = random.randint(2, 6)

    for _ in range(num_horizontal):
        y = random.randint(0, size)
        x_start = random.randint(0, size // 3)
        x_end = random.randint(size // 2, size)
        color = random.choice(COPPER_COLORS)
        width = random.choice([1, 2, 3])
        # Add some jitter/turns
        points = [(x_start, y)]
        x = x_start
        while x < x_end:
            x += random.randint(15, 50)
            y_jitter = y + random.randint(-10, 10)
            points.append((min(x, x_end), y_jitter))
        if len(points) >= 2:
            draw.line(points, fill=color, width=width)

    for _ in range(num_vertical):
        x = random.randint(0, size)
        y_start = random.randint(0, size // 3)
        y_end = random.randint(size // 2, size)
        color = random.choice(COPPER_COLORS)
        width = random.choice([1, 2, 3])
        points = [(x, y_start)]
        y = y_start
        while y < y_end:
            y += random.randint(15, 50)
            x_jitter = x + random.randint(-10, 10)
            points.append((x_jitter, min(y, y_end)))
        if len(points) >= 2:
            draw.line(points, fill=color, width=width)

    for _ in range(num_diagonal):
        x1 = random.randint(0, size)
        y1 = random.randint(0, size)
        x2 = x1 + random.randint(-80, 80)
        y2 = y1 + random.randint(-80, 80)
        color = random.choice(COPPER_COLORS)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=random.choice([1, 2]))


def draw_pads(draw: ImageDraw.Draw, size: int):
    """Draw solder pads (circular/square connection points)."""
    num_pads = random.randint(15, 40)
    for _ in range(num_pads):
        x = random.randint(10, size - 10)
        y = random.randint(10, size - 10)
        pad_size = random.randint(3, 8)
        color = random.choice(SOLDER_COLORS)

        if random.random() > 0.5:
            draw.ellipse(
                [x - pad_size, y - pad_size, x + pad_size, y + pad_size],
                fill=color, outline=random.choice(COPPER_COLORS)
            )
        else:
            draw.rectangle(
                [x - pad_size, y - pad_size, x + pad_size, y + pad_size],
                fill=color, outline=random.choice(COPPER_COLORS)
            )


def draw_components(draw: ImageDraw.Draw, size: int):
    """Draw electronic components (ICs, resistors, capacitors)."""
    # Large IC chips
    num_ics = random.randint(1, 3)
    for _ in range(num_ics):
        w = random.randint(20, 50)
        h = random.randint(15, 35)
        x = random.randint(10, size - w - 10)
        y = random.randint(10, size - h - 10)
        color = random.choice(COMPONENT_COLORS[:4])
        draw.rectangle([x, y, x + w, y + h], fill=color)
        # IC marking line
        draw.line([(x + 3, y + h // 2), (x + w - 3, y + h // 2)],
                  fill=(80, 80, 80), width=1)
        # Pins on sides
        for pin_y in range(y + 3, y + h - 3, 4):
            draw.rectangle([x - 3, pin_y, x, pin_y + 2],
                           fill=random.choice(SOLDER_COLORS))
            draw.rectangle([x + w, pin_y, x + w + 3, pin_y + 2],
                           fill=random.choice(SOLDER_COLORS))

    # Small components (resistors, capacitors)
    num_small = random.randint(5, 15)
    for _ in range(num_small):
        w = random.randint(6, 14)
        h = random.randint(3, 7)
        x = random.randint(5, size - w - 5)
        y = random.randint(5, size - h - 5)
        color = random.choice(COMPONENT_COLORS[4:])
        if random.random() > 0.5:
            draw.rectangle([x, y, x + w, y + h], fill=color)
        else:
            draw.rectangle([x, y, x + h, y + w], fill=color)

    # Via holes
    num_vias = random.randint(5, 20)
    for _ in range(num_vias):
        x = random.randint(5, size - 5)
        y = random.randint(5, size - 5)
        r = random.randint(2, 4)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     fill=random.choice(COPPER_COLORS),
                     outline=(100, 80, 30))


def draw_silkscreen(draw: ImageDraw.Draw, size: int):
    """Draw silkscreen markings (text labels, outlines)."""
    # Component outlines
    num_outlines = random.randint(3, 8)
    for _ in range(num_outlines):
        x = random.randint(10, size - 40)
        y = random.randint(10, size - 30)
        w = random.randint(15, 40)
        h = random.randint(10, 25)
        draw.rectangle([x, y, x + w, y + h], outline=(255, 255, 255), width=1)

    # Reference designators (small marks)
    num_marks = random.randint(3, 10)
    for _ in range(num_marks):
        x = random.randint(5, size - 15)
        y = random.randint(5, size - 10)
        draw.rectangle([x, y, x + random.randint(4, 10), y + random.randint(3, 6)],
                       fill=(255, 255, 255))


def generate_clean_pcb(size: int = 224) -> Image.Image:
    """Generate a complete clean (Pass) PCB image."""
    img = generate_base_pcb(size)
    draw = ImageDraw.Draw(img)

    draw_traces(draw, size)
    draw_pads(draw, size)
    draw_components(draw, size)
    draw_silkscreen(draw, size)

    # Slight blur for realism
    if random.random() > 0.5:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Random brightness/contrast variation
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.85, 1.15))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(0.9, 1.1))

    return img


def add_scratch_defect(img: Image.Image) -> Image.Image:
    """Add scratch marks across the PCB."""
    draw = ImageDraw.Draw(img)
    size = img.size[0]
    num_scratches = random.randint(2, 6)

    for _ in range(num_scratches):
        x1 = random.randint(0, size)
        y1 = random.randint(0, size)
        length = random.randint(30, size // 2)
        angle = random.uniform(0, 3.14159)
        x2 = int(x1 + length * np.cos(angle))
        y2 = int(y1 + length * np.sin(angle))

        scratch_color = random.choice([
            (220, 200, 160), (200, 180, 140), (180, 160, 120),
            (240, 220, 180), (160, 140, 100),
        ])
        width = random.randint(1, 4)
        draw.line([(x1, y1), (x2, y2)], fill=scratch_color, width=width)

    return img


def add_burn_defect(img: Image.Image) -> Image.Image:
    """Add burn marks / dark spots on the PCB."""
    pixels = np.array(img, dtype=np.float32)
    size = img.size[0]
    num_burns = random.randint(1, 4)

    for _ in range(num_burns):
        cx = random.randint(20, size - 20)
        cy = random.randint(20, size - 20)
        radius = random.randint(8, 30)

        y_grid, x_grid = np.ogrid[:size, :size]
        distance = np.sqrt((x_grid - cx) ** 2 + (y_grid - cy) ** 2)
        mask = distance < radius

        # Darken the burn area
        burn_intensity = random.uniform(0.2, 0.5)
        pixels[mask] *= burn_intensity

        # Add brownish tint
        pixels[mask, 0] += random.randint(20, 50)
        pixels[mask, 1] += random.randint(5, 15)

    pixels = np.clip(pixels, 0, 255).astype(np.uint8)
    return Image.fromarray(pixels)


def add_missing_trace_defect(img: Image.Image) -> Image.Image:
    """Simulate missing/broken copper traces."""
    draw = ImageDraw.Draw(img)
    size = img.size[0]
    num_gaps = random.randint(2, 5)

    for _ in range(num_gaps):
        x = random.randint(10, size - 30)
        y = random.randint(10, size - 15)
        w = random.randint(15, 40)
        h = random.randint(5, 15)

        # Cover trace area with PCB base color (simulating missing copper)
        base_color = random.choice(PCB_GREENS)
        draw.rectangle([x, y, x + w, y + h], fill=base_color)

    return img


def add_corrosion_defect(img: Image.Image) -> Image.Image:
    """Add corrosion/oxidation spots."""
    pixels = np.array(img, dtype=np.float32)
    size = img.size[0]
    num_spots = random.randint(3, 8)

    for _ in range(num_spots):
        cx = random.randint(10, size - 10)
        cy = random.randint(10, size - 10)
        radius = random.randint(5, 20)

        y_grid, x_grid = np.ogrid[:size, :size]
        distance = np.sqrt((x_grid - cx) ** 2 + (y_grid - cy) ** 2)
        mask = distance < radius

        # Greenish-white oxidation
        pixels[mask, 0] = np.clip(pixels[mask, 0] + random.randint(40, 80), 0, 255)
        pixels[mask, 1] = np.clip(pixels[mask, 1] + random.randint(50, 100), 0, 255)
        pixels[mask, 2] = np.clip(pixels[mask, 2] + random.randint(30, 60), 0, 255)

    pixels = np.clip(pixels, 0, 255).astype(np.uint8)
    return Image.fromarray(pixels)


def add_solder_bridge_defect(img: Image.Image) -> Image.Image:
    """Add solder bridges between pads."""
    draw = ImageDraw.Draw(img)
    size = img.size[0]
    num_bridges = random.randint(2, 5)

    for _ in range(num_bridges):
        x = random.randint(15, size - 30)
        y = random.randint(15, size - 15)
        length = random.randint(10, 30)

        solder_color = random.choice(SOLDER_COLORS)
        blob_w = random.randint(3, 8)

        draw.ellipse(
            [x, y, x + length, y + blob_w],
            fill=solder_color
        )

    return img


def generate_defective_pcb(size: int = 224) -> Image.Image:
    """Generate a defective PCB image by applying 1-3 random defect types."""
    img = generate_clean_pcb(size)

    defect_types = [
        add_scratch_defect,
        add_burn_defect,
        add_missing_trace_defect,
        add_corrosion_defect,
        add_solder_bridge_defect,
    ]

    # Apply 1-3 random defects
    num_defects = random.randint(1, 3)
    selected = random.sample(defect_types, num_defects)

    for defect_fn in selected:
        img = defect_fn(img)

    return img


def generate_dataset(
    output_dir: str = None,
    count_per_class: int = 500,
    image_size: int = 224,
):
    """
    Generate the full synthetic PCB dataset.

    Args:
        output_dir: Root output directory.
        count_per_class: Number of images per class (Pass and Defect).
        image_size: Output image size (square).
    """
    if output_dir is None:
        output_dir = str(DATASETS_DIR)

    pass_dir = Path(output_dir) / "Pass"
    defect_dir = Path(output_dir) / "Defect"
    pass_dir.mkdir(parents=True, exist_ok=True)
    defect_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("  VisionSpec QC — Synthetic PCB Dataset Generator")
    print("=" * 65)
    print(f"  Output Directory : {output_dir}")
    print(f"  Images per Class : {count_per_class}")
    print(f"  Image Size       : {image_size}x{image_size}")
    print(f"  Total Images     : {count_per_class * 2}")
    print("=" * 65)
    print()

    # ── Generate Pass images ───────────────────────────────
    print(f"✅ Generating {count_per_class} PASS images...")
    for i in range(count_per_class):
        img = generate_clean_pcb(image_size)
        img.save(pass_dir / f"pass_{i:04d}.jpg", "JPEG", quality=92)
        if (i + 1) % 100 == 0:
            print(f"   ... {i + 1}/{count_per_class}")
    print(f"   ✅ Done! Saved to: {pass_dir}")

    # ── Generate Defect images ─────────────────────────────
    print(f"\n❌ Generating {count_per_class} DEFECT images...")
    for i in range(count_per_class):
        img = generate_defective_pcb(image_size)
        img.save(defect_dir / f"defect_{i:04d}.jpg", "JPEG", quality=92)
        if (i + 1) % 100 == 0:
            print(f"   ... {i + 1}/{count_per_class}")
    print(f"   ✅ Done! Saved to: {defect_dir}")

    print()
    print("=" * 65)
    print(f"  🎉 Dataset Generation Complete!")
    print(f"  Total: {count_per_class * 2} images")
    print(f"    Pass   : {count_per_class} images")
    print(f"    Defect : {count_per_class} images")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic PCB dataset for VisionSpec QC"
    )
    parser.add_argument(
        "--output_dir", type=str, default=str(DATASETS_DIR),
        help="Output directory for the dataset",
    )
    parser.add_argument(
        "--count", type=int, default=500,
        help="Number of images per class (default: 500)",
    )
    parser.add_argument(
        "--size", type=int, default=224,
        help="Image size in pixels (default: 224)",
    )
    args = parser.parse_args()

    generate_dataset(
        output_dir=args.output_dir,
        count_per_class=args.count,
        image_size=args.size,
    )
