"""
VisionSpec QC - Data Augmentation Pipeline
Implements Keras ImageDataGenerator for robust PCB image augmentation.
"""

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from backend.app.config.settings import settings

# ── Training Data Generator (with augmentation) ────────────
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

# ── Validation Data Generator (NO augmentation, only rescale) ─
val_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    validation_split=0.2,
)


def get_train_generator(dataset_dir: str = None):
    """
    Create a training data generator from the dataset directory.

    Expected directory structure:
        datasets/
        ├── Pass/
        │   ├── img001.jpg
        │   └── ...
        └── Defect/
            ├── img001.jpg
            └── ...

    Args:
        dataset_dir: Path to the root dataset folder.

    Returns:
        A Keras DirectoryIterator for training data.
    """
    if dataset_dir is None:
        dataset_dir = str(settings.DATASETS_DIR)

    return train_datagen.flow_from_directory(
        dataset_dir,
        target_size=(settings.IMAGE_SIZE, settings.IMAGE_SIZE),
        batch_size=settings.BATCH_SIZE,
        class_mode="binary",
        subset="training",
        shuffle=True,
    )


def get_val_generator(dataset_dir: str = None):
    """
    Create a validation data generator from the dataset directory.

    Args:
        dataset_dir: Path to the root dataset folder.

    Returns:
        A Keras DirectoryIterator for validation data.
    """
    if dataset_dir is None:
        dataset_dir = str(settings.DATASETS_DIR)

    return val_datagen.flow_from_directory(
        dataset_dir,
        target_size=(settings.IMAGE_SIZE, settings.IMAGE_SIZE),
        batch_size=settings.BATCH_SIZE,
        class_mode="binary",
        subset="validation",
        shuffle=False,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("VisionSpec QC - Data Augmentation Pipeline")
    print("=" * 60)
    print(f"Dataset Directory : {settings.DATASETS_DIR}")
    print(f"Image Size        : {settings.IMAGE_SIZE}x{settings.IMAGE_SIZE}")
    print(f"Batch Size        : {settings.BATCH_SIZE}")
    print()
    print("Augmentation Techniques Applied:")
    print("  ✅ Rotation (±30°)")
    print("  ✅ Width/Height Shift (20%)")
    print("  ✅ Shear (15%)")
    print("  ✅ Zoom (±25%)")
    print("  ✅ Horizontal & Vertical Flip")
    print("  ✅ Brightness Adjustment (0.7–1.3)")
    print("  ✅ Normalization (0–1)")
    print()
    print("⚠️  Place your PCB images in:")
    print(f"    {settings.DATASETS_DIR}/Pass/")
    print(f"    {settings.DATASETS_DIR}/Defect/")
    print("=" * 60)
