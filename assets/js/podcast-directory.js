(async()=>{
  const root=document.getElementById("podcast-series");
  const esc=(s="")=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
  try{
    const response=await fetch("../data/podcasts/podcast-index.json");
    if(!response.ok) throw new Error(`Podcast index returned ${response.status}`);
    const data=await response.json();

    if(!Array.isArray(data.podcasts)||data.podcasts.length!==8){
      throw new Error(`Expected 8 podcast records; received ${data.podcasts?.length||0}`);
    }

    root.innerHTML=data.podcasts.map(podcast=>`<article class="podcast-card">
      <div class="podcast-card-icon">🎙️</div>
      <h2>${esc(podcast.name)}</h2>
      <div class="podcast-card-facts">
        <div><span>Hosts</span><strong>${esc((podcast.hosts||[]).join(", ")||"Not listed")}</strong></div>
        <div><span>Launch year</span><strong>${esc(podcast.launchYear||"Not listed")}</strong></div>
        <div><span>Connected entities</span><strong>${Number(podcast.connectedEntities)||0}</strong></div>
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
