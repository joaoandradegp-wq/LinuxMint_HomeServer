#!/bin/bash

# Detecta o usuário real
if [ -n "$SUDO_USER" ]; then
    CURRENT_USER="$SUDO_USER"
else
    CURRENT_USER="$(whoami)"
fi

USER_HOME="$(eval echo ~"$CURRENT_USER")"

# Descobre a área de trabalho real do XFCE (PT/EN safe)
DESKTOP_DIR=$(sudo -u "$CURRENT_USER" xdg-user-dir DESKTOP 2>/dev/null)

# fallback caso xdg-user-dir não exista
if [ -z "$DESKTOP_DIR" ] || [ ! -d "$DESKTOP_DIR" ]; then
    DESKTOP_DIR="$USER_HOME/Desktop"
fi

echo "User       : $CURRENT_USER"
echo "Home       : $USER_HOME"
echo "Desktop Dir: $DESKTOP_DIR"

# =====================================================
echo "=== SHOWING DESKTOP ICONS (HOME + TRASH) ==="
# =====================================================

sudo -u "$CURRENT_USER" xfconf-query -c xfce4-desktop \
-p /desktop-icons/file-icons/show-home \
-s true 2>/dev/null

sudo -u "$CURRENT_USER" xfconf-query -c xfce4-desktop \
-p /desktop-icons/file-icons/show-trash \
-s true 2>/dev/null

sudo -u "$CURRENT_USER" xfdesktop --reload 2>/dev/null || true

# =====================================================
echo "=== DOWNLOADING SERVER PANEL ==="
# =====================================================

wget -q -O "$USER_HOME/Python_AdminPanel.py" \
https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Python_AdminPanel.py

chmod +x "$USER_HOME/Python_AdminPanel.py"
chown "$CURRENT_USER:$CURRENT_USER" "$USER_HOME/Python_AdminPanel.py"

# =====================================================
echo "=== CREATING SERVER SHORTCUT ==="
# =====================================================

cat > "$DESKTOP_DIR/Server.desktop" << EOF
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

cat > "$DESKTOP_DIR/Conky.desktop" << EOF
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

cat > "$DESKTOP_DIR/ServerPanel.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Server Panel
Exec=python3 "$USER_HOME/Python_AdminPanel.py"
Icon=preferences-system
Terminal=false
EOF

# =====================================================
echo "=== FIX PERMISSIONS ==="
# =====================================================

chmod +x "$DESKTOP_DIR"/*.desktop 2>/dev/null
chown "$CURRENT_USER:$CURRENT_USER" "$DESKTOP_DIR"/*.desktop 2>/dev/null

chown "$CURRENT_USER:$CURRENT_USER" "$USER_HOME/Python_AdminPanel.py"

# =====================================================
echo "=========================================="
echo " Desktop configuration completed successfully"
echo "=========================================="