import tkinter as tk
from tkinter import ttk, simpledialog, Toplevel, messagebox
from pathlib import Path

import subprocess
import re
import socket
import urllib.request

########################################################
# GLOBAL CONFIG
########################################################

FONT_TITLE = ("Arial", 12, "bold")
FONT_STATUS = ("Arial", 10, "bold")
FONT_NOTE = ("Arial", 9)

PAD = 10
BTN_WIDTH = 16
ENTRY_WIDTH = 45

SAMBA_USER = ""

FILEBROWSER_SERVICE = "filebrowser"
MONITOR_SERVICE = "sevastolink"
MONITOR_PORT = 8181

root = tk.Tk()

root.title("Home Server Control Panel")
root.geometry("860x540")
root.minsize(780, 480)

style = ttk.Style()
style.configure("Treeview", rowheight=24)
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

########################################################
# HELPERS
########################################################

def section_title(parent, text):

    lbl = tk.Label(parent, text=text, font=FONT_TITLE)
    lbl.pack(anchor="w", pady=(0, PAD))

    return lbl


def make_treeview(parent, columns, headings, widths):

    container = tk.Frame(parent)
    container.pack(fill="both", expand=True)

    tree = ttk.Treeview(container, columns=columns, show="headings")

    for col, head, width in zip(columns, headings, widths):
        tree.heading(col, text=head)
        tree.column(col, width=width)

    scroll = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    scroll.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    return tree


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
        label.config(text="Status: ONLINE", fg="green")
    else:
        label.config(text="Status: OFFLINE", fg="red")

########################################################
# TABS
########################################################

tabs = ttk.Notebook(root)

tab_shares = ttk.Frame(tabs)
tab_conky = ttk.Frame(tabs)
tab_filebrowser = ttk.Frame(tabs)
tab_monitor = ttk.Frame(tabs)

tabs.add(tab_shares, text="Shares")
tabs.add(tab_conky, text="Conky")
tabs.add(tab_filebrowser, text="FileBrowser")
tabs.add(tab_monitor, text="Server Monitor")

tabs.pack(fill="both", expand=True)

########################################################
# SHARES TAB
########################################################

frame_shares = tk.Frame(tab_shares, padx=PAD, pady=PAD)
frame_shares.pack(fill="both", expand=True)

section_title(frame_shares, "Samba Shares")

tree_shares = make_treeview(
    frame_shares,
    columns=("name", "path"),
    headings=("Share", "Path"),
    widths=(220, 480)
)


def on_share_double_click(event):

    item = tree_shares.identify_row(event.y)

    if item:
        tree_shares.selection_set(item)
        edit_share(True)


tree_shares.bind("<Double-1>", on_share_double_click)

toolbar_shares = tk.Frame(frame_shares)
toolbar_shares.pack(fill="x", pady=(PAD, 0))

lbl_samba = tk.Label(toolbar_shares, text="Force User: -")

########################################################
# CONKY TAB
########################################################

frame_conky = tk.Frame(tab_conky, padx=PAD, pady=PAD)
frame_conky.pack(fill="both", expand=True)

section_title(frame_conky, "Conky Disks")

tree_conky = make_treeview(
    frame_conky,
    columns=("idx", "name", "path"),
    headings=("#", "Name", "Path"),
    widths=(40, 200, 320)
)


def on_conky_double_click(event):

    item = tree_conky.identify_row(event.y)

    if item:
        tree_conky.selection_set(item)
        edit_conky(True)


tree_conky.bind("<Double-1>", on_conky_double_click)

toolbar_conky = tk.Frame(frame_conky)
toolbar_conky.pack(fill="x", pady=(PAD, 0))

########################################################
# FILEBROWSER TAB
########################################################

frame_fb = tk.Frame(tab_filebrowser, padx=PAD, pady=PAD)
frame_fb.pack(fill="both", expand=True)

section_title(frame_fb, "FileBrowser")

tk.Label(frame_fb, text="Root Path", anchor="w").pack(fill="x")

txt_fb = tk.Text(frame_fb, height=3, width=70)
txt_fb.pack(pady=(5, PAD), fill="x")

