import starlight from '@astrojs/starlight';
import { defineConfig } from 'astro/config';
import starlightLinksValidator from 'starlight-links-validator';

const description =
  'Claude Code agents, slash commands and Copier templates that take a product from a new repo to Kubernetes via GitOps: secrets, Postgres, OpenTelemetry and Kyverno guard rails are one declaration each.';

export default defineConfig({
  site: 'https://ika100.github.io',
  base: '/claude-platform',
  trailingSlash: 'always',
  integrations: [
    starlight({
      title: 'claude-platform',
      description,
      favicon: '/favicon.svg',
      social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/ika100/claude-platform' }],
      customCss: ['./src/styles/custom.css'],
      components: { Footer: './src/components/Footer.astro' },
      lastUpdated: false,
      pagination: true,
      head: [
        { tag: 'meta', attrs: { name: 'theme-color', content: '#4f46e5' } },
        { tag: 'meta', attrs: { property: 'og:type', content: 'website' } },
        { tag: 'meta', attrs: { name: 'keywords', content: 'claude code, gitops, kubernetes, argocd, copier, devbox, platform engineering, opentelemetry, kyverno' } },
      ],
      plugins: [starlightLinksValidator({ errorOnRelativeLinks: false, errorOnInvalidHashes: false })],
      sidebar: [
        {
          label: 'Why claude-platform',
          items: [
            { label: 'Vision', slug: 'vision' },
            { label: 'The problem', slug: 'problem' },
            { label: 'Client value', slug: 'value' },
            { label: 'Usage scenarios', slug: 'scenarios' },
          ],
        },
        { label: 'Get started', items: [{ label: 'Your first product', slug: 'get-started' }, { label: 'Run it on your laptop', slug: 'get-started/local-cluster' }] },
        { label: 'Concepts', items: [{ autogenerate: { directory: 'concepts' } }] },
        { label: 'Guides', items: [{ autogenerate: { directory: 'guides' } }] },
        {
          label: 'Reference',
          items: [
            { label: 'Slash commands', slug: 'reference/commands' },
            { label: 'Shapes', slug: 'reference/shapes' },
            { label: 'Configuration', slug: 'reference/configuration' },
            { label: 'The cplat CLI', slug: 'reference/cplat' },
            { label: 'Measured baselines', slug: 'reference/baselines' },
            { label: 'Architecture decisions', collapsed: true, items: [{ autogenerate: { directory: 'reference/adr' } }] },
            { label: 'Changelog', slug: 'reference/changelog' },
          ],
        },
        { label: 'Design history', collapsed: true, items: [{ slug: 'vision/design-history' }, { slug: 'vision/end-to-end-scenario' }] },
        { label: 'Community', items: [{ autogenerate: { directory: 'community' } }] },
      ],
    }),
  ],
});
