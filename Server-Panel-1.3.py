import tkinter as tk
from tkinter import ttk, messagebox

from pathlib import Path

import subprocess
import re
import socket
import urllib.request

########################################################
# PALETTE
########################################################

BG = "#eef1f6"
SURFACE = "#ffffff"
BORDER = "#dde2ea"
TEXT = "#1f2937"
MUTED = "#6b7280"

ACCENT = "#2f6fed"
ACCENT_HOVER = "#2558c9"

SUCCESS = "#16a34a"
SUCCESS_BG = "#e7f6ec"

ERROR = "#dc2626"
ERROR_BG = "#fdecea"
ERROR_BG_HOVER = "#fbd5d0"

FONT = "Segoe UI"

DIALOG_WIDTH = 460
DIALOG_HEIGHT = 280

########################################################
# STATE
########################################################

SAMBA_USER = ""
SUDO_PASSWORD = None

FILEBROWSER_SERVICE = "filebrowser"
MONITOR_SERVICE = "sevastolink"
MONITOR_PORT = 8181

########################################################
# ROOT
########################################################

root = tk.Tk()

root.title("Home Server Control Panel")
root.geometry("960x620")
root.minsize(860, 560)
root.configure(bg=BG)

style = ttk.Style()

if "clam" in style.theme_names():
    style.theme_use("clam")

style.configure("TFrame", background=BG)
style.configure("TLabel", background=BG, foreground=TEXT, font=(FONT, 10))

style.configure("Title.TLabel", background=BG, foreground=TEXT, font=(FONT, 18, "bold"))
style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=(FONT, 10))

style.configure("Card.TLabel", background=SURFACE, foreground=TEXT, font=(FONT, 10))
style.configure("CardMuted.TLabel", background=SURFACE, foreground=MUTED, font=(FONT, 9))
style.configure("CardBold.TLabel", background=SURFACE, foreground=TEXT, font=(FONT, 10, "bold"))

style.configure(
    "TButton",
    background=SURFACE,
    foreground=TEXT,
    borderwidth=1,
    bordercolor=BORDER,
    relief="flat",
    font=(FONT, 10),
    padding=(14, 8)
)
style.map(
    "TButton",
    background=[("active", "#f4f6f9")],
    bordercolor=[("active", BORDER)]
)

style.configure(
    "Accent.TButton",
    background=ACCENT,
    foreground="white",
    borderwidth=0,
    font=(FONT, 10, "bold"),
    padding=(14, 8)
)
style.map("Accent.TButton", background=[("active", ACCENT_HOVER)])

style.configure(
    "Danger.TButton",
    background=ERROR_BG,
    foreground=ERROR,
    borderwidth=0,
    font=(FONT, 10),
    padding=(14, 8)
)
style.map("Danger.TButton", background=[("active", ERROR_BG_HOVER)])

style.configure(
    "TEntry",
    fieldbackground=SURFACE,
    foreground=TEXT,
    bordercolor=BORDER,
    lightcolor=SURFACE,
    darkcolor=SURFACE,
    padding=6
)

style.configure(
    "Treeview",
    background=SURFACE,
    fieldbackground=SURFACE,
    foreground=TEXT,
    borderwidth=0,
    rowheight=28,
    font=(FONT, 10)
)
style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "white")])

style.configure(
    "Treeview.Heading",
    background=SURFACE,
    foreground=MUTED,
    borderwidth=0,
    font=(FONT, 9, "bold")
)
style.map("Treeview.Heading", background=[("active", SURFACE)])

style.configure("TScrollbar", background=BG, troughcolor=BG, bordercolor=BG, arrowcolor=MUTED)

