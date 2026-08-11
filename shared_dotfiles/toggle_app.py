import subprocess
import time
from collections.abc import Callable

from python_helper import is_hyprland


def toggle_app_hyprland(binary: str, class_name: str):
    # Show/hide via the app's dedicated special workspace (see its hl.window_rule).
    pids = [
        int(pid)
        for pid in subprocess.run(
            ["pidof", binary], check=False, capture_output=True, text=True
        )
        .stdout.strip()
        .split()
    ]
    pids.sort()
    if not pids:
        print("Spawning new app")
        subprocess.Popen([binary], start_new_session=True)
        time.sleep(1)  # give it a moment to map into its special workspace
    else:
        for pid in pids[1:]:
            subprocess.run(["kill", str(pid)], check=True)

    subprocess.run(
        ["hyprctl", "dispatch", f'hl.dsp.workspace.toggle_special("{class_name}")']
    )


def toggle_app_bspwm(
    binary: str, class_name: str, is_running_func: Callable[[], bool] | None = None
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
                ["xdotool", "search", "--sync", "--class", class_name],
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


def toggle_app(
    binary: str, class_name: str, is_running_func: Callable[[], bool] | None = None
):
    if is_hyprland():
        toggle_app_hyprland(binary, class_name)
    else:
        toggle_app_bspwm(binary, class_name, is_running_func)
