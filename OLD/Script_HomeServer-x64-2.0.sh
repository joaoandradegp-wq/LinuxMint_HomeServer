#!/bin/bash

# ── Detects the real user (whoever ran the script, even via sudo) ─────────────
if [ -n "$SUDO_USER" ]; then
    CURRENT_USER="$SUDO_USER"
else
    CURRENT_USER="$(whoami)"
fi
USER_HOME="$(eval echo ~"$CURRENT_USER")"

echo "=== User detected: $CURRENT_USER (home: $USER_HOME) ==="

echo "=== UPDATING SYSTEM ==="
sudo apt update && sudo apt upgrade -y

echo "=== REMOVING UNNECESSARY PACKAGES ==="

# --ignore-missing prevents errors if a package no longer exists in Mint 22
sudo apt remove -y --ignore-missing \
libreoffice* thunderbird hexchat \
transmission-gtk pidgin drawing \
rhythmbox simple-scan cheese

sudo apt autoremove -y

echo "=== DISABLING UNUSED SERVICES ==="

sudo systemctl disable bluetooth    2>/dev/null
sudo systemctl disable cups         2>/dev/null
sudo systemctl disable avahi-daemon 2>/dev/null

echo "=== INSTALLING REQUIRED PACKAGES ==="

# zram-config was renamed to zram-tools in Ubuntu 24.04 (Mint 22 base)
sudo apt install -y \
samba cifs-utils curl wget net-tools \
lm-sensors hdparm dconf-cli conky-all \
zram-tools

echo "=== CONFIGURING SWAPPINESS ==="

echo "vm.swappiness=10" | \
sudo tee /etc/sysctl.d/99-swappiness.conf

sudo sysctl -w vm.swappiness=10

echo "=== CONFIGURING CPU GOVERNOR ==="

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

echo "=== INSTALLING PYTHON ENVIRONMENT ==="

sudo apt update

sudo apt install -y \
python3 \
python3-pip \
python3-tk

echo "=== CONFIGURING HDD SCHEDULER ==="

# On kernel 5.x+ (Mint 22 uses kernel 6.x) the "deadline" scheduler was
# renamed to "mq-deadline". The script uses whichever is available.
sudo bash -c 'cat > /etc/udev/rules.d/60-ioschedulers.rules << EOF
ACTION=="add|change", KERNEL=="sda", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="mq-deadline"
ACTION=="add|change", KERNEL=="sdb", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="mq-deadline"
EOF'

sudo udevadm control --reload-rules
sudo udevadm trigger

echo "=== CONFIGURING JOURNAL IN RAM ==="

sudo mkdir -p /etc/systemd/journald.conf.d

sudo bash -c 'cat > /etc/systemd/journald.conf.d/ram.conf << EOF
[Journal]
Storage=volatile
RuntimeMaxUse=50M
EOF'

sudo systemctl restart systemd-journald

sudo journalctl --vacuum-size=50M

echo "=== DISABLING DESKTOP ANIMATIONS ==="

# Mint 22 XFCE: only xfconf-query is relevant here.
# The gnome/cinnamon commands have 2>/dev/null so they won't cause errors.
gsettings set org.gnome.desktop.interface \
enable-animations false 2>/dev/null

gsettings set org.cinnamon \
desktop-effects false 2>/dev/null

gsettings set org.cinnamon.muffin \
desktop-effects false 2>/dev/null

xfconf-query -c xfwm4 \
-p /general/use_compositing \
-s false 2>/dev/null

echo "=== CONFIGURING NOATIME ==="

sudo cp /etc/fstab /etc/fstab.backup

if ! grep -q noatime /etc/fstab; then

sudo sed -i \
's/errors=remount-ro/errors=remount-ro,noatime,nodiratime/' \
/etc/fstab

sudo sed -i \
's/defaults,nofail/defaults,noatime,nodiratime,nofail/' \
/etc/fstab

fi

