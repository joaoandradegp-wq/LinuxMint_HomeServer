import tkinter as tk
from tkinter import ttk, messagebox

from pathlib import Path

import subprocess
import re
import socket
import os
import urllib.request

########################################################
# CONSTANTS
########################################################

DIALOG_WIDTH = 420
DIALOG_HEIGHT = 220

STATUS_OK = "#0a7d2c"
STATUS_ERROR = "#c0392b"

########################################################
# STATE
########################################################

SUDO_PASSWORD = None

FILEBROWSER_SERVICE = "filebrowser"
MONITOR_SERVICE = "sevastolink"
MONITOR_PORT = 8181

MONITOR_INSTALL_DIR = Path.home() / "SevastolinkMonitor"
MONITOR_VENV_DIR = MONITOR_INSTALL_DIR / ".venv"
MONITOR_API_PATH = MONITOR_INSTALL_DIR / "api.py"
MONITOR_SERVICE_UNIT_PATH = "/etc/systemd/system/sevastolink.service"
MONITOR_INSTALL_STEPS = 10

MONITOR_API_PY = '''from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn, psutil, socket, subprocess, platform, os, time
from datetime import timedelta

app = FastAPI(title="Sevastolink Monitor")

def run(cmd):
    try:
        return subprocess.check_output(cmd,shell=True,text=True,stderr=subprocess.DEVNULL).strip()
    except:
        return ""

def svc(name):
    return "ONLINE" if run(f"systemctl is-active {name}")=="active" else "OFFLINE"

def cpu_model():
    return run("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d ':' -f2").strip()

def cpu_temp():
    try:
        for v in psutil.sensors_temperatures().values():
            for e in v:
                return round(e.current,1)
    except:
        pass
    return None

def iface():
    for n,s in psutil.net_if_stats().items():
        if s.isup and n!="lo" and not n.startswith("tailscale"):
            return n
    return ""

IFACE=iface()
old=psutil.net_io_counters(pernic=True)
oldt=time.time()

def speed():
    global old,oldt
    if IFACE not in psutil.net_io_counters(pernic=True): return (0,0)
    now=time.time()
    cur=psutil.net_io_counters(pernic=True)
    dt=max(now-oldt,0.001)
    d=(cur[IFACE].bytes_recv-old[IFACE].bytes_recv)/dt/1024/1024
    u=(cur[IFACE].bytes_sent-old[IFACE].bytes_sent)/dt/1024/1024
    old,oldt=cur,now
    return round(d,2),round(u,2)

def ip():
    for a in psutil.net_if_addrs().get(IFACE,[]):
        if a.family==socket.AF_INET:
            return a.address
    return "Offline"

def linkspeed():
    p=f"/sys/class/net/{IFACE}/speed"
    try:
        s=int(open(p).read().strip())
        return f"{s//1000} Gb/s" if s>=1000 else f"{s} Mb/s"
    except:
        return "Unknown"

@app.get("/api/rainmeter", response_class=PlainTextResponse)
def rain():
    cpu=psutil.cpu_percent(interval=0.5)
    mem=psutil.virtual_memory()
    sw=psutil.swap_memory()
    dk=psutil.disk_usage("/")
    down,up=speed()
    uptime=str(timedelta(seconds=int(time.time()-psutil.boot_time())))
    tsip=run("ip -4 addr show tailscale0 | grep inet | awk '{print $2}' | cut -d/ -f1") or "Offline"
    lines=[
        f"HOSTNAME={platform.node()}",
        f"CPU_MODEL={cpu_model()}",
        f"CPU_CORES={psutil.cpu_count(logical=False)}",
        f"CPU_THREADS={psutil.cpu_count(logical=True)}",
        f"CPU_FREQ={round(psutil.cpu_freq().current/1000,2)}",
        f"CPU_TEMP={cpu_temp()}",
        f"CPU_USAGE={cpu}",
        f"RAM_USED={round(mem.used/1024**3,2)}",
        f"RAM_TOTAL={round(mem.total/1024**3,2)}",
        f"RAM_PERCENT={mem.percent}",
        f"SWAP_USED={round(sw.used/1024**3,2)}",
        f"SWAP_TOTAL={round(sw.total/1024**3,2)}",
        f"SWAP_PERCENT={sw.percent}",
        f"DISK_USED={round(dk.used/1024**3,2)}",
        f"DISK_TOTAL={round(dk.total/1024**3,2)}",
        f"DISK_PERCENT={dk.percent}",
        f"LAN_IP={ip()}",
        f"DOWNLOAD={down}",
        f"UPLOAD={up}",
        f"LINK_SPEED={linkspeed()}",
        f"FILEBROWSER={svc('filebrowser')}",
        f"TAILSCALE={svc('tailscaled')}",
        f"TAILSCALE_IP={tsip}",
        f"UPTIME={uptime}"
    ]
    return "\\n".join(lines)

if __name__=="__main__":
    uvicorn.run("api:app",host="0.0.0.0",port=8181)
'''

