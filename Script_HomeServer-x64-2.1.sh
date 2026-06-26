#!/bin/bash

# ══════════════════════════════════════════════════════════════════════════════
#  HOME SERVER SETUP — Linux Mint 22.3 (Noble/Ubuntu 24.04 base) — v2.1
#  Created by João Andrade aka Phobos
#  Tested on: Linux Mint 22.3 XFCE x64
#  GitHub: https://github.com/joaoandradegp-wq/LinuxMint_HomeServer
#  Note: Run as root or with sudo. The real user is detected automatically.
# ══════════════════════════════════════════════════════════════════════════════

# ── Detects the real user (whoever ran the script, even via sudo) ─────────────
if [ -n "$SUDO_USER" ]; then
    CURRENT_USER="$SUDO_USER"
else
    CURRENT_USER="$(whoami)"
fi
USER_HOME="$(eval echo ~"$CURRENT_USER")"

echo "=== User detected: $CURRENT_USER (home: $USER_HOME) ==="

# ── Log de execução ───────────────────────────────────────────────────────────
LOG_FILE="$USER_HOME/homeserver-setup-$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "=== Log iniciado: $LOG_FILE ==="

# ══════════════════════════════════════════════════════════════════════════════
echo "=== UPDATING SYSTEM ==="
# ══════════════════════════════════════════════════════════════════════════════

sudo apt update && sudo apt upgrade -y

# ══════════════════════════════════════════════════════════════════════════════
echo "=== REMOVING UNNECESSARY PACKAGES ==="
# ══════════════════════════════════════════════════════════════════════════════

# --ignore-missing prevents errors if a package no longer exists in Mint 22
sudo apt remove -y --ignore-missing \
    libreoffice* thunderbird hexchat \
    transmission-gtk pidgin drawing \
    rhythmbox simple-scan cheese

sudo apt autoremove -y

# ══════════════════════════════════════════════════════════════════════════════
echo "=== DISABLING UNUSED SERVICES ==="
# ══════════════════════════════════════════════════════════════════════════════

sudo systemctl disable bluetooth           2>/dev/null
sudo systemctl disable cups                2>/dev/null
sudo systemctl disable avahi-daemon        2>/dev/null

# Added in v2.1: disable modem and speech services rarely needed on a server
sudo systemctl disable ModemManager.service    2>/dev/null
sudo systemctl stop    ModemManager.service    2>/dev/null

sudo systemctl disable speech-dispatcher.service 2>/dev/null
sudo systemctl stop    speech-dispatcher.service 2>/dev/null

# ══════════════════════════════════════════════════════════════════════════════
echo "=== DISABLING TRACKER (if present) ==="
# ══════════════════════════════════════════════════════════════════════════════

# tracker3 indexes files for desktop search — not useful on a headless server
if command -v tracker3 >/dev/null 2>&1; then
    systemctl --user mask tracker-miner-fs-3.service 2>/dev/null
    systemctl --user stop tracker-miner-fs-3.service 2>/dev/null
    echo "tracker3 disabled."
else
    echo "tracker3 not found — skipping."
fi

# ══════════════════════════════════════════════════════════════════════════════
echo "=== INSTALLING REQUIRED PACKAGES ==="
# ══════════════════════════════════════════════════════════════════════════════

# zram-config was renamed to zram-tools in Ubuntu 24.04 (Mint 22 base)
sudo apt install -y \
    samba cifs-utils curl wget net-tools \
    lm-sensors hdparm dconf-cli conky-all \
    zram-tools

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING KERNEL MEMORY PARAMETERS ==="
# ══════════════════════════════════════════════════════════════════════════════

# v2.1: replaced the old 99-swappiness.conf with a single unified file.
# Remove the old file if it exists to avoid duplicate/conflicting settings.
sudo rm -f /etc/sysctl.d/99-swappiness.conf

sudo tee /etc/sysctl.d/99-homeserver.conf > /dev/null << EOF
vm.swappiness=10
vm.vfs_cache_pressure=50
vm.dirty_background_ratio=2
vm.dirty_ratio=10
EOF

sudo sysctl --system

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING CPU GOVERNOR ==="
# ══════════════════════════════════════════════════════════════════════════════

sudo bash -c 'cat > /etc/systemd/system/cpu-governor.service << EOF
[Unit]
Description=CPU Governor Schedutil

[Service]
Type=oneshot
ExecStart=/bin/bash -c "for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo schedutil > \$cpu; done"

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable cpu-governor
sudo systemctl restart cpu-governor

# ══════════════════════════════════════════════════════════════════════════════
echo "=== INSTALLING PYTHON ENVIRONMENT ==="
# ══════════════════════════════════════════════════════════════════════════════

sudo apt install -y \
    python3 \
    python3-pip \
    python3-tk

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING HDD SCHEDULER ==="
# ══════════════════════════════════════════════════════════════════════════════

# Mint 22 uses kernel 6.x; "deadline" was renamed to "mq-deadline" in kernel 5+
sudo bash -c 'cat > /etc/udev/rules.d/60-ioschedulers.rules << EOF
ACTION=="add|change", KERNEL=="sda", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="mq-deadline"
ACTION=="add|change", KERNEL=="sdb", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="mq-deadline"
EOF'

sudo udevadm control --reload-rules
sudo udevadm trigger

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING JOURNAL IN RAM ==="
# ══════════════════════════════════════════════════════════════════════════════

sudo mkdir -p /etc/systemd/journald.conf.d

sudo tee /etc/systemd/journald.conf.d/ram.conf > /dev/null << EOF
[Journal]
Storage=volatile
RuntimeMaxUse=50M
RuntimeKeepFree=30M
MaxRetentionSec=1day
EOF

sudo systemctl restart systemd-journald
sudo journalctl --vacuum-size=50M

# ══════════════════════════════════════════════════════════════════════════════
echo "=== DISABLING DESKTOP ANIMATIONS ==="
# ══════════════════════════════════════════════════════════════════════════════

# Mint 22 XFCE: only xfconf-query is relevant.
# GNOME/Cinnamon commands are silenced with 2>/dev/null.
gsettings set org.gnome.desktop.interface enable-animations false 2>/dev/null
gsettings set org.cinnamon desktop-effects false                  2>/dev/null
gsettings set org.cinnamon.muffin desktop-effects false           2>/dev/null
xfconf-query -c xfwm4 -p /general/use_compositing -s false       2>/dev/null

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING NOATIME ==="
# ══════════════════════════════════════════════════════════════════════════════

# Idempotent: only write a backup and modify fstab if noatime isn't already set
if ! grep -q noatime /etc/fstab; then
    sudo cp /etc/fstab /etc/fstab.backup
    sudo sed -i 's/errors=remount-ro/errors=remount-ro,noatime,nodiratime/' /etc/fstab
    sudo sed -i 's/defaults,nofail/defaults,noatime,nodiratime,nofail/'     /etc/fstab
    echo "noatime applied to /etc/fstab."
else
    echo "noatime already present in /etc/fstab — skipping."
fi

sudo mount -o remount /
sudo mount -o remount /mnt/hd2 2>/dev/null

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CREATING SERVER DIRECTORY ==="
# ══════════════════════════════════════════════════════════════════════════════

mkdir -p "$USER_HOME/Server"
chown "$CURRENT_USER":"$CURRENT_USER" "$USER_HOME/Server"
chmod 755 "$USER_HOME/Server"

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING SAMBA ==="
# ══════════════════════════════════════════════════════════════════════════════

# Idempotent: always rewrites the full config from scratch.
# socket options intentionally omitted — modern kernels handle TCP_NODELAY
# automatically and Samba 4.x deprecated manual tuning of this option.
cp /etc/samba/smb.conf /etc/samba/smb.conf.bak 2>/dev/null || true

sudo bash -c "cat > /etc/samba/smb.conf << EOF
[global]
workgroup = WORKGROUP
server string = Linux Home Server
security = user
map to guest = bad user
min protocol = SMB2
deadtime = 15
aio read size = 1
aio write size = 1

