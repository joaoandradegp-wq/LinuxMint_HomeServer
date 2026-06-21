import tkinter as tk
from tkinter import ttk, simpledialog, Toplevel, messagebox
from pathlib import Path

import subprocess
import re

root = tk.Tk()

root.title("Lightweight Home Server Manager")
root.geometry("760x480")
root.minsize(700, 450)

########################################################
# TABS
########################################################

tabs = ttk.Notebook(root)

tab_share = ttk.Frame(tabs)
tab_conky = ttk.Frame(tabs)
tab_fb = ttk.Frame(tabs)

tabs.add(tab_share, text="Compartilhamentos")
tabs.add(tab_conky, text="Conky")
tabs.add(tab_fb, text="FileBrowser")

tabs.pack(fill="both", expand=True)

########################################################
# ABA COMPARTILHAMENTOS
########################################################

tree_share = ttk.Treeview(
    tab_share,
    columns=("nome", "path"),
    show="headings"
)

tree_share.heading("nome", text="Compartilhamento")
tree_share.heading("path", text="Caminho")

tree_share.column("nome", width=200)
tree_share.column("path", width=500)

tree_share.pack(fill="both", expand=True, padx=5, pady=5)


def on_share_double_click(event):

    item = tree_share.identify_row(event.y)

    if item:
        tree_share.selection_set(item)
        edit_share(True)


tree_share.bind("<Double-1>", on_share_double_click)

frame_share = tk.Frame(tab_share)
frame_share.pack(pady=5)

########################################################
# ABA CONKY
########################################################

tree_conky = ttk.Treeview(
    tab_conky,
    columns=("idx", "nome", "path"),
    show="headings"
)

tree_conky.heading("idx", text="#")
tree_conky.heading("nome", text="Nome")
tree_conky.heading("path", text="Caminho")

tree_conky.column("idx", width=40)
tree_conky.column("nome", width=180)
tree_conky.column("path", width=300)

tree_conky.pack(fill="both", expand=True, padx=5, pady=(5, 0))

frame_conky = tk.Frame(tab_conky)
frame_conky.pack(fill="x", pady=5, padx=5)


def on_conky_double_click(event):

    item = tree_conky.identify_row(event.y)

    if item:
        tree_conky.selection_set(item)
        edit_conky(True)


tree_conky.bind("<Double-1>", on_conky_double_click)

########################################################
# ABA FILEBROWSER
########################################################

frame_fb = tk.Frame(tab_fb)
frame_fb.pack(pady=20)

tk.Label(frame_fb, text="Root FileBrowser").pack()

txt_fb = tk.Text(frame_fb, height=3, width=70)
txt_fb.pack(pady=10)

########################################################
# SAMBA GLOBAL
########################################################

SAMBA_USER = ""
lbl_samba = tk.Label(frame_share, text="Force User: -")

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

    m = re.search(r'force user\s*=\s*(.+)',txt,re.I)

    SAMBA_USER = m.group(1).strip() if m else ""

    lbl_samba.config(text=f"Force User: {SAMBA_USER}")


def load_samba():

    tree_share.delete(*tree_share.get_children())

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

        nome = s.group(1).strip()

        if nome.lower() in ignore:
            continue

        body = s.group(2)

        m = re.search(r'path\s*=\s*(.+)', body)

        caminho = m.group(1).strip() if m else ""

        tree_share.insert("", "end", values=(nome, caminho))

########################################################
# EDIT SHARE
########################################################

def edit_share(edit=False):

    item = None
    nome = ""
    caminho = ""

    if edit:

        sel = tree_share.selection()

        if not sel:
            return

        item = sel[0]

        nome, caminho = tree_share.item(item)["values"]

    win = Toplevel(root)

    win.title("Compartilhamento")
    win.geometry("520x240")
    win.resizable(False, False)

    frame = tk.Frame(win, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="Configuração do Compartilhamento",
        font=("Arial", 12, "bold")
    ).pack(pady=(0, 15))

    row1 = tk.Frame(frame)
    row1.pack(fill="x", pady=5)

    tk.Label(row1, text="Nome", width=15, anchor="w").pack(side="left")

    e_nome = tk.Entry(row1, width=45)
    e_nome.pack(side="left", fill="x", expand=True)
    e_nome.insert(0, nome)

    row2 = tk.Frame(frame)
    row2.pack(fill="x", pady=5)

    tk.Label(row2, text="Caminho", width=15, anchor="w").pack(side="left")

    e_path = tk.Entry(row2, width=45)
    e_path.pack(side="left", fill="x", expand=True)
    e_path.insert(0, caminho)

    tk.Label(
        frame,
        text="A pasta será criada automaticamente caso não exista.",
        fg="gray"
    ).pack(pady=15)

    bottom = tk.Frame(frame)
    bottom.pack(side="bottom", fill="x")

    def save():

        nome = e_nome.get().strip()
        caminho = e_path.get().strip()

        if not nome or not caminho:
            return

        subprocess.run(["sudo", "mkdir", "-p", caminho])
        subprocess.run(["sudo", "chmod", "755", caminho])

        subprocess.run(["sudo","chown",f"{SAMBA_USER}:{SAMBA_USER}",caminho])

        values = (nome, caminho)

        if edit:
            tree_share.item(item, values=values)

        else:
            tree_share.insert("", "end", values=values)

        win.destroy()

    tk.Button(bottom, text="Salvar", width=12, command=save).pack(side="right", padx=5)
    tk.Button(bottom, text="Cancelar", width=12, command=win.destroy).pack(side="right")

