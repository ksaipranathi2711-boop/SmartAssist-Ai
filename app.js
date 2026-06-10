function initChat(){
  const form = document.getElementById('chatForm');
  const input = document.getElementById('chatInput');
  const box = document.getElementById('messages');
  function add(text, who){
    const d = document.createElement('div');
    d.className = 'msg ' + who;
    d.textContent = text;
    box.appendChild(d); box.scrollTop = box.scrollHeight;
    return d;
  }
  form.addEventListener('submit', async e=>{
    e.preventDefault();
    const msg = input.value.trim(); if(!msg) return;
    add(msg,'user'); input.value=''; input.focus();
    const t = add('','bot'); t.innerHTML='<span class="typing"><span></span><span></span><span></span></span>';
    try{
      const r = await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
      const j = await r.json();
      t.textContent = j.reply || 'Sorry, something went wrong.';
    }catch(err){ t.textContent='Network error.'; }
  });
}
