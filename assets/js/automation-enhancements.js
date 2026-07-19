(async()=>{
  const app=document.getElementById('entity-app');
  if(!app) return;
  const id=(new URLSearchParams(location.search).get('id')||'').replace(/[^a-z0-9-]/gi,'');
  if(!id) return;
  try{
    const [related,index]=await Promise.all([
      fetch('../data/related-content.json').then(r=>r.json()),
      fetch('../data/entity-index.json').then(r=>r.json())
    ]);
    const map=Object.fromEntries(index.entities.map(e=>[e.id,e]));
    const current=map[id]; if(!current) return;
    const icon={person:'👤',hearing:'🏛️',organization:'🏢',document:'📄',topic:'🧭',case:'🛸',interview:'🎙️',podcast_episode:'🎙️',legislation:'📜',timeline_event:'🕒',publication:'📰',claim:'⚖️',podcast_series:'🎙️'};
    const makeCard=(row,extra='')=>`<a class="connection-card" href="entity.html?id=${row.id}"><span class="connection-type">${row.type==='podcast_episode'?'Podcast episode':'Referenced in'}</span><strong>${icon[row.type]||'🔗'} ${row.name}</strong>${row.summary?`<p>${row.summary}</p>`:''}${extra}<span class="connection-action">Explore →</span></a>`;
    const refs=(related.referencedIn[id]||[]).filter(r=>r.type==='podcast_episode'||r.type==='interview').slice(0,12).map(r=>({...r,summary:(map[r.id]||{}).summary||''}));
    const eps=(related.relatedEpisodes[id]||[]).map(r=>({...r,type:'podcast_episode',summary:(map[r.id]||{}).summary||''}));
    const sections=[];
    if(refs.length) sections.push(`<section class="entity-connection-section"><div class="section-head"><div><p class="kicker">Source discovery</p><h2>Referenced In</h2></div><p>${refs.length} media record${refs.length===1?'':'s'}</p></div><div class="connection-grid">${refs.map(r=>makeCard(r,r.context?`<span class="connection-context">${r.context}</span>`:'')).join('')}</div></section>`);
    if(current.type==='podcast_episode'&&eps.length) sections.push(`<section class="entity-connection-section"><div class="section-head"><div><p class="kicker">Continue listening</p><h2>Related Episodes</h2></div><p>Generated from shared entities</p></div><div class="connection-grid">${eps.map(r=>makeCard(r,`<span class="connection-context">${r.sharedEntityCount} shared connection${r.sharedEntityCount===1?'':'s'}</span>`)).join('')}</div></section>`);
    if(!sections.length) return;
    const insert=()=>{
      const continueSection=[...app.querySelectorAll('section')].find(s=>s.textContent.includes('Where to explore next'));
      const target=continueSection||null;
      const holder=document.createElement('div'); holder.innerHTML=sections.join('');
      [...holder.children].forEach(node=>target?app.insertBefore(node,target):app.appendChild(node));
    };
    if(app.querySelector('.entity-hero')) insert(); else new MutationObserver((m,o)=>{if(app.querySelector('.entity-hero')){o.disconnect();insert();}}).observe(app,{childList:true,subtree:true});
  }catch(err){console.warn('GreyAlien automation enhancements unavailable:',err);}
})();
