(() => {
  const config = window.GREYALIEN_CONFIG || {};
  const measurementId = config.ga4MeasurementId;

  if (measurementId) {
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`;
    document.head.appendChild(tag);

    window.dataLayer = window.dataLayer || [];
    window.gtag = function(){ window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', measurementId, {
      send_page_view: true,
      anonymize_ip: true
    });
  }

  const clarityId = config.microsoftClarityProjectId;
  if (clarityId) {
    (function(c,l,a,r,i,t,y){
      c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", clarityId);
  }

  document.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link) return;

    const href = link.getAttribute('href') || '';
    const label = (link.dataset.analyticsLabel || link.textContent || '').trim().slice(0, 100);

    if (href.startsWith('http') && !href.includes(location.hostname)) {
      window.gtag?.('event', 'outbound_link_click', {
        link_url: href,
        link_text: label
      });
    }

    if (
      href.includes('/hearings/') ||
      href.includes('/categories/') ||
      link.classList.contains('topic-chip') ||
      link.classList.contains('hearing-nav-card')
    ) {
      window.gtag?.('event', 'knowledge_navigation', {
        destination_url: href,
        navigation_label: label,
        source_path: location.pathname + location.search
      });
    }
  });
})();
