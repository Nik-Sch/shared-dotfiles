import subprocess
from typing import Callable, Optional


def toggle_app(
    binary: str, class_name: str, is_running_func: Optional[Callable[[], bool]] = None
):

    if is_running_func is not None:
        if not is_running_func():
            print("Spawning new app")
            subprocess.Popen([binary], start_new_session=True)
    else:
        pids = [
            int(pid)
            for pid in subprocess.run(
                ["pidof", binary],
                check=False,  # pidof returns error when no pid found
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .split()
        ]
        pids.sort()
        if len(pids) == 0:
            print("Spawning new app")
            subprocess.Popen([binary], start_new_session=True)
        elif len(pids) > 1:
            for pid in pids[1:]:
                subprocess.run(["kill", str(pid)], check=True)

    ids = sorted(
        [
            int(id)
            for id in subprocess.run(
                ["xdotool", "search", "--class", class_name],
                check=True,
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .split()
        ]
    )
    if len(ids) > 1:
        for id in ids[1:]:
            print(f"closing {id}")
            subprocess.run(["xdotool", "windowclose", str(id)])
    id = ids[0]
    subprocess.run(["bspc", "node", str(id), "-d", "focused"])
    subprocess.run(["bspc", "node", str(id), "--flag", "hidden", "-f"])
