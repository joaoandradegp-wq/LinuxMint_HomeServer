import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from pathlib import Path

import subprocess
import re
import socket
import urllib.request

########################################################
# CONFIG
########################################################

DIALOG_WIDTH = 460
DIALOG_HEIGHT = 260

COLOR_OK = "#0a7d2c"
COLOR_WARN = "#b8860b"
COLOR_ERROR = "#c0392b"
COLOR_NEUTRAL = "#555555"

SAMBA_USER = ""

FILEBROWSER_SERVICE = "filebrowser"
MONITOR_SERVICE = "sevastolink"
MONITOR_PORT = 8181

########################################################
# ROOT
########################################################

root = tk.Tk()

root.title("Home Server Control Panel")
root.geometry("900x580")
root.minsize(820, 520)

style = ttk.Style()

if "clam" in style.theme_names():
    style.theme_use("clam")

style.configure("Treeview", rowheight=24)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("TNotebook.Tab", padding=[16, 8], font=("Segoe UI", 10))

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
# HELPERS
########################################################

def build_header(parent, title, subtitle):

    header = ttk.Frame(parent, padding=10)
    header.pack(fill="x")

    ttk.Label(header, text=title, font=("Segoe UI", 16, "bold")).pack(anchor="w")
    ttk.Label(header, text=subtitle, foreground=COLOR_NEUTRAL).pack(anchor="w")

    return header


def build_treeview(parent, columns, headings, widths):

    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame, columns=columns, show="headings")

    for col, head, width in zip(columns, headings, widths):
        tree.heading(col, text=head)
        tree.column(col, width=width)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    return tree


def build_buttonbar(parent):

    bar = ttk.Frame(parent, padding=10)
    bar.pack(fill="x", side="bottom")

    return bar


def center_dialog(win, width, height):

    root.update_idletasks()

    x = root.winfo_x() + root.winfo_width() // 2 - width // 2
    y = root.winfo_y() + root.winfo_height() // 2 - height // 2

    win.geometry(f"{width}x{height}+{x}+{y}")


def open_dialog(title):

    win = tk.Toplevel(root)

    win.title(title)

    center_dialog(win, DIALOG_WIDTH, DIALOG_HEIGHT)

    win.resizable(False, False)
    win.transient(root)
    win.grab_set()

    return win


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
    subprocess.run(["sudo", "systemctl", "start", name])


def stop_service(name):
    subprocess.run(["sudo", "systemctl", "stop", name])


def restart_service(name):
    subprocess.run(["sudo", "systemctl", "restart", name])


def set_status_label(label, active):

    if active:
        label.config(text="Status: Online", foreground=COLOR_OK)
    else:
        label.config(text="Status: Offline", foreground=COLOR_ERROR)

########################################################
# SHARES TAB
########################################################

def build_shares_tab(parent):

    global tree_shares, lbl_samba

    build_header(
        parent,
        "Samba Shares",
        "Manage folders shared on the network via Samba."
    )

    tree_shares = build_treeview(
        parent,
        columns=("name", "path"),
        headings=("Share", "Path"),
        widths=(240, 460)
    )

    def on_double_click(event):

        item = tree_shares.identify_row(event.y)

        if item:
            tree_shares.selection_set(item)
            edit_share(True)

    tree_shares.bind("<Double-1>", on_double_click)

    bar = build_buttonbar(parent)

    lbl_samba = ttk.Label(bar, text="Force User: -", foreground=COLOR_NEUTRAL)
    lbl_samba.pack(side="left", padx=(0, 20))

    ttk.Button(bar, text="Change User", command=change_samba_user).pack(side="left", padx=5)

    ttk.Button(bar, text="Save", command=save_samba).pack(side="right")
    ttk.Button(bar, text="Delete", command=delete_share).pack(side="right", padx=5)
    ttk.Button(bar, text="Edit", command=lambda: edit_share(True)).pack(side="right", padx=5)
    ttk.Button(bar, text="Add", command=edit_share).pack(side="right", padx=5)


def load_samba_user():

    global SAMBA_USER

    path = Path("/etc/samba/smb.conf")

    if not path.exists():
        SAMBA_USER = ""
        return

    txt = path.read_text()

    m = re.search(r'force user\s*=\s*(.+)', txt, re.I)

    SAMBA_USER = m.group(1).strip() if m else ""

    lbl_samba.config(text=f"Force User: {SAMBA_USER}")


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

    ttk.Label(frame, text="Share name:").pack(anchor="w")

    e_name = ttk.Entry(frame)
    e_name.insert(0, name)
    e_name.pack(fill="x", pady=(5, 10))

    ttk.Label(frame, text="Path:").pack(anchor="w")

    e_path = ttk.Entry(frame)
    e_path.insert(0, path_value)
    e_path.pack(fill="x", pady=(5, 10))

    ttk.Label(
        frame,
        text="The folder will be created automatically if it doesn't exist.",
        foreground=COLOR_NEUTRAL
    ).pack(anchor="w")

    btns = ttk.Frame(win)
    btns.pack(side="bottom", fill="x", padx=20, pady=12)

    def save():

        new_name = e_name.get().strip()
        new_path = e_path.get().strip()

        if not new_name or not new_path:
            messagebox.showwarning("Warning", "Please fill in both fields")
            return

        subprocess.run(["sudo", "mkdir", "-p", new_path])
        subprocess.run(["sudo", "chmod", "755", new_path])
        subprocess.run(["sudo", "chown", f"{SAMBA_USER}:{SAMBA_USER}", new_path])

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
force user = {SAMBA_USER}

