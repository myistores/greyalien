(()=>{
  "use strict";

  const directory = document.getElementById("entity-directory");
  const navList = document.getElementById("entity-quick-nav-list");
  const backToTop = document.getElementById("entity-back-to-top");

  const order = [
    "person","hearing","organization","document","topic","case",
    "interview","legislation","timeline_event","publication","claim","podcast_series"
  ];

  const labels = {
    person: { singular:"Person", plural:"People", icon:"👤" },
    hearing: { singular:"Hearing", plural:"Hearings", icon:"🏛️" },
    organization: { singular:"Organization", plural:"Organizations", icon:"🏢" },
    document: { singular:"Document", plural:"Documents", icon:"📄" },
    topic: { singular:"Topic", plural:"Topics", icon:"🧭" },
    case: { singular:"Case", plural:"Cases", icon:"🛸" },
    interview: { singular:"Interview", plural:"Interviews", icon:"🎙️" },
    legislation: { singular:"Legislation", plural:"Legislation", icon:"📜" },
    timeline_event: { singular:"Timeline Event", plural:"Timeline Events", icon:"🕒" },
    publication: { singular:"Publication", plural:"Publications", icon:"📰" },
    claim: { singular:"Claim", plural:"Claims", icon:"⚖️" },
    podcast_series: { singular:"Podcast Series", plural:"Podcast Series", icon:"🎙️" }
  };

  const escapeHtml = value => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const slugFor = type => `entity-section-${type.replaceAll("_", "-")}`;

  function entityCard(entity, type){
    const meta = labels[type];
    return `<a class="connection-card" href="entity.html?id=${encodeURIComponent(entity.id)}">
      <span class="connection-type">${escapeHtml(meta.singular)}</span>
      <strong>${escapeHtml(entity.name)}</strong>
      <p>${escapeHtml(entity.summary || "Explore this entity and its connections across the GreyAlien knowledge graph.")}</p>
      <span class="connection-action">Explore connections →</span>
    </a>`;
  }

  function groupMarkup(type, entities){
    const meta = labels[type];
    const sectionId = slugFor(type);
    const countLabel = entities.length === 1 ? meta.singular : meta.plural;
    const cards = entities.length
      ? entities.map(entity => entityCard(entity, type)).join("")
      : `<div class="entity-empty-state"><strong>No ${escapeHtml(meta.plural.toLowerCase())} yet.</strong><p>This category will appear here as the knowledge graph grows.</p></div>`;

    return `<section class="entity-type-group" id="${sectionId}" data-entity-section="${type}">
      <div class="section-head">
        <div><p class="kicker">${escapeHtml(meta.singular)}</p><h2>${meta.icon} ${escapeHtml(meta.plural)}</h2></div>
        <p class="entity-section-count"><strong>${entities.length}</strong> ${escapeHtml(countLabel)}</p>
      </div>
      <div class="entity-directory-list">${cards}</div>
    </section>`;
  }

  function navMarkup(type, count){
    const meta = labels[type];
    return `<a class="entity-quick-nav-link" href="#${slugFor(type)}" data-nav-type="${type}">
      <span>${meta.icon} ${escapeHtml(meta.plural)}</span><strong>${count}</strong>
    </a>`;
  }

  function activateNavigation(){
    const links = [...document.querySelectorAll(".entity-quick-nav-link")];
    const sections = [...document.querySelectorAll("[data-entity-section]")];

    links.forEach(link => {
      link.addEventListener("click", event => {
        const target = document.querySelector(link.getAttribute("href"));
        if(!target) return;
        event.preventDefault();
        target.scrollIntoView({behavior:"smooth", block:"start"});
        history.replaceState(null, "", link.getAttribute("href"));
      });
    });

    const observer = new IntersectionObserver(entries => {
      const visible = entries
        .filter(entry => entry.isIntersecting)
        .sort((a,b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top))[0];
      if(!visible) return;
      const type = visible.target.dataset.entitySection;
      links.forEach(link => link.classList.toggle("is-active", link.dataset.navType === type));
      const active = links.find(link => link.dataset.navType === type);
      if(active) active.scrollIntoView({behavior:"smooth", block:"nearest", inline:"center"});
    }, {rootMargin:"-24% 0px -62% 0px", threshold:[0,0.05,0.2]});

    sections.forEach(section => observer.observe(section));
  }

  function activateBackToTop(){
    if(!backToTop) return;
    const update = () => backToTop.classList.toggle("is-visible", window.scrollY > 700);
    window.addEventListener("scroll", update, {passive:true});
    update();
    backToTop.addEventListener("click", () => window.scrollTo({top:0, behavior:"smooth"}));
  }

  async function init(){
    try{
      const response = await fetch("../data/entity-index.json");
      if(!response.ok) throw new Error(`Entity index request failed (${response.status})`);
      const index = await response.json();
      const entities = Array.isArray(index.entities) ? index.entities : [];
      const grouped = Object.fromEntries(order.map(type => [type, []]));

      for(const entity of entities){
        if(grouped[entity.type]) grouped[entity.type].push(entity);
      }
      for(const type of order){
        grouped[type].sort((a,b) => String(a.name || "").localeCompare(String(b.name || "")));
      }

      directory.innerHTML = order.map(type => groupMarkup(type, grouped[type])).join("");
      navList.innerHTML = order.map(type => navMarkup(type, grouped[type].length)).join("");
      activateNavigation();
      activateBackToTop();
    }catch(error){
      console.error(error);
      directory.innerHTML = `<div class="entity-empty-state"><strong>Entity Explorer could not be loaded.</strong><p>Please refresh the page and try again.</p></div>`;
      navList.innerHTML = `<span class="entity-nav-loading">Categories unavailable</span>`;
      activateBackToTop();
    }
  }

  init();
})();
