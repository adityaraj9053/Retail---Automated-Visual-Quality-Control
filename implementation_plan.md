# VisionSpec QC - Real-Time Implementation Plan

This plan breaks down the project into logical, agile phases, assigning parallel responsibilities to all three team members to ensure continuous integration and a smooth workflow.

## Phase 1: Environment Setup & Data Preparation (Weeks 1-2)
**Goal:** Establish the foundation, tools, and raw data required for the project.

*   **🧠 Member 1 (ML Engineer):** Collect PCB image datasets (pass/defect), perform data cleaning, and set up the Keras `ImageDataGenerator` for augmentation (rotation, flipping, brightness).
*   **⚙️ Member 2 (Backend Engineer):** Set up the FastAPI boilerplate, establish the Git repository, configure the chosen database (SQLite/PostgreSQL), and define the initial API input/output schemas (Pydantic).
*   **💻 Member 3 (Frontend Developer):** Initialize the React/TypeScript app via Vite, set up TailwindCSS and the global design system, and create the basic routing structure (Dashboard, Live Detection, Analysis, History).

---

## Phase 2: Core Detection Model & Base APIs (Weeks 3-4)
**Goal:** Train the first working AI model and connect it to a static image upload API.

*   **🧠 Member 1:** Build and train the core CNN (ResNet50 or MobileNetV2). Monitor validation metrics, tweak hyperparameters, and export the first stable `SavedModel` or `.h5` file.
*   **⚙️ Member 2:** Develop the core `POST /predict` API. Write the logic to accept an uploaded image, pass it to Member 1's inference script, and return the predicted label and confidence score.
*   **💻 Member 3:** Build the **Defect Analysis Page** UI where users can upload an image. Connect this UI to Member 2's `/predict` API and display the result.

---

## Phase 3: Explainable AI & Real-Time Video Pipeline (Weeks 5-6)
**Goal:** Add visual explainability (heatmaps) and establish the live video streaming foundation.

*   **🧠 Member 1:** Implement Grad-CAM logic to generate heatmaps for defective regions. Verify that the heatmaps accurately highlight PCB flaws.
*   **⚙️ Member 2:** Integrate the Grad-CAM output into the API response. Develop the `POST /webcam/predict` or WebSocket endpoint utilizing OpenCV to process frame-by-frame data.
*   **💻 Member 3:** Update the Defect Analysis UI to render the new Grad-CAM heatmaps. Build the **Live Detection Page** UI to capture the user's webcam feed and send frames to the backend.

---

## Phase 4: Analytics & Full System Integration (Weeks 7-8)
**Goal:** Tie everything together, record history, and display analytics.

*   **🧠 Member 1:** Focus on performance optimization (quantization, removing bottlenecks) to ensure the model runs fast enough for real-time video (>10-15 FPS).
*   **⚙️ Member 2:** Implement the prediction logging system (saving every prediction to the DB). Build the `GET /analytics` and `GET /history` APIs.
*   **💻 Member 3:** Build the **Analytics Page** using a charting library (like Chart.js/Recharts) to show trends, and create the **Prediction History** table. Ensure the Live Detection Page smoothly renders the real-time bounding boxes/labels.

---

## Phase 5: Polish, Dockerization, & Deployment (Weeks 9-10)
**Goal:** Make the system production-ready, robust, and deploy it.

*   **🧠 Member 1:** Conduct final evaluation testing on unseen test datasets. Generate the final performance report (Accuracy, Precision, Recall, Confusion Matrix).
*   **⚙️ Member 2:** Write the `Dockerfile` for the FastAPI backend. Secure the APIs (CORS, error handling). Deploy the backend to a cloud provider (e.g., Render, AWS, or local server).
*   **💻 Member 3:** Polish the UI/UX for a premium feel (micro-animations, responsive mobile views). Handle edge cases (e.g., camera disconnected, backend offline). Deploy the frontend (e.g., Vercel).

---

## 🚦 Milestones Checklist
- [ ] **Milestone 1:** Model successfully classifying static images with >90% accuracy.
- [ ] **Milestone 2:** Frontend successfully uploading an image and displaying the AI result.
- [ ] **Milestone 3:** Live webcam feed functioning with real-time AI inference.
- [ ] **Milestone 4:** Full system deployed and running end-to-end.
