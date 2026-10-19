// Rectify photographed waveform grids without altering their recorded traces.
for (const photo of document.querySelectorAll('img[data-waveform-corners]')) {
  const rectify = () => {
    if (!photo.naturalWidth || photo.dataset.rectified) return;
    photo.dataset.rectified = 'true';
    const points = photo.dataset.waveformCorners.split(',').map(Number);
    const target = [[0, 0], [1, 0], [1, 1], [0, 1]];
    const rows = [];
    target.forEach(([u, v], i) => {
      const x = points[2 * i], y = points[2 * i + 1];
      rows.push([u, v, 1, 0, 0, 0, -u * x, -v * x, x]);
      rows.push([0, 0, 0, u, v, 1, -u * y, -v * y, y]);
    });
    // Solve the inverse projective map from a rectangle to the screen corners.
    for (let col = 0; col < 8; col++) {
      let pivot = col;
      for (let r = col + 1; r < 8; r++) {
        if (Math.abs(rows[r][col]) > Math.abs(rows[pivot][col])) pivot = r;
      }
      [rows[col], rows[pivot]] = [rows[pivot], rows[col]];
      const divisor = rows[col][col];
      for (let k = col; k < 9; k++) rows[col][k] /= divisor;
      for (let r = 0; r < 8; r++) {
        if (r === col) continue;
        const factor = rows[r][col];
        for (let k = col; k < 9; k++) rows[r][k] -= factor * rows[col][k];
      }
    }
    const h = rows.map(row => row[8]);
    const source = document.createElement('canvas');
    source.width = photo.naturalWidth;
    source.height = photo.naturalHeight;
    const context = source.getContext('2d', { willReadFrequently: true });
    context.drawImage(photo, 0, 0);
    const pixels = context.getImageData(0, 0, source.width, source.height).data;
    const output = document.createElement('canvas');
    output.width = 1200;
    output.height = 750;
    const outContext = output.getContext('2d');
    const result = outContext.createImageData(output.width, output.height);
    for (let y = 0; y < output.height; y++) {
      for (let x = 0; x < output.width; x++) {
        const u = x / (output.width - 1), v = y / (output.height - 1);
        const divisor = h[6] * u + h[7] * v + 1;
        const sx = Math.max(0, Math.min(source.width - 2, (h[0] * u + h[1] * v + h[2]) / divisor * source.width));
        const sy = Math.max(0, Math.min(source.height - 2, (h[3] * u + h[4] * v + h[5]) / divisor * source.height));
        const ix = Math.floor(sx), iy = Math.floor(sy), dx = sx - ix, dy = sy - iy;
        const offset = (y * output.width + x) * 4;
        for (let channel = 0; channel < 3; channel++) {
          const at = (px, py) => pixels[(py * source.width + px) * 4 + channel];
          result.data[offset + channel] = (1 - dy) * ((1 - dx) * at(ix, iy) + dx * at(ix + 1, iy))
            + dy * ((1 - dx) * at(ix, iy + 1) + dx * at(ix + 1, iy + 1));
        }
        result.data[offset + 3] = 255;
      }
    }
    outContext.putImageData(result, 0, 0);
    photo.width = output.width;
    photo.height = output.height;
    photo.src = output.toDataURL('image/png');
    photo.removeAttribute('srcset');
  };
  photo.addEventListener('load', rectify, { once: true });
  if (photo.complete) rectify();
}
