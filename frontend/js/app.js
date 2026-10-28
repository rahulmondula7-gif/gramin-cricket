// Change this URL when deploying the FastAPI backend.
const API_BASE = 'http://127.0.0.1:8000/api';
let currentStatus = 'all';
const form = document.querySelector('#teamForm');
const message = document.querySelector('#formMessage');
const table = document.querySelector('#teamsTable');
const listMessage = document.querySelector('#listMessage');

function escapeHTML(value='') { return String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])); }
function statusLabel(status) { return status === 'confirmed' ? 'पुष्टी झालेले' : 'वेटिंग लिस्ट'; }
async function loadTeams() {
  table.innerHTML = '<tr><td colspan="6" class="empty">यादी लोड होत आहे…</td></tr>';
  try {
    const response = await fetch(`${API_BASE}/teams`);
    if (!response.ok) throw new Error((await response.json()).detail || 'API कडून डेटा मिळाला नाही.');
    const data = await response.json();
    const teams = data.teams || [];
    document.querySelector('#totalCount').textContent = teams.length;
    document.querySelector('#confirmedCount').textContent = teams.filter(t=>t.status==='confirmed').length;
    document.querySelector('#waitingCount').textContent = teams.filter(t=>t.status==='waiting').length;
    const shown = currentStatus === 'all' ? teams : teams.filter(t=>t.status===currentStatus);
    if (!shown.length) table.innerHTML = '<tr><td colspan="6" class="empty">या विभागात अजून कोणतीही नोंदणी नाही.</td></tr>';
    else table.innerHTML = shown.map((t,i)=>`<tr><td>${i+1}</td><td><strong>${escapeHTML(t.team_name)}</strong></td><td>${escapeHTML(t.village)}</td><td>${escapeHTML(t.captain_name)}</td><td><a href="tel:${escapeHTML(t.mobile)}">${escapeHTML(t.mobile)}</a></td><td><span class="status ${t.status}">${statusLabel(t.status)}</span></td></tr>`).join('');
    listMessage.textContent = 'ही यादी डेटाबेसमधील नोंदणीवरून अपडेट होते.';
  } catch (e) {
    table.innerHTML = '<tr><td colspan="6" class="empty">डेटाबेसशी संपर्क होत नाही. Backend सुरू आहे आणि Supabase सेटअप पूर्ण आहे का ते तपासा.</td></tr>';
    listMessage.textContent = e.message;
    ['totalCount','confirmedCount','waitingCount'].forEach(id=>document.getElementById(id).textContent='—');
  }
}
form.addEventListener('submit', async e => {
  e.preventDefault(); message.className=''; message.textContent='नोंदणी सेव्ह होत आहे…';
  const body = Object.fromEntries(new FormData(form).entries());
  try {
    const response = await fetch(`${API_BASE}/teams`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || 'नोंदणी करता आली नाही.');
    message.className='success'; message.textContent = `नोंदणी यशस्वी! ${result.team.team_name} — स्थिती: ${statusLabel(result.team.status)}.`;
    form.reset(); currentStatus='all'; document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.status==='all'));
    await loadTeams();
  } catch (err) { message.className='error'; message.textContent=err.message; }
});
document.querySelectorAll('.tab').forEach(button=>button.addEventListener('click',()=>{currentStatus=button.dataset.status;document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b===button));loadTeams();}));
document.querySelector('#refreshBtn').addEventListener('click',loadTeams);
loadTeams();
