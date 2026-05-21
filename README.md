<h1 align="center">🖥️ Lightweight Home Server</h1>

<p align="center">
Lightweight Home Server is an automated setup script that transforms old or low-spec machines (especially legacy 32-bit systems) into efficient always-on home servers.
It focuses on minimal resource usage while providing file sharing, secure remote access, web-based file management, remote desktop support, and real-time system monitoring.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Stable-success">
  <img src="https://img.shields.io/badge/Platform-Linux%20Mint-blue">
  <img src="https://img.shields.io/badge/Architecture-i686-orange">
</p>

---

## ✨ Features

<table>
<tr>

<td width="50%" valign="top">

### 📁 File Server (Samba)

- Automatic shared directory creation:

```bash
/home/phobos/Server
```

- Pre-configured Samba service
  - Local network access
  - User authentication
  - Auto-start on boot

- Compatible with:
  - Windows
  - Linux
  - Mobile devices

<br>
</td>

<td width="50%" valign="top">

### 🌐 Remote Access (VPN)

- Secure VPN access using Tailscale
- No port forwarding required
- Access your server remotely through a private network

### 🖥️ Remote Desktop

- Automatic AnyDesk installation
- Automatic fallback to VNC (x11vnc) on unsupported systems
- Full remote desktop control

</td>

</tr>

<tr>

<td width="50%" valign="top">

### 💻 Web File Manager

- Automatic File Browser installation
- Runs as a systemd service

Access through:

```text
http://SERVER_IP:8080
```

Features:

- Upload / Download
- File management
- Browser-based remote access

</td>

<td width="50%" valign="top">

### ⚡ System Optimization

Removes unnecessary components:

- LibreOffice
- Media applications
- Desktop utilities

Disables unused services:

- Bluetooth
- CUPS (printing)
- Avahi

Additional optimizations:

- Desktop animations disabled
- Reduced CPU and RAM usage

<br>
</td>

</tr>

<tr>

<td width="50%" valign="top">

### 💽 Hard Drive Optimization

- Automatic HDD spindown configuration
- Activates after 15 minutes of inactivity
- Persistent after reboot
- Ideal for mechanical drives

</td>

<td width="50%" valign="top">

### 📊 Monitoring & HUD

Hardware monitoring:

- Automatic sensor detection
- Temperature monitoring enabled

Desktop HUD (Conky):

- CPU usage
- Memory usage
- Disk usage
- Network throughput
- Local IP address
- Tailscale IP
- Server uptime

Features:

- Auto-start on login
- Lightweight
- Customizable

<br>
</td>

</tr>

</table>

---

## 🎯 Target Use Cases

- Legacy desktops and laptops (Core 2 Duo / i686)
- Home NAS
- Always-on file server
- Personal cloud storage
- Remote desktop environment
- Lightweight monitoring station

---

## 📌 Access Points

**Samba (LAN)**

```text
smb://SERVER_IP/server
```

**Web Interface**

```text
http://SERVER_IP:8080
```

**Remote Access**

```text
Tailscale Network
```

**Remote Desktop**

```text
AnyDesk / VNC
```

---

## ⚠️ Notes

- AnyDesk may not support some 32-bit environments
- VNC fallback is automatic
- Samba password configuration is required during setup
- Network interface names may vary by hardware
- Designed for Linux Mint and Ubuntu-based distributions
- Optimized for legacy hardware (i686)

---

<p align="center">
Made with ❤️ for lightweight server enthusiasts.
</p>
