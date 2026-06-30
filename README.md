<h1 align="center">🖥️ Lightweight Home Server</h1>

<p align="center">
Lightweight Home Server is an automated setup script that transforms old or low-spec machines into efficient always-on home servers.
It focuses on minimal resource usage while providing file sharing, secure remote access, web-based file management, remote desktop support, real-time system monitoring, and a management GUI.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Stable-success">
  <img src="https://img.shields.io/badge/Platform-Linux%20Mint%2022.3%20XFCE-blue">
  <img src="https://img.shields.io/badge/Optimized-Home%20Server-orange">
  <img src="https://img.shields.io/badge/Language-EN%20-purple">
  <img src="https://img.shields.io/badge/Python-Tkinter%20GUI-green">
</p>

---

## ⬇️ Releases

### 🟢 Linux Mint 22.3 (64-bit)
```bash
curl -fsSL https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Script_HomeServer-x64-2.1.sh | sudo bash
```

### 🟡 Linux Mint 19 (32-bit)
```bash
curl -fsSL https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Script_HomeServer-x86-1.0.sh | sudo bash
```

> **Recommended:** Use the **64-bit** installer if you're running Linux Mint 22.3 or newer.  
> The **32-bit** version is provided for legacy hardware running Linux Mint 19.
<br>

Choose the installer that matches your Linux Mint version and system architecture.
| Version | Architecture | Release Date | Download |
|----------|-------------|--------------|----------|
| Linux Mint 22.3 XFCE | **64-bit (x64)** | 2026-06-25 | <a href="https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Script_HomeServer-x64-2.1.sh"><b>Click here</b></a> |
| Linux Mint 19.x XFCE | **32-bit (x86)** | 2026-04-26 | <a href="https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Script_HomeServer-x86-1.0.sh"><b>Click here</b></a> |

| Version | Architecture | Download |
|----------|-------------|----------|
| Server Panel 1.0 | **Python 3** | <a href="https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Python_AdminPanel.py"><b>Click here</b></a> |

> **Recommended:** Use the **Python GUI Manager (Tkinter)** on Linux Mint 22.3 XFCE or newer for full visual management of Samba shares, Conky monitoring configuration, and FileBrowser settings.  
> The tool is included as part of the modern (64-bit) Home Server installer and provides a graphical alternative to manual configuration files.

---

## ✨ Script details
<table>
<tr>

<td width="50%" valign="top">

<h3>📁 File Server (Samba)</h3>

<ul>
<li>Dynamic user detection (SUDO_USER / current user)</li>
<li>Automatic shared directory creation</li>
</ul>

<pre><code>~/Server</code></pre>

<ul>
<li>Pre-configured Samba service</li>
<li>Local network access</li>
<li>User authentication</li>
<li>Auto-start on boot</li>
<li>Compatible with Windows, Linux and mobile devices</li>
</ul>
<br>
</td>

<td width="50%" valign="top">

<h3>🌐 Remote Access (VPN)</h3>

<ul>
<li>Secure VPN access using Tailscale</li>
<li>No port forwarding required</li>
<li>Private network access from anywhere</li>
</ul>

</td>

</tr>

<tr>

<td width="50%" valign="top">

<h3>🖥️ Remote Desktop</h3>

<ul>
<li>Automatic AnyDesk installation</li>
<li>Fallback to x11vnc if unavailable</li>
<li>Full remote desktop control</li>
</ul>

</td>

<td width="50%" valign="top">

<h3>💻 Web File Manager</h3>

<ul>
<li>Automatic FileBrowser installation</li>
<li>Runs as a systemd service</li>
</ul>

<p><b>Access:</b></p>

<pre><code>http://SERVER_IP:8080</code></pre>

<ul>
<li>Upload / Download files</li>
<li>Browser-based file management</li>
<li>Remote access via web interface</li>
</ul>
<br>
</td>

</tr>

<tr>

<td width="50%" valign="top">

<h3>⚡ System Optimization</h3>

<ul>
<li>Removal of unnecessary packages:
  <ul>
    <li>LibreOffice</li>
    <li>Thunderbird</li>
    <li>Hexchat / media tools</li>
    <li>Games & utilities</li>
  </ul>
</li>

<li>Disabled services:
  <ul>
    <li>Bluetooth</li>
    <li>CUPS</li>
    <li>Avahi daemon</li>
  </ul>
</li>

<li>Desktop optimizations:
  <ul>
    <li>Animations disabled (XFCE / Cinnamon safe)</li>
  </ul>
</li>

<li>Memory tuning:
  <ul>
    <li>Swappiness set to 10</li>
    <li>ZRAM enabled (modern kernel support)</li>
  </ul>
</li>
</ul>
<br>
</td>

<td width="50%" valign="top">

