# Datasets Directory

This folder is designated for storing the raw and processed image data used for training the VisionSpec QC defect detection model.

## Structure
* `/raw` - Unprocessed images collected from the PCB manufacturing line.
* `/processed` - Images that have undergone data augmentation (rotation, zooming, brightness shifts) using `ImageDataGenerator`.
* `/test` - Unseen data reserved exclusively for final model evaluation.

**Note:** Large datasets should not be committed to version control. Add specific data file extensions (e.g., `*.jpg`, `*.png`) to `.gitignore`.
