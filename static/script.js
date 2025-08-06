document.addEventListener('DOMContentLoaded', () => {
  const generateBtn = document.getElementById('generateBtn');
  const textInput = document.getElementById('textInput');
  const audioContainer = document.getElementById('audioContainer');

  generateBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();

    if (!text) {
      alert("⚠️ Please enter some text.");
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
      });

      const result = await response.json();

      if (response.ok && result.audio_url) {
        // Display audio player
        audioContainer.innerHTML = `
          <p>🔊 Your generated audio:</p>
          <audio controls autoplay>
            <source src="${result.audio_url}" type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        `;
      } else {
        console.error('Server error:', result);
        alert('❌ Failed to generate audio. Please try again.');
      }
    } catch (err) {
      console.error('Network error:', err);
      alert('❌ Could not connect to server. Is it running?');
    }
  });

  // =========================
  // Echo Bot Functionality 🎤
  // =========================
  const startBtn = document.getElementById('startRecording');
  const stopBtn = document.getElementById('stopRecording');
  const playbackAudio = document.getElementById('playbackAudio');

  let mediaRecorder;
  let audioChunks = [];

  startBtn.addEventListener('click', async () => {
    // Ask for mic permission and start recording
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        audioChunks.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        const audioURL = URL.createObjectURL(blob);
        playbackAudio.src = audioURL;
        playbackAudio.style.display = 'block';

        // Upload to server
        const formData = new FormData();
        formData.append('file', blob, 'recording.webm');

        const statusMsg = document.createElement('p');
        statusMsg.textContent = "Uploading...";
        playbackAudio.parentNode.appendChild(statusMsg);

        try {
          const res = await fetch('http://127.0.0.1:8000/upload', {
            method: 'POST',
            body: formData
          });

          const result = await res.json();
          statusMsg.textContent = `✅ Uploaded: ${result.filename} (${result.content_type}, ${result.size} bytes)`;
        } catch (err) {
          console.error(err);
          statusMsg.textContent = "❌ Upload failed!";
        }
      };

      mediaRecorder.start();
      startBtn.disabled = true;
      stopBtn.disabled = false;
    } catch (err) {
      console.error('Microphone access denied or error:', err);
      alert("❌ Cannot access microphone.");
    }
  });

  stopBtn.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      startBtn.disabled = false;
      stopBtn.disabled = true;
    }
  });
});
