FROM searxng/searxng:latest

COPY settings.yml /etc/searxng/settings.yml
COPY searx/engines/google_api.py /usr/local/searxng/searx/engines/google_api.py

ENV SEARXNG_SETTINGS_PATH=/etc/searxng/settings.yml
