#!/bin/bash

# Detecta o usuário real
if [ -n "$SUDO_USER" ]; then
    CURRENT_USER="$SUDO_USER"
else
    CURRENT_USER="$(whoami)"
fi

USER_HOME="$(eval echo ~"$CURRENT_USER")"

echo "User : $CURRENT_USER"
echo "Home : $USER_HOME"

# =====================================================
echo "=== SHOWING DESKTOP ICONS ==="
# =====================================================

xfconf-query -c xfce4-desktop \
-p /desktop-icons/file-icons/show-home \
-s true 2>/dev/null

xfconf-query -c xfce4-desktop \
-p /desktop-icons/file-icons/show-trash \
-s true 2>/dev/null

# =====================================================
echo "=== REMOVING FIREFOX FROM PANEL ==="
# =====================================================

for launcher in $(xfconf-query -c xfce4-panel -p /plugins -lv 2>/dev/null | awk '{print $1}'); do

    if xfconf-query -c xfce4-panel -p "$launcher/items" >/dev/null 2>&1; then

        items=$(xfconf-query -c xfce4-panel -p "$launcher/items")

        for item in $items; do

            desktop_file=$(xfconf-query \
                -c xfce4-panel \
                -p "/plugins/plugin-$item/item-files" \
                2>/dev/null)

            if echo "$desktop_file" | grep -qi firefox; then

                echo "Removing Firefox launcher..."

                xfconf-query \
                    -c xfce4-panel \
                    -p "/plugins/plugin-$item" \
                    -r -R 2>/dev/null

            fi
        done
    fi
done

xfce4-panel -r >/dev/null 2>&1 &

# =====================================================
echo "=== DOWNLOADING SERVER PANEL ==="
# =====================================================

wget -q \
-O "$USER_HOME/Python_AdminPanel.py" \
https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Python_AdminPanel.py

chmod +x "$USER_HOME/Python_AdminPanel.py"
chown "$CURRENT_USER:$CURRENT_USER" "$USER_HOME/Python_AdminPanel.py"

# =====================================================
echo "=== CREATING SERVER SHORTCUT ==="
# =====================================================

mkdir -p "$USER_HOME/Desktop"

cat > "$USER_HOME/Desktop/Server.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Server
Exec=xdg-open "$USER_HOME/Server"
Icon=folder
Terminal=false
EOF

# =====================================================
echo "=== CREATING CONKY SHORTCUT ==="
# =====================================================

cat > "$USER_HOME/Desktop/Conky.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Conky Configuration
Exec=xdg-open "$USER_HOME/.conkyrc"
Icon=utilities-system-monitor
Terminal=false
EOF

# =====================================================
echo "=== CREATING SERVER PANEL SHORTCUT ==="
# =====================================================

cat > "$USER_HOME/Desktop/ServerPanel.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Server Panel
Exec=python3 "$USER_HOME/Python_AdminPanel.py"
Icon=preferences-system
Terminal=false
EOF

chmod +x "$USER_HOME/Desktop/"*.desktop
chown "$CURRENT_USER:$CURRENT_USER" "$USER_HOME/Desktop/"*.desktop

echo ""
echo "=========================================="
echo "Desktop configuration completed."
echo "=========================================="