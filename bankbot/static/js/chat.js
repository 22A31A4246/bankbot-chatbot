const chat = document.getElementById('chat');
const input = document.getElementById('msg');
const sendBtn = document.getElementById('send');
const quick = document.getElementById('quick');

function addMsg(text, who='bot') {
  const div = document.createElement('div');
  div.className = (who === 'bot') ? 'bot-msg' : 'user-msg';
  div.innerText = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function renderOptions(options) {
  quick.innerHTML = '';
  options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-outline-primary';
    btn.textContent = opt.label;
    btn.onclick = () => {
      input.value = opt.text;
      send();
    };
    quick.appendChild(btn);
  });
}

async function send() {
  const text = input.value.trim();
  if (!text) return;
  addMsg(text, 'user');
  input.value = '';

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();
    addMsg(data.reply || '...');
    if (data.options) renderOptions(data.options);
  } catch (e) {
    addMsg('Network error.');
  }
}

sendBtn.addEventListener('click', send);
input.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });

// load default options
fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message: 'show options'})})
  .then(r=>r.json())
  .then(d=>{ if (d.options) renderOptions(d.options); });
