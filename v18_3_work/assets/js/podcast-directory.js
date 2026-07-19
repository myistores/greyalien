(async()=>{
  const root=document.getElementById("podcast-series");
  const esc=(s="")=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
  try{
    const [podcastResponse,indexResponse,vocabResponse]=await Promise.all([
      fetch("../data/podcasts/podcast-index.json"),
      fetch("../data/entity-index.json"),
      fetch("../data/schema/relationship-vocabulary.json")
    ]);
    if(!podcastResponse.ok) throw new Error(`Podcast index returned ${podcastResponse.status}`);
    if(!indexResponse.ok) throw new Error(`Entity index returned ${indexResponse.status}`);
    if(!vocabResponse.ok) throw new Error(`Relationship vocabulary returned ${vocabResponse.status}`);

    const [data,index,vocab]=await Promise.all([
      podcastResponse.json(),
      indexResponse.json(),
      vocabResponse.json()
    ]);

    if(!Array.isArray(data.podcasts)){ throw new Error("Podcast index is invalid"); }

    const entities=await Promise.all(index.entities.map(async entry=>{
      const response=await fetch(`../data/entities/${entry.id}.json`);
      if(!response.ok) throw new Error(`Entity ${entry.id} returned ${response.status}`);
      return response.json();
    }));
    const entityMap=Object.fromEntries(entities.map(entity=>[entity.id,entity]));
    const connectionCounts=Object.fromEntries(data.podcasts.map(podcast=>[podcast.id,0]));

    entities.forEach(source=>{
      (source.relationships||[]).forEach(relationship=>{
        if(!entityMap[relationship.target]||!vocab[relationship.type]) return;
        if(Object.hasOwn(connectionCounts,source.id)) connectionCounts[source.id]++;
        if(Object.hasOwn(connectionCounts,relationship.target)) connectionCounts[relationship.target]++;
      });
    });

    root.innerHTML=data.podcasts.map(podcast=>`<article class="podcast-card">
      <div class="podcast-card-icon">🎙️</div>
      <h2>${esc(podcast.name)}</h2>
      <div class="podcast-card-facts">
        <div><span>Hosts</span><strong>${esc((podcast.hosts||[]).join(", ")||"Not listed")}</strong></div>
        <div><span>Launch year</span><strong>${esc(podcast.launchYear||"Not listed")}</strong></div>
        <div><span>Researched episodes</span><strong>${podcast.episodeCount||0}</strong></div><div><span>Connected entities</span><strong>${podcast.connectedEntityCount??connectionCounts[podcast.id]??0}</strong></div>
      </div>
      <p>${esc(podcast.summary)}</p>
      <div class="podcast-card-actions">
        <a class="button secondary-button" href="${podcast.officialWebsite}" target="_blank" rel="noopener">Official Website ↗</a>
        <a class="button" href="../entities/entity.html?id=${encodeURIComponent(podcast.id)}">Explore Podcast</a>
      </div>
    </article>`).join("");

    document.getElementById("year").textContent=new Date().getFullYear();
    window.GreyAlienSEO?.apply({
      title:"Podcasts | GreyAlien",
      description:"Explore foundational UAP podcast series and their connections throughout the GreyAlien knowledge graph.",
      canonical:"https://greyalien.com/categories/podcasts.html"
    });
  }catch(error){
    console.error("Podcast directory error:",error);
    root.innerHTML="<p>The podcast series are temporarily unavailable.</p>";
  }
})();
