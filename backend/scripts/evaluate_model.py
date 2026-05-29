"""
VisionSpec QC — Model Evaluation Script
Generates a comprehensive evaluation report with metrics and visualizations.

Usage:
    python backend/scripts/evaluate_model.py
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
)

# ── Resolve project paths ──────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
MODELS_DIR = BACKEND_DIR / "trained_models"
DATASETS_DIR = BACKEND_DIR / "datasets"
REPORTS_DIR = MODELS_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_SIZE = 224
BATCH_SIZE = 32


def evaluate():
    """Run full model evaluation and generate reports."""

    model_path = MODELS_DIR / "pcb_model.h5"
    if not model_path.exists():
        print("❌ Model not found! Train the model first.")
        return

    print("=" * 65)
    print("  VisionSpec QC — Model Evaluation Report")
    print("=" * 65)

    # ── Load model ─────────────────────────────────────────
    print("\n📦 Loading model...")
    model = keras.models.load_model(str(model_path))
    print("   ✅ Model loaded successfully.")

    # ── Load validation data ───────────────────────────────
    print("\n📂 Loading validation data...")
    val_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        validation_split=0.2,
    )

    val_gen = val_datagen.flow_from_directory(
        str(DATASETS_DIR),
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="binary",
        subset="validation",
        shuffle=False,
    )

    class_indices = val_gen.class_indices
    idx_to_label = {v: k for k, v in class_indices.items()}
    print(f"   Classes: {class_indices}")
    print(f"   Validation samples: {val_gen.samples}")

    # ── Evaluate ───────────────────────────────────────────
    print("\n📊 Evaluating model...")
    val_loss, val_acc = model.evaluate(val_gen, verbose=1)
    print(f"\n   Loss     : {val_loss:.4f}")
    print(f"   Accuracy : {val_acc:.4f} ({val_acc * 100:.1f}%)")

    # ── Get predictions ────────────────────────────────────
    print("\n🔍 Generating predictions...")
    val_gen.reset()
    y_pred_raw = model.predict(val_gen, verbose=1)
    y_pred_raw = y_pred_raw.flatten()
    y_pred = (y_pred_raw >= 0.5).astype(int)
    y_true = val_gen.classes

    # ── Classification Report ──────────────────────────────
    print("\n" + "=" * 65)
    print("  Classification Report")
    print("=" * 65)
    target_names = [idx_to_label[i] for i in sorted(idx_to_label.keys())]
    report_str = classification_report(y_true, y_pred, target_names=target_names)
    print(report_str)

    report_dict = classification_report(
        y_true, y_pred, target_names=target_names, output_dict=True
    )

    # ── Confusion Matrix ───────────────────────────────────
    cm = confusion_matrix(y_true, y_pred)
    print("Confusion Matrix:")
    print(cm)

    # ── Generate Plots ─────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Confusion Matrix Plot
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.set_title("Confusion Matrix — VisionSpec QC", fontsize=14, fontweight="bold")
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=target_names,
        yticklabels=target_names,
        xlabel="Predicted Label",
        ylabel="True Label",
    )
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], "d"),
                    ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black",
                    fontsize=16, fontweight="bold")
    plt.tight_layout()
    cm_path = REPORTS_DIR / f"confusion_matrix_{timestamp}.png"
    plt.savefig(str(cm_path), dpi=150)
    plt.close()
    print(f"\n📈 Confusion matrix saved: {cm_path}")

    # 2. ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_pred_raw)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax.plot(fpr, tpr, color="#2563eb", lw=2,
            label=f"ROC Curve (AUC = {roc_auc:.4f})")
    ax.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve — VisionSpec QC", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right")
    plt.tight_layout()
    roc_path = REPORTS_DIR / f"roc_curve_{timestamp}.png"
    plt.savefig(str(roc_path), dpi=150)
    plt.close()
    print(f"📈 ROC curve saved: {roc_path}")

    # 3. Prediction Distribution
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax.hist(y_pred_raw[y_true == 0], bins=50, alpha=0.7,
            label="Defect (True)", color="#ef4444")
    ax.hist(y_pred_raw[y_true == 1], bins=50, alpha=0.7,
            label="Pass (True)", color="#22c55e")
    ax.axvline(x=0.5, color="black", linestyle="--", label="Threshold (0.5)")
    ax.set_xlabel("Prediction Score")
    ax.set_ylabel("Count")
    ax.set_title("Prediction Distribution — VisionSpec QC",
                 fontsize=14, fontweight="bold")
    ax.legend()
    plt.tight_layout()
    dist_path = REPORTS_DIR / f"prediction_distribution_{timestamp}.png"
    plt.savefig(str(dist_path), dpi=150)
    plt.close()
    print(f"📈 Prediction distribution saved: {dist_path}")

    # ── Save Full Report JSON ──────────────────────────────
    full_report = {
        "timestamp": timestamp,
        "model_path": str(model_path),
        "dataset_path": str(DATASETS_DIR),
        "validation_samples": val_gen.samples,
        "val_loss": round(float(val_loss), 4),
        "val_accuracy": round(float(val_acc), 4),
        "roc_auc": round(float(roc_auc), 4),
        "classification_report": report_dict,
        "confusion_matrix": cm.tolist(),
        "plots": {
            "confusion_matrix": str(cm_path),
            "roc_curve": str(roc_path),
            "prediction_distribution": str(dist_path),
        },
    }

    report_json_path = REPORTS_DIR / f"evaluation_report_{timestamp}.json"
    with open(report_json_path, "w") as f:
        json.dump(full_report, f, indent=2)
    print(f"\n📝 Full report saved: {report_json_path}")

    print()
    print("=" * 65)
    print("  ✅ Evaluation Complete!")
    print(f"  Accuracy : {val_acc * 100:.1f}%")
    print(f"  AUC      : {roc_auc:.4f}")
    print(f"  Reports  : {REPORTS_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    evaluate()