"""

    Path("/tmp/smb.conf").write_text(txt)

    subprocess.run(["sudo", "cp", "/tmp/smb.conf", "/etc/samba/smb.conf"])
    subprocess.run(["sudo", "systemctl", "restart", "smbd"])

    messagebox.showinfo("Saved", "Samba configuration updated")


def change_samba_user():

    global SAMBA_USER

    user = simpledialog.askstring(
        "Force User",
        "Linux user:",
        initialvalue=SAMBA_USER
    )

    if not user:
        return

    SAMBA_USER = user

    lbl_samba.config(text=f"Force User: {user}")

########################################################
# CONKY TAB
########################################################

def build_conky_tab(parent):

    global tree_conky

    build_header(
        parent,
        "Conky Disks",
        "Disks displayed in the Conky system monitor."
    )

    tree_conky = build_treeview(
        parent,
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

    bar = build_buttonbar(parent)

    ttk.Button(bar, text="Save", command=save_conky).pack(side="right")
    ttk.Button(bar, text="Delete", command=delete_conky).pack(side="right", padx=5)
    ttk.Button(bar, text="Edit", command=lambda: edit_conky(True)).pack(side="right", padx=5)
    ttk.Button(bar, text="Add", command=edit_conky).pack(side="right", padx=5)


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

    ttk.Label(frame, text="Name:").pack(anchor="w")

    e_name = ttk.Entry(frame)
    e_name.insert(0, name)
    e_name.pack(fill="x", pady=(5, 10))

    ttk.Label(frame, text="Path:").pack(anchor="w")

    e_path = ttk.Entry(frame)
    e_path.insert(0, path_value)
    e_path.pack(fill="x", pady=(5, 10))

    ttk.Label(
        frame,
        text="This disk will be displayed in the Conky panel.",
        foreground=COLOR_NEUTRAL
    ).pack(anchor="w")

    btns = ttk.Frame(win)
    btns.pack(side="bottom", fill="x", padx=20, pady=12)

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

    global en_fb_path, lbl_fb_status

    build_header(
        parent,
        "FileBrowser",
        "Web-based file manager exposed on the local network."
    )

    form = ttk.Frame(parent, padding=10)
    form.pack(fill="x")

    ttk.Label(form, text="Root Path:").pack(anchor="w")

    en_fb_path = ttk.Entry(form)
    en_fb_path.pack(fill="x", pady=(5, 10))

    lbl_fb_status = ttk.Label(form, text="Status: -", font=("Segoe UI", 10, "bold"))
    lbl_fb_status.pack(anchor="w")

    bar = build_buttonbar(parent)

    ttk.Button(bar, text="Refresh Status", command=refresh_filebrowser_status).pack(side="left")
    ttk.Button(bar, text="Stop", command=stop_filebrowser).pack(side="left", padx=5)
    ttk.Button(bar, text="Start", command=start_filebrowser).pack(side="left")


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
    set_status_label(lbl_fb_status, service_is_active(FILEBROWSER_SERVICE))


def start_filebrowser():
    start_service(FILEBROWSER_SERVICE)
    refresh_filebrowser_status()


def stop_filebrowser():
    stop_service(FILEBROWSER_SERVICE)
    refresh_filebrowser_status()

########################################################
# SERVER MONITOR TAB
########################################################

def build_monitor_tab(parent):

    global lbl_monitor_status, tree_monitor

    build_header(
        parent,
        "Server Monitor",
        "Controls the Sevastolink API used to feed the Rainmeter skin."
    )

    info = ttk.Frame(parent, padding=(10, 0, 10, 10))
    info.pack(fill="x")

    lbl_monitor_status = ttk.Label(info, text="Status: -", font=("Segoe UI", 10, "bold"))
    lbl_monitor_status.pack(anchor="w")

    ttk.Label(
        info,
        text=f"Endpoint: http://{socket.gethostname()}:{MONITOR_PORT}/api/rainmeter",
        foreground=COLOR_NEUTRAL
    ).pack(anchor="w", pady=(2, 0))

    tree_monitor = build_treeview(
        parent,
        columns=("metric", "value"),
        headings=("Metric", "Value"),
        widths=(240, 460)
    )

    bar = build_buttonbar(parent)

    ttk.Button(bar, text="Refresh Data", command=fetch_monitor_data).pack(side="right")
    ttk.Button(bar, text="Restart", command=restart_monitor).pack(side="left", padx=(0, 5))
    ttk.Button(bar, text="Stop", command=stop_monitor).pack(side="left", padx=5)
    ttk.Button(bar, text="Start", command=start_monitor).pack(side="left")


def refresh_monitor_status():
    set_status_label(lbl_monitor_status, service_is_active(MONITOR_SERVICE))


def start_monitor():
    start_service(MONITOR_SERVICE)
    refresh_monitor_status()


def stop_monitor():
    stop_service(MONITOR_SERVICE)
    refresh_monitor_status()


def restart_monitor():
    restart_service(MONITOR_SERVICE)
    refresh_monitor_status()


def fetch_monitor_data():

    tree_monitor.delete(*tree_monitor.get_children())

    url = f"http://127.0.0.1:{MONITOR_PORT}/api/rainmeter"

    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            data = response.read().decode()

    except Exception:
        messagebox.showerror(
            "Error",
            "Could not reach the Server Monitor API.\nMake sure the service is running."
        )
        refresh_monitor_status()
        return

    for line in data.strip().splitlines():

        if "=" in line:
            key, value = line.split("=", 1)
            tree_monitor.insert("", "end", values=(key, value))

    refresh_monitor_status()

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

load_samba_user()
load_samba()
load_conky()
load_filebrowser()

refresh_filebrowser_status()
refresh_monitor_status()

root.mainloop()
