<h1 align="center">🖥️ Lightweight Home Server</h1>

<p align="center">
Lightweight Home Server is an automated setup script that transforms old or low-spec machines into efficient always-on home servers.
It focuses on minimal resource usage while providing file sharing, secure remote access, web-based file management, remote desktop support, real-time system monitoring, a built-in monitoring API, and an intuitive graphical Server Panel.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Stable-success">
  <img src="https://img.shields.io/badge/Platform-Linux%20Mint%2022.3%20XFCE-blue">
  <img src="https://img.shields.io/badge/Optimized-Home%20Server-orange">
  <img src="https://img.shields.io/badge/Language-EN-purple">
  <img src="https://img.shields.io/badge/Python-Tkinter%20GUI-green">
</p>

---

## ⬇️ Releases

### 🟢 Linux Mint 22.3 (64-bit)

```bash
curl -fsSL https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Script_HomeServer-x64-2.2.sh | sudo bash
```

### 🟡 Linux Mint 19 (32-bit)

```bash
curl -fsSL https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Script_HomeServer-x86-1.0.sh | sudo bash
```

> **Recommended:** Use the **64-bit** installer if you're running Linux Mint 22.3 or newer.  
> The **32-bit** version is provided for legacy hardware running Linux Mint 19.

<br>

Choose the installer that matches your Linux Mint version and system architecture.

| Version | Architecture | Release | Download |
|----------|-------------|---------|----------|
| Linux Mint 22.3 XFCE | **64-bit (x64)** | **v2.2** | <a href="https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Script_HomeServer-x64-2.2.sh"><b>Click here</b></a> |
| Linux Mint 19.x XFCE | **32-bit (x86)** | **v1.0** | <a href="https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Script_HomeServer-x86-1.0.sh"><b>Click here</b></a> |

Server Panel + Server Monitor API Add-on
| Version | Architecture | Release | Download |
|----------|-------------|---------|----------|
| Python 3 | **64-bit (x64)** | **v1.1** | <a href="https://raw.githubusercontent.com/joaoandradegp-wq/LinuxMint_HomeServer/refs/heads/main/Server-Panel-1.1.py"><b>Click here</b></a> |

---

## ✨ Script Details

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

<li>Fully manageable through the Server Panel</li>

</ul>

<br>

</td>

<td width="50%" valign="top">

<h3>🌐 Remote Access (VPN)</h3>

<ul>

<li>Secure VPN access using Tailscale</li>

<li>No port forwarding required</li>

<li>Private network access from anywhere</li>

<li>Displays assigned Tailscale IP after installation</li>

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

<li>Start/Stop directly from the Server Panel</li>

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

<li>Removal of unnecessary packages</li>

<li>Disabled unnecessary background services</li>

<li>Tracker indexing disabled</li>

<li>Desktop animations disabled</li>

<li>Kernel memory tuning</li>

<li>Reduced disk writes</li>

<li>ZRAM enabled</li>

</ul>

<br>

</td>

<td width="50%" valign="top">

<h3>⚙️ Kernel & Storage Tuning</h3>

<ul>

<li>CPU governor set to <code>schedutil</code></li>

<li>HDD I/O scheduler set to <code>mq-deadline</code></li>

<li>HDD power management (APM)</li>

<li>Automatic HDD spindown</li>

<li>Filesystem optimizations:</li>

<ul>

<li>noatime</li>

<li>nodiratime</li>

</ul>

<li>Persistent configuration via systemd and udev</li>

</ul>

</td>

</tr>

<tr>

<td width="50%" valign="top">

<h3>📊 Monitoring (Conky HUD)</h3>

<ul>

<li>CPU usage & temperature</li>

<li>RAM & swap usage</li>

<li>Disk usage</li>

<li>LAN IP</li>

<li>Ethernet Link Speed</li>

<li>FileBrowser status</li>

<li>Tailscale IP</li>

<li>System uptime</li>

</ul>

