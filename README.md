<h1 align="center">🖥️ Lightweight Home Server</h1>

<p align="center">
Lightweight Home Server is a fully automated setup script designed to transform old or low-spec machines especially 32-bit systems into efficient, always-on home servers.
It focuses on minimal resource usage while providing essential services such as file sharing, secure remote access, web-based file management, remote desktop access, and real-time system monitoring through a desktop HUD.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Stable-success">
  <img src="https://img.shields.io/badge/Platform-Linux%20Mint-blue">
  <img src="https://img.shields.io/badge/Architecture-i686-orange">
</p>

---

## ✨ Features

<table style="border: none; border-collapse: collapse;">
<tr>
<td width="50%" valign="top" style="border: none; padding: 15px;">

### 📁 FILE SERVER (SAMBA)

<ul>
<li>Automatic creation of shared directory:
  <ul>
    <li><code>/home/phobos/Server</code></li>
  </ul>
</li>

<li>Pre-configured Samba service:
  <ul>
    <li>Local network access</li>
    <li>User authentication</li>
    <li>Auto-start on boot</li>
  </ul>
</li>

<li>Access from:
  <ul>
    <li>Windows</li>
    <li>Linux</li>
    <li>Mobile devices</li>
  </ul>
</li>
</ul>

</td>

<td width="50%" valign="top" style="border: none; padding: 15px;">

### 🌐 REMOTE ACCESS (VPN)

<ul>
<li>Secure VPN setup using :contentReference[oaicite:0]{index=0}</li>
<br>
<li>No port forwarding required</li>
<br>
<li>Access your server from anywhere via private network</li>
</ul>

<br>

### 🖥️ REMOTE DESKTOP

<ul>
<li>Automatic installation of :contentReference[oaicite:1]{index=1}</li>
<br>
<li>Fallback to VNC (x11vnc) if unsupported on 32-bit systems</li>
<br>
<li>Full remote control of desktop environment</li>
</ul><br>

</td>
</tr>

<tr>
<td width="50%" valign="top" style="border: none; padding: 15px;">

### 💻 WEB FILE MANAGER

<ul>
<li>File Browser installation and configuration</li>
<br>
<li>Runs as a system service (systemd)</li>
<br>
<li>Access via browser:
  <ul>
    <li><code>http://SERVER_IP:8080</code></li>
  </ul>
</li>
<br>
<li>Features:
  <ul>
    <li>Upload / Download</li>
    <li>File management</li>
    <li>Remote access via browser</li>
  </ul>
</li>
</ul>

</td>

<td width="50%" valign="top" style="border: none; padding: 15px;">

### ⚡ SYSTEM OPTIMIZATION

<ul>
<li>Removes unnecessary applications:
  <ul>
    <li>LibreOffice</li>
    <li>Media tools</li>
    <li>Desktop utilities</li>
  </ul>
</li>

<li>Disables background services:
  <ul>
    <li>Bluetooth</li>
    <li>Printing (CUPS)</li>
    <li>Avahi</li>
  </ul>
</li>

<li>Disables desktop animations</li>
<br>
<li>Optimized for low CPU and RAM usage</li>
</ul><br>

</td>
</tr>

<tr>
<td width="50%" valign="top" style="border: none; padding: 15px;">

### 💽 HARD DRIVE OPTIMIZATION

<ul>
<li>Automatic HDD spindown configuration</li>
<br>
<li>Triggers after 15 minutes of inactivity</li>
<br>
<li>Persistent across reboots</li>
<br>
<li>Ideal for mechanical drives</li>
</ul>

</td>

<td width="50%" valign="top" style="border: none; padding: 15px;">

### 🌡️ HARDWARE MONITORING

<ul>
<li>Automatic sensors detection</li>
<br>
<li>Temperature and hardware stats enabled</li>
</ul>

<br>

### 📊 DESKTOP HUD

<ul>
<li>Real-time overlay using :contentReference[oaicite:2]{index=2}</li>
<br>
<li>Displays:
  <ul>
    <li>CPU usage</li>
    <li>Memory usage</li>
    <li>Disk usage</li>
    <li>Network speed (Download / Upload)</li>
    <li>Local IP address</li>
    <li>Tailscale IP</li>
  </ul>
</li>

<br>

<li>Auto-start on login</li>
<li>Lightweight and customizable</li>
</ul><br>

</td>
</tr>
</table>

---

## 🎯 Target Use Case

<ul>
<li>Old desktops or laptops (Core 2 Duo, 32-bit systems)</li>
<li>Home NAS (Network Attached Storage)</li>
<li>Always-on file server</li>
<li>Personal cloud with remote access</li>
<li>Remote desktop access environment</li>
<li>Lightweight monitoring dashboard</li>
</ul>

---

## 📌 Access Points

<ul>
<li><b>Samba (Local Network):</b><br>
<code>smb://SERVER_IP/server</code></li>
<br>
<li><b>Web Interface:</b><br>
<code>http://SERVER_IP:8080</code></li>
<br>
<li><b>Remote Access:</b><br>
Via Tailscale network</li>
<br>
<li><b>Remote Desktop:</b><br>
AnyDesk or VNC (fallback)</li>
</ul>

---

## ⚠️ Notes

<ul>
<li>AnyDesk may not be fully supported on 32-bit systems</li>
<li>Fallback to VNC is automatic if installation fails</li>
<li>Samba user password is required during setup</li>
<li>Network interface may need adjustment depending on hardware</li>
<li>Designed for Linux Mint / Ubuntu-based systems</li>
<li>Optimized specifically for legacy hardware (i686)</li>
</ul>

---

<p align="center">
Made with ❤️ for lightweight server enthusiasts
</p>
