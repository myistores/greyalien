(async()=>{
  const root=document.getElementById("whistleblower-profiles");
  const esc=(s="")=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
  try{
    const [profileIndex,entityIndex,vocab]=await Promise.all([
      fetch("../data/whistleblowers/whistleblower-index.json").then(r=>r.json()),
      fetch("../data/entity-index.json").then(r=>r.json()),
      fetch("../data/schema/relationship-vocabulary.json").then(r=>r.json())
    ]);
    const entities=await Promise.all(entityIndex.entities.map(e=>fetch(`../data/entities/${e.id}.json`).then(r=>r.json())));
    const map=Object.fromEntries(entities.map(e=>[e.id,e]));
    const edges=[];
    entities.forEach(source=>(source.relationships||[]).forEach(rel=>{
      if(map[rel.target]&&vocab[rel.type]) edges.push({source:source.id,target:rel.target,type:rel.type});
    }));

    root.innerHTML=profileIndex.profiles.map(profile=>{
      const person=map[profile.id];
      const connected=edges.filter(e=>e.source===profile.id||e.target===profile.id)
        .map(e=>map[e.source===profile.id?e.target:e.source])
        .filter(Boolean);
      const counts={};
      connected.forEach(e=>counts[e.type]=(counts[e.type]||0)+1);
      const countLine=[
        counts.hearing?`${counts.hearing} hearing${counts.hearing===1?"":"s"}`:"",
        counts.document?`${counts.document} document${counts.document===1?"":"s"}`:"",
        counts.interview?`${counts.interview} interview${counts.interview===1?"":"s"}`:"",
        counts.claim?`${counts.claim} claim${counts.claim===1?"":"s"}`:"",
        counts.organization?`${counts.organization} organization${counts.organization===1?"":"s"}`:""
      ].filter(Boolean).join(" · ");

      return `<article class="whistleblower-card">
        <span class="profile-status">${esc(profile.status)}</span>
        <h2><a href="../entities/entity.html?id=${encodeURIComponent(profile.id)}">${esc(person.name)}</a></h2>
        <p>${esc(profile.summary)}</p>
        <div class="profile-counts">${esc(countLine||"Connected profile")}</div>
        <details>
          <summary>Why this profile is included</summary>
          <p>${esc(profile.inclusionNote)}</p>
        </details>
        <a class="button" href="../entities/entity.html?id=${encodeURIComponent(profile.id)}">Open connected profile</a>
      </article>`;
    }).join("");
  }catch(err){
    root.innerHTML="<p>The whistleblower profiles are temporarily unavailable.</p>";
  }
  document.getElementById("year").textContent=new Date().getFullYear();
  window.GreyAlienSEO?.apply({
    title:"Witness & Whistleblower Database | GreyAlien",
    description:"Documented profiles connecting people to congressional testimony, interviews, organizations, hearings, claims and supporting source material.",
    canonical:"https://greyalien.com/categories/whistleblower-database.html"
  });
})();
