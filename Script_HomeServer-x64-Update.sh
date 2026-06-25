#!/bin/bash

echo "========================================="
echo " HOME SERVER - EXTRA OPTIMIZATIONS"
echo "========================================="

echo ""
echo "=== CONFIGURING SYSTEMD JOURNAL ==="

sudo mkdir -p /etc/systemd/journald.conf.d

sudo tee /etc/systemd/journald.conf.d/ram.conf > /dev/null <<EOF
[Journal]
Storage=volatile
RuntimeMaxUse=50M
RuntimeKeepFree=30M
MaxRetentionSec=1day
EOF

sudo systemctl restart systemd-journald

echo ""
echo "=== CONFIGURING KERNEL MEMORY PARAMETERS ==="

sudo tee /etc/sysctl.d/99-homeserver.conf > /dev/null <<EOF
vm.swappiness=10
vm.vfs_cache_pressure=50
vm.dirty_background_ratio=2
vm.dirty_ratio=10
EOF

sudo sysctl --system

echo ""
echo "=== CONFIGURING ZRAM ==="

if [ -f /etc/default/zramswap ]; then

    sudo sed -i 's/^ALGO=.*/ALGO=zstd/' /etc/default/zramswap
    sudo sed -i 's/^PERCENT=.*/PERCENT=50/' /etc/default/zramswap
    sudo sed -i 's/^PRIORITY=.*/PRIORITY=100/' /etc/default/zramswap

    sudo systemctl restart zramswap 2>/dev/null

else
    echo "zramswap configuration file not found."
fi

echo ""
echo "=== OPTIMIZING SAMBA ==="

if ! grep -q "deadtime = 15" /etc/samba/smb.conf; then

sudo sed -i '/^\[global\]/a\
socket options = TCP_NODELAY IPTOS_LOWDELAY\
deadtime = 15\
aio read size = 1\
aio write size = 1' /etc/samba/smb.conf

fi

sudo systemctl restart smbd

echo ""
echo "=== CONFIGURING HDD POWER MANAGEMENT ==="

sudo tee /etc/hdparm.conf > /dev/null <<EOF
/dev/sda {
    spindown_time = 180
    apm = 254
}

/dev/sdb {
    spindown_time = 180
    apm = 254
}
EOF

sudo systemctl restart hdparm 2>/dev/null || true

echo ""
echo "=== DISABLING OPTIONAL SERVICES ==="

sudo systemctl disable ModemManager.service 2>/dev/null
sudo systemctl stop ModemManager.service 2>/dev/null

sudo systemctl disable speech-dispatcher.service 2>/dev/null
sudo systemctl stop speech-dispatcher.service 2>/dev/null

echo ""
echo "=== CHECKING TRACKER ==="

if command -v tracker3 >/dev/null 2>&1; then

    systemctl --user mask tracker-miner-fs-3.service 2>/dev/null
    systemctl --user stop tracker-miner-fs-3.service 2>/dev/null

fi

echo ""
echo "=== VALIDATION ==="

echo ""
echo "--- Kernel Parameters ---"
sysctl vm.swappiness
sysctl vm.vfs_cache_pressure
sysctl vm.dirty_background_ratio
sysctl vm.dirty_ratio

echo ""
echo "--- ZRAM ---"
swapon --show

echo ""
echo "--- Journal ---"
journalctl --disk-usage

echo ""
echo "--- Memory ---"
free -h

echo ""
echo "========================================="
echo " EXTRA OPTIMIZATIONS COMPLETED"
echo " Recommended reboot"
echo "========================================="