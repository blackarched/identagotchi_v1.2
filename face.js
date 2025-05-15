// face.js - Handles interactive face animations and real-time dashboard socket data

document.addEventListener('DOMContentLoaded', () => {
  const face = document.getElementById('pwnface');

  // Create face structure
  function createFace() {
    face.innerHTML = `
      <div class="eye left"><div class="pupil"></div></div>
      <div class="eye right"><div class="pupil"></div></div>
      <div class="mouth"></div>
    `;
  }

  createFace();

  // Face states management
  const states = ['neutral', 'happy', 'sad', 'angry'];
  let currentState = 'neutral';

  function setFaceState(state) {
    face.classList.remove(...states);
    face.classList.add(state);
    currentState = state;
  }

  // Initial state
  setFaceState('neutral');

  // Blink eyes periodically
  setInterval(() => {
    face.classList.add('blinking');
    setTimeout(() => face.classList.remove('blinking'), 300);
  }, 5000);

  // Socket.IO connection
  const socket = io();

  // Handle Scan tab interactions
  const startScanBtn = document.getElementById('startScan');
  const scanResultsList = document.getElementById('scanResults');

  startScanBtn.onclick = () => {
    startScanBtn.disabled = true;
    scanResultsList.innerHTML = '<li class="list-group-item">Scanning...</li>';
    socket.emit('start_scan');
  };

  socket.on('scan_results', (data) => {
    scanResultsList.innerHTML = '';
    if (data.networks && data.networks.length > 0) {
      data.networks.forEach((net) => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.textContent = `${net.ssid} [${net.bssid}] - Signal: ${net.signal} dBm`;
        li.onclick = () => {
          document.getElementById('deauthTarget').value = net.bssid;
          setFaceState('happy');
        };
        scanResultsList.appendChild(li);
      });
    } else {
      scanResultsList.innerHTML = '<li class="list-group-item">No networks found.</li>';
      setFaceState('sad');
    }
    startScanBtn.disabled = false;
  });

  // Handle Deauth tab
  const deauthBtn = document.getElementById('sendDeauth');
  const deauthStatus = document.getElementById('deauthStatus');

  deauthBtn.onclick = () => {
    const target = document.getElementById('deauthTarget').value.trim();
    if (!target) {
      deauthStatus.textContent = 'Please enter a target SSID or MAC.';
      setFaceState('angry');
      return;
    }
    deauthStatus.textContent = 'Sending deauth packets...';
    setFaceState('neutral');
    socket.emit('send_deauth', { target });
  };

  socket.on('deauth_status', (msg) => {
    deauthStatus.textContent = msg.status;
    setFaceState(msg.success ? 'happy' : 'angry');
  });

  // Handle Brute tab
  const bruteBtn = document.getElementById('startBrute');
  const bruteStatus = document.getElementById('bruteStatus');

  bruteBtn.onclick = () => {
    const target = document.getElementById('bruteTarget').value.trim();
    if (!target) {
      bruteStatus.textContent = 'Please enter a target SSID or MAC.';
      setFaceState('angry');
      return;
    }
    bruteStatus.textContent = 'Starting brute force attack...';
    setFaceState('neutral');
    socket.emit('start_brute', { target });
  };

  socket.on('brute_status', (msg) => {
    bruteStatus.textContent = msg.status;
    setFaceState(msg.success ? 'happy' : 'angry');
  });

  // Setup charts for status tab
  const cpuCtx = document.getElementById('cpuChart').getContext('2d');
  const memCtx = document.getElementById('memChart').getContext('2d');
  const ppsCtx = document.getElementById('ppsChart').getContext('2d');

  const chartOptions = {
    responsive: true,
    animation: false,
    scales: {
      y: { min: 0, max: 100 },
      x: { display: false }
    },
    plugins: {
      legend: { display: false }
    }
  };

  const cpuChart = new Chart(cpuCtx, {
    type: 'line',
    data: { labels: [], datasets: [{ data: [], borderColor: '#0ff', fill: false }] },
    options: chartOptions
  });

  const memChart = new Chart(memCtx, {
    type: 'line',
    data: { labels: [], datasets: [{ data: [], borderColor: '#0f0', fill: false }] },
    options: chartOptions
  });

  const ppsChart = new Chart(ppsCtx, {
    type: 'line',
    data: { labels: [], datasets: [{ data: [], borderColor: '#ff0', fill: false }] },
    options: {
      ...chartOptions,
      scales: {
        y: { min: 0, max: undefined },
        x: { display: false }
      }
    }
  });

  // Update charts with new data from server
  socket.on('status_update', (data) => {
    updateChart(cpuChart, data.cpu);
    updateChart(memChart, data.memory);
    updateChart(ppsChart, data.pps);
  });

  function updateChart(chart, value) {
    const maxPoints = 30;
    if (chart.data.labels.length >= maxPoints) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }
    const timeLabel = new Date().toLocaleTimeString();
    chart.data.labels.push(timeLabel);
    chart.data.datasets[0].data.push(value);
    chart.update('none');
  }
});