[server]
path = $USER_HOME/Server
browseable = yes
read only = no
valid users = $CURRENT_USER
EOF"

# ══════════════════════════════════════════════════════════════════════════════
echo "=== SETTING SAMBA AND FILEBROWSER PASSWORD ==="
# ══════════════════════════════════════════════════════════════════════════════

GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"

while true; do
    echo -e "${GREEN}Enter the password for Samba and FileBrowser (minimum 12 characters): ${RESET}"
    read -s SMB_PASS < /dev/tty
    echo
    echo -e "${GREEN}Confirm password: ${RESET}"
    read -s SMB_PASS2 < /dev/tty
    echo
    if [ ${#SMB_PASS} -lt 12 ]; then
        echo -e "${RED}Password must contain at least 12 characters.${RESET}"
        continue
    fi
    if [ "$SMB_PASS" != "$SMB_PASS2" ]; then
        echo -e "${RED}Passwords do not match.${RESET}"
        continue
    fi
    break
done

sudo smbpasswd -x "$CURRENT_USER" 2>/dev/null || true
printf "%s\n%s\n" "$SMB_PASS" "$SMB_PASS" | sudo smbpasswd -a "$CURRENT_USER"
sudo smbpasswd -e "$CURRENT_USER"

FB_PASS="$SMB_PASS"

sudo systemctl restart smbd
sudo systemctl enable smbd

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING FIREWALL ==="
# ══════════════════════════════════════════════════════════════════════════════

sudo ufw allow samba 2>/dev/null

# ══════════════════════════════════════════════════════════════════════════════
echo "=== INSTALLING TAILSCALE ==="
# ══════════════════════════════════════════════════════════════════════════════

curl -fsSL https://tailscale.com/install.sh | sh

if ! command -v tailscale >/dev/null 2>&1; then
    echo "Tailscale installation failed."
    exit 1
fi

echo ""
echo "============================================================"
echo "TAILSCALE SETUP"
echo "============================================================"
echo ""
echo "Press ENTER to start the authentication process."
read -p "" < /dev/tty

sudo tailscale up --accept-dns=false < /dev/tty

# ══════════════════════════════════════════════════════════════════════════════
echo "=== REMOVING FIREFOX ==="
# ══════════════════════════════════════════════════════════════════════════════

sudo apt purge -y firefox firefox-locale-*
sudo apt autoremove -y
sudo apt autoclean

# ══════════════════════════════════════════════════════════════════════════════
echo "=== INSTALLING FILEBROWSER ==="
# ══════════════════════════════════════════════════════════════════════════════

curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash

sleep 2
command -v filebrowser >/dev/null 2>&1 || {
    echo "FileBrowser install failed"
    exit 1
}
mkdir -p "$USER_HOME/Server"

rm -f "$USER_HOME/filebrowser.db"
touch "$USER_HOME/filebrowser.db"

chown "$CURRENT_USER:$CURRENT_USER" "$USER_HOME/filebrowser.db"
chmod 600 "$USER_HOME/filebrowser.db"

chown -R "$CURRENT_USER:$CURRENT_USER" "$USER_HOME/Server"
chmod 755 "$USER_HOME/Server"

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING FILEBROWSER USER ==="
# ══════════════════════════════════════════════════════════════════════════════

# Remove banco antigo para garantir estado limpo
rm -f "$USER_HOME/filebrowser.db"

# Inicializa o banco corretamente
filebrowser config init -d "$USER_HOME/filebrowser.db"
filebrowser config set -d "$USER_HOME/filebrowser.db" --root "$USER_HOME/Server"

# Remove o admin padrão e cria o usuário correto
filebrowser users rm admin -d "$USER_HOME/filebrowser.db" 2>/dev/null || true

filebrowser users add "$CURRENT_USER" "$FB_PASS" \
    -d "$USER_HOME/filebrowser.db" \
    --perm.admin \
    --scope "$USER_HOME/Server"

chown "$CURRENT_USER":"$CURRENT_USER" "$USER_HOME/filebrowser.db"
chmod 600 "$USER_HOME/filebrowser.db"

sudo bash -c "cat > /etc/systemd/system/filebrowser.service << EOF
[Unit]
Description=File Browser
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$USER_HOME
ExecStart=/usr/local/bin/filebrowser \\
    -r /home/$CURRENT_USER/Server \\
    -d $USER_HOME/filebrowser.db \\
    -a 0.0.0.0 \\
    -p 8080

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable filebrowser

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING SENSORS ==="
# ══════════════════════════════════════════════════════════════════════════════

sudo sensors-detect --auto || true

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING HDD SPINDOWN AND POWER MANAGEMENT ==="
# ══════════════════════════════════════════════════════════════════════════════

# v2.1: added apm = 254 to keep APM active without aggressive power-saving
# spindown_time = 180 → approx. 15 minutes (180 × 5 s)
sudo tee /etc/hdparm.conf > /dev/null << EOF
/dev/sda {
    spindown_time = 180
    apm = 254
}

/dev/sdb {
    spindown_time = 180
    apm = 254
}
EOF

# ══════════════════════════════════════════════════════════════════════════════
echo "=== INSTALLING ANYDESK ==="
# ══════════════════════════════════════════════════════════════════════════════

# Mint 22 is 64-bit (noble/jammy base). apt-key is deprecated;
# using the modern method with keyring in /etc/apt/keyrings/.
sudo install -m 0755 -d /etc/apt/keyrings

wget -qO - https://keys.anydesk.com/repos/DEB-GPG-KEY \
    | gpg --dearmor \
    | sudo tee /etc/apt/keyrings/anydesk.gpg > /dev/null

echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/anydesk.gpg] \
http://deb.anydesk.com/ all main" \
    | sudo tee /etc/apt/sources.list.d/anydesk.list

sudo apt update

if ! sudo apt install -y anydesk; then
    echo "AnyDesk not available, installing x11vnc as alternative..."
    sudo apt install -y x11vnc
fi

# ══════════════════════════════════════════════════════════════════════════════
echo "=== CONFIGURING CONKY ==="
# ══════════════════════════════════════════════════════════════════════════════

# Conky 1.19+ (Mint 22) removed use_xft; font is configured via 'font' only.
cat > "$USER_HOME/.conkyrc" << 'EOF'
conky.config = {
    alignment = 'top_right',
    gap_x = 20,
    gap_y = 5,

    minimum_width = 300,
    maximum_width = 400,

    background = false,
    update_interval = 1,
    double_buffer = true,

    own_window = true,
    own_window_type = 'dock',
    own_window_transparent = true,
    own_window_argb_visual = true,
    own_window_argb_value = 0,

    draw_shades = false,
    draw_outline = false,
    draw_borders = false,

    use_xft = true,
    font = 'DejaVu Sans:size=11',
};

conky.text = [[
${alignr}${execi 3600 cat /proc/cpuinfo | grep "model name" | head -1 | cut -d ':' -f2 | sed 's/^ //'}

${color grey}Cores:${color} ${execi 60 nproc}
${color grey}Frequency:${color} ${freq_g}GHz 
${color grey}Temperature:${color} ${execi 5 sensors | grep 'Core 0' | awk '{print $3}'}
${color grey}Usage:${color} ${cpu}% 
${cpubar 8}

${color grey}RAM:${color}
$mem / $memmax
${membar 8}

${color grey}SWAP:${color}
$swap / $swapmax
${swapbar 8}

${color grey}DISK 01 (HDD):${color} ${fs_used_perc /}% 
${fs_bar 8 /}
${fs_used /} / ${fs_size /}

${color grey}NETWORK (LAN):${color}
IP: ${execi 10 hostname -I | awk '{print $1}' | sed 's/^$/Offline/'}
Down: ${downspeed enp2s0}
Up:     ${upspeed enp2s0}

${color grey}FILE BROWSER:${color} \
${if_match ${execi 10 systemctl is-active filebrowser | grep -c active} == 1}\
${color green}ONLINE${color}\
${else}\
${color red}OFFLINE${color}\
${endif}

${color grey}TAILSCALE:${color}
IP: ${if_up tailscale0}${addr tailscale0}${else}Offline${endif}

${color grey}SYSTEM:${color}
Uptime: ${uptime_short}
]];
EOF

chown "$CURRENT_USER":"$CURRENT_USER" "$USER_HOME/.conkyrc"

# ══════════════════════════════════════════════════════════════════════════════
echo "=== ENABLING CONKY AUTO START ==="
# ══════════════════════════════════════════════════════════════════════════════

mkdir -p "$USER_HOME/.config/autostart"

cat > "$USER_HOME/.config/autostart/conky.desktop" << EOF
[Desktop Entry]
Type=Application
Exec=conky
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Conky Monitor
EOF

chown -R "$CURRENT_USER":"$CURRENT_USER" "$USER_HOME/.config"

echo "=== INSTALLING DESKTOP SHORTCUTS ==="

DESKTOP_DIR=$(sudo -u "$CURRENT_USER" xdg-user-dir DESKTOP 2>/dev/null)
if [ -z "$DESKTOP_DIR" ]; then
    DESKTOP_DIR="$USER_HOME/Desktop"
fi

wget -q -O "$USER_HOME/Python_ServerPanel.py" \
https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Python_ServerPanel.py

chmod +x "$USER_HOME/Python_ServerPanel.py"
chown "$CURRENT_USER:$CURRENT_USER" "$USER_HOME/Python_ServerPanel.py"

cat > "$DESKTOP_DIR/Server.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Link
Name=Server Folder
Comment=
Icon=web-icq
URL=$USER_HOME/Server/
EOF

cat > "$DESKTOP_DIR/Conky.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Link
Name=Conky Configuration
Comment=
Icon=utilities-system-monitor
URL=$USER_HOME/.conkyrc
EOF

cat > "$DESKTOP_DIR/ServerPanel.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Server Panel
Exec=python3 /home/phobos/Python_ServerPanel.py
Icon=preferences-system
Terminal=false
EOF

chmod +x "$DESKTOP_DIR"/*.desktop 2>/dev/null
chown "$CURRENT_USER:$CURRENT_USER" "$DESKTOP_DIR"/*.desktop 2>/dev/null

echo "=== STARTING FILEBROWSER ==="
sudo systemctl restart filebrowser
sleep 2

# ══════════════════════════════════════════════════════════════════════════════
echo ""
echo "===== VALIDATION ====="
# ══════════════════════════════════════════════════════════════════════════════

echo ""
echo "--- CPU Governor ---"
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

echo ""
echo "--- Kernel Parameters ---"
sysctl vm.swappiness
sysctl vm.vfs_cache_pressure
sysctl vm.dirty_background_ratio
sysctl vm.dirty_ratio

echo ""
echo "--- SWAP / ZRAM ---"
swapon --show

echo ""
echo "--- noatime mounts ---"
mount | grep noatime

echo ""
echo "--- Journal disk usage ---"
journalctl --disk-usage

echo ""
echo "--- I/O Schedulers ---"
cat /sys/block/sda/queue/scheduler 2>/dev/null || echo "sda not found"
cat /sys/block/sdb/queue/scheduler 2>/dev/null || echo "sdb not found"

echo ""
echo "--- Memory ---"
free -h

echo ""

HOSTNAME_LOCAL=$(hostname)
TAILSCALE_IP=$(tailscale ip -4)

echo "═════════════════════════════════════════════"
echo "  SETUP COMPLETED — v2.1"
echo "═════════════════════════════════════════════"
echo ""
echo "  Tailscale IP: $TAILSCALE_IP"
echo "  Samba:        smb://$HOSTNAME_LOCAL/server"
echo "  FileBrowser:  http://$TAILSCALE_IP:8080"
echo ""
echo "  Recommended: reboot the system now."
echo "═════════════════════════════════════════════"
