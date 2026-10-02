"""Keep the Lightning Studio running on the FREE CPU machine (free Studios stop every 4 hours).

Run from GitHub Actions. The Studio's on_start.sh then launches the swarm.
Needs env: LIGHTNING_USER_ID, LIGHTNING_API_KEY, and optionally LIGHTNING_TEAMSPACE,
LIGHTNING_ORG / LIGHTNING_USER, SWARM_STUDIO (default "swarm").
LOOP_MINUTES > 0 keeps checking every CHECK_EVERY seconds for that long (GitHub's cron
runs hours late, so one long run watching the Studio is the reliable way).

Spend guard (Amit's no-spend rule): if the Studio is ever on anything but the free CPU machine
(a GPU, a bigger machine, or interruptible/spot), it is stopped at once and the run fails at the
end, so GitHub emails the repo owner. The next check starts it again on the free CPU machine.
This works even if something on the Studio ignores the rule.
"""
import os
import sys
import threading
import time

from lightning_sdk import Machine, Studio
from lightning_sdk.status import Status

where = {k: os.environ[f"LIGHTNING_{k.upper()}"] for k in ("teamspace", "org", "user") if os.environ.get(f"LIGHTNING_{k.upper()}")}
studio = Studio(name=os.environ.get("SWARM_STUDIO", "swarm"), create_ok=False, **where)
end = time.time() + 60 * int(os.environ.get("LOOP_MINUTES", "0"))
every = int(os.environ.get("CHECK_EVERY", "300"))
START_WAIT = 120  # seconds to wait for start() before carrying on with the watch
alarms = []

while True:
    try:
        status = studio.status
        print(f"{time.strftime('%H:%M:%S')} studio status: {status.name}", flush=True)
        if status in (Status.Stopped, Status.Completed, Status.Failed):
            # studio.start() can block for a long time; run it in the background so the watch never hangs
            t = threading.Thread(target=lambda: studio.start(Machine.CPU), daemon=True)
            t.start()
            t.join(START_WAIT)
            print("start requested on the free CPU machine" + ("" if not t.is_alive() else f" (still starting after {START_WAIT}s)"), flush=True)
        elif status == Status.Running:
            machine, spot = studio.machine, bool(getattr(studio, "interruptible", False))
            if machine != Machine.CPU or spot:
                msg = f"SPEND GUARD: Studio was on {machine} (interruptible={spot}), not the free CPU machine; stopping it"
                print(f"::error::{msg}", flush=True)
                alarms.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} UTC {msg}")
                studio.stop()
    except Exception as e:  # a network blip must not end the watch
        print(f"check failed: {type(e).__name__}: {e}", flush=True)
    if time.time() + every > end:
        break
    time.sleep(every)

if alarms:
    print("\n".join(alarms), flush=True)
    sys.exit(1)  # fail the run so GitHub emails the owner
