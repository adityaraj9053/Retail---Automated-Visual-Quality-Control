# VisionSpec QC — Execution Guide

Follow these instructions to start the backend AI server and the frontend React application. You will need to open **two separate terminals**.

---

## 1. Start the Backend (FastAPI & AI Model)

Open your first terminal in the root project folder (`d:\Zaalima Intern Project 2`) and run the following commands:

```powershell
# Step 1: Activate the Python virtual environment
d:\venv_vqc\Scripts\activate

# Step 2: Set encoding to prevent UTF-8 console errors
$env:PYTHONIOENCODING='utf-8'

# Step 3: Start the backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

*✅ The backend API and AI Model will now be active at `http://127.0.0.1:8000`*

---

## 2. Start the Frontend (React Dashboard)

Open a **second terminal**, navigate to the frontend directory, and start the Vite server:

```powershell
# Step 1: Navigate to the frontend directory
cd "d:\Zaalima Intern Project 2\frontend"

# Step 2: Start the React application
npm run dev
```

*✅ The User Interface will now be active at `http://localhost:5173`. Open this URL in your web browser.*

---

## 3. (Optional) AI Pipeline Commands

If you need to regenerate the dataset, retrain the model, or generate new diagnostic reports, run these commands from the root directory with the virtual environment activated:

**Generate a synthetic PCB dataset:**
```powershell
python backend/scripts/generate_dataset.py --count 500 --size 224
```

**Train the AI Model:**
```powershell
python backend/scripts/train_model.py --dataset_dir "d:\Zaalima Intern Project 2\backend\datasets" --epochs 20
```

**Evaluate the Model (Generate Charts & Reports):**
```powershell
python backend/scripts/evaluate_model.py
```