lbl_fb_status = tk.Label(frame_fb, text="Status: -", font=FONT_STATUS)
lbl_fb_status.pack(anchor="w", pady=(0, PAD))

toolbar_fb = tk.Frame(frame_fb)
toolbar_fb.pack(fill="x")

########################################################
# SERVER MONITOR TAB
########################################################

frame_monitor = tk.Frame(tab_monitor, padx=PAD, pady=PAD)
frame_monitor.pack(fill="both", expand=True)

section_title(frame_monitor, "Server Monitor (Sevastolink API)")

lbl_monitor_status = tk.Label(frame_monitor, text="Status: -", font=FONT_STATUS)
lbl_monitor_status.pack(anchor="w")

lbl_monitor_url = tk.Label(
    frame_monitor,
    text=f"Endpoint: http://{socket.gethostname()}:{MONITOR_PORT}/api/rainmeter",
    fg="gray",
    font=FONT_NOTE
)
lbl_monitor_url.pack(anchor="w", pady=(0, PAD))

tree_monitor = make_treeview(
    frame_monitor,
    columns=("metric", "value"),
    headings=("Metric", "Value"),
    widths=(220, 480)
)

toolbar_monitor = tk.Frame(frame_monitor)
toolbar_monitor.pack(fill="x", pady=(PAD, 0))

########################################################
# LOAD SAMBA
########################################################

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

########################################################
# EDIT SHARE
########################################################

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

    win = Toplevel(root)

    win.title("Share Configuration")
    win.geometry("520x240")
    win.resizable(False, False)

    frame = tk.Frame(win, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="Share Configuration",
        font=FONT_TITLE
    ).pack(pady=(0, 15))

    row1 = tk.Frame(frame)
    row1.pack(fill="x", pady=5)

    tk.Label(row1, text="Name", width=15, anchor="w").pack(side="left")

    e_name = tk.Entry(row1, width=ENTRY_WIDTH)
    e_name.pack(side="left", fill="x", expand=True)
    e_name.insert(0, name)

    row2 = tk.Frame(frame)
    row2.pack(fill="x", pady=5)

    tk.Label(row2, text="Path", width=15, anchor="w").pack(side="left")

    e_path = tk.Entry(row2, width=ENTRY_WIDTH)
    e_path.pack(side="left", fill="x", expand=True)
    e_path.insert(0, path_value)

    tk.Label(
        frame,
        text="The folder will be created automatically if it doesn't exist.",
        fg="gray",
        font=FONT_NOTE
    ).pack(pady=15)

    bottom = tk.Frame(frame)
    bottom.pack(side="bottom", fill="x")

    def save():

        name = e_name.get().strip()
        path_value = e_path.get().strip()

        if not name or not path_value:
            return

        subprocess.run(["sudo", "mkdir", "-p", path_value])
        subprocess.run(["sudo", "chmod", "755", path_value])

        subprocess.run(["sudo", "chown", f"{SAMBA_USER}:{SAMBA_USER}", path_value])

        values = (name, path_value)

        if edit:
            tree_shares.item(item, values=values)

        else:
            tree_shares.insert("", "end", values=values)

        win.destroy()

    tk.Button(bottom, text="Save", width=12, command=save).pack(side="right", padx=5)
    tk.Button(bottom, text="Cancel", width=12, command=win.destroy).pack(side="right")

########################################################
# DELETE SHARE
########################################################

def delete_share():

    sel = tree_shares.selection()

    if sel:
        tree_shares.delete(sel[0])

########################################################
# SAVE SAMBA
########################################################

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

    messagebox.showinfo("OK", "Samba configuration updated")

