# eclears-updater

A Render web service that exposes a health endpoint for UptimeRobot and updates Scratch cloud variables.

## Render

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --workers 1 --threads 4 --timeout 0 app:app`
- Add `SCRATCH_USERNAME` and `SCRATCH_PASSWORD` as environment variables.
- Do not commit your Scratch password; use `.env.example` only as a template.

## UptimeRobot

Monitor:

`https://YOUR-RENDER-SERVICE.onrender.com/health`

The free Render service may still sleep depending on Render's current plan rules; UptimeRobot cannot guarantee that a provider will remain awake.
