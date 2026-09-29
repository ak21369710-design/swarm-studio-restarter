# swarm-studio-restarter
Keeps the Lightning AI Studio `swarm` running: checks every 5 minutes and starts it if it has stopped
(free Studios stop every 4 hours). The Studio's `on_start.sh` then launches the swarm.
Credentials live only in this repo's Actions secrets.
