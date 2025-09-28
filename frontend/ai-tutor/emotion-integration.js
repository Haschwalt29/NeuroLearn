export function createEmotionCapture({ intervalMs = 7000, getToken, getOptIn }) {
  let timer = null;
  const video = document.createElement('video');
  video.autoplay = true;
  video.playsInline = true;
  const canvas = document.createElement('canvas');

  async function start() {
    if (timer) return;
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
    // Wait for video to be ready
    await new Promise((res) => (video.onloadedmetadata = () => res()));
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    timer = setInterval(captureAndSend, intervalMs);
  }

  function stop() {
    if (timer) clearInterval(timer);
    timer = null;
    const stream = video.srcObject;
    if (stream) stream.getTracks().forEach((t) => t.stop());
  }

  async function captureAndSend() {
    if (typeof getOptIn === 'function' && !getOptIn()) return;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
    const headers = { 'Content-Type': 'application/json' };
    const token = typeof getToken === 'function' ? getToken() : null;
    if (token) headers['Authorization'] = `Bearer ${token}`;
    try {
      const resp = await fetch('/api/emotion', {
        method: 'POST',
        headers,
        body: JSON.stringify({ image: dataUrl })
      });
      // Optionally handle response
      await resp.json().catch(() => ({}));
    } catch (e) {
      // swallow errors; it's background
    }
  }

  return { start, stop };
}


