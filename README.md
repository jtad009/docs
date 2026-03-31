# Flagmint Documentation

Source for [docs.flagmint.com](https://docs.flagmint.com), powered by [Mintlify](https://mintlify.com).

## Local Development

```bash
# Install the Mintlify CLI
npm i -g mintlify

# Start the dev server
mintlify dev
```

Open http://localhost:3000 to preview.

## Structure

```
flagmint-docs/
├── docs.json                 # Mintlify configuration (nav, branding, settings)
├── getting-started/          # Intro, quickstart, concepts, tutorial
├── sdks/                     # React, Vue, Node.js, REST API
├── platform/                 # Flags, targeting, segments, rollouts, etc.
├── billing/                  # Plans, usage, subscriptions
├── security/                 # GDPR, data residency, DPA, security practices
├── api-reference/            # Auth, evaluation endpoint, management APIs
├── resources/                # Migration guide, best practices, troubleshooting
├── images/                   # Screenshots and diagrams
├── logo/                     # Light/dark logos
└── snippets/                 # Reusable MDX snippets
```

## Writing Content

Pages are MDX files (Markdown + components). Mintlify provides built-in components:

- `<Card>`, `<CardGroup>` — linked cards
- `<Steps>`, `<Step>` — step-by-step instructions
- `<CodeGroup>` — tabbed code blocks
- `<Accordion>`, `<AccordionGroup>` — collapsible sections
- `<Info>`, `<Warning>`, `<Tip>`, `<Note>` — callout boxes

See [Mintlify docs](https://mintlify.com/docs) for the full component reference.

## Deploying

Push to `main` and Mintlify auto-deploys via the GitHub integration.
