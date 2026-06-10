# VisionSpec QC — Weekly Progress Report
### AI-Powered PCB Visual Inspection System
**Internship Project 2 — Zaalima**

> Reporting period: 4 weeks | Status: ✅ Completed & running end-to-end
> Stack: TensorFlow/Keras (MobileNetV2), FastAPI, SQLite, React + TypeScript (Vite)

---

## Week 1 — Foundation, Dataset & Project Scaffolding

**Goal:** Establish the development environment, raw data, and skeleton of all three layers (AI, backend, frontend).

### Work Completed
- **Environment setup:** Created the Python virtual environment (`venv_vqc`), installed the core stack (TensorFlow, FastAPI, OpenCV, NumPy, Pandas, SQLAlchemy), and initialized the React + TypeScript app via Vite with TailwindCSS.
- **Repository structure:** Laid out the modular `backend/` (app, routes, services, models, schemas, config) and `frontend/` (pages, components, services) architecture.
- **Synthetic dataset generation:** Built a procedural **PCB Dataset Generator** (`generate_dataset.py`) since real proprietary PCB images were unavailable. It draws circuit traces, pads, and SMD components, then injects defects (scratches, burns, oxidation, missing traces).
  - **Output:** 1,000 images @ 224×224 — 500 *Pass* / 500 *Defect*.
- **Data pipeline:** Configured Keras `ImageDataGenerator` for augmentation (rotation, flip, brightness) and preprocessing utilities.
- **API & UI skeleton:** FastAPI boilerplate with Pydantic schemas and CORS; React routing for the four core pages (Dashboard, Live Detection, Defect Analysis, History).

### Deliverables
- Working dev environment for all 3 layers
- 1,000-image synthetic dataset
- Project scaffolding + routing in place

---

## Week 2 — Core Detection Model & Prediction API

**Goal:** Train the first working classifier and connect it to an image-upload API + UI.

### Work Completed
- **Model architecture (MobileNetV2 transfer learning):**
  - Base: MobileNetV2 (ImageNet weights, frozen backbone).
  - Head: `GlobalAveragePooling2D → Dense(256)+BatchNorm+Dropout → Dense(128)+BatchNorm+Dropout → Dense(1, Sigmoid)`.
  - Optimizer: Adam (LR 1e-4) + `ReduceLROnPlateau`; Loss: Binary Crossentropy.
- **Two-phase training strategy:**
  - *Phase A:* Trained custom head for 10 epochs (frozen backbone).
  - *Phase B:* Fine-tuned top conv layers (from layer 100) for 10 more epochs at LR 1e-5.
  - Early stopping triggered at epoch 17 to curb overfitting. Exported `pcb_model.h5`.
- **`POST /api/predict` endpoint:** Accepts multipart image upload → validates type/size (max 10 MB) → preprocesses → runs inference → returns `predicted_label`, `confidence`, `inference_time_ms`, `image_size`.
- **Defect Analysis page:** Drag-and-drop upload UI wired to `/predict`, displaying label + confidence.

### Deliverables
- Trained, exported MobileNetV2 model
- Functional prediction API
- End-to-end "upload → AI result" flow

---

## Week 3 — Explainable AI (Grad-CAM) & Real-Time Video Pipeline

**Goal:** Add visual explainability and a live webcam inference path.

### Work Completed
- **Grad-CAM (Explainable AI):** Implemented gradient-weighted class activation mapping against MobileNetV2's final conv layer (`out_relu`). Generates a thermal heatmap overlay showing *where* the model focused — solving the CNN "black-box" problem.
- **Heatmap integration:** Grad-CAM output encoded as base64 and returned inside the `/predict` response; rendered as an overlay on the Defect Analysis page.
- **Live video pipeline:** Built `POST /api/webcam/predict` using OpenCV to process webcam frames on the fly.
- **Live Detection page:** Captures the browser webcam feed, streams frames to the backend, and displays real-time results with FPS monitoring.

### Deliverables
- Real-time Grad-CAM heatmaps (~128 KB overlay per image)
- Webcam inference endpoint
- Live Detection UI with FPS readout

---

## Week 4 — Analytics, Logging, Dashboard & Final Integration

**Goal:** Tie everything together — persistence, analytics, evaluation, and polish.

### Work Completed
- **Prediction logging:** Every inference is persisted to SQLite (`PredictionLog`: timestamp, filename, label, confidence, latency, source).
- **Analytics & history APIs:** `GET /api/analytics` (totals, defect rate, avg confidence, avg latency, today's count) and `GET /api/history` (paginated log with CSV export).
- **Live Dashboard:** Real-time command center showing total inspections, pass/defect counts, defect rate, avg inference time, derived FPS, recent predictions, and system status (auto-refresh every 5 s).
- **System Monitor:** `GET /api/system/metrics` exposes CPU / memory / uptime.
- **Human-in-the-Loop feedback:** "Correct this prediction" action (`POST /api/feedback`) lets operators flag wrong predictions for future retraining.
- **Model evaluation:** Generated final metrics, confusion matrix, ROC curve, and prediction-distribution charts.

### Final Evaluation Metrics (200-image validation set)
| Metric | Value |
| :--- | :--- |
| Accuracy | 67.0% |
| AUC (ROC) | 0.7652 |
| Validation Loss | 0.5867 |
| Avg. Inference Time | ~280–620 ms (CPU) |

| Class | Precision | Recall | F1 | Support |
| :--- | :--- | :--- | :--- | :--- |
| Defect | 0.77 | 0.48 | 0.59 | 100 |
| Pass | 0.62 | 0.86 | 0.72 | 100 |

> *Note:* 67% is an expected baseline for highly randomized synthetic noise. The same architecture on a real dataset (e.g., Kaggle PCB Defect) typically reaches 95%+.

### Deliverables
- Full analytics + history + dashboard
- Human-in-the-Loop feedback loop
- Evaluation report with diagnostic charts
- **Complete system running end-to-end** (backend at `:8000`, frontend at `:5173`)

---

## 4-Week Summary

| Week | Focus | Key Outcome |
| :--- | :--- | :--- |
| **1** | Setup & Data | Environment + 1,000-image synthetic dataset + scaffolding |
| **2** | Model & API | Trained MobileNetV2 + `/predict` + upload UI |
| **3** | XAI & Live | Grad-CAM heatmaps + webcam inference pipeline |
| **4** | Integration | Analytics, logging, dashboard, feedback, evaluation |

### Milestones
- ✅ Model classifying static images (baseline accuracy established)
- ✅ Frontend uploading images and displaying AI results + heatmaps
- ✅ Live webcam feed with real-time inference
- ✅ Full system running end-to-end with analytics & history

### Next Steps (Future Enhancements)
- Train on a real-world PCB dataset to push accuracy to 95%+
- Multi-class defect categorization (short, burn, missing solder, scratch)
- Dockerization & cloud deployment (Render + Vercel)
- Edge AI (TFLite/TensorRT) "ultra-fast" mode
- Auto-generated PDF QA reports and Slack/email defect alerts
