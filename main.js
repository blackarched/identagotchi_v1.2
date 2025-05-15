<!-- File: static/js/main.js -->
```js
// Socket.IO setup
const socket = io();

// Populate interface dropdown from RPC
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const ifaces = await apiPost('/api/interfaces', {});
    const select = document.getElementById('iface-select');
    ifaces.forEach(i => {
      const opt = document.createElement('option'); opt.value = i; opt.textContent = i;
      select.appendChild(opt);
    });
  } catch (e) { console.error('Interfaces load error', e); }
});

// Tab switching
const tabs = document.querySelectorAll('.tab-button');
tabs.forEach(btn => btn.addEventListener('click', () => {
  tabs.forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(btn.dataset.tab).classList.add('active');
}));

// Helper functions
function toggleSpinner(id, show) { document.getElementById(id).classList.toggle('hidden', !show); }
async function apiPost(path, data) {
  const resp = await fetch(path, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
  if (!resp.ok) { const err = await resp.json(); throw new Error(err.error||'Error'); }
  return resp.json();
}

// Scan action
document.getElementById('btn-scan').addEventListener('click', async () => {
  const iface = document.getElementById('iface-select').value;
  const errorDiv = document.getElementById('scan-error');
  try {
    toggleSpinner('scan-spinner', true);
    const results = await apiPost('/api/scan', {interface: iface});
    const tbody = document.querySelector('#scan-results tbody'); tbody.innerHTML = '';
    results.forEach(ap => { const tr = document.createElement('tr'); tr.innerHTML = `<td>${ap.ssid}</td><td>${ap.bssid}</td><td>${ap.signal}</td>`; tbody.appendChild(tr); });
    errorDiv.textContent = '';
  } catch (e) { errorDiv.textContent = e.message; }
  toggleSpinner('scan-spinner', false);
});

// Deauth action
document.getElementById('btn-deauth').addEventListener('click', async () => {
  const data = { interface: document.getElementById('iface-select').value,
    bssid: document.getElementById('bssid-deauth').value,
    count: +document.getElementById('count-deauth').value,
    interval: +document.getElementById('interval-deauth').value
  };
  const errDiv = document.getElementById('deauth-error'); document.getElementById('deauth-log').textContent = '';
  try { toggleSpinner('deauth-spinner', true); await apiPost('/api/deauth', data); errDiv.textContent = ''; }
  catch (e) { errDiv.textContent = e.message; }
  toggleSpinner('deauth-spinner', false);
});

// Brute action
document.getElementById('btn-brute').addEventListener('click', async () => {
  const data = { interface: document.getElementById('iface-select').value,
    ssid: document.getElementById('ssid-brute').value,
    bssid: document.getElementById('bssid-brute').value,
    wordlist: document.getElementById('wordlist-brute').value,
    delay: +document.getElementById('delay-brute').value
  };
  const errDiv = document.getElementById('brute-error'); document.getElementById('brute-log').textContent = '';
  try { toggleSpinner('brute-spinner', true); await apiPost('/api/brute', data); errDiv.textContent = ''; }
  catch (e) { errDiv.textContent = e.message; }
  toggleSpinner('brute-spinner', false);
});

// Status refresh
document.getElementById('btn-refresh-status').addEventListener('click', async () => {
  const errDiv = document.getElementById('status-error');
  try {
    toggleSpinner('status-spinner', true);
    const status = await apiPost('/api/status', {});
    document.getElementById('status-uptime').textContent = status.uptime;
    document.getElementById('status-handshakes').textContent = status.handshakes;
    document.getElementById('status-state').textContent = status.state;
    errDiv.textContent = '';
  } catch (e) { errDiv.textContent = e.message; }
  toggleSpinner('status-spinner', false);
});

// Real-time logs
socket.on('deauth_log', msg => { const log = document.getElementById('deauth-log'); log.textContent += msg + '
'; });
socket.on('brute_log', msg => { const log = document.getElementById('brute-log'); log.textContent += msg + '
'; });