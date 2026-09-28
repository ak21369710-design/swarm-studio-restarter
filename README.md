# swarm-studio-restarter
Every 30 minutes, starts the Lightning AI Studio `swarm` if it has stopped (free Studios stop every 4 hours).
The Studio's `on_start.sh` then launches the swarm. Credentials live only in this repo's Actions secrets.
