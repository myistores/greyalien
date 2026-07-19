(function(){
  const roleLabels={host:'Host',co_host:'Co-host',guest:'Guest',primary_subject:'Primary subject',co_subject:'Co-subject',interviewer:'Interviewer',mentioned:'Mentioned',referenced:'Referenced',creator:'Creator',producer:'Producer',narrator:'Narrator',publisher:'Publisher',claimant:'Claimant',participant:'Participant',location:'Location',associated_location:'Associated location',discussed:'Discussed',related_media:'Related media',related_topic:'Related topic',related_claim:'Related claim',documented_by:'Documented by',investigator:'Investigated by'};
  const typeLabels={person:'People',hearing:'Hearings',organization:'Organizations',document:'Documents',topic:'Topics',case:'Cases',interview:'Media',podcast_episode:'Media',legislation:'Legislation',timeline_event:'Timeline',publication:'Publications',claim:'Claims',podcast_series:'Podcast Series'};
  const icons={person:'👤',hearing:'🏛️',organization:'🏢',document:'📄',topic:'🧭',case:'🛸',interview:'🎙️',podcast_episode:'🎙️',legislation:'📜',timeline_event:'🕒',publication:'📰',claim:'⚖️',podcast_series:'🎙️'};
  const score=e=>(e.meta.role?10:0)+(e.meta.context?2:0)+(e.direction==='incoming'?1:0);
  function buildGraph(entities,vocabulary){
    const map=Object.fromEntries(entities.map(e=>[e.id,e]));
    const edges=[];
    entities.forEach(source=>(source.relationships||[]).forEach(meta=>{if(map[meta.target]&&vocabulary[meta.type]) edges.push({source:source.id,target:meta.target,type:meta.type,meta});}));
    return {map,edges,vocabulary};
  }
  function connectionsFor(graph,id){
    const raw=[
      ...graph.edges.filter(e=>e.source===id).map(e=>({...e,direction:'outgoing',other:graph.map[e.target],label:roleLabels[e.meta.role]||graph.vocabulary[e.type].forward})),
      ...graph.edges.filter(e=>e.target===id).map(e=>({...e,direction:'incoming',other:graph.map[e.source],label:roleLabels[e.meta.role]||graph.vocabulary[e.type].reverse}))
    ];
    const deduped=new Map(); raw.forEach(e=>{const old=deduped.get(e.other.id);if(!old||score(e)>score(old))deduped.set(e.other.id,e)});
    return {raw,unique:[...deduped.values()]};
  }
  function groupByType(connections){return connections.reduce((a,e)=>((a[e.other.type]??=[]).push(e),a),{});}
  window.GreyAlienGraph={roleLabels,typeLabels,icons,buildGraph,connectionsFor,groupByType};
})();
