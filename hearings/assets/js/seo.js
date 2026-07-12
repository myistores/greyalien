(() => {
  const config = window.GREYALIEN_CONFIG || {};

  function ensureMeta(selector, attrs) {
    let node = document.head.querySelector(selector);
    if (!node) {
      node = document.createElement('meta');
      document.head.appendChild(node);
    }
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  }

  function ensureLink(rel, href) {
    let node = document.head.querySelector(`link[rel="${rel}"]`);
    if (!node) {
      node = document.createElement('link');
      node.rel = rel;
      document.head.appendChild(node);
    }
    node.href = href;
    return node;
  }

  window.GreyAlienSEO = {
    apply({
      title = config.defaultTitle,
      description = config.defaultDescription,
      canonical = location.href.split('#')[0],
      image = config.defaultImage,
      type = 'website',
      jsonLd = null
    } = {}) {
      document.title = title;

      ensureMeta('meta[name="description"]', { name: 'description', content: description });
      ensureMeta('meta[property="og:title"]', { property: 'og:title', content: title });
      ensureMeta('meta[property="og:description"]', { property: 'og:description', content: description });
      ensureMeta('meta[property="og:type"]', { property: 'og:type', content: type });
      ensureMeta('meta[property="og:url"]', { property: 'og:url', content: canonical });
      ensureMeta('meta[property="og:image"]', { property: 'og:image', content: image });
      ensureMeta('meta[name="twitter:card"]', { name: 'twitter:card', content: config.twitterCard || 'summary_large_image' });
      ensureMeta('meta[name="twitter:title"]', { name: 'twitter:title', content: title });
      ensureMeta('meta[name="twitter:description"]', { name: 'twitter:description', content: description });
      ensureMeta('meta[name="twitter:image"]', { name: 'twitter:image', content: image });

      if (config.googleSiteVerification) {
        ensureMeta('meta[name="google-site-verification"]', {
          name: 'google-site-verification',
          content: config.googleSiteVerification
        });
      }

      if (config.bingSiteVerification) {
        ensureMeta('meta[name="msvalidate.01"]', {
          name: 'msvalidate.01',
          content: config.bingSiteVerification
        });
      }

      ensureLink('canonical', canonical);

      document.querySelectorAll('script[data-greyalien-jsonld]').forEach(node => node.remove());
      if (jsonLd) {
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.dataset.greyalienJsonld = 'true';
        script.textContent = JSON.stringify(jsonLd);
        document.head.appendChild(script);
      }
    }
  };
})();
