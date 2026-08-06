import json
import subprocess
import time
from collections.abc import Callable
from typing import Any

from shared_dotfiles.python_helper import is_hyprland


def window_exists(class_name: str) -> bool:
    """True if at least one window of that class is mapped."""
    if is_hyprland():
        return len(_hypr_clients(class_name)) > 0
    try:
        out = subprocess.run(
            ["xdotool", "search", "--class", class_name],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        return len(out.split()) > 0
    except subprocess.CalledProcessError:
        return False


def _hyprctl(*args: str) -> str:
    return subprocess.run(
        ["hyprctl", *args], check=True, capture_output=True, text=True
    ).stdout


def _dispatch(lua: str) -> None:
    """hyprctl wraps the argument in hl.dispatch(...), so it must be lua."""
    _hyprctl("dispatch", lua)


def _class_matches(app_id: str, class_name: str) -> bool:
    """Exact, or a reverse-DNS app id ending in the class (io.github.Qalculate.x)."""
    app_id = app_id.lower()
    class_name = class_name.lower()
    return app_id == class_name or app_id.rsplit(".", 1)[-1] == class_name


def _hypr_clients(class_name: str) -> list[dict[str, Any]]:
    clients = json.loads(_hyprctl("-j", "clients"))
    matching = [
        client
        for client in clients
        if any(
            _class_matches(client.get(key) or "", class_name)
            for key in ("class", "initialClass")
        )
    ]
    matching.sort(key=lambda client: int(client["address"], 16))
    return matching


def _hypr_active_workspace() -> dict[str, Any]:
    """Workspace of the focused monitor, never a special one."""
    monitors = json.loads(_hyprctl("-j", "monitors"))
    focused = next((m for m in monitors if m["focused"]), monitors[0])
    return focused["activeWorkspace"]


def _workspace_arg(workspace: dict[str, Any]) -> str:
    # named workspaces have negative ids, which a dispatcher reads as relative
    return f"name:{workspace['name']}" if workspace["id"] < 0 else str(workspace["id"])


def _hypr_focus(address: str) -> None:
    _dispatch(f'hl.dsp.focus({{window="address:{address}"}})')


def _hypr_close(address: str) -> None:
    # window.close takes no target, so the window has to be focused first --
    # without the check below a failed focus would close an unrelated window
    _hypr_focus(address)
    active = json.loads(_hyprctl("-j", "activewindow"))
    if active.get("address") != address:
        print(f"not closing {address}, it could not be focused")
        return
    _dispatch("hl.dsp.window.close()")


def _hypr_move(address: str, workspace: str) -> None:
    _dispatch(
        f'hl.dsp.window.move({{workspace="{workspace}", window="address:{address}"}})'
    )


def _hypr_visible_special() -> str:
    monitors = json.loads(_hyprctl("-j", "monitors"))
    focused = next((m for m in monitors if m["focused"]), monitors[0])
    return focused["specialWorkspace"]["name"]


def _hypr_wait_for_clients(class_name: str) -> list[dict[str, Any]]:
    deadline = time.monotonic() + 10
    while True:
        clients = _hypr_clients(class_name)
        if len(clients) > 0:
            return clients
        if time.monotonic() > deadline:
            raise RuntimeError(f"no window of class {class_name} appeared")
        time.sleep(0.05)


def _hypr_toggle(class_name: str, spawned: bool = False) -> None:
    clients = _hypr_wait_for_clients(class_name)

    client = clients[0]
    for extra in clients[1:]:
        print(f"closing {extra['address']}")
        _hypr_close(extra["address"])
    if len(clients) > 1:
        # closing moved the focus around, so the kept window's state is stale
        client = next(
            (c for c in _hypr_clients(class_name) if c["address"] == client["address"]),
            client,
        )
    address = client["address"]
    scratchpad = f"toggle_{class_name}"
    active_workspace = _hypr_active_workspace()

    elsewhere = client["workspace"]["id"] != active_workspace["id"]
    if elsewhere:
        # stashed in the scratchpad or sitting on another workspace: pull it here
        _hypr_move(address, _workspace_arg(active_workspace))

    # a freshly spawned window is never hidden -- that would swallow the app the
    # keypress just asked for, and its focus may not have settled yet
    if elsewhere or spawned or client["focusHistoryID"] != 0:
        _hypr_focus(address)
    else:
        _hypr_move(address, f"special:{scratchpad}")
        # moving into a special workspace reveals it, so hide it again
        if _hypr_visible_special() == f"special:{scratchpad}":
            _dispatch(f'hl.dsp.workspace.toggle_special("{scratchpad}")')


def _bspwm_toggle(class_name: str) -> None:
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


def _spawn(binary: str) -> None:
    print("Spawning new app")
    # detached from our stdio, otherwise the app holds the caller's pipes open
    subprocess.Popen(
        [binary],
        start_new_session=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def toggle_app(
    binary: str, class_name: str, is_running_func: Callable[[], bool] | None = None
):
    spawned = False

    if is_hyprland():
        # a window is the thing being toggled, and hyprctl lists it even while it
        # sits in the scratchpad -- unlike a pid, which also matches a dying app
        if not _hypr_clients(class_name):
            _spawn(binary)
            spawned = True
        _hypr_toggle(class_name, spawned)
        return

    if is_running_func is not None:
        if not is_running_func():
            _spawn(binary)
            spawned = True
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
            _spawn(binary)
        elif len(pids) > 1:
            for pid in pids[1:]:
                subprocess.run(["kill", str(pid)], check=True)

    _bspwm_toggle(class_name)