########################################################
# ROOT
########################################################

root = tk.Tk()

root.title("Home Server Control Panel")
root.geometry("640x480")
root.minsize(430, 280)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab_shares = ttk.Frame(notebook)
tab_conky = ttk.Frame(notebook)
tab_filebrowser = ttk.Frame(notebook)
tab_monitor = ttk.Frame(notebook)

notebook.add(tab_shares, text="Shares")
notebook.add(tab_conky, text="Conky")
notebook.add(tab_filebrowser, text="FileBrowser")
notebook.add(tab_monitor, text="Server Monitor")

########################################################
# LAYOUT HELPERS
########################################################

def build_page(parent, title, subtitle):
    """Creates the standard page skeleton: header, bottom toolbar, content area."""

    header = ttk.Frame(parent, padding=10)
    header.pack(fill="x")

    ttk.Label(header, text=title, font=("Segoe UI", 16, "bold")).pack(anchor="w")
    ttk.Label(header, text=subtitle).pack(anchor="w")

    toolbar = ttk.Frame(parent, padding=10)
    toolbar.pack(fill="x", side="bottom")

    content = ttk.Frame(parent, padding=10)
    content.pack(fill="both", expand=True)

    return content, toolbar


def build_treeview(content, columns, headings, widths):

    tree = ttk.Treeview(content, columns=columns, show="headings")

    for col, head, width in zip(columns, headings, widths):
        tree.heading(col, text=head)
        tree.column(col, width=width)

    scroll = ttk.Scrollbar(content, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    return tree


def status_badge(parent):
    """Plain colored-text label used to show ONLINE / OFFLINE."""
    return ttk.Label(parent, text="-")


def set_status_badge(label, active):

    if active:
        label.config(text="ONLINE", foreground=STATUS_OK)
    else:
        label.config(text="OFFLINE", foreground=STATUS_ERROR)


def center_dialog(win, width, height):

    root.update_idletasks()

    x = root.winfo_x() + root.winfo_width() // 2 - width // 2
    y = root.winfo_y() + root.winfo_height() // 2 - height // 2

    win.geometry(f"{width}x{height}+{x}+{y}")


def open_dialog(title, width=DIALOG_WIDTH, height=DIALOG_HEIGHT):

    win = tk.Toplevel(root)

    win.title(title)

    center_dialog(win, width, height)

    win.resizable(False, False)
    win.transient(root)
    win.grab_set()

    return win

########################################################
# SUDO HELPER
########################################################

def ask_sudo_password():

    global SUDO_PASSWORD

    win = open_dialog("Administrator Password", 380, 190)

    frame = ttk.Frame(win, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Administrator Password", font=("Segoe UI", 11, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Required to manage system services.").pack(anchor="w", pady=(2, 12))

    entry = ttk.Entry(frame, show="*")
    entry.pack(fill="x")
    entry.focus()

    result = {"value": None}

    def confirm():
        result["value"] = entry.get()
        win.destroy()

    def cancel():
        result["value"] = None
        win.destroy()

    btns = ttk.Frame(frame)
    btns.pack(fill="x", pady=(20, 0))

    ttk.Button(btns, text="Cancel", command=cancel).pack(side="right")
    ttk.Button(btns, text="Confirm", command=confirm).pack(side="right", padx=5)

    win.bind("<Return>", lambda e: confirm())
    win.bind("<Escape>", lambda e: cancel())

    win.wait_window()

    SUDO_PASSWORD = result["value"] if result["value"] else None


def run_sudo(cmd):
    """Runs a command with sudo, feeding the cached password via stdin
    so the user is never dropped into a terminal prompt."""

    global SUDO_PASSWORD

    if SUDO_PASSWORD is None:

        ask_sudo_password()

        if SUDO_PASSWORD is None:
            return False, "Cancelled by user"

    try:
        result = subprocess.run(
            ["sudo", "-S", "-p", ""] + cmd,
            input=SUDO_PASSWORD + "\n",
            capture_output=True,
            text=True,
            timeout=15
        )

    except Exception as e:
        return False, str(e)

    if result.returncode != 0:

        stderr = (result.stderr or "").lower()

        if "incorrect password" in stderr or "sorry" in stderr or "authentication" in stderr:
            SUDO_PASSWORD = None

        return False, (result.stderr or "Command failed").strip()

    return True, result.stdout.strip()


def service_is_active(name):

    try:
        result = subprocess.run(
            ["systemctl", "is-active", name],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == "active"

    except Exception:
        return False


def start_service(name):

    ok, msg = run_sudo(["systemctl", "start", name])

    if not ok:
        messagebox.showerror("Error", f"Failed to start {name}:\n{msg}")

    return ok


def stop_service(name):

    ok, msg = run_sudo(["systemctl", "stop", name])

    if not ok:
        messagebox.showerror("Error", f"Failed to stop {name}:\n{msg}")

    return ok


def restart_service(name):

    ok, msg = run_sudo(["systemctl", "restart", name])

    if not ok:
        messagebox.showerror("Error", f"Failed to restart {name}:\n{msg}")

    return ok

########################################################
# SHARES TAB
########################################################

def build_shares_tab(parent):

    global tree_shares

    content, toolbar = build_page(
        parent,
        "Samba Shares",
        "Manage folders shared on the network via Samba."
    )

    tree_shares = build_treeview(
        content,
        columns=("name", "path"),
        headings=("Share", "Path"),
        widths=(240, 240)
    )

    def on_double_click(event):

        item = tree_shares.identify_row(event.y)

        if item:
            tree_shares.selection_set(item)
            edit_share(True)

    tree_shares.bind("<Double-1>", on_double_click)

    ttk.Button(toolbar, text="Save", command=save_samba).pack(side="right")
    ttk.Button(toolbar, text="Delete", command=delete_share).pack(side="right", padx=5)
    ttk.Button(toolbar, text="Edit", command=lambda: edit_share(True)).pack(side="right", padx=5)
    ttk.Button(toolbar, text="Add", command=edit_share).pack(side="right", padx=5)


def load_samba():

    tree_shares.delete(*tree_shares.get_children())

    path = Path("/etc/samba/smb.conf")

    if not path.exists():
        return

    txt = path.read_text()

    shares = re.finditer(
        r'\[(.*?)\](.*?)(?=\n\[|\Z)',
        txt,
        re.S
    )

    ignore = ["global", "printers", "print$"]

    for s in shares:

        name = s.group(1).strip()

        if name.lower() in ignore:
            continue

        body = s.group(2)

        m = re.search(r'path\s*=\s*(.+)', body)

        path_value = m.group(1).strip() if m else ""

        tree_shares.insert("", "end", values=(name, path_value))


def edit_share(edit=False):

    item = None
    name = ""
    path_value = ""

    if edit:

        sel = tree_shares.selection()

        if not sel:
            return

        item = sel[0]

        name, path_value = tree_shares.item(item)["values"]

    win = open_dialog("Share")

    frame = ttk.Frame(win, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Share name").pack(anchor="w")

    e_name = ttk.Entry(frame)
    e_name.insert(0, name)
    e_name.pack(fill="x", pady=(5, 12))

    ttk.Label(frame, text="Path").pack(anchor="w")

    e_path = ttk.Entry(frame)
    e_path.insert(0, path_value)
    e_path.pack(fill="x", pady=(5, 12))

    ttk.Label(
        frame,
        text="The folder will be created automatically if it doesn't exist."
    ).pack(anchor="w")

    btns = ttk.Frame(win, padding=(20, 12))
    btns.pack(side="bottom", fill="x")

    def save():

        new_name = e_name.get().strip()
        new_path = e_path.get().strip()

        if not new_name or not new_path:
            messagebox.showwarning("Warning", "Please fill in both fields")
            return

        ok1, m1 = run_sudo(["mkdir", "-p", new_path])
        ok2, m2 = run_sudo(["chmod", "755", new_path])

        if not (ok1 and ok2):
            messagebox.showerror("Error", f"Failed to prepare the folder:\n{m1 or m2}")
            return

        values = (new_name, new_path)

        if edit:
            tree_shares.item(item, values=values)
        else:
            tree_shares.insert("", "end", values=values)

        win.destroy()

    ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right")
    ttk.Button(btns, text="Save", command=save).pack(side="right", padx=5)

    e_name.focus()

    win.bind("<Return>", lambda e: save())
    win.bind("<Escape>", lambda e: win.destroy())


def delete_share():

    sel = tree_shares.selection()

    if sel:
        tree_shares.delete(sel[0])


def save_samba():

    txt = """
[global]

workgroup = WORKGROUP
server string = K7 Server

security = user
map to guest = bad user

min protocol = SMB2

"""

    for item in tree_shares.get_children():

        name, path_value = tree_shares.item(item)["values"]

        txt += f"""

[{name}]
path = {path_value}

browseable = yes
read only = no

guest ok = yes

"""

    Path("/tmp/smb.conf").write_text(txt)

    ok1, m1 = run_sudo(["cp", "/tmp/smb.conf", "/etc/samba/smb.conf"])
    ok2, m2 = run_sudo(["systemctl", "restart", "smbd"])

    if not (ok1 and ok2):
        messagebox.showerror("Error", f"Failed to apply the Samba configuration:\n{m1 or m2}")
        return

    messagebox.showinfo("Saved", "Samba configuration updated")


########################################################
# CONKY TAB
########################################################

def build_conky_tab(parent):

    global tree_conky

    content, toolbar = build_page(
        parent,
        "Conky Disks",
        "Disks displayed in the Conky system monitor."
    )

    tree_conky = build_treeview(
        content,
        columns=("idx", "name", "path"),
        headings=("#", "Name", "Path"),
        widths=(50, 220, 350)
    )

    def on_double_click(event):

        item = tree_conky.identify_row(event.y)

        if item:
            tree_conky.selection_set(item)
            edit_conky(True)

    tree_conky.bind("<Double-1>", on_double_click)

    ttk.Button(toolbar, text="Save", command=save_conky).pack(side="right")
    ttk.Button(toolbar, text="Delete", command=delete_conky).pack(side="right", padx=5)
    ttk.Button(toolbar, text="Edit", command=lambda: edit_conky(True)).pack(side="right", padx=5)
    ttk.Button(toolbar, text="Add", command=edit_conky).pack(side="right", padx=5)


def load_conky():

    tree_conky.delete(*tree_conky.get_children())

    path = Path.home() / ".conkyrc"

    if not path.exists():
        return

    txt = path.read_text()

    pattern = re.findall(
        r'DISK\s+(\d+)\s+\((.*?)\):\$\{color\}\s+\$\{fs_used_perc\s+(.*?)\}',
        txt
    )

    for idx, name, mount in pattern:
        tree_conky.insert("", "end", values=(int(idx), name.strip(), mount.strip()))


def edit_conky(edit=False):

    item = None

    idx = 0
    name = ""
    path_value = ""

    if edit:

        sel = tree_conky.selection()

        if not sel:
            return

        item = sel[0]

        idx, name, path_value = tree_conky.item(item)["values"]

    else:
        idx = len(tree_conky.get_children()) + 1

    win = open_dialog("Conky Disk")

    frame = ttk.Frame(win, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Name").pack(anchor="w")

    e_name = ttk.Entry(frame)
    e_name.insert(0, name)
    e_name.pack(fill="x", pady=(5, 12))

    ttk.Label(frame, text="Path").pack(anchor="w")

    e_path = ttk.Entry(frame)
    e_path.insert(0, path_value)
    e_path.pack(fill="x", pady=(5, 12))

    ttk.Label(
        frame,
        text="This disk will be displayed in the Conky panel."
    ).pack(anchor="w")

    btns = ttk.Frame(win, padding=(20, 12))
    btns.pack(side="bottom", fill="x")

    def save():

        new_name = e_name.get().strip()
        new_path = e_path.get().strip()

        if not new_name or not new_path:
            messagebox.showwarning("Warning", "Please fill in both fields")
            return

        values = (idx, new_name, new_path)

        if edit:
            tree_conky.item(item, values=values)
        else:
            tree_conky.insert("", "end", values=values)

        win.destroy()

    ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right")
    ttk.Button(btns, text="Save", command=save).pack(side="right", padx=5)

    e_name.focus()

    win.bind("<Return>", lambda e: save())
    win.bind("<Escape>", lambda e: win.destroy())


def delete_conky():

    sel = tree_conky.selection()

    if sel:
        tree_conky.delete(sel[0])


def save_conky():

    path = Path.home() / ".conkyrc"

    if not path.exists():
        return

    txt = path.read_text()

    disk_lines = []

    for item in tree_conky.get_children():

        idx, name, path_value = tree_conky.item(item)["values"]

        disk_lines.extend([
            f"${{color grey}}DISK {int(idx):02d} ({name}):${{color}} ${{fs_used_perc {path_value}}}%",
            f"${{fs_bar 8 {path_value}}}",
            f"${{fs_used {path_value}}} / ${{fs_size {path_value}}}",
            ""
        ])

    disks = "\n".join(disk_lines)

    pattern = re.compile(
        r'\$\{color grey\}DISK.*?(?=\n\$\{color grey\}NETWORK)',
        re.S
    )

    txt = pattern.sub(disks, txt)

    path.write_text(txt)

    subprocess.run(["pkill", "conky"])
    subprocess.Popen(["conky"])

    messagebox.showinfo("Saved", "Conky updated")

########################################################
# FILEBROWSER TAB
########################################################

def build_filebrowser_tab(parent):

    global en_fb_path, lbl_fb_status, btn_fb_stop, btn_fb_start

    content, toolbar = build_page(
        parent,
        "FileBrowser",
        "Web-based file manager exposed on the local network."
    )

    ttk.Label(content, text="Root Path").pack(anchor="w")

    en_fb_path = ttk.Entry(content)
    en_fb_path.pack(fill="x", pady=(6, 20))

    ttk.Label(content, text="Service Status").pack(anchor="w")

    lbl_fb_status = status_badge(content)
    lbl_fb_status.pack(anchor="w", pady=(6, 0))

    ttk.Button(toolbar, text="Refresh Status", command=refresh_filebrowser_status).pack(side="left")

    btn_fb_stop = ttk.Button(toolbar, text="Stop", command=stop_filebrowser)
    btn_fb_stop.pack(side="left", padx=5)

    btn_fb_start = ttk.Button(toolbar, text="Start", command=start_filebrowser)
    btn_fb_start.pack(side="left")


def load_filebrowser():

    path = Path("/etc/systemd/system/filebrowser.service")

    if not path.exists():
        return

    txt = path.read_text()

    m = re.search(r'-r\s+(.*?)\s', txt)

    if m:
        en_fb_path.insert(0, m.group(1))

    en_fb_path.config(state="readonly")


def refresh_filebrowser_status():

    active = service_is_active(FILEBROWSER_SERVICE)

    set_status_badge(lbl_fb_status, active)

    if active:
        btn_fb_start.state(["disabled"])
        btn_fb_stop.state(["!disabled"])
    else:
        btn_fb_start.state(["!disabled"])
        btn_fb_stop.state(["disabled"])


def start_filebrowser():

    if start_service(FILEBROWSER_SERVICE):
        refresh_filebrowser_status()


def stop_filebrowser():

    if stop_service(FILEBROWSER_SERVICE):
        refresh_filebrowser_status()

########################################################
# SERVER MONITOR TAB
########################################################

def build_monitor_tab(parent):

    global lbl_monitor_status, tree_monitor, progress_monitor
    global btn_monitor_install, btn_monitor_refresh, btn_monitor_restart
    global btn_monitor_stop, btn_monitor_start

    content, toolbar = build_page(
        parent,
        "Server Monitor",
        "Controls the Sevastolink API used to feed the Rainmeter skin."
    )

    info = ttk.Frame(content)
    info.pack(fill="x", pady=(0, 10))

    lbl_monitor_status = status_badge(info)
    lbl_monitor_status.pack(side="left")

    ttk.Label(
        info,
        text=f"Endpoint: http://{socket.gethostname()}:{MONITOR_PORT}/api/rainmeter"
    ).pack(side="left", padx=(12, 0))

    progress_monitor = ttk.Progressbar(
        content,
        mode="determinate",
        maximum=MONITOR_INSTALL_STEPS
    )
    progress_monitor.pack(fill="x", pady=(0, 10))

    tree_monitor = build_treeview(
        content,
        columns=("metric", "value"),
        headings=("Metric", "Value"),
        widths=(240, 460)
    )

    btn_monitor_refresh = ttk.Button(toolbar, text="Refresh Data", command=fetch_monitor_data)
    btn_monitor_refresh.pack(side="right")

    btn_monitor_restart = ttk.Button(toolbar, text="Restart", command=restart_monitor)
    btn_monitor_restart.pack(side="left", padx=(0, 5))

    btn_monitor_stop = ttk.Button(toolbar, text="Stop", command=stop_monitor)
    btn_monitor_stop.pack(side="left", padx=5)

    btn_monitor_start = ttk.Button(toolbar, text="Start", command=start_monitor)
    btn_monitor_start.pack(side="left", padx=(0, 5))

    btn_monitor_install = ttk.Button(toolbar, text="Install Monitor", command=install_monitor)
    btn_monitor_install.pack(side="left")


def update_monitor_buttons(active):

    if active:
        btn_monitor_install.state(["disabled"])
        btn_monitor_refresh.state(["!disabled"])
        btn_monitor_restart.state(["!disabled"])
        btn_monitor_stop.state(["!disabled"])
        btn_monitor_start.state(["disabled"])
    else:
        btn_monitor_install.state(["!disabled"])
        btn_monitor_refresh.state(["disabled"])
        btn_monitor_restart.state(["disabled"])
        btn_monitor_stop.state(["disabled"])
        btn_monitor_start.state(["disabled"])


def refresh_monitor_status():

    active = service_is_active(MONITOR_SERVICE)

    set_status_badge(lbl_monitor_status, active)
    update_monitor_buttons(active)


def install_monitor():

    proceed = messagebox.askyesno(
        "Install Monitor",
        "This will install python3-venv, curl, the FastAPI dependencies, "
        "and register the \"sevastolink\" service so the Server Monitor "
        "endpoint comes online.\n\nContinue?"
    )

    if not proceed:
        return

    btn_monitor_install.state(["disabled"])
    progress_monitor["value"] = 0
    root.update_idletasks()

    ok, msg = run_monitor_install()

    progress_monitor["value"] = 0

    if not ok:
        messagebox.showerror("Error", f"Failed to install the Server Monitor:\n{msg}")
    else:
        messagebox.showinfo("Installed", "Server Monitor installed and running.")

    refresh_monitor_status()


def advance_monitor_progress(step, description):

    progress_monitor["value"] = step
    lbl_monitor_status.config(text=f"Installing... ({description})", foreground=STATUS_OK)
    root.update_idletasks()


def run_monitor_install():
    """Reproduces Script_Server-Monitor-1.0.sh: installs the OS packages,
    creates the venv, writes api.py, and registers/starts the systemd
    service that exposes the Rainmeter endpoint."""

    advance_monitor_progress(1, "updating packages")
    ok, msg = run_sudo(["apt-get", "update"])

    if not ok:
        return False, msg

    advance_monitor_progress(2, "installing OS dependencies")
    ok, msg = run_sudo(["apt-get", "install", "-y", "python3", "python3-venv", "python3-pip", "curl"])

    if not ok:
        return False, msg

    advance_monitor_progress(3, "writing api.py")
    try:
        MONITOR_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
        MONITOR_API_PATH.write_text(MONITOR_API_PY)

    except OSError as e:
        return False, str(e)

    advance_monitor_progress(4, "creating virtual environment")
    if not MONITOR_VENV_DIR.exists():

        result = subprocess.run(
            ["python3", "-m", "venv", str(MONITOR_VENV_DIR)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, result.stderr.strip()

    pip_bin = MONITOR_VENV_DIR / "bin" / "pip"

    advance_monitor_progress(5, "upgrading pip")
    result = subprocess.run(
        [str(pip_bin), "install", "--upgrade", "pip"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return False, result.stderr.strip()

    advance_monitor_progress(6, "installing Python packages")
    result = subprocess.run(
        [str(pip_bin), "install", "fastapi", "uvicorn", "psutil"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return False, result.stderr.strip()

    python_bin = MONITOR_VENV_DIR / "bin" / "python"

    unit = f"""[Unit]
Description=Sevastolink Monitor API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User={os.environ.get("USER", "")}
WorkingDirectory={MONITOR_INSTALL_DIR}
ExecStart={python_bin} {MONITOR_API_PATH}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

    advance_monitor_progress(7, "writing service file")
    Path("/tmp/sevastolink.service").write_text(unit)

    ok, msg = run_sudo(["cp", "/tmp/sevastolink.service", MONITOR_SERVICE_UNIT_PATH])

    if not ok:
        return False, msg

    advance_monitor_progress(8, "reloading systemd")
    ok, msg = run_sudo(["systemctl", "daemon-reload"])

    if not ok:
        return False, msg

    advance_monitor_progress(9, "enabling service")
    ok, msg = run_sudo(["systemctl", "enable", MONITOR_SERVICE])

    if not ok:
        return False, msg

    advance_monitor_progress(10, "starting service")
    ok, msg = run_sudo(["systemctl", "restart", MONITOR_SERVICE])

    if not ok:
        return False, msg

    return True, "Service installed"


def start_monitor():

    if start_service(MONITOR_SERVICE):
        refresh_monitor_status()


def stop_monitor():

    if stop_service(MONITOR_SERVICE):
        refresh_monitor_status()


def restart_monitor():

    if restart_service(MONITOR_SERVICE):
        refresh_monitor_status()


def fetch_monitor_data():

    tree_monitor.delete(*tree_monitor.get_children())

    url = f"http://127.0.0.1:{MONITOR_PORT}/api/rainmeter"

    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            data = response.read().decode()

    except Exception:
        refresh_monitor_status()
        return

    for line in data.strip().splitlines():

        if "=" in line:
            key, value = line.split("=", 1)
            tree_monitor.insert("", "end", values=(key, value))

    refresh_monitor_status()

########################################################
# TAB CHANGE - AUTO REFRESH SERVER MONITOR
########################################################

def on_tab_changed(event):

    selected = event.widget.select()
    tab_text = event.widget.tab(selected, "text")

    if tab_text == "Server Monitor":
        fetch_monitor_data()


notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

########################################################
# BUILD TABS
########################################################

build_shares_tab(tab_shares)
build_conky_tab(tab_conky)
build_filebrowser_tab(tab_filebrowser)
build_monitor_tab(tab_monitor)

########################################################
# INITIAL LOAD
########################################################

load_samba()
load_conky()
load_filebrowser()

refresh_filebrowser_status()
refresh_monitor_status()

root.mainloop()
