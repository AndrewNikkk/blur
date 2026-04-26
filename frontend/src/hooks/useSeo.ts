import { useEffect } from 'react';

type SeoOptions = {
  title: string;
  description: string;
  canonicalPath?: string;
  noindex?: boolean;
  ogType?: string;
  ogImage?: string;
  jsonLd?: Record<string, unknown>;
};

function upsertMetaTag(
  selector: string,
  create: () => HTMLMetaElement,
  setContent: (meta: HTMLMetaElement) => void
) {
  let meta = document.head.querySelector(selector) as HTMLMetaElement | null;
  if (!meta) {
    meta = create();
    document.head.appendChild(meta);
  }
  setContent(meta);
}

export function useSeo({
  title,
  description,
  canonicalPath,
  noindex = false,
  ogType = 'website',
  ogImage,
  jsonLd,
}: SeoOptions) {
  useEffect(() => {
    document.title = title;

    upsertMetaTag(
      'meta[name="description"]',
      () => {
        const meta = document.createElement('meta');
        meta.setAttribute('name', 'description');
        return meta;
      },
      (meta) => meta.setAttribute('content', description)
    );

    upsertMetaTag(
      'meta[name="robots"]',
      () => {
        const meta = document.createElement('meta');
        meta.setAttribute('name', 'robots');
        return meta;
      },
      (meta) => meta.setAttribute('content', noindex ? 'noindex,nofollow' : 'index,follow')
    );

    const canonicalHref = canonicalPath
      ? `${window.location.origin}${canonicalPath}`
      : window.location.href;

    let canonical = document.head.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.setAttribute('rel', 'canonical');
      document.head.appendChild(canonical);
    }
    canonical.setAttribute('href', canonicalHref);

    upsertMetaTag(
      'meta[property="og:title"]',
      () => {
        const meta = document.createElement('meta');
        meta.setAttribute('property', 'og:title');
        return meta;
      },
      (meta) => meta.setAttribute('content', title)
    );

    upsertMetaTag(
      'meta[property="og:description"]',
      () => {
        const meta = document.createElement('meta');
        meta.setAttribute('property', 'og:description');
        return meta;
      },
      (meta) => meta.setAttribute('content', description)
    );

    upsertMetaTag(
      'meta[property="og:type"]',
      () => {
        const meta = document.createElement('meta');
        meta.setAttribute('property', 'og:type');
        return meta;
      },
      (meta) => meta.setAttribute('content', ogType)
    );

    upsertMetaTag(
      'meta[property="og:url"]',
      () => {
        const meta = document.createElement('meta');
        meta.setAttribute('property', 'og:url');
        return meta;
      },
      (meta) => meta.setAttribute('content', canonicalHref)
    );

    if (ogImage) {
      upsertMetaTag(
        'meta[property="og:image"]',
        () => {
          const meta = document.createElement('meta');
          meta.setAttribute('property', 'og:image');
          return meta;
        },
        (meta) => meta.setAttribute('content', ogImage)
      );
    }

    const existingJsonLd = document.head.querySelector('script[data-seo-jsonld="true"]');
    if (existingJsonLd) {
      existingJsonLd.remove();
    }

    if (jsonLd) {
      const script = document.createElement('script');
      script.type = 'application/ld+json';
      script.dataset.seoJsonld = 'true';
      script.text = JSON.stringify(jsonLd);
      document.head.appendChild(script);
    }
  }, [title, description, canonicalPath, noindex, ogType, ogImage, jsonLd]);
}

