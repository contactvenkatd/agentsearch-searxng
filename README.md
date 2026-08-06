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

## Google API engine on Render

The custom `google_api` engine calls the official Google Programmable Search
JSON API. Configure these secret environment variables on the Render service:

- `GOOGLE_API_KEY`: an API key authorized for the Custom Search JSON API.
- `GOOGLE_CSE_ID`: the Programmable Search Engine identifier (`cx`).

The engine reads both values directly from the container environment during
startup. Never put their values in `settings.yml`, the Dockerfile, Render build
arguments, logs, or commits. A missing value prevents the engine from loading;
authentication and quota errors yield no Google results without interrupting
the other SearXNG engines.

## Native Google primary search

AgentSearch general web searches use the official Google Programmable Search
JSON API before falling back to this SearXNG instance. Configure the native
browser process at runtime with:

- `AGENTSEARCH_GOOGLE_SEARCH_API_KEY`: an API key authorized for the Custom
  Search JSON API.
- `AGENTSEARCH_GOOGLE_SEARCH_ENGINE_ID`: the Programmable Search Engine ID
  (`cx`).

OAuth client IDs and client secrets are unrelated and must not be used for
these values. Never store either search credential in source code, `args.gn`,
generated resources, the application bundle, shell history, or commits.
Google currently limits this API to eligible existing customers and documents
a January 1, 2027 transition deadline, so confirm current API availability for
the Google Cloud project before configuring AgentSearch.

For local development, load the values into the launching shell without
printing them, then start the browser from that same shell:

```sh
export AGENTSEARCH_GOOGLE_SEARCH_API_KEY="<local-secret>"
export AGENTSEARCH_GOOGLE_SEARCH_ENGINE_ID="<local-engine-id>"
out/Vanilla/AgentSearch.app/Contents/MacOS/AgentSearch \
  --user-data-dir=/tmp/agentsearch-google-search \
  --no-first-run --enable-logging=stderr --v=1
```

If either variable is absent, or Google reports an authentication, quota,
timeout, malformed-response, or empty-result failure, Chromium falls back in
this order:

1. Bing
2. Brave
3. Yahoo
4. Dogpile
5. Fynd

The browser stops after the first usable provider response. Category searches
(News, Images, Videos, and Maps) continue to use SearXNG directly. For Google
HTTP 401/403 responses, verify API enablement, API-key restrictions, and the
`cx`. For quota failures, inspect the Custom Search JSON API quota in Google
Cloud; do not log or paste the key while troubleshooting.

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