<p>Auto-starts as a lightweight desktop overlay.</p>

<br>

</td>

<td width="50%" valign="top">

<h3>📡 Server Monitor API <sup>NEW</sup></h3>

<ul>

<li>Integrated FastAPI monitoring service</li>

<li>Designed for Rainmeter dashboards</li>

<li>Plain-text API endpoint</li>

<li>CPU, RAM, Swap & Disk metrics</li>

<li>Network traffic statistics</li>

<li>Service status reporting</li>

<li>Host information</li>

</ul>

<pre><code>http://SERVER_NAME:8181/api/rainmeter</code></pre>

</td>

</tr>

<tr>

<td width="50%" valign="top">

<h3>🖥️ Server Panel <sup>NEW</sup></h3>

<ul>

<li>Modern Tkinter management application</li>

<li>Tabbed interface</li>

<ul>

<li>📁 Samba Shares</li>

<li>📊 Conky Manager</li>

<li>🌐 FileBrowser</li>

<li>📡 Server Monitor</li>

</ul>

<li>Create/Edit/Delete Samba shares</li>

<li>Configure Conky disks</li>

<li>Manage FileBrowser service</li>

<li>Install and manage Server Monitor</li>

<li>Live monitoring data viewer</li>

</ul>

<br>

</td>

<td width="50%" valign="top">

<h3>🧠 Smart Installer</h3>

<ul>

<li>Idempotent installation</li>

<li>Automatic user detection</li>

<li>Automatic desktop shortcuts</li>

<li>Automatic password validation</li>

<li>Improved installation validation</li>

<li>Detailed completion summary</li>

<li>Optimized for Linux Mint 22.3 XFCE</li>

</ul>

</td>

</tr>

</table>

---

## 🎯 Target Use Cases

<ul>

<li>Old laptops and desktops</li>

<li>Home NAS / File Server</li>

<li>Personal cloud storage</li>

<li>Remote access node</li>

<li>Rainmeter monitoring server</li>

<li>Low-power always-on machine</li>

</ul>

---

## 📌 Access Points

<p><b>Samba (LAN)</b></p>

<pre><code>smb://SERVER_IP/server</code></pre>

<p><b>FileBrowser</b></p>

<pre><code>http://SERVER_IP:8080</code></pre>

<p><b>Server Monitor API</b></p>

<pre><code>http://SERVER_NAME:8181/api/rainmeter</code></pre>

<p><b>Tailscale</b></p>

<pre><code>Private VPN Network</code></pre>

<p><b>Remote Desktop</b></p>

<pre><code>AnyDesk / x11vnc</code></pre>

<p><b>Server Panel</b></p>

<pre><code>python3 ~/Python_ServerPanel.py</code></pre>

---

## ⚠️ Notes

<ul>

<li>Designed for Linux Mint 22.3 XFCE (64-bit)</li>

<li>Legacy 32-bit installer remains available for Linux Mint 19</li>

<li>Requires sudo privileges</li>

<li>Internet connection required during installation</li>

<li>Network interface names may vary between systems</li>

</ul>

---

## 📸 Linux Mint Preview

<p align="center">
<img width="500" src="https://github.com/user-attachments/assets/d9a12f77-6fb3-4b87-a80d-207cc040fa36">
</p>

---

## 📸 Personal Server Project (VHS Case)

<p align="center">
<img width="250" src="https://github.com/user-attachments/assets/865475c4-c716-4783-b014-eb803b48e3a4" />
<img width="250" src="https://github.com/user-attachments/assets/1299835f-8826-4ca6-badc-f688f726b320" /><br>
<img width="250" src="https://github.com/user-attachments/assets/5bc835c1-9d4f-4bac-9c8d-a5916e34a222" />
<img width="250" src="https://github.com/user-attachments/assets/3b29c7b0-6788-467b-95d0-4bbd265b1cb3" />
</p>

---

<p align="center">
Made for lightweight server enthusiasts. 🐧
</p>