sudo mount -o remount /

sudo mount -o remount /mnt/hd2 \
2>/dev/null

echo "=== CREATING SERVER DIRECTORY ==="

mkdir -p "$USER_HOME/Server"

chown "$CURRENT_USER":"$CURRENT_USER" "$USER_HOME/Server"

chmod 755 "$USER_HOME/Server"

echo "=== CONFIGURING SAMBA ==="

cp /etc/samba/smb.conf /etc/samba/smb.conf.bak 2>/dev/null || true

sudo bash -c "cat > /etc/samba/smb.conf << EOF
[global]
workgroup = WORKGROUP
server string = K7 Server
security = user
map to guest = bad user
min protocol = SMB2

[server]
path = $USER_HOME/Server
browseable = yes
read only = no
valid users = $CURRENT_USER
EOF"

echo "=== SETTING SAMBA PASSWORD ==="

read -s -p "Enter the Linux/Samba user password: " SMB_PASS
echo

sudo smbpasswd -x "$CURRENT_USER" 2>/dev/null || true
printf "%s\n%s\n" "$SMB_PASS" "$SMB_PASS" | sudo smbpasswd -a "$CURRENT_USER"
sudo smbpasswd -e "$CURRENT_USER"

FB_PASS="$SMB_PASS"

sudo systemctl restart smbd
sudo systemctl enable smbd

echo "=== CONFIGURING FIREWALL ==="

sudo ufw allow samba 2>/dev/null

echo "=== INSTALLING TAILSCALE ==="

curl -fsSL \
https://tailscale.com/install.sh | sh

sudo tailscale up --accept-dns=false 2>/dev/null || true

echo ""
echo "==========================================="
echo "Authenticate Tailscale in the browser."
echo "When done, press ENTER to continue..."
echo "==========================================="
read

echo "=== REMOVING FIREFOX ==="

sudo apt purge -y firefox firefox-locale-*
sudo apt autoremove -y
sudo apt autoclean

echo "=== INSTALLING FILEBROWSER ==="

curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash

sleep 2
command -v filebrowser >/dev/null 2>&1 || {
    echo "FileBrowser install failed"
    exit 1
}

touch "$USER_HOME/filebrowser.db"
chown "$CURRENT_USER":"$CURRENT_USER" "$USER_HOME/filebrowser.db"
chmod 600 "$USER_HOME/filebrowser.db"

echo "=== CONFIGURING FILEBROWSER USER ==="

filebrowser users add "$CURRENT_USER" "$FB_PASS" "$USER_HOME/Server" \
-d "$USER_HOME/filebrowser.db" \
--perm.admin 2>/dev/null || filebrowser users update "$CURRENT_USER" "$FB_PASS" -d "$USER_HOME/filebrowser.db"

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
-r $USER_HOME/Server \\
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
sudo systemctl restart filebrowser

echo "=== CONFIGURING SENSORS ==="
sudo sensors-detect --auto || true

echo "=== CONFIGURING HDD SPINDOWN ==="

sudo bash -c 'cat > /etc/hdparm.conf << EOF
/dev/sda {
spindown_time = 180
}

/dev/sdb {
spindown_time = 180
}
EOF'

echo "=== INSTALLING ANYDESK ==="

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

echo "=== CONFIGURING CONKY ==="

# Conky 1.19+ (Mint 22) removed use_xft; font is configured
# only via 'font'. The rest of the config remains compatible.
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

echo "=== ENABLING CONKY AUTO START ==="

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

echo ""
echo "===== VALIDATION ====="

cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

swapon --show

mount | grep noatime

journalctl --disk-usage

cat /sys/block/sda/queue/scheduler
cat /sys/block/sdb/queue/scheduler

echo ""
echo "SETUP COMPLETED"
echo ""
echo "Samba: smb://SERVER_IP/server"
echo "FileBrowser: http://SERVER_IP:8080"
echo ""
echo "Recommended reboot"
