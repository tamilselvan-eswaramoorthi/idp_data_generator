let pdfDoc = null;
let pageNum = 1;
let canvas = null;
let context = null;
let selectedRect = null;
const drawnRectangles = [];
let isResizing = false;
let isMoving = false;
let resizeHandleSize = 8;
let startX, startY;

document.getElementById('upload').addEventListener('change', handleFileSelect, false);

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
        const reader = new FileReader();
        reader.onload = function(e) {
            const pdfData = new Uint8Array(e.target.result);
            pdfjsLib.getDocument(pdfData).promise.then(function(pdfDoc_) {
                pdfDoc = pdfDoc_;
                return pdfDoc.getPage(pageNum);
              }).then(function(page) {
                const scale = 1.5;
                const viewport = page.getViewport({ scale: scale });
              
                // Prepare canvas using PDF page dimensions
                canvas = document.createElement('canvas');
                context = canvas.getContext('2d');
                canvas.width = viewport.width;
                canvas.height = viewport.height;
                document.getElementById('pdf-container').appendChild(canvas);
              
                // Render the PDF page into the canvas context
                return page.render({ canvasContext: context, viewport: viewport }).promise;
              }).then(function() {
                // Add event listeners for drawing
                addDrawingListeners(canvas, context);
                addDeleteButtonListener();
                addDeleteAllButtonListener();
                addDownloadButtonListener();
              });
        };
        reader.readAsArrayBuffer(file);
    }
}

function addDrawingListeners(canvas, context) {
  const overlayCanvas = document.createElement('canvas');
  overlayCanvas.width = canvas.width;
  overlayCanvas.height = canvas.height;
  overlayCanvas.style.position = 'absolute';
  overlayCanvas.style.top = canvas.offsetTop + 'px';
  overlayCanvas.style.left = canvas.offsetLeft + 'px';
  overlayCanvas.style.pointerEvents = 'none';
  document.getElementById('pdf-container').appendChild(overlayCanvas);
  const overlayContext = overlayCanvas.getContext('2d');

  canvas.addEventListener('mousedown', function(e) {
    const [x, y] = getMousePos(canvas, e);
    selectedRect = getRectangleAt(x, y);
    if (selectedRect) {
      const handle = getResizeHandleAt(x, y, selectedRect);
      if (handle) {
        isResizing = true;
        document.getElementById('delete-button').disabled = false;
        startX = x;
        startY = y;
        return;
      }
      isMoving = true;
      document.getElementById('delete-button').disabled = false;
      startX = x - selectedRect.x;
      startY = y - selectedRect.y;
    } else {
      isDrawing = true;
      [startX, startY] = getMousePos(canvas, e);
    }
  });

  canvas.addEventListener('mousemove', function(e) {
    const [x, y] = getMousePos(canvas, e);
    if (isDrawing) {
      overlayContext.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
      redrawRectangles(overlayContext, drawnRectangles);
      drawRectangle(overlayContext, startX, startY, x - startX, y - startY);
    } else if (isMoving && selectedRect) {
      selectedRect.x = x - startX;
      selectedRect.y = y - startY;
      overlayContext.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
      redrawRectangles(overlayContext, drawnRectangles);
    } else if (isResizing && selectedRect) {
      selectedRect.width = x - selectedRect.x;
      selectedRect.height = y - selectedRect.y;
      overlayContext.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
      redrawRectangles(overlayContext, drawnRectangles);
    }
  });

  canvas.addEventListener('mouseup', function(e) {
    if (isDrawing) {
      isDrawing = false;
      const [x, y] = getMousePos(canvas, e);
      drawnRectangles.push({ x: startX, y: startY, width: x - startX, height: y - startY });
      overlayContext.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
      redrawRectangles(overlayContext, drawnRectangles);
      document.getElementById('delete-all-button').disabled = false;
      document.getElementById('download-button').disabled = false;
    } else if (isMoving) {
      isMoving = false;
    } else if (isResizing) {
      isResizing = false;
    }
  });

  canvas.addEventListener('mouseout', function(e) {
    if (isDrawing) {
      isDrawing = false;
      overlayContext.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
      redrawRectangles(overlayContext, drawnRectangles);
    } else if (isMoving) {
      isMoving = false;
    } else if (isResizing) {
      isResizing = false;
    }
  });
}

