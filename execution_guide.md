# VisionSpec QC — Execution Guide

This document provides a step-by-step walkthrough of how to execute and run the application locally on your machine.

## Option A: Running Natively (Local Environment)

You will need to open two separate terminals to run the frontend and backend concurrently.

### 1. Start the Backend (FastAPI)
1. Open your terminal and ensure you are in the project root: `d:\Zaalima Intern Project 2`
2. Install the required Python dependencies (if you haven't already):
   ```powershell
   pip install -r backend/requirements.txt
   ```
3. Start the FastAPI server using Uvicorn:
   ```powershell
   python -m uvicorn backend.app.main:app --reload --host localhost --port 8000
   ```
   - **Backend URL**: `http://localhost:8000`
   - **API Documentation (Swagger UI)**: `http://localhost:8000/docs`

### 2. Start the Frontend (React + Vite)
1. Open a **second** terminal window and navigate to the frontend folder:
   ```powershell
   cd "d:\Zaalima Intern Project 2\frontend"
   ```
2. Install the Node modules:
   ```powershell
   npm install
   ```
3. Start the Vite development server:
   ```powershell
   npm run dev
   ```
   - **Frontend UI**: `http://localhost:5173`
   *(Open this URL in your browser to access the dashboard)*

---

## Option B: Running via Docker (Recommended for Production)

Since we have created a `Dockerfile` and `docker-compose.yml`, you can run the entire application stack with a single command. Note: You must have Docker Desktop installed and running.

1. Open a terminal in the project root: `d:\Zaalima Intern Project 2`
2. Build and spin up the containers:
   ```powershell
   docker-compose up --build
   ```
3. Docker will automatically install dependencies and expose the same ports:
   - Frontend: `http://localhost:5173`
   - Backend: `http://localhost:8000`

---

## Using the Application
1. **Dashboard**: Once running, navigate to `http://localhost:5173`.
2. **Defect Analysis**: Upload an image to test the core model (Grad-CAM heatmaps will be generated for defects).
3. **Live Detection**: Ensure your webcam is connected, click "Start Camera", and click "Start Detection" to see real-time bounding boxes and FPS.
4. **Prediction History**: View past records and use the "Action" button to provide Human-in-the-loop feedback if a prediction is incorrect.
5. **System Monitor**: Check the real-time API uptime, CPU, and RAM load while the model is processing.
