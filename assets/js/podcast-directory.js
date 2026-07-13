(async()=>{
  const root=document.getElementById("podcast-series");
  const esc=(s="")=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
  try{
    const [podcastIndex,entityIndex,vocab]=await Promise.all([
      fetch("../data/podcasts/podcast-index.json").then(r=>r.json()),
      fetch("../data/entity-index.json").then(r=>r.json()),
      fetch("../data/schema/relationship-vocabulary.json").then(r=>r.json())
    ]);
    const entities=await Promise.all(entityIndex.entities.map(e=>fetch(`../data/entities/${e.id}.json`).then(r=>r.json())));
    const map=Object.fromEntries(entities.map(e=>[e.id,e]));
    const edges=[];
    entities.forEach(source=>(source.relationships||[]).forEach(rel=>{
      if(map[rel.target]&&vocab[rel.type]) edges.push({source:source.id,target:rel.target,type:rel.type});
    }));

    root.innerHTML=podcastIndex.podcasts.map(item=>{
      const podcast=map[item.id];
      if(!podcast) return "";
      const connected=new Set();
      edges.forEach(edge=>{
        if(edge.source===podcast.id) connected.add(edge.target);
        if(edge.target===podcast.id) connected.add(edge.source);
      });
      const hosts=(podcast.podcastHosts||[]).join(", ");
      return `<article class="podcast-card">
        <div class="podcast-card-icon">🎙️</div>
        <h2>${esc(podcast.name)}</h2>
        <div class="podcast-card-facts">
          <div><span>Hosts</span><strong>${esc(hosts||"Not listed")}</strong></div>
          <div><span>Launch year</span><strong>${esc(podcast.launchYear||"Not listed")}</strong></div>
          <div><span>Connected entities</span><strong>${connected.size}</strong></div>
        </div>
        <p>${esc(podcast.summary)}</p>
        <div class="podcast-card-actions">
          <a class="button secondary-button" href="${podcast.externalUrl}" target="_blank" rel="noopener">Official Website ↗</a>
          <a class="button" href="../entities/entity.html?id=${encodeURIComponent(podcast.id)}">Explore Podcast</a>
        </div>
      </article>`;
    }).join("");

    document.getElementById("year").textContent=new Date().getFullYear();
    window.GreyAlienSEO?.apply({
      title:"Podcasts | GreyAlien",
      description:"Explore foundational UAP podcast series and their connections throughout the GreyAlien knowledge graph.",
      canonical:"https://greyalien.com/categories/podcasts.html"
    });
  }catch(error){
    console.error(error);
    root.innerHTML="<p>The podcast series are temporarily unavailable.</p>";
  }
})();
