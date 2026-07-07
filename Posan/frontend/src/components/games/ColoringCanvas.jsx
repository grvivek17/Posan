import { useState, useRef, useEffect, useCallback } from 'react';
import './ColoringCanvas.css';

const PASTEL_COLORS = [
  { id: 'pink', color: '#FFB3BA', label: 'Pink' },
  { id: 'peach', color: '#FFDFBA', label: 'Peach' },
  { id: 'yellow', color: '#FFFFBA', label: 'Yellow' },
  { id: 'mint', color: '#BAFFC9', label: 'Mint' },
  { id: 'sky', color: '#BAE1FF', label: 'Sky' },
  { id: 'lavender', color: '#E8BAFF', label: 'Lavender' },
  { id: 'rose', color: '#FFC4E1', label: 'Rose' },
  { id: 'aqua', color: '#C4F0FF', label: 'Aqua' },
  { id: 'coral', color: '#FFB5A7', label: 'Coral' },
  { id: 'lilac', color: '#D4BAFF', label: 'Lilac' },
  { id: 'white', color: '#FFFFFF', label: 'White' },
  { id: 'cream', color: '#FFF8E7', label: 'Cream' },
];

const BRUSH_SIZES = [
  { id: 'small', size: 6, label: 'Small' },
  { id: 'medium', size: 14, label: 'Medium' },
  { id: 'large', size: 24, label: 'Large' },
  { id: 'xlarge', size: 40, label: 'Extra Large' },
];

const STAMPS = [
  '', '', '', '', '', '', '', '', '', '', '', '',
];

const ColoringCanvas = () => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentColor, setCurrentColor] = useState(PASTEL_COLORS[0].color);
  const [brushSize, setBrushSize] = useState(BRUSH_SIZES[1].size);
  const [tool, setTool] = useState('brush');
  const [selectedStamp, setSelectedStamp] = useState(STAMPS[0]);
  const [sparkleCount, setSparkleCount] = useState(0);
  const [showSparkle, setShowSparkle] = useState(null);
  const lastPos = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    canvas.width = canvas.offsetWidth * 2;
    canvas.height = canvas.offsetHeight * 2;
    const ctx = canvas.getContext('2d');
    ctx.scale(2, 2);
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
  }, []);

  const getPosition = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const touch = e.touches ? e.touches[0] : e;
    return {
      x: touch.clientX - rect.left,
      y: touch.clientY - rect.top,
    };
  };

  const drawLine = useCallback((from, to) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.strokeStyle = tool === 'eraser' ? '#FFFFFF' : currentColor;
    ctx.lineWidth = tool === 'eraser' ? brushSize * 2 : brushSize;
    ctx.globalAlpha = tool === 'eraser' ? 1 : 0.7;
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
    ctx.globalAlpha = 1;
  }, [currentColor, brushSize, tool]);

  const drawStamp = useCallback((pos) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const size = 24 + brushSize;
    ctx.font = `${size}px serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(selectedStamp, pos.x, pos.y);
  }, [selectedStamp, brushSize]);

  const startDrawing = (e) => {
    e.preventDefault();
    const pos = getPosition(e);
    setIsDrawing(true);
    lastPos.current = pos;

    if (tool === 'stamp') {
      drawStamp(pos);
      triggerSparkle(pos);
    }
  };

  const draw = (e) => {
    e.preventDefault();
    if (!isDrawing) return;
    const pos = getPosition(e);
    if (tool === 'brush' || tool === 'eraser') {
      if (lastPos.current) {
        drawLine(lastPos.current, pos);
      }
    }
    lastPos.current = pos;
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    lastPos.current = null;
  };

  const triggerSparkle = (pos) => {
    const count = sparkleCount + 1;
    setSparkleCount(count);
    if (count % 5 === 0) {
      setShowSparkle({ x: pos.x, y: pos.y });
      setTimeout(() => setShowSparkle(null), 800);
    }
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);
  };

  return (
    <div className="coloring-canvas-game">
      <div className="cc-header">
        <h2>Coloring Canvas</h2>
        <p className="cc-hint">Draw, stamp, and create something beautiful!</p>
      </div>

      <div className="cc-tools-bar">
        <div className="cc-tool-group">
          <button
            className={`cc-tool-btn ${tool === 'brush' ? 'active' : ''}`}
            onClick={() => setTool('brush')}
            title="Brush"
          >
            
          </button>
          <button
            className={`cc-tool-btn ${tool === 'stamp' ? 'active' : ''}`}
            onClick={() => setTool('stamp')}
            title="Stamps"
          >
            
          </button>
          <button
            className={`cc-tool-btn ${tool === 'eraser' ? 'active' : ''}`}
            onClick={() => setTool('eraser')}
            title="Eraser"
          >
            
          </button>
        </div>

        <div className="cc-size-group">
          {BRUSH_SIZES.map(b => (
            <button
              key={b.id}
              className={`cc-size-btn ${brushSize === b.size ? 'active' : ''}`}
              onClick={() => setBrushSize(b.size)}
              title={b.label}
            >
              <div className="cc-size-dot" style={{ width: b.size * 0.7, height: b.size * 0.7 }} />
            </button>
          ))}
        </div>

        <button className="cc-clear-btn" onClick={clearCanvas}>New Page</button>
      </div>

      {tool === 'stamp' && (
        <div className="cc-stamps-row">
          {STAMPS.map((stamp, i) => (
            <button
              key={i}
              className={`cc-stamp-btn ${selectedStamp === stamp ? 'active' : ''}`}
              onClick={() => setSelectedStamp(stamp)}
            >
              {stamp}
            </button>
          ))}
        </div>
      )}

      <div className="cc-canvas-wrapper">
        <canvas
          ref={canvasRef}
          className="cc-canvas"
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />
        {showSparkle && (
          <div
            className="cc-sparkle-burst"
            style={{ left: showSparkle.x, top: showSparkle.y }}
          >
            
          </div>
        )}
      </div>

      <div className="cc-colors-row">
        {PASTEL_COLORS.map(c => (
          <button
            key={c.id}
            className={`cc-color-btn ${currentColor === c.color ? 'active' : ''}`}
            style={{ background: c.color }}
            onClick={() => { setCurrentColor(c.color); setTool('brush'); }}
            title={c.label}
          />
        ))}
      </div>
    </div>
  );
};

export default ColoringCanvas;