########################################################
# CHANGE SAMBA USER
########################################################

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
# CONKY
########################################################

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

    win = Toplevel(root)

    win.title("Conky Disk")
    win.geometry("520x240")
    win.resizable(False, False)

    frame = tk.Frame(win, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="Conky Disk Configuration",
        font=FONT_TITLE
    ).pack(pady=(0, 15))

    row1 = tk.Frame(frame)
    row1.pack(fill="x", pady=5)

    tk.Label(row1, text="Name", width=15, anchor="w").pack(side="left")

    e_name = tk.Entry(row1, width=ENTRY_WIDTH)
    e_name.pack(side="left", fill="x", expand=True)
    e_name.insert(0, name)

    row2 = tk.Frame(frame)
    row2.pack(fill="x", pady=5)

    tk.Label(row2, text="Path", width=15, anchor="w").pack(side="left")

    e_path = tk.Entry(row2, width=ENTRY_WIDTH)
    e_path.pack(side="left", fill="x", expand=True)
    e_path.insert(0, path_value)

    tk.Label(
        frame,
        text="This disk will be displayed in the Conky panel.",
        fg="gray",
        font=FONT_NOTE
    ).pack(pady=15)

    bottom = tk.Frame(frame)
    bottom.pack(side="bottom", fill="x")

    def save():

        name = e_name.get().strip()
        path_value = e_path.get().strip()

        if not name or not path_value:
            return

        values = (idx, name, path_value)

        if edit:
            tree_conky.item(item, values=values)

        else:
            tree_conky.insert("", "end", values=values)

        win.destroy()

    tk.Button(bottom, text="Save", width=12, command=save).pack(side="right", padx=5)
    tk.Button(bottom, text="Cancel", width=12, command=win.destroy).pack(side="right")


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

    messagebox.showinfo("OK", "Conky updated")

########################################################
# FILEBROWSER
########################################################

def load_filebrowser():

    path = Path("/etc/systemd/system/filebrowser.service")

    if not path.exists():
        return

    txt = path.read_text()

    m = re.search(r'-r\s+(.*?)\s', txt)

    if m:
        txt_fb.insert("1.0", m.group(1))

    txt_fb.config(state="disabled")


def refresh_filebrowser_status():
    set_status_label(lbl_fb_status, service_is_active(FILEBROWSER_SERVICE))


def start_filebrowser():
    start_service(FILEBROWSER_SERVICE)
    refresh_filebrowser_status()


def stop_filebrowser():
    stop_service(FILEBROWSER_SERVICE)
    refresh_filebrowser_status()

########################################################
# SERVER MONITOR
########################################################

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
# BUTTONS - SHARES
########################################################

tk.Button(toolbar_shares, text="Add", width=BTN_WIDTH, command=edit_share).pack(side="left", padx=5)
tk.Button(toolbar_shares, text="Delete", width=BTN_WIDTH, command=delete_share).pack(side="left", padx=5)
tk.Button(toolbar_shares, text="Save", width=BTN_WIDTH, command=save_samba).pack(side="left", padx=5)

lbl_samba.pack(side="left", padx=20)

tk.Button(
    toolbar_shares,
    text="Change User",
    width=BTN_WIDTH,
    command=change_samba_user
).pack(side="left")

########################################################
# BUTTONS - CONKY
########################################################

tk.Button(toolbar_conky, text="Add", width=BTN_WIDTH, command=edit_conky).pack(side="left", padx=5)
tk.Button(toolbar_conky, text="Delete", width=BTN_WIDTH, command=delete_conky).pack(side="left", padx=5)
tk.Button(toolbar_conky, text="Save", width=BTN_WIDTH, command=save_conky).pack(side="left", padx=5)

########################################################
# BUTTONS - FILEBROWSER
########################################################

tk.Button(toolbar_fb, text="Start", width=BTN_WIDTH, command=start_filebrowser).pack(side="left", padx=5)
tk.Button(toolbar_fb, text="Stop", width=BTN_WIDTH, command=stop_filebrowser).pack(side="left", padx=5)
tk.Button(toolbar_fb, text="Refresh Status", width=BTN_WIDTH, command=refresh_filebrowser_status).pack(side="left", padx=5)

########################################################
# BUTTONS - SERVER MONITOR
########################################################

tk.Button(toolbar_monitor, text="Start", width=BTN_WIDTH, command=start_monitor).pack(side="left", padx=5)
tk.Button(toolbar_monitor, text="Stop", width=BTN_WIDTH, command=stop_monitor).pack(side="left", padx=5)
tk.Button(toolbar_monitor, text="Restart", width=BTN_WIDTH, command=restart_monitor).pack(side="left", padx=5)
tk.Button(toolbar_monitor, text="Refresh Data", width=BTN_WIDTH, command=fetch_monitor_data).pack(side="left", padx=5)

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