<h3>⚙️ Kernel & Storage Tuning</h3>

<ul>
<li>CPU governor set to <code>schedutil</code></li>
<li>HDD I/O scheduler set to <code>mq-deadline</code></li>
<li>Persistent configuration via systemd + udev rules</li>
<li>Filesystem optimizations:
  <ul>
    <li>noatime</li>
    <li>nodiratime</li>
  </ul>
</li>
</ul>

</td>

</tr>

<tr>

<td width="50%" valign="top">

<h3>💽 Storage & RAM Optimization</h3>

<ul>
<li>HDD spindown enabled (180 seconds idle)</li>
<li>Journald limited to RAM usage</li>
<li>Automatic log vacuum cleanup</li>
<li>ZRAM compression enabled</li>
</ul>

</td>

<td width="50%" valign="top">

<h3>📊 Monitoring (Conky HUD)</h3>

<ul>
<li>CPU usage and frequency</li>
<li>RAM and swap usage</li>
<li>Disk usage (system + data)</li>
<li>Network IP address</li>
<li>FileBrowser status</li>
<li>Tailscale IP</li>
<li>System uptime</li>
</ul>

<p>Auto-starts as lightweight desktop overlay.</p>
<br>
</td>

</tr>

<tr>

<td width="50%" valign="top">

<h3>🐍 Python GUI Manager</h3>

<ul>
<li>Tkinter-based control panel</li>
<li>Tabbed interface:
  <ul>
    <li>📁 Samba shares manager</li>
    <li>📊 Conky disk editor</li>
    <li>🌐 FileBrowser configuration</li>
  </ul>
</li>

<li>Live Samba config editor:
  <ul>
    <li>Add / edit / remove shares</li>
    <li>Change force-user dynamically</li>
    <li>Auto-restart Samba service</li>
  </ul>
</li>

<li>Conky live editor:
  <ul>
    <li>Add/remove mounted disks</li>
    <li>Auto-restart Conky</li>
  </ul>
</li>

<li>FileBrowser viewer:
  <ul>
    <li>Reads root path from systemd service</li>
  </ul>
</li>
<br>
</ul>

</td>

<td width="50%" valign="top">

<h3>🧠 Smart Installer Improvements</h3>

<ul>
<li>Auto-detects real user (SUDO_USER support)</li>
<li>No hardcoded usernames anymore</li>
<li>Works on fresh Mint 22.3 XFCE installs</li>
<li>Python + Tkinter installed automatically</li>
<li>Safer Samba + FileBrowser setup</li>
</ul>

</td>

</tr>

</table>

---

<h2>🎯 Target Use Cases</h2>

<ul>
<li>Old laptops and desktops</li>
<li>Home NAS / file server</li>
<li>Lightweight cloud storage</li>
<li>Remote access node</li>
<li>Monitoring server</li>
<li>Low-power always-on machine</li>
</ul>

---

<h2>📌 Access Points</h2>

<p><b>Samba (LAN)</b></p>
<pre><code>smb://SERVER_IP/server</code></pre>

<p><b>FileBrowser (Web UI)</b></p>
<pre><code>http://SERVER_IP:8080</code></pre>

<p><b>Tailscale</b></p>
<pre><code>Private network access</code></pre>

<p><b>Remote Desktop</b></p>
<pre><code>AnyDesk / x11vnc</code></pre>

<p><b>GUI Manager</b></p>
<pre><code>python3 Python_ServerPanel.py</code></pre>

---

<h2>⚠️ Notes</h2>

<ul>
<li>Designed for Linux Mint 22.3 XFCE (64-bit)</li>
<li>Legacy 32-bit support removed in this version</li>
<li>Some services may vary depending on hardware</li>
<li>Network interface names may vary (enp*, eth*, wlan*)</li>
<li>Requires sudo privileges for setup</li>
</ul>

---

## 📸 Linux Mint Preview

<p align="center">
  <img width="500" alt="image" src="https://github.com/user-attachments/assets/b60e2523-349c-4d17-8a40-26412744eaa2" />
</p>

---

## 📸 Personal Server Project (VHS Case)

<p align="center">
  <img width="250" alt="image" src="https://github.com/user-attachments/assets/865475c4-c716-4783-b014-eb803b48e3a4" />
  <img width="250" alt="image" src="https://github.com/user-attachments/assets/1299835f-8826-4ca6-badc-f688f726b320" /><br>
  <img width="250" alt="image" src="https://github.com/user-attachments/assets/5bc835c1-9d4f-4bac-9c8d-a5916e34a222" />
  <img width="250" alt="image" src="https://github.com/user-attachments/assets/3b29c7b0-6788-467b-95d0-4bbd265b1cb3" />

</p>

---

<p align="center">
Made for lightweight server enthusiasts. 🐧
</p>
