// Poll /api/v1/schedule for today's items and show current activity with timer
(function(){
  const api = (from, to) => `/api/v1/schedule?from=${from}&to=${to}`;
  function todayStr(d = new Date()){
    return d.toISOString().slice(0,10);
  }

  let items = [];
  let current = null;
  let nextItem = null;
  let remaining = 0;

  function fetchSchedule(){
    const t = todayStr();
    fetch(api(t,t)).then(r => r.json()).then(j => {
      if(j && j.items){ items = j.items; computeCurrent(); renderList(); }
    }).catch(()=>{});
  }

  // WebSocket: prefer push updates
  function startWebSocket(){
    try{
      const scheme = location.protocol === 'https:' ? 'wss' : 'ws';
      // include token if provided via global `WS_AUTH_TOKEN` variable (set in page if needed)
      const tokenParam = (typeof window !== 'undefined' && window.WS_AUTH_TOKEN) ? `?token=${encodeURIComponent(window.WS_AUTH_TOKEN)}` : '';
      const ws = new WebSocket(`${scheme}://${location.host}/ws/live${tokenParam}`);
      ws.addEventListener('message', (ev)=>{
        try{
          const data = JSON.parse(ev.data);
          if(!data) return;
          // full snapshot
          if(data.items){ items = data.items; computeCurrent(); renderList(); return; }

          // diff message
          if(data.type === 'diff' && data.diff){
            const key = (it)=>`${it.date}|${it.start_time}|${it.name}|${it.source}`;
            const removed = new Set(data.diff.removed || []);
            // remove
            items = items.filter(it => !removed.has(key(it)));
            // update existing
            const updates = (data.diff.updated || []);
            for(const u of updates){
              const k = key(u); const idx = items.findIndex(it=>key(it)===k);
              if(idx !== -1) items[idx] = u;
              else items.push(u);
            }
            // add new
            const adds = (data.diff.added || []);
            for(const a of adds){ items.push(a); }

            // ensure deterministic order
            items.sort((a,b)=> (a.date + a.start_time + a.name).localeCompare(b.date + b.start_time + b.name));
            computeCurrent(); renderList();
            return;
          }
        }catch(e){}
      });
      ws.addEventListener('open', ()=>{ console.info('ws connected'); });
      ws.addEventListener('close', ()=>{ console.info('ws closed, falling back to polling'); setTimeout(() => startWebSocket(), 5000); });
      return ws;
    }catch(e){
      return null;
    }
  }

  function timeToSeconds(hm){
    if(!hm) return 0; const [h,m]=hm.split(':').map(Number); return h*3600 + m*60;
  }

  function computeCurrent(){
    const now = new Date();
    const todayMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0,0,0,0).getTime();
    const nowMs = now.getTime();
    current = null; nextItem = null; remaining = 0;

    const intervals = [];
    for(const it of items){
      if(!it.start_time) continue;
      const startSec = timeToSeconds(it.start_time);
      let accMs = todayMidnight + startSec*1000;
      for(const act of it.activities || []){
        const durMs = (Number(act.duration_minutes)||0) * 60 * 1000;
        const endMs = accMs + durMs;
        intervals.push({startMs: accMs, endMs, instance: it, activity: act});
        accMs = endMs;
      }
    }

    intervals.sort((a,b)=>a.startMs - b.startMs);

    for(const iv of intervals){
      if(nowMs >= iv.startMs && nowMs < iv.endMs){
        current = {instance: iv.instance, activity: iv.activity, endsAtMs: iv.endMs};
        remaining = Math.ceil((iv.endMs - nowMs)/1000);
        return;
      }
    }

    for(const iv of intervals){
      if(iv.startMs > nowMs){
        nextItem = {instance: iv.instance, activity: iv.activity, startsAtMs: iv.startMs};
        remaining = Math.ceil((iv.startMs - nowMs)/1000);
        return;
      }
    }
  }

  function renderList(){
    const container = document.querySelector('.activities');
    if(!container) return;
    container.innerHTML = '';
    for(const it of items){
      for(const act of it.activities || []){
        const row = document.createElement('div'); row.className='activity-row';
        if(current && current.activity === act) row.classList.add('current');
        const left = document.createElement('div'); left.textContent = `${act.topic || act.activity_type}`;
        const right = document.createElement('div'); right.textContent = `${act.duration_minutes || 0} min`;
        row.append(left,right); container.append(row);
      }
    }
  }

  function formatMMSS(s){ const m=Math.floor(s/60); const sec=s%60; return `${m.toString().padStart(2,'0')}:${sec.toString().padStart(2,'0')}` }

  function tick(){
    const nameEl = document.getElementById('activity-name');
    const timerEl = document.getElementById('activity-timer');
    const card = document.getElementById('current-activity');
    if(current){
      nameEl.textContent = current.activity.topic || current.activity.activity_type || 'Aktivität';
      timerEl.textContent = formatMMSS(remaining);
      card.classList.add('active');
      if(remaining <= 10){ timerEl.classList.add('warning'); }
      if(remaining === 10){ try{ beep(); }catch(e){} }
      remaining = Math.max(0, remaining-1);
      if(remaining === 0){ fetchSchedule(); }
    } else if(nextItem){
      nameEl.textContent = `Nächste: ${nextItem.activity.topic || nextItem.activity.activity_type || 'Aktivität'}`;
      timerEl.textContent = formatMMSS(remaining);
      card.classList.remove('active');
      timerEl.classList.remove('warning');
      remaining = Math.max(0, remaining-1);
      if(remaining === 0){ fetchSchedule(); }
    } else {
      nameEl.textContent = 'Keine aktive Aktivität';
      timerEl.textContent = '--:--';
      card.classList.remove('active');
    }
  }

  function beep(){
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator(); const g = ctx.createGain();
    o.type='sine'; o.frequency.value=880; g.gain.value=0.05; o.connect(g); g.connect(ctx.destination); o.start(); setTimeout(()=>{ o.stop(); ctx.close(); },120);
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    fetchSchedule(); setInterval(fetchSchedule, 30000);
    setInterval(tick, 1000);
  });
})();
