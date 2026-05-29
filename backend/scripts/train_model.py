"""
VisionSpec QC — Phase 2: Core CNN Training Script
Trains a MobileNetV2-based binary classifier for PCB defect detection.

Usage:
    python -m backend.scripts.train_model
    
    Or directly:
    python backend/scripts/train_model.py --dataset_dir path/to/dataset
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    ReduceLROnPlateau,
    TensorBoard,
)

# ── Resolve project paths ──────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
MODELS_DIR = BACKEND_DIR / "trained_models"
DATASETS_DIR = BACKEND_DIR / "datasets"
LOGS_DIR = BACKEND_DIR / "logs"

for d in [MODELS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Default Hyperparameters ─────────────────────────────────
IMAGE_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 30
LEARNING_RATE = 1e-4
FINE_TUNE_AT = 100  # Unfreeze MobileNetV2 layers from this index onward


def build_model(image_size: int = IMAGE_SIZE) -> keras.Model:
    """
    Build a MobileNetV2-based binary classifier.

    Architecture:
        - MobileNetV2 backbone (ImageNet weights, frozen initially)
        - Global Average Pooling
        - Dense 256 → BatchNorm → Dropout(0.5)
        - Dense 128 → BatchNorm → Dropout(0.3)
        - Sigmoid output for binary classification

    Args:
        image_size: Input image dimension (square).

    Returns:
        Compiled Keras Model.
    """
    base_model = MobileNetV2(
        input_shape=(image_size, image_size, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False  # Freeze for initial training

    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(1, activation="sigmoid"),
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    return model


def create_data_generators(dataset_dir: str, image_size: int, batch_size: int):
    """
    Create training and validation data generators with augmentation.

    Expected directory structure:
        dataset_dir/
        ├── Defect/
        │   ├── img001.jpg
        │   └── ...
        └── Pass/
            ├── img001.jpg
            └── ...

    Args:
        dataset_dir: Path to root dataset folder.
        image_size: Target image size.
        batch_size: Batch size for generators.

    Returns:
        Tuple of (train_generator, val_generator).
    """
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.15,
        zoom_range=0.25,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.7, 1.3],
        fill_mode="nearest",
        validation_split=0.2,
    )

    val_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        validation_split=0.2,
    )

    train_gen = train_datagen.flow_from_directory(
        dataset_dir,
        target_size=(image_size, image_size),
        batch_size=batch_size,
        class_mode="binary",
        subset="training",
        shuffle=True,
    )

    val_gen = val_datagen.flow_from_directory(
        dataset_dir,
        target_size=(image_size, image_size),
        batch_size=batch_size,
        class_mode="binary",
        subset="validation",
        shuffle=False,
    )

    return train_gen, val_gen


def train(dataset_dir: str = None, epochs: int = EPOCHS):
    """
    Full training pipeline:
    1. Build model
    2. Train with frozen backbone
    3. Fine-tune top layers of MobileNetV2
    4. Save model and training report

    Args:
        dataset_dir: Path to dataset. Defaults to backend/datasets.
        epochs: Number of training epochs.
    """
    if dataset_dir is None:
        dataset_dir = str(DATASETS_DIR)

    print("=" * 65)
    print("  VisionSpec QC — Phase 2: CNN Model Training")
    print("=" * 65)
    print(f"  Dataset      : {dataset_dir}")
    print(f"  Image Size   : {IMAGE_SIZE}x{IMAGE_SIZE}")
    print(f"  Batch Size   : {BATCH_SIZE}")
    print(f"  Epochs       : {epochs}")
    print(f"  Architecture : MobileNetV2 + Custom Head")
    print(f"  Output       : {MODELS_DIR / 'pcb_model.h5'}")
    print("=" * 65)
    print()

    # ── Step 1: Create generators ──────────────────────────
    print("📂 Loading dataset...")
    train_gen, val_gen = create_data_generators(dataset_dir, IMAGE_SIZE, BATCH_SIZE)

    class_indices = train_gen.class_indices
    print(f"   Classes found: {class_indices}")
    print(f"   Training samples  : {train_gen.samples}")
    print(f"   Validation samples: {val_gen.samples}")
    print()

    # ── Step 2: Build model ────────────────────────────────
    print("🏗️  Building MobileNetV2 model...")
    model = build_model(IMAGE_SIZE)
    model.summary()
    print()

    # ── Step 3: Callbacks ──────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    callbacks = [
        ModelCheckpoint(
            str(MODELS_DIR / "pcb_model.h5"),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_loss",
            patience=7,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
        TensorBoard(
            log_dir=str(LOGS_DIR / f"tensorboard_{timestamp}"),
            histogram_freq=1,
        ),
    ]

    # ── Step 4: Phase A — Train with frozen backbone ───────
    print("🚀 Phase A: Training with frozen backbone...")
    initial_epochs = min(epochs // 2, 10)
    history_frozen = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=initial_epochs,
        callbacks=callbacks,
    )

    # ── Step 5: Phase B — Fine-tune top layers ─────────────
    print(f"\n🔓 Phase B: Fine-tuning from layer {FINE_TUNE_AT}...")
    base = model.layers[0]  # MobileNetV2 base
    base.trainable = True
    for layer in base.layers[:FINE_TUNE_AT]:
        layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE / 10),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    remaining_epochs = epochs - initial_epochs
    history_finetuned = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs,
        initial_epoch=initial_epochs,
        callbacks=callbacks,
    )

    # ── Step 6: Evaluate ───────────────────────────────────
    print("\n📊 Final Evaluation on Validation Set:")
    val_loss, val_acc = model.evaluate(val_gen, verbose=0)
    print(f"   Validation Loss     : {val_loss:.4f}")
    print(f"   Validation Accuracy : {val_acc:.4f} ({val_acc * 100:.1f}%)")

    # ── Step 7: Save training report ───────────────────────
    report = {
        "timestamp": timestamp,
        "architecture": "MobileNetV2 + Custom Head",
        "image_size": IMAGE_SIZE,
        "batch_size": BATCH_SIZE,
        "epochs_trained": epochs,
        "class_indices": class_indices,
        "val_loss": round(float(val_loss), 4),
        "val_accuracy": round(float(val_acc), 4),
        "model_path": str(MODELS_DIR / "pcb_model.h5"),
    }

    report_path = MODELS_DIR / "training_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📝 Training report saved to: {report_path}")

    # ── Step 8: Save class labels ──────────────────────────
    labels_path = MODELS_DIR / "class_labels.json"
    # Invert: {0: "Defect", 1: "Pass"} → ensure index-to-label
    idx_to_label = {v: k for k, v in class_indices.items()}
    with open(labels_path, "w") as f:
        json.dump(idx_to_label, f, indent=2)
    print(f"🏷️  Class labels saved to: {labels_path}")

    print()
    print("=" * 65)
    print("  ✅ Training Complete!")
    print(f"  Model saved: {MODELS_DIR / 'pcb_model.h5'}")
    print("=" * 65)

    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train VisionSpec QC PCB Defect Classifier")
    parser.add_argument(
        "--dataset_dir",
        type=str,
        default=str(DATASETS_DIR),
        help="Path to the dataset directory",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=EPOCHS,
        help="Number of training epochs",
    )
    args = parser.parse_args()

    train(dataset_dir=args.dataset_dir, epochs=args.epochs)
