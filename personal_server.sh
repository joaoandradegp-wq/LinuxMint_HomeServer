#!/bin/bash

echo "=== UPDATING SYSTEM ==="
sudo apt update && sudo apt upgrade -y

echo "=== REMOVING UNNECESSARY PACKAGES ==="

sudo apt remove -y \
libreoffice* thunderbird hexchat \
transmission-gtk pidgin drawing \
rhythmbox simple-scan cheese

sudo apt autoremove -y

echo "=== DISABLING UNUSED SERVICES ==="

sudo systemctl disable bluetooth 2>/dev/null
sudo systemctl disable cups 2>/dev/null
sudo systemctl disable avahi-daemon 2>/dev/null

echo "=== INSTALLING REQUIRED PACKAGES ==="

sudo apt install -y \
samba cifs-utils curl wget net-tools \
lm-sensors hdparm dconf-cli conky-all \
zram-config

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

echo "=== CONFIGURING HDD SCHEDULER ==="

sudo bash -c 'cat > /etc/udev/rules.d/60-ioschedulers.rules << EOF
ACTION=="add|change", KERNEL=="sda", ATTR{queue/scheduler}="deadline"
ACTION=="add|change", KERNEL=="sdb", ATTR{queue/scheduler}="deadline"
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

mkdir -p /home/phobos/Server

chown phobos:phobos /home/phobos/Server

chmod 755 /home/phobos/Server

echo "=== CONFIGURING SAMBA ==="

sudo bash -c 'cat > /etc/samba/smb.conf << EOF
[global]
workgroup = WORKGROUP
server string = K7 Server
security = user
map to guest = bad user
min protocol = SMB2

[server]
path = /home/phobos/Server
browseable = yes
read only = no
valid users = phobos
EOF'

echo "=== SETTING SAMBA PASSWORD ==="

sudo smbpasswd -a phobos

sudo systemctl restart smbd
sudo systemctl enable smbd

echo "=== CONFIGURING FIREWALL ==="

sudo ufw allow samba 2>/dev/null

echo "=== INSTALLING TAILSCALE ==="

curl -fsSL \
https://tailscale.com/install.sh | sh

sudo tailscale up

echo "=== INSTALLING FILEBROWSER ==="

curl -fsSL \
https://raw.githubusercontent.com/filebrowser/get/master/get.sh \
| bash

sudo bash -c 'cat > /etc/systemd/system/filebrowser.service << EOF
[Unit]
Description=File Browser
After=network.target

[Service]
ExecStart=/usr/local/bin/filebrowser \
-r /home/phobos/Server \
-a 0.0.0.0

Restart=always
User=phobos

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload

sudo systemctl enable filebrowser
sudo systemctl start filebrowser

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

if [ "$(uname -m)" = "i686" ]; then

wget -qO - \
https://keys.anydesk.com/repos/DEB-GPG-KEY \
| sudo apt-key add -

echo \
"deb http://deb.anydesk.com/ all main" \
| sudo tee \
/etc/apt/sources.list.d/anydesk.list

sudo apt update

if ! sudo apt install -y anydesk; then
sudo apt install -y x11vnc
fi

else

sudo apt install -y anydesk

fi

echo "=== CONFIGURING CONKY ==="

cat > /home/phobos/.conkyrc << 'EOF'
conky.config = {
    alignment = 'top_right',
    gap_x = 20,
    gap_y = 5,

    minimum_width = 300,
    maximum_width = 300,

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
${color grey}Frequência:${color} ${freq_g}GHz
${color grey}Temperatura:${color} ${execi 5 sensors | grep 'Core 0' | awk '{print $3}'}
${color grey}Uso:${color} ${cpu}%
${cpubar 8}

${color grey}RAM:${color}
$mem / $memmax
${membar 8}

${color grey}SWAP:${color}
$swap / $swapmax
${swapbar 8}

${color grey}DISK 01 (SYSTEM):${color} ${fs_used_perc /}%
${fs_bar 8 /}
${fs_used /} / ${fs_size /}

${color grey}DISK 02 (DATA):${color} ${fs_used_perc /mnt/hd2}%
${fs_bar 8 /mnt/hd2}
${fs_used /mnt/hd2} / ${fs_size /mnt/hd2}

${color grey}NETWORK (LAN):${color}
IP: ${execi 10 hostname -I | awk '{print $1}' | sed 's/^$/Offline/'}
Down: ${downspeed enp2s0}
Up: ${upspeed enp2s0}

${color grey}CPU GOVERNOR:${color}
${execi 30 cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor}

${color grey}DISK SCHEDULER:${color}
${execi 30 cat /sys/block/sda/queue/scheduler | sed 's/.*\\[\\(.*\\)\\].*/\\1/'}

${color grey}ZRAM:${color}
${execi 30 swapon --show | grep zram | wc -l} devices

${color grey}FILE BROWSER:${color} \
${if_match ${execi 10 systemctl is-active filebrowser | grep -c active} == 1}\
${color green}ONLINE${color}\
${else}\
${color red}OFFLINE${color}\
${endif}

${color grey}TAILSCALE:${color}
IP: ${if_up tailscale0}${addr tailscale0}${else}Offline${endif}

${color grey}SYSTEM:${color}
Tempo Ligado: ${uptime_short}
]];
EOF

chown phobos:phobos /home/phobos/.conkyrc

echo "=== ENABLING CONKY AUTO START ==="

mkdir -p /home/phobos/.config/autostart

cat > /home/phobos/.config/autostart/conky.desktop << EOF
[Desktop Entry]
Type=Application
Exec=conky
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Conky Monitor
EOF

chown -R phobos:phobos /home/phobos/.config

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