########################################################
# DELETE SHARE
########################################################

def delete_share():

    sel = tree_share.selection()

    if sel:
        tree_share.delete(sel[0])

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

    for item in tree_share.get_children():

        nome, caminho = tree_share.item(item)["values"]

        txt += f"""

[{nome}]
path = {caminho}

browseable = yes
read only = no

guest ok = yes
force user = {SAMBA_USER}

"""

    Path("/tmp/smb.conf").write_text(txt)

    subprocess.run(["sudo","cp","/tmp/smb.conf","/etc/samba/smb.conf"])

    subprocess.run(["sudo","systemctl","restart","smbd"])

    messagebox.showinfo("OK", "Samba atualizado")

########################################################
# ALTERAR SENHA SAMBA
########################################################

def change_samba_user():

    global SAMBA_USER

    user = simpledialog.askstring(
        "Force User",
        "Usuário Linux:",
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

    for idx, nome, mount in pattern:

        tree_conky.insert("","end",values=(int(idx), nome.strip(), mount.strip()))


def edit_conky(edit=False):

    item = None

    idx = 0
    nome = ""
    caminho = ""

    if edit:

        sel = tree_conky.selection()

        if not sel:
            return

        item = sel[0]

        idx, nome, caminho = tree_conky.item(item)["values"]

    else:

        idx = len(tree_conky.get_children()) + 1

    win = Toplevel(root)

    win.title("Disco Conky")
    win.geometry("520x240")
    win.resizable(False, False)

    frame = tk.Frame(win, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="Configuração Disco Conky",
        font=("Arial", 12, "bold")
    ).pack(pady=(0, 15))

    row1 = tk.Frame(frame)
    row1.pack(fill="x", pady=5)

    tk.Label(row1, text="Nome", width=15, anchor="w").pack(side="left")

    e_nome = tk.Entry(row1, width=45)
    e_nome.pack(side="left", fill="x", expand=True)
    e_nome.insert(0, nome)

    row2 = tk.Frame(frame)
    row2.pack(fill="x", pady=5)

    tk.Label(row2, text="Caminho", width=15, anchor="w").pack(side="left")

    e_path = tk.Entry(row2, width=45)
    e_path.pack(side="left", fill="x", expand=True)
    e_path.insert(0, caminho)

    tk.Label(
        frame,
        text="Este disco será exibido no painel Conky.",
        fg="gray"
    ).pack(pady=15)

    bottom = tk.Frame(frame)
    bottom.pack(side="bottom", fill="x")

    def save():

        nome = e_nome.get().strip()
        caminho = e_path.get().strip()

        if not nome or not caminho:
            return

        values = (idx, nome, caminho)

        if edit:
            tree_conky.item(item, values=values)

        else:
            tree_conky.insert("", "end", values=values)

        win.destroy()

    tk.Button(bottom, text="Salvar", width=12, command=save).pack(side="right", padx=5)
    tk.Button(bottom, text="Cancelar", width=12, command=win.destroy).pack(side="right")


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

        idx, nome, caminho = tree_conky.item(item)["values"]

        disk_lines.extend([
            f"${{color grey}}DISK {int(idx):02d} ({nome}):${{color}} ${{fs_used_perc {caminho}}}%",
            f"${{fs_bar 8 {caminho}}}",
            f"${{fs_used {caminho}}} / ${{fs_size {caminho}}}",
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

    messagebox.showinfo("OK", "Conky atualizado")

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

########################################################
# BOTÕES
########################################################

tk.Button(frame_share, text="Adicionar", command=edit_share).pack(side="left", padx=5)
tk.Button(frame_share, text="Excluir", command=delete_share).pack(side="left", padx=5)
tk.Button(frame_share, text="Salvar", command=save_samba).pack(side="left", padx=5)

lbl_samba.pack(side="left", padx=20)

tk.Button(
    frame_share,
    text="Alterar Usuário / Senha",
    command=change_samba_user
).pack(side="left")

tk.Button(frame_conky, text="Adicionar", command=edit_conky).pack(side="left")
tk.Button(frame_conky, text="Excluir", command=delete_conky).pack(side="left")
tk.Button(frame_conky, text="Salvar", command=save_conky).pack(side="left")

########################################################

load_samba_user()
load_samba()
load_conky()
load_filebrowser()

root.mainloop()
