# VisionSpec QC - Project Features

This document outlines the core functionalities required for the system as well as advanced unique features to differentiate the project.

## 🎯 Exact Features (Core Architecture)

These are the standard, non-negotiable features based on the current project requirements:

1.  **Live Real-Time Inference:** Streaming video from a webcam through OpenCV to detect defects frame-by-frame on the fly.
2.  **Static Image Analysis:** A robust manual upload tool where users can upload high-resolution photos of PCBs for deep inspection.
3.  **Explainable AI (Grad-CAM XAI):** Generating heatmaps to show exactly *where* the AI looked to make its decision, removing the "black box" problem.
4.  **Live System Dashboard:** A React-based command center displaying real-time system health, inference speed (FPS), and current detection status.
5.  **Quality Assurance (QA) Analytics:** Automated tracking of defect rates, total scanned items, and accuracy trends over time using charts.
6.  **Inspection History & Auditing:** A database-backed log (SQLite/PostgreSQL) storing all past predictions, timestamps, and confidence scores for historical tracking.

---

## 🚀 Unique Features (Advanced Enhancements)

These are advanced features that can be added to make the project stand out as a premium, enterprise-level product:

1.  **Active Learning Feedback Loop (Human-in-the-Loop):**
    *   *Concept:* Add a "Correct this prediction" button. If the AI makes a mistake, the human operator flags it. The backend saves this image to automatically retrain and improve the model later.
2.  **Multi-Class Defect Categorization:**
    *   *Concept:* Instead of just "Pass / Fail," train the model to identify the *exact type* of defect (e.g., "Missing Solder," "Short Circuit," "Burnt Component," "Scratched Trace").
3.  **Auto-Generated PDF QA Reports:**
    *   *Concept:* Add a button on the Analytics page that automatically compiles the day's inspection history, heatmaps, and stats into a downloadable, professional PDF report.
4.  **Smart Cropping & Zooming (Region of Interest):**
    *   *Concept:* When a defect is detected, the frontend automatically crops the image to the bounding box of the defect and zooms in, improving the operator's experience.
5.  **Slack/Email Alert System:**
    *   *Concept:* If the backend detects a streak of defects (e.g., 5 defective PCBs in a row), it automatically triggers an API call to send a warning to a Slack channel or email.
6.  **Edge AI Simulation (TensorRT / TFLite):**
    *   *Concept:* Convert the TensorFlow model into a TFLite or TensorRT format and add a toggle in the UI to switch between "High Accuracy Mode" and "Ultra-Fast Edge Mode."
