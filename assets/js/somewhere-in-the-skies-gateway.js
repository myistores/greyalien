(async()=>{
  const state={year:"",topic:"",query:"",sort:"newest",page:1};
  const els={
    stats:document.getElementById("sits-stats"),years:document.getElementById("sits-years"),topics:document.getElementById("sits-topics"),
    search:document.getElementById("sits-search"),sort:document.getElementById("sits-sort"),results:document.getElementById("sits-results"),
    pagination:document.getElementById("sits-pagination"),active:document.getElementById("sits-active-filters"),title:document.getElementById("sits-results-title"),
    clear:document.getElementById("sits-clear")
  };
  const esc=(s="")=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
  const normalize=s=>String(s||"").toLowerCase();
  const formatDate=value=>{if(!value)return "Date not listed";const d=new Date(`${value}T00:00:00`);return Number.isNaN(d.valueOf())?value:d.toLocaleDateString("en-US",{year:"numeric",month:"short",day:"numeric"});};
  try{
    const response=await fetch("../data/podcasts/somewhere-in-the-skies-archive.json");
    if(!response.ok)throw new Error(`Archive returned ${response.status}`);
    const data=await response.json();
    const episodes=Array.isArray(data.episodes)?data.episodes:[];
    const topicMap=Object.fromEntries((data.topics||[]).map(t=>[t.id,t]));
    const pageSize=data.pageSize||25;

    const countsByYear=Object.fromEntries((data.years||[]).map(y=>[String(y),0]));
    const countsByTopic=Object.fromEntries((data.topics||[]).map(t=>[t.id,0]));
    episodes.forEach(ep=>{
      if(ep.year&&Object.hasOwn(countsByYear,String(ep.year)))countsByYear[String(ep.year)]++;
      (ep.topics||[]).forEach(t=>{if(Object.hasOwn(countsByTopic,t))countsByTopic[t]++;});
    });
    const researched=episodes.filter(ep=>ep.tier==="full").length;
    const standard=episodes.filter(ep=>ep.tier==="standard").length;
    const catalog=episodes.filter(ep=>ep.tier==="catalog").length;
    els.stats.innerHTML=`<div><span>Indexed episodes</span><strong>${episodes.length}</strong></div><div><span>Full research</span><strong>${researched}</strong></div><div><span>Standard records</span><strong>${standard}</strong></div><div><span>Catalog records</span><strong>${catalog}</strong></div>`;

    els.years.innerHTML=(data.years||[]).map(y=>`<button type="button" class="sits-option" data-year="${y}"><span>${y}</span><strong>${countsByYear[String(y)]||0}</strong></button>`).join("");
    els.topics.innerHTML=(data.topics||[]).map(t=>`<button type="button" class="sits-option" data-topic="${esc(t.id)}" title="${esc(t.description)}"><span>${esc(t.name)}</span><strong>${countsByTopic[t.id]||0}</strong></button>`).join("");

    function filtered(){
      const q=normalize(state.query).trim();
      return episodes.filter(ep=>{
        if(state.year&&String(ep.year)!==state.year)return false;
        if(state.topic&&!(ep.topics||[]).includes(state.topic))return false;
        if(q){
          const haystack=[ep.title,ep.summary,ep.guest,ep.episodeNumber,...(ep.guests||[]),...(ep.cases||[]),...(ep.tags||[])].map(normalize).join(" ");
          if(!haystack.includes(q))return false;
        }
        return true;
      }).sort((a,b)=>{
        if(state.sort==="oldest")return String(a.date||"").localeCompare(String(b.date||""));
        if(state.sort==="episode")return Number(a.episodeNumber||999999)-Number(b.episodeNumber||999999);
        return String(b.date||"").localeCompare(String(a.date||""));
      });
    }

    function syncButtons(){
      document.querySelectorAll("[data-year]").forEach(b=>b.classList.toggle("active",b.dataset.year===state.year));
      document.querySelectorAll("[data-topic]").forEach(b=>b.classList.toggle("active",b.dataset.topic===state.topic));
    }

    function render(){
      syncButtons();
      const list=filtered();
      const pages=Math.max(1,Math.ceil(list.length/pageSize));
      state.page=Math.min(state.page,pages);
      const start=(state.page-1)*pageSize;
      const pageItems=list.slice(start,start+pageSize);
      const labels=[];
      if(state.year)labels.push(state.year);
      if(state.topic)labels.push(topicMap[state.topic]?.name||state.topic);
      if(state.query)labels.push(`“${state.query}”`);
      els.title.textContent=labels.length?labels.join(" + "):"All 2017 releases";
      els.active.innerHTML=labels.length?`<span>Showing ${list.length} matching record${list.length===1?"":"s"}</span>`:`<span>${episodes.length} episode record${episodes.length===1?"":"s"} available</span>`;

      if(!episodes.length){
        els.results.innerHTML=`<div class="sits-empty"><h3>Gateway ready for episode ingestion</h3><p>The year-and-topic archive is active, but no Somewhere in the Skies episodes have been ingested into V22.1 yet. Future records will populate this page automatically through the archive index.</p><a class="button" href="../entities/entity.html?id=somewhere-in-the-skies-podcast">Explore the series entity</a></div>`;
        els.pagination.innerHTML="";
        return;
      }
      if(!pageItems.length){
        els.results.innerHTML=`<div class="sits-empty"><h3>No matching episodes</h3><p>Try another year, topic, or search term.</p></div>`;
        els.pagination.innerHTML="";
        return;
      }
      els.results.innerHTML=pageItems.map(ep=>{
        const topics=(ep.topics||[]).slice(0,3).map(id=>`<span>${esc(topicMap[id]?.name||id)}</span>`).join("");
        const guests=(ep.guests||[]).join(", ")||ep.guest||"Guest not listed";
        const href=ep.entityId?`../entities/entity.html?id=${encodeURIComponent(ep.entityId)}`:(ep.officialUrl||"#");
        const external=!ep.entityId&&ep.officialUrl?' target="_blank" rel="noopener"':"";
        return `<article class="sits-episode-row"><div class="sits-episode-number">${ep.episodeNumber?`#${esc(ep.episodeNumber)}`:"Special"}</div><div class="sits-episode-copy"><div class="sits-row-meta"><time>${esc(formatDate(ep.date))}</time><span>${esc(ep.tier||"catalog")}</span></div><h3><a href="${esc(href)}"${external}>${esc(ep.title||"Untitled episode")}</a></h3><p>${esc(ep.summary||"")}</p><div class="mini-meta"><span>${esc(guests)}</span>${topics}</div></div><a class="sits-open" href="${esc(href)}"${external} aria-label="Open ${esc(ep.title||"episode")}">Open →</a></article>`;
      }).join("");
      els.pagination.innerHTML=pages>1?`${state.page>1?'<button type="button" data-page="prev">← Previous</button>':""}<span>Page ${state.page} of ${pages}</span>${state.page<pages?'<button type="button" data-page="next">Next →</button>':""}`:"";
    }

    els.years.addEventListener("click",e=>{const b=e.target.closest("[data-year]");if(!b)return;state.year=state.year===b.dataset.year?"":b.dataset.year;state.page=1;render();});
    els.topics.addEventListener("click",e=>{const b=e.target.closest("[data-topic]");if(!b)return;state.topic=state.topic===b.dataset.topic?"":b.dataset.topic;state.page=1;render();});
    els.search.addEventListener("input",()=>{state.query=els.search.value;state.page=1;render();});
    els.sort.addEventListener("change",()=>{state.sort=els.sort.value;state.page=1;render();});
    els.pagination.addEventListener("click",e=>{const b=e.target.closest("[data-page]");if(!b)return;state.page+=b.dataset.page==="next"?1:-1;render();document.querySelector(".sits-results-panel")?.scrollIntoView({behavior:"smooth",block:"start"});});
    document.querySelectorAll("[data-reset]").forEach(b=>b.addEventListener("click",()=>{state[b.dataset.reset]="";state.page=1;render();}));
    els.clear.addEventListener("click",()=>{Object.assign(state,{year:"",topic:"",query:"",sort:"newest",page:1});els.search.value="";els.sort.value="newest";render();});

    render();
    document.getElementById("year").textContent=new Date().getFullYear();
    window.GreyAlienSEO?.apply({title:"Somewhere in the Skies Podcast Archive | GreyAlien",description:"Explore Somewhere in the Skies by year and research topic through the GreyAlien podcast knowledge base.",canonical:"https://greyalien.com/categories/somewhere-in-the-skies.html"});
  }catch(error){
    console.error("Somewhere in the Skies gateway error:",error);
    els.results.innerHTML="<p>The Somewhere in the Skies archive is temporarily unavailable.</p>";
  }
})();