function getMousePos(canvas, event) {
  const rect = canvas.getBoundingClientRect();
  return [
    event.clientX - rect.left,
    event.clientY - rect.top
  ];
}

function drawRectangle(context, x, y, width, height) {
  context.fillStyle = 'rgba(0, 0, 255, 0.3)'; 
  context.fillRect(x, y, width, height);
  context.strokeStyle = 'blue';
  context.lineWidth = 2;
  context.beginPath();
  context.rect(x, y, width, height);
  context.stroke();

  // Draw resize handle
  drawResizeHandle(context, x + width - resizeHandleSize / 2, y + height - resizeHandleSize / 2);
}

function drawResizeHandle(context, x, y) {
  context.fillStyle = 'red';
  context.fillRect(x, y, resizeHandleSize, resizeHandleSize);
}

function redrawRectangles(context, rectangles) {
  rectangles.forEach(rect => {
    drawRectangle(context, rect.x, rect.y, rect.width, rect.height);
  });
}

function getRectangleAt(x, y) {
  for (const rect of drawnRectangles) {
    if (x >= rect.x && x <= rect.x + rect.width && y >= rect.y && y <= rect.y + rect.height) {
      return rect;
    }
  }
  return null;
}

function getResizeHandleAt(x, y, rect) {
  const handleX = rect.x + rect.width - resizeHandleSize / 2;
  const handleY = rect.y + rect.height - resizeHandleSize / 2;
  if (x >= handleX && x <= handleX + resizeHandleSize && y >= handleY && y <= handleY + resizeHandleSize) {
    return { x: handleX, y: handleY };
  }
  return null;
}

function addDeleteButtonListener() {
  const deleteButton = document.getElementById('delete-button');
  deleteButton.addEventListener('click', function() {
    if (selectedRect) {
      const index = drawnRectangles.indexOf(selectedRect);
      if (index > -1) {
        drawnRectangles.splice(index, 1);
        selectedRect = null;
        deleteButton.disabled = true;

        // Clear and redraw the rectangles
        const overlayCanvas = document.querySelector('canvas:last-of-type');
        const overlayContext = overlayCanvas.getContext('2d');
        overlayContext.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
        redrawRectangles(overlayContext, drawnRectangles);
        if (drawnRectangles.length === 0) {
          document.getElementById('delete-all-button').disabled = true;
          document.getElementById('download-button').disabled = true;
        }
      }
    }
  });
}

function addDeleteAllButtonListener() {
  const deleteAllButton = document.getElementById('delete-all-button');
  deleteAllButton.addEventListener('click', function() {
    drawnRectangles.length = 0;
    selectedRect = null;
    deleteAllButton.disabled = true;
    document.getElementById('delete-button').disabled = true;
    document.getElementById('download-button').disabled = true;

    // Clear and redraw the rectangles
    const overlayCanvas = document.querySelector('canvas:last-of-type');
    const overlayContext = overlayCanvas.getContext('2d');
    overlayContext.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
  });
}

function addDownloadButtonListener() {
  const downloadButton = document.getElementById('download-button');
  downloadButton.addEventListener('click', function() {
    const data = JSON.stringify(drawnRectangles, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rectangles.json';
    a.click();
    URL.revokeObjectURL(url);
  });
}

function highlightRectangle(context, rect) {
  context.fillStyle = 'rgba(255, 255, 0, 0.3)'; // Yellow fill with transparency
  context.fillRect(rect.x, rect.y, rect.width, rect.height);
  context.strokeStyle = 'red';
  context.lineWidth = 2;
  context.strokeRect(rect.x, rect.y, rect.width, rect.height);
}
