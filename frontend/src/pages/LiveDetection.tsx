/**
 * VisionSpec QC — Live Detection Page (Phase 3)
 * Real-time PCB inspection via webcam feed with AI inference.
 * Captures frames from the user's camera, sends them to the backend,
 * and displays predictions with FPS monitoring.
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import {
  Video,
  VideoOff,
  Play,
  Square,
  Zap,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Camera,
  Activity,
  TrendingUp,
} from 'lucide-react';
import { predictWebcamFrame } from '../services/api';

interface LiveResult {
  predicted_label: string;
  confidence: number;
  inference_time_ms: number;
  fps: number;
  heatmap_base64: string | null;
}

export default function LiveDetection() {
  // ── State ───────────────────────────────────────────────
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [currentResult, setCurrentResult] = useState<LiveResult | null>(null);
  const [totalFrames, setTotalFrames] = useState(0);
  const [defectsFound, setDefectsFound] = useState(0);
  const [sessionHistory, setSessionHistory] = useState<Array<LiveResult & { timestamp: Date }>>([]);

  // ── Refs ────────────────────────────────────────────────
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const detectionLoopRef = useRef<number | null>(null);
  const isDetectingRef = useRef(false);

  // Keep ref in sync with state
  useEffect(() => {
    isDetectingRef.current = isDetecting;
  }, [isDetecting]);

  // ── Camera Control ──────────────────────────────────────
  const startCamera = useCallback(async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'environment', // prefer rear camera on mobile
        },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setIsCameraOn(true);
    } catch (err: any) {
      console.error('Camera access error:', err);
      if (err.name === 'NotAllowedError') {
        setCameraError('Camera permission denied. Please allow camera access in your browser settings.');
      } else if (err.name === 'NotFoundError') {
        setCameraError('No camera found. Please connect a webcam and try again.');
      } else {
        setCameraError(`Camera error: ${err.message}`);
      }
    }
  }, []);

  const stopCamera = useCallback(() => {
    // Stop detection first
    if (isDetecting) {
      stopDetection();
    }
    // Release camera stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraOn(false);
  }, [isDetecting]);

  // ── Frame Capture ───────────────────────────────────────
  const captureFrame = useCallback((): Blob | null => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return null;

    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to blob synchronously using toDataURL
    const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
    const byteString = atob(dataUrl.split(',')[1]);
    const mimeString = dataUrl.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
  }, []);

  // ── Detection Loop ──────────────────────────────────────
  const runDetectionLoop = useCallback(async () => {
    if (!isDetectingRef.current) return;

    const frameBlob = captureFrame();
    if (!frameBlob) {
      // Retry after a short delay
      detectionLoopRef.current = window.setTimeout(runDetectionLoop, 100);
      return;
    }

    try {
      const response = await predictWebcamFrame(frameBlob);
      const result: LiveResult = response.data;

      if (isDetectingRef.current) {
        setCurrentResult(result);
        setTotalFrames((prev) => prev + 1);
        if (result.predicted_label === 'Defect') {
          setDefectsFound((prev) => prev + 1);
        }

        // Keep last 10 results in session history
        setSessionHistory((prev) => [
          { ...result, timestamp: new Date() },
          ...prev.slice(0, 9),
        ]);
      }
    } catch (err: any) {
      console.error('Detection error:', err);
      if (isDetectingRef.current) {
        setCurrentResult({
          predicted_label: 'Error',
          confidence: 0,
          inference_time_ms: 0,
          fps: 0,
          heatmap_base64: null,
        });
      }
    }

    // Schedule next frame (throttled to ~5-10 FPS for REST API)
    if (isDetectingRef.current) {
      detectionLoopRef.current = window.setTimeout(runDetectionLoop, 200);
    }
  }, [captureFrame]);

  const startDetection = useCallback(() => {
    setIsDetecting(true);
    isDetectingRef.current = true;
    setTotalFrames(0);
    setDefectsFound(0);
    setSessionHistory([]);
    // Small delay to let state update
    setTimeout(runDetectionLoop, 100);
  }, [runDetectionLoop]);

  const stopDetection = useCallback(() => {
    setIsDetecting(false);
    isDetectingRef.current = false;
    if (detectionLoopRef.current) {
      clearTimeout(detectionLoopRef.current);
      detectionLoopRef.current = null;
    }
  }, []);

  // ── Cleanup on unmount ──────────────────────────────────
  useEffect(() => {
    return () => {
      if (detectionLoopRef.current) {
        clearTimeout(detectionLoopRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // ── Confidence color helper ──────────────────────────────
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'var(--color-success)';
    if (confidence >= 0.7) return 'var(--color-warning)';
    return 'var(--color-danger)';
  };

  return (
    <div>
      <div className="page-header">
        <h2>Live Detection</h2>
        <p>Real-time PCB inspection via webcam feed with AI inference</p>
      </div>

      {/* Stats Bar */}
      <div className="stats-grid" style={{ marginBottom: '20px' }}>
        <div className="stat-card">
          <div className="stat-icon primary"><Camera size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{isCameraOn ? 'Active' : 'Off'}</div>
            <div className="stat-label">Camera Status</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon info"><Zap size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">
              {currentResult ? `${currentResult.fps} FPS` : '— FPS'}
            </div>
            <div className="stat-label">Processing Speed</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon success"><Activity size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{totalFrames}</div>
            <div className="stat-label">Frames Analyzed</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon danger"><TrendingUp size={22} /></div>
          <div className="stat-content">
            <div className="stat-value">{defectsFound}</div>
            <div className="stat-label">Defects Found</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        {/* ── LEFT: Camera Feed ───────────────────────────── */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Webcam Feed</span>
            <div style={{ display: 'flex', gap: '8px' }}>
              {!isCameraOn ? (
                <button className="btn btn-primary btn-sm" onClick={startCamera} id="start-camera-btn">
                  <Video size={14} />
                  <span>Start Camera</span>
                </button>
              ) : (
                <>
                  {!isDetecting ? (
                    <button className="btn btn-success btn-sm" onClick={startDetection} id="start-detection-btn">
                      <Play size={14} />
                      <span>Start Detection</span>
                    </button>
                  ) : (
                    <button className="btn btn-danger btn-sm" onClick={stopDetection} id="stop-detection-btn">
                      <Square size={14} />
                      <span>Stop</span>
                    </button>
                  )}
                  <button className="btn btn-outline btn-sm" onClick={stopCamera} id="stop-camera-btn">
                    <VideoOff size={14} />
                    <span>Off</span>
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Camera Error */}
          {cameraError && (
            <div className="result-error" style={{ marginBottom: '16px' }}>
              <AlertTriangle size={18} />
              <div>
                <strong>Camera Error</strong>
                <p>{cameraError}</p>
              </div>
            </div>
          )}

          {/* Video Container */}
          <div className="webcam-container" id="webcam-feed">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              style={{ display: isCameraOn ? 'block' : 'none' }}
            />
            {/* Hidden canvas for frame capture */}
            <canvas ref={canvasRef} style={{ display: 'none' }} />

            {/* Overlays */}
            {isCameraOn && (
              <div className="webcam-overlay">
                {isDetecting && <span className="webcam-badge live">● LIVE</span>}
                {currentResult && isDetecting && (
                  <span className="webcam-badge">
                    {currentResult.inference_time_ms}ms
                  </span>
                )}
              </div>
            )}

            {/* Loading overlay during detection */}
            {isDetecting && !currentResult && (
              <div className="loading-overlay">
                <div className="spinner" />
                <p>Initializing AI detection...</p>
              </div>
            )}

            {/* Camera off placeholder */}
            {!isCameraOn && !cameraError && (
              <div className="webcam-placeholder">
                <Camera size={48} />
                <h3>Camera Not Active</h3>
                <p>Click "Start Camera" to begin real-time PCB inspection</p>
              </div>
            )}
          </div>
        </div>

        {/* ── RIGHT: Results Panel ───────────────────────── */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Live Results</span>
            {currentResult && isDetecting && (
              <span
                className={`badge ${currentResult.predicted_label === 'Pass' ? 'badge-pass' : 'badge-defect'}`}
              >
                {currentResult.predicted_label}
              </span>
            )}
          </div>

          {/* No Detection State */}
          {!isDetecting && !currentResult && (
            <div className="result-empty">
              <Video size={40} />
              <p>Start the camera and detection to see live results</p>
              <span>AI will analyze each frame in real-time</span>
            </div>
          )}

          {/* Active Detection Result */}
          {currentResult && (
            <div className="result-display">
              {/* Verdict */}
              <div
                className={`verdict-card ${currentResult.predicted_label === 'Pass' ? 'verdict-pass' : currentResult.predicted_label === 'Defect' ? 'verdict-defect' : ''}`}
              >
                <div className="verdict-icon">
                  {currentResult.predicted_label === 'Pass' ? (
                    <CheckCircle2 size={36} />
                  ) : currentResult.predicted_label === 'Defect' ? (
                    <XCircle size={36} />
                  ) : (
                    <AlertTriangle size={36} />
                  )}
                </div>
                <div className="verdict-info">
                  <h3>
                    {currentResult.predicted_label === 'Pass'
                      ? 'PCB Passed'
                      : currentResult.predicted_label === 'Defect'
                      ? 'Defect Detected!'
                      : 'Detection Error'}
                  </h3>
                  <p>
                    Confidence: {(currentResult.confidence * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Confidence Bar */}
              <div className="confidence-bar-container">
                <div className="confidence-label">
                  <span style={{ color: 'var(--text-secondary)' }}>Confidence</span>
                  <span style={{ color: getConfidenceColor(currentResult.confidence), fontWeight: 700 }}>
                    {(currentResult.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{
                      width: `${currentResult.confidence * 100}%`,
                      background:
                        currentResult.predicted_label === 'Pass'
                          ? 'linear-gradient(90deg, #22c55e, #16a34a)'
                          : 'linear-gradient(90deg, #ef4444, #dc2626)',
                      transition: 'width 0.2s ease',
                    }}
                  />
                </div>
              </div>

              {/* Live Metrics */}
              <div className="result-meta-grid" style={{ marginTop: '16px' }}>
                <div className="result-meta-item">
                  <Zap size={14} />
                  <span className="meta-label">FPS</span>
                  <span className="meta-value">{currentResult.fps}</span>
                </div>
                <div className="result-meta-item">
                  <Clock size={14} />
                  <span className="meta-label">Latency</span>
                  <span className="meta-value">{currentResult.inference_time_ms}ms</span>
                </div>
                <div className="result-meta-item">
                  <Activity size={14} />
                  <span className="meta-label">Frames</span>
                  <span className="meta-value">{totalFrames}</span>
                </div>
              </div>

              {/* Heatmap for defects */}
              {currentResult.heatmap_base64 && (
                <div className="gradcam-section" style={{ marginTop: '16px' }}>
                  <div className="gradcam-header">
                    <span className="gradcam-title">🔬 Grad-CAM</span>
                    <span className="gradcam-subtitle">Defect region highlight</span>
                  </div>
                  <div className="heatmap-display">
                    <img
                      src={`data:image/png;base64,${currentResult.heatmap_base64}`}
                      alt="Grad-CAM Heatmap"
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Session Stopped Results */}
          {!isDetecting && currentResult && (
            <div style={{ marginTop: '16px', textAlign: 'center' }}>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Detection stopped. {totalFrames} frames analyzed, {defectsFound} defects found.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* ── Session Log ──────────────────────────────────── */}
      {sessionHistory.length > 0 && (
        <div className="card" style={{ marginTop: '24px' }}>
          <div className="card-header">
            <span className="card-title">Detection Log</span>
            <span className="card-subtitle">Last {sessionHistory.length} results</span>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Result</th>
                  <th>Confidence</th>
                  <th>Latency</th>
                  <th>FPS</th>
                </tr>
              </thead>
              <tbody>
                {sessionHistory.map((r, i) => (
                  <tr key={i}>
                    <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                      {r.timestamp.toLocaleTimeString()}
                    </td>
                    <td>
                      <span className={`badge ${r.predicted_label === 'Pass' ? 'badge-pass' : 'badge-defect'}`}>
                        {r.predicted_label}
                      </span>
                    </td>
                    <td style={{ color: getConfidenceColor(r.confidence), fontWeight: 600 }}>
                      {(r.confidence * 100).toFixed(1)}%
                    </td>
                    <td>{r.inference_time_ms}ms</td>
                    <td>{r.fps} FPS</td>
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
