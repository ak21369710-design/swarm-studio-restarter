"""Start the Lightning Studio if it has stopped (free Studios stop every 4 hours).

Run on a schedule (GitHub Actions). The Studio's on_start.sh then launches the swarm.
Needs env: LIGHTNING_USER_ID, LIGHTNING_API_KEY, and optionally LIGHTNING_TEAMSPACE,
LIGHTNING_ORG / LIGHTNING_USER, SWARM_STUDIO (default "swarm").
"""
import os

from lightning_sdk import Machine, Studio
from lightning_sdk.status import Status

where = {k: os.environ[f"LIGHTNING_{k.upper()}"] for k in ("teamspace", "org", "user") if os.environ.get(f"LIGHTNING_{k.upper()}")}
studio = Studio(name=os.environ.get("SWARM_STUDIO", "swarm"), create_ok=False, **where)
status = studio.status
print(f"studio status: {status.name}")
if status in (Status.Stopped, Status.Completed, Status.Failed):
    studio.start(Machine.CPU)
    print("started")
