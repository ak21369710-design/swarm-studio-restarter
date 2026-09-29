"""Start the Lightning Studio if it has stopped (free Studios stop every 4 hours).

Run from GitHub Actions. The Studio's on_start.sh then launches the swarm.
Needs env: LIGHTNING_USER_ID, LIGHTNING_API_KEY, and optionally LIGHTNING_TEAMSPACE,
LIGHTNING_ORG / LIGHTNING_USER, SWARM_STUDIO (default "swarm").
LOOP_MINUTES > 0 keeps checking every CHECK_EVERY seconds for that long (GitHub's cron
runs hours late, so one long run watching the Studio is the reliable way).
"""
import os
import time

from lightning_sdk import Machine, Studio
from lightning_sdk.status import Status

where = {k: os.environ[f"LIGHTNING_{k.upper()}"] for k in ("teamspace", "org", "user") if os.environ.get(f"LIGHTNING_{k.upper()}")}
studio = Studio(name=os.environ.get("SWARM_STUDIO", "swarm"), create_ok=False, **where)
end = time.time() + 60 * int(os.environ.get("LOOP_MINUTES", "0"))
every = int(os.environ.get("CHECK_EVERY", "300"))

while True:
    try:
        status = studio.status
        print(f"{time.strftime('%H:%M:%S')} studio status: {status.name}", flush=True)
        if status in (Status.Stopped, Status.Completed, Status.Failed):
            studio.start(Machine.CPU)
            print("started", flush=True)
    except Exception as e:  # a network blip must not end the watch
        print(f"check failed: {type(e).__name__}: {e}", flush=True)
    if time.time() + every > end:
        break
    time.sleep(every)
