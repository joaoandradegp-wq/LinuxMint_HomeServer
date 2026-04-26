#!/bin/bash

echo "=== ATUALIZANDO SISTEMA ==="
sudo apt update && sudo apt upgrade -y

echo "=== REMOVENDO BLOAT ==="
sudo apt remove -y libreoffice* thunderbird hexchat transmission-gtk pidgin \
    drawing rhythmbox simple-scan cheese
sudo apt autoremove -y

echo "=== DESATIVANDO SERVIÇOS DESNECESSÁRIOS ==="
sudo systemctl disable bluetooth 2>/dev/null
sudo systemctl disable cups 2>/dev/null
sudo systemctl disable avahi-daemon 2>/dev/null

echo "=== INSTALANDO PACOTES ESSENCIAIS ==="
sudo apt install -y samba cifs-utils curl wget net-tools \
    lm-sensors hdparm dconf-cli conky-all

echo "=== DESATIVANDO ANIMAÇÕES ==="
gsettings set org.gnome.desktop.interface enable-animations false 2>/dev/null
gsettings set org.cinnamon desktop-effects false 2>/dev/null
gsettings set org.cinnamon.muffin desktop-effects false 2>/dev/null
xfconf-query -c xfwm4 -p /general/use_compositing -s false 2>/dev/null

echo "=== CRIANDO PASTA DO SERVIDOR ==="
mkdir -p /home/phobos/Server
chown phobos:phobos /home/phobos/Server
chmod 755 /home/phobos/Server

echo "=== CONFIGURANDO SAMBA ==="
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

echo "=== CRIANDO USUÁRIO SAMBA ==="
sudo smbpasswd -a phobos

echo "=== REINICIANDO SAMBA ==="
sudo systemctl restart smbd
sudo systemctl enable smbd

echo "=== FIREWALL ==="
sudo ufw allow samba 2>/dev/null

echo "=== INSTALANDO TAILSCALE ==="
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

echo "=== INSTALANDO FILE BROWSER ==="
curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash

echo "=== CONFIGURANDO FILEBROWSER ==="
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

echo "=== CONFIGURANDO SENSORES ==="
sudo sensors-detect --auto

echo "=== CONFIGURANDO SPINDOWN HD ==="
sudo bash -c 'cat > /etc/hdparm.conf << EOF
/dev/sda {
    spindown_time = 180
}
EOF'

sudo hdparm -S 180 /dev/sda 2>/dev/null

echo "=== CONFIGURANDO CONKY (HUD) ==="
cat > /home/phobos/.conkyrc << 'EOF'
conky.config = {
    alignment = 'top_right',
    gap_x = 20,
    gap_y = 40,

    minimum_width = 300,
    maximum_width = 300,

    background = false,
    update_interval = 1,
    double_buffer = true,

    own_window = true,
    own_window_type = 'override',
    own_window_transparent = true,

    own_window_hints = 'undecorated,below,sticky,skip_taskbar,skip_pager',

    draw_shades = false,
    draw_outline = false,
    draw_borders = false,

    use_xft = true,
    font = 'DejaVu Sans:size=11',
};

conky.text = [[
${color grey}CPU:${color} ${cpu}% ${cpubar 8}

${color grey}RAM:${color}
$mem / $memmax
${membar 8}

${color grey}DISK:${color}
${fs_used /} / ${fs_size /}
${fs_bar 8 /}

${color grey}NETWORK:${color}
↓ ${downspeed enp2s0}   ↑ ${upspeed enp2s0}
${downspeedgraph enp2s0 30,300}
${upspeedgraph enp2s0 30,300}

${color grey}IP LOCAL:${color} ${addr enp2s0}
${color grey}TAILSCALE:${color} ${addr tailscale0}
]];
EOF

chown phobos:phobos /home/phobos/.conkyrc

echo "=== AUTO START CONKY ==="
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

echo "=== FINALIZADO 🚀 ==="
echo ""
echo "Acesse:"
echo "Samba: smb://IP_DO_SERVIDOR/server"
echo "Web: http://IP_DO_SERVIDOR:8080"
echo ""
echo "Reinicie o sistema para aplicar tudo."

echo ""