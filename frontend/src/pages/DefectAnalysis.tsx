/**
 * VisionSpec QC — Defect Analysis Page (Phase 2)
 * Upload a PCB image → AI predicts Pass/Defect with confidence score.
 * Includes drag-and-drop, image preview, result display, and history sidebar.
 */

import { useState, useRef, useCallback } from 'react';
import {
  Upload,
  CheckCircle2,
  XCircle,
  Loader2,
  ImagePlus,
  Trash2,
  Clock,
  Maximize2,
  AlertTriangle,
  RefreshCw,
} from 'lucide-react';
import { predictImage } from '../services/api';

interface PredictionResult {
  predicted_label: string;
  confidence: number;
  heatmap_base64: string | null;
  inference_time_ms: number;
  image_size: string | null;
}

export default function DefectAnalysis() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [recentResults, setRecentResults] = useState<Array<PredictionResult & { filename: string; timestamp: Date }>>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── File Selection Handlers ──────────────────────────────
  const handleFileSelect = useCallback((file: File) => {
    // Validate type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff'];
    if (!allowedTypes.includes(file.type)) {
      setError('Unsupported file type. Please upload JPG, PNG, BMP, or TIFF.');
      return;
    }

    // Validate size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File is too large. Maximum size is 10MB.');
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  // ── Drag & Drop ──────────────────────────────────────────
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  // ── Run Prediction ───────────────────────────────────────
  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await predictImage(formData);
      const prediction: PredictionResult = response.data;
      setResult(prediction);

      // Add to recent results
      setRecentResults((prev) => [
        { ...prediction, filename: selectedFile.name, timestamp: new Date() },
        ...prev.slice(0, 4), // Keep last 5
      ]);
    } catch (err: any) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        'Failed to analyze image. Is the backend running?';
      setError(message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // ── Clear / Reset ────────────────────────────────────────
  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // ── Confidence color helper ──────────────────────────────
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'var(--color-success)';
    if (confidence >= 0.7) return 'var(--color-warning)';
    return 'var(--color-danger)';
  };

  return (
    <div>
      <div className="page-header">
        <h2>Defect Analysis</h2>
        <p>Upload a PCB image for AI-powered defect inspection</p>
      </div>

      <div className="grid-2">
        {/* ── LEFT: Upload Panel ─────────────────────────── */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Upload PCB Image</span>
            {selectedFile && (
              <button className="btn btn-outline btn-sm" onClick={handleClear} id="clear-image-btn">
                <Trash2 size={14} />
                <span>Clear</span>
              </button>
            )}
          </div>

          {/* Hidden file input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleInputChange}
            accept="image/jpeg,image/png,image/bmp,image/tiff"
            style={{ display: 'none' }}
            id="file-upload-input"
          />

          {!selectedFile ? (
            /* Upload Zone */
            <div
              className={`upload-zone ${isDragging ? 'upload-zone-active' : ''}`}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              id="upload-drop-zone"
            >
              <ImagePlus size={48} />
              <h3>Drag & drop or click to upload</h3>
              <p>Supports JPG, PNG, BMP — Max 10MB</p>
            </div>
          ) : (
            /* Image Preview */
            <div className="image-preview-container" id="image-preview">
              <img src={previewUrl!} alt="PCB Preview" className="image-preview" />
              <div className="image-preview-info">
                <span className="image-filename">{selectedFile.name}</span>
                <span className="image-filesize">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </span>
              </div>
            </div>
          )}

          {/* Analyze Button */}
          {selectedFile && (
            <div style={{ marginTop: '16px' }}>
              <button
                className={`btn btn-primary btn-full ${isAnalyzing ? 'btn-loading' : ''}`}
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                id="analyze-btn"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 size={16} className="spin-icon" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Upload size={16} />
                    <span>Analyze Image</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* ── RIGHT: Result Panel ────────────────────────── */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Analysis Result</span>
            {result && (
              <span
                className={`badge ${result.predicted_label === 'Pass' ? 'badge-pass' : 'badge-defect'}`}
              >
                {result.predicted_label}
              </span>
            )}
          </div>

          {/* Error State */}
          {error && (
            <div className="result-error" id="prediction-error">
              <AlertTriangle size={20} />
              <div>
                <strong>Analysis Failed</strong>
                <p>{error}</p>
              </div>
            </div>
          )}

          {/* Loading State */}
          {isAnalyzing && (
            <div className="result-loading" id="prediction-loading">
              <div className="spinner" />
              <p>Running AI inference...</p>
              <span className="result-loading-sub">Processing image through MobileNetV2</span>
            </div>
          )}

          {/* Empty State */}
          {!result && !isAnalyzing && !error && (
            <div className="result-empty" id="result-placeholder">
              <Upload size={40} />
              <p>Upload an image to see AI analysis results</p>
              <span>The model will classify the PCB as Pass or Defect</span>
            </div>
          )}

          {/* Result Display */}
          {result && !isAnalyzing && (
            <div className="result-display" id="prediction-result">
              {/* Main Verdict */}
              <div
                className={`verdict-card ${result.predicted_label === 'Pass' ? 'verdict-pass' : 'verdict-defect'}`}
              >
                <div className="verdict-icon">
                  {result.predicted_label === 'Pass' ? (
                    <CheckCircle2 size={40} />
                  ) : (
                    <XCircle size={40} />
                  )}
                </div>
                <div className="verdict-info">
                  <h3>{result.predicted_label === 'Pass' ? 'PCB Passed' : 'Defect Detected'}</h3>
                  <p>
                    {result.predicted_label === 'Pass'
                      ? 'No defects found in this PCB image.'
                      : 'Potential defect identified in this PCB image.'}
                  </p>
                </div>
              </div>

              {/* Confidence Bar */}
              <div className="confidence-section">
                <div className="confidence-bar-container">
                  <div className="confidence-label">
                    <span style={{ color: 'var(--text-secondary)' }}>Confidence</span>
                    <span style={{ color: getConfidenceColor(result.confidence), fontWeight: 700 }}>
                      {(result.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${result.confidence * 100}%`,
                        background:
                          result.predicted_label === 'Pass'
                            ? 'linear-gradient(90deg, #22c55e, #16a34a)'
                            : 'linear-gradient(90deg, #ef4444, #dc2626)',
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Metadata Grid */}
              <div className="result-meta-grid">
                <div className="result-meta-item">
                  <Clock size={14} />
                  <span className="meta-label">Inference Time</span>
                  <span className="meta-value">{result.inference_time_ms} ms</span>
                </div>
                {result.image_size && (
                  <div className="result-meta-item">
                    <Maximize2 size={14} />
                    <span className="meta-label">Image Size</span>
                    <span className="meta-value">{result.image_size}</span>
                  </div>
                )}
                <div className="result-meta-item">
                  <RefreshCw size={14} />
                  <span className="meta-label">Model</span>
                  <span className="meta-value">MobileNetV2</span>
                </div>
              </div>

              {/* Grad-CAM Heatmap Display */}
              {result.heatmap_base64 ? (
                <div className="gradcam-section" id="gradcam-display">
                  <div className="gradcam-header">
                    <span className="gradcam-title">🔬 Grad-CAM Visualization</span>
                    <span className="gradcam-subtitle">AI attention heatmap overlay</span>
                  </div>
                  <div className="gradcam-grid">
                    <div className="gradcam-panel">
                      <div className="gradcam-label">Original</div>
                      <div className="heatmap-display">
                        {previewUrl && <img src={previewUrl} alt="Original PCB" />}
                      </div>
                    </div>
                    <div className="gradcam-panel">
                      <div className="gradcam-label">Grad-CAM Heatmap</div>
                      <div className="heatmap-display">
                        <img
                          src={`data:image/png;base64,${result.heatmap_base64}`}
                          alt="Grad-CAM Heatmap"
                        />
                      </div>
                    </div>
                  </div>
                  <p className="gradcam-description">
                    Warm colors (red/yellow) indicate regions the AI focused on for its decision.
                  </p>
                </div>
              ) : (
                <div className="heatmap-placeholder">
                  <span>Grad-CAM heatmap not available for this prediction</span>
                </div>
              )}

              {/* Re-analyze button */}
              <button
                className="btn btn-outline btn-full"
                onClick={() => fileInputRef.current?.click()}
                style={{ marginTop: '12px' }}
                id="upload-another-btn"
              >
                <ImagePlus size={14} />
                <span>Upload Another Image</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* ── Recent Analyses ─────────────────────────────── */}
      {recentResults.length > 0 && (
        <div className="card" style={{ marginTop: '24px' }}>
          <div className="card-header">
            <span className="card-title">Recent Analyses</span>
            <span className="card-subtitle">Session history</span>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>File</th>
                  <th>Result</th>
                  <th>Confidence</th>
                  <th>Inference</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {recentResults.map((r, i) => (
                  <tr key={i}>
                    <td style={{ maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {r.filename}
                    </td>
                    <td>
                      <span className={`badge ${r.predicted_label === 'Pass' ? 'badge-pass' : 'badge-defect'}`}>
                        {r.predicted_label}
                      </span>
                    </td>
                    <td style={{ color: getConfidenceColor(r.confidence), fontWeight: 600 }}>
                      {(r.confidence * 100).toFixed(1)}%
                    </td>
                    <td>{r.inference_time_ms} ms</td>
                    <td style={{ color: 'var(--text-muted)' }}>
                      {r.timestamp.toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
