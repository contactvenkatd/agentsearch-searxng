# AgentSearch SearXNG instance

Custom SearXNG deployment for AgentSearch's branded search results page.
Extends the official `searxng/searxng:latest` image with JSON API output
enabled and the request limiter configured for programmatic access.

## Why this exists

The stock SearXNG image ships with JSON output disabled and a bot-detection
limiter that blocks non-browser requests by default. This repo overrides
both via a custom `settings.yml` baked into the image at build time — the
default image doesn't support mounting config files after deploy, so this
needed a real Dockerfile rather than a dashboard setting.

## Deploying to Render

This repo deploys as a Render Web Service, "Deploy from a Git repository"
mode instead of "Existing Image" — Render needs to build the Dockerfile,
not just pull the base image.

Environment variable required: `SEARXNG_SECRET` (already generated in the
existing Render service — reuse the same value). SearXNG's settings loader
automatically applies this environment variable as the runtime override for
`server.secret_key`, so no secret or placeholder is stored in `settings.yml`.

The Render service should use:

- Runtime: Docker
- Repository root: this directory (or `/` if this directory is its own repo)
- Dockerfile path: `./Dockerfile`
- Health check path: `/`
- Environment: preserve the existing `SEARXNG_SECRET`

## Verifying it works

```
curl "https://<your-render-url>/search?q=test&format=json"
```

Should return JSON, not a 403.
