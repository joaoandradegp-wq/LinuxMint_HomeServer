#!/bin/bash

echo "=== UPDATING SYSTEM ==="
sudo apt update && sudo apt upgrade -y

echo "=== REMOVING UNNECESSARY PACKAGES ==="
sudo apt remove -y libreoffice* thunderbird hexchat transmission-gtk pidgin \
    drawing rhythmbox simple-scan cheese
sudo apt autoremove -y

echo "=== DISABLING UNUSED SERVICES ==="
sudo systemctl disable bluetooth 2>/dev/null
sudo systemctl disable cups 2>/dev/null
sudo systemctl disable avahi-daemon 2>/dev/null

echo "=== INSTALLING REQUIRED PACKAGES ==="
sudo apt install -y samba cifs-utils curl wget net-tools \
    lm-sensors hdparm dconf-cli conky-all

echo "=== DISABLING DESKTOP ANIMATIONS ==="
gsettings set org.gnome.desktop.interface enable-animations false 2>/dev/null
gsettings set org.cinnamon desktop-effects false 2>/dev/null
gsettings set org.cinnamon.muffin desktop-effects false 2>/dev/null
xfconf-query -c xfwm4 -p /general/use_compositing -s false 2>/dev/null

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

echo "=== SETTING SAMBA USER PASSWORD ==="
sudo smbpasswd -a phobos

echo "=== RESTARTING SAMBA SERVICE ==="
sudo systemctl restart smbd
sudo systemctl enable smbd

echo "=== CONFIGURING FIREWALL ==="
sudo ufw allow samba 2>/dev/null

echo "=== INSTALLING TAILSCALE ==="
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

echo "=== INSTALLING FILE BROWSER ==="
curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash

echo "=== CONFIGURING FILE BROWSER SERVICE ==="
sudo bash -c 'cat > /etc/systemd/system/filebrowser.service << EOF
[Unit]
Description=File Browser
After=network.target

[Service]
ExecStart=/usr/local/bin/filebrowser -r /home/phobos/Server -a 0.0.0.0
Restart=always
User=phobos

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable filebrowser
sudo systemctl start filebrowser

echo "=== CONFIGURING HARDWARE SENSORS ==="
sudo sensors-detect --auto

echo "=== CONFIGURING HDD SPINDOWN ==="
sudo bash -c 'cat > /etc/hdparm.conf << EOF
/dev/sda {
    spindown_time = 180
}
EOF'

sudo hdparm -S 180 /dev/sda 2>/dev/null

echo "=== INSTALLING ANYDESK WITH FALLBACK ==="
if [ "$(uname -m)" = "i686" ]; then
    echo "32-bit system detected. Attempting to install AnyDesk."

    wget -qO - https://keys.anydesk.com/repos/DEB-GPG-KEY | sudo apt-key add - 2>/dev/null
    echo "deb http://deb.anydesk.com/ all main" | sudo tee /etc/apt/sources.list.d/anydesk.list
    sudo apt update

    if sudo apt install -y anydesk; then
        echo "AnyDesk installed successfully."
    else
        echo "AnyDesk installation failed. Installing VNC as fallback."
        sudo apt install -y x11vnc
    fi
else
    sudo apt install -y anydesk
fi

echo "=== CONFIGURING CONKY SYSTEM MONITOR ==="
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
${color grey}CPU:${color} ${cpu}% @ ${freq_g}GHz ${cpubar 8}
${color grey}Temp:${color} ${execi 5 sensors | grep 'Core 0' | awk '{print $3}'}

${color grey}RAM:${color}
$mem / $memmax
${membar 8}

${color grey}DISK 01 (HDD):${color} ${fs_used_perc /}% 
${fs_bar 8 /}
${fs_used /} / ${fs_size /}

${color grey}DISK 02 (USB):${color} ${fs_used_perc /mnt/hd2}% 
${fs_bar 8 /mnt/hd2}
${fs_used /mnt/hd2} / ${fs_size /mnt/hd2}

${color grey}NETWORK (LAN):${color}
Down: ${downspeed enp2s0}
Up:   ${upspeed enp2s0}
IP:   ${execi 10 hostname -I | awk '{print $1}' | sed 's/^$/Offline/'}

${color grey}FILE BROWSER:${color} \
${if_match ${execi 10 systemctl is-active filebrowser | grep -c active} == 1}\
${color green}ONLINE${color}\
${else}\
${color red}OFFLINE${color}\
${endif}

${color grey}TAILSCALE:${color}
IP:   ${if_up tailscale0}${addr tailscale0}${else}Offline${endif}
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

echo "=== SETUP COMPLETED ==="
echo ""
echo "Samba access: smb://SERVER_IP/server"
echo "Web interface: http://SERVER_IP:8080"
echo ""
echo "Reboot the system to apply all settings."
echo ""