style.configure("TNotebook", background=BG, borderwidth=0)
style.configure(
    "TNotebook.Tab",
    background=BG,
    foreground=MUTED,
    padding=[18, 10],
    font=(FONT, 10)
)
style.map(
    "TNotebook.Tab",
    background=[("selected", SURFACE)],
    foreground=[("selected", TEXT)]
)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=16, pady=16)

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
    """Creates the standard page skeleton: header, card (for content), toolbar."""

    page = tk.Frame(parent, bg=BG)
    page.pack(fill="both", expand=True, padx=6, pady=6)

    header = tk.Frame(page, bg=BG)
    header.pack(fill="x", pady=(0, 14))

    tk.Label(header, text=title, bg=BG, fg=TEXT, font=(FONT, 18, "bold")).pack(anchor="w")
    tk.Label(header, text=subtitle, bg=BG, fg=MUTED, font=(FONT, 10)).pack(anchor="w", pady=(2, 0))

    card = tk.Frame(page, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
    card.pack(fill="both", expand=True)

    toolbar = tk.Frame(page, bg=BG)
    toolbar.pack(fill="x", pady=(14, 0))

    return page, card, toolbar


def build_treeview(card, columns, headings, widths):

    inner = tk.Frame(card, bg=SURFACE)
    inner.pack(fill="both", expand=True, padx=16, pady=16)

    tree = ttk.Treeview(inner, columns=columns, show="headings")

    for col, head, width in zip(columns, headings, widths):
        tree.heading(col, text=head)
        tree.column(col, width=width)

    scroll = ttk.Scrollbar(inner, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    return tree


def status_badge(parent):
    """A small colored pill label used to show ONLINE / OFFLINE."""

    lbl = tk.Label(
        parent,
        text=" - ",
        font=(FONT, 9, "bold"),
        bg=SURFACE,
        fg=MUTED,
        padx=10,
        pady=3
    )
    return lbl


def set_status_badge(label, active):

    if active:
        label.config(text=" ONLINE ", bg=SUCCESS_BG, fg=SUCCESS)
    else:
        label.config(text=" OFFLINE ", bg=ERROR_BG, fg=ERROR)


def center_dialog(win, width, height):

    root.update_idletasks()

    x = root.winfo_x() + root.winfo_width() // 2 - width // 2
    y = root.winfo_y() + root.winfo_height() // 2 - height // 2

    win.geometry(f"{width}x{height}+{x}+{y}")


def open_dialog(title, width=DIALOG_WIDTH, height=DIALOG_HEIGHT):

    win = tk.Toplevel(root)

    win.title(title)
    win.configure(bg=SURFACE)

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

    win = open_dialog("Administrator Password", 380, 210)

    frame = tk.Frame(win, bg=SURFACE, padx=24, pady=24)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame, text="Administrator Password", bg=SURFACE, fg=TEXT, font=(FONT, 12, "bold")
    ).pack(anchor="w")

    tk.Label(
        frame, text="Required to manage system services.", bg=SURFACE, fg=MUTED, font=(FONT, 9)
    ).pack(anchor="w", pady=(2, 14))

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

    btns = tk.Frame(frame, bg=SURFACE)
    btns.pack(fill="x", pady=(20, 0))

    ttk.Button(btns, text="Cancel", command=cancel).pack(side="right")
    ttk.Button(btns, text="Confirm", style="Accent.TButton", command=confirm).pack(side="right", padx=5)

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

    global tree_shares, lbl_samba

    page, card, toolbar = build_page(
        parent,
        "Samba Shares",
        "Manage folders shared on the network via Samba."
    )

    tree_shares = build_treeview(
        card,
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

    lbl_samba = tk.Label(toolbar, text="Force User: -", bg=BG, fg=MUTED, font=(FONT, 9))
    lbl_samba.pack(side="left", padx=(0, 16))

    ttk.Button(toolbar, text="Change User", command=change_samba_user).pack(side="left")

    ttk.Button(toolbar, text="Save", style="Accent.TButton", command=save_samba).pack(side="right")
    ttk.Button(toolbar, text="Delete", style="Danger.TButton", command=delete_share).pack(side="right", padx=5)
    ttk.Button(toolbar, text="Edit", command=lambda: edit_share(True)).pack(side="right", padx=5)
    ttk.Button(toolbar, text="Add", command=edit_share).pack(side="right", padx=5)


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

    frame = tk.Frame(win, bg=SURFACE, padx=24, pady=24)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Share name", bg=SURFACE, fg=TEXT, font=(FONT, 10)).pack(anchor="w")

    e_name = ttk.Entry(frame)
    e_name.insert(0, name)
    e_name.pack(fill="x", pady=(5, 12))

    tk.Label(frame, text="Path", bg=SURFACE, fg=TEXT, font=(FONT, 10)).pack(anchor="w")

    e_path = ttk.Entry(frame)
    e_path.insert(0, path_value)
    e_path.pack(fill="x", pady=(5, 12))

    tk.Label(
        frame,
        text="The folder will be created automatically if it doesn't exist.",
        bg=SURFACE, fg=MUTED, font=(FONT, 9)
    ).pack(anchor="w")

    btns = tk.Frame(win, bg=SURFACE)
    btns.pack(side="bottom", fill="x", padx=24, pady=18)

    def save():

        new_name = e_name.get().strip()
        new_path = e_path.get().strip()

        if not new_name or not new_path:
            messagebox.showwarning("Warning", "Please fill in both fields")
            return

        ok1, m1 = run_sudo(["mkdir", "-p", new_path])
        ok2, m2 = run_sudo(["chmod", "755", new_path])
        ok3, m3 = run_sudo(["chown", f"{SAMBA_USER}:{SAMBA_USER}", new_path])

        if not (ok1 and ok2 and ok3):
            messagebox.showerror("Error", f"Failed to prepare the folder:\n{m1 or m2 or m3}")
            return

        values = (new_name, new_path)

        if edit:
            tree_shares.item(item, values=values)
        else:
            tree_shares.insert("", "end", values=values)

        win.destroy()

    ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right")
    ttk.Button(btns, text="Save", style="Accent.TButton", command=save).pack(side="right", padx=5)

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

    ok1, m1 = run_sudo(["cp", "/tmp/smb.conf", "/etc/samba/smb.conf"])
    ok2, m2 = run_sudo(["systemctl", "restart", "smbd"])

    if not (ok1 and ok2):
        messagebox.showerror("Error", f"Failed to apply the Samba configuration:\n{m1 or m2}")
        return

    messagebox.showinfo("Saved", "Samba configuration updated")


def change_samba_user():

    global SAMBA_USER

    win = open_dialog("Force User", 380, 190)

    frame = tk.Frame(win, bg=SURFACE, padx=24, pady=24)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Linux user", bg=SURFACE, fg=TEXT, font=(FONT, 10)).pack(anchor="w")

    entry = ttk.Entry(frame)
    entry.insert(0, SAMBA_USER)
    entry.pack(fill="x", pady=(5, 0))
    entry.focus()

    btns = tk.Frame(frame, bg=SURFACE)
    btns.pack(fill="x", pady=(20, 0))

    def confirm():

        global SAMBA_USER

        user = entry.get().strip()

        if not user:
            win.destroy()
            return

        SAMBA_USER = user
        lbl_samba.config(text=f"Force User: {user}")

        win.destroy()

    ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right")
    ttk.Button(btns, text="Confirm", style="Accent.TButton", command=confirm).pack(side="right", padx=5)

    win.bind("<Return>", lambda e: confirm())
    win.bind("<Escape>", lambda e: win.destroy())

########################################################
# CONKY TAB
########################################################

def build_conky_tab(parent):

    global tree_conky

    page, card, toolbar = build_page(
        parent,
        "Conky Disks",
        "Disks displayed in the Conky system monitor."
    )

    tree_conky = build_treeview(
        card,
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

    ttk.Button(toolbar, text="Save", style="Accent.TButton", command=save_conky).pack(side="right")
    ttk.Button(toolbar, text="Delete", style="Danger.TButton", command=delete_conky).pack(side="right", padx=5)
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

    frame = tk.Frame(win, bg=SURFACE, padx=24, pady=24)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Name", bg=SURFACE, fg=TEXT, font=(FONT, 10)).pack(anchor="w")

    e_name = ttk.Entry(frame)
    e_name.insert(0, name)
    e_name.pack(fill="x", pady=(5, 12))

    tk.Label(frame, text="Path", bg=SURFACE, fg=TEXT, font=(FONT, 10)).pack(anchor="w")

    e_path = ttk.Entry(frame)
    e_path.insert(0, path_value)
    e_path.pack(fill="x", pady=(5, 12))

    tk.Label(
        frame,
        text="This disk will be displayed in the Conky panel.",
        bg=SURFACE, fg=MUTED, font=(FONT, 9)
    ).pack(anchor="w")

    btns = tk.Frame(win, bg=SURFACE)
    btns.pack(side="bottom", fill="x", padx=24, pady=18)

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
    ttk.Button(btns, text="Save", style="Accent.TButton", command=save).pack(side="right", padx=5)

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

    page, card, toolbar = build_page(
        parent,
        "FileBrowser",
        "Web-based file manager exposed on the local network."
    )

    inner = tk.Frame(card, bg=SURFACE)
    inner.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(inner, text="Root Path", bg=SURFACE, fg=TEXT, font=(FONT, 10)).pack(anchor="w")

    en_fb_path = ttk.Entry(inner)
    en_fb_path.pack(fill="x", pady=(6, 20))

    tk.Label(inner, text="Service Status", bg=SURFACE, fg=TEXT, font=(FONT, 10)).pack(anchor="w")

    lbl_fb_status = status_badge(inner)
    lbl_fb_status.pack(anchor="w", pady=(6, 0))

    ttk.Button(toolbar, text="Refresh Status", command=refresh_filebrowser_status).pack(side="left")
    ttk.Button(toolbar, text="Stop", style="Danger.TButton", command=stop_filebrowser).pack(side="left", padx=5)
    ttk.Button(toolbar, text="Start", style="Accent.TButton", command=start_filebrowser).pack(side="left")


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
    set_status_badge(lbl_fb_status, service_is_active(FILEBROWSER_SERVICE))


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

    global lbl_monitor_status, tree_monitor

    page, card, toolbar = build_page(
        parent,
        "Server Monitor",
        "Controls the Sevastolink API used to feed the Rainmeter skin."
    )

    info = tk.Frame(card, bg=SURFACE)
    info.pack(fill="x", padx=16, pady=(16, 0))

    lbl_monitor_status = status_badge(info)
    lbl_monitor_status.pack(side="left")

    tk.Label(
        info,
        text=f"Endpoint: http://{socket.gethostname()}:{MONITOR_PORT}/api/rainmeter",
        bg=SURFACE, fg=MUTED, font=(FONT, 9)
    ).pack(side="left", padx=(12, 0))

    tree_monitor = build_treeview(
        card,
        columns=("metric", "value"),
        headings=("Metric", "Value"),
        widths=(240, 460)
    )

    ttk.Button(toolbar, text="Refresh Data", style="Accent.TButton", command=fetch_monitor_data).pack(side="right")
    ttk.Button(toolbar, text="Restart", command=restart_monitor).pack(side="left", padx=(0, 5))
    ttk.Button(toolbar, text="Stop", style="Danger.TButton", command=stop_monitor).pack(side="left", padx=5)
    ttk.Button(toolbar, text="Start", command=start_monitor).pack(side="left")


def refresh_monitor_status():
    set_status_badge(lbl_monitor_status, service_is_active(MONITOR_SERVICE))


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

load_samba_user()
load_samba()
load_conky()
load_filebrowser()

refresh_filebrowser_status()
refresh_monitor_status()

root.mainloop()
