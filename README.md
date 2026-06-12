<h1 align="center">🖥️ Lightweight Home Server</h1>

<p align="center">
Lightweight Home Server is an automated setup script that transforms old or low-spec machines into efficient always-on home servers.
It focuses on minimal resource usage while providing file sharing, secure remote access, web-based file management, remote desktop support, and real-time system monitoring.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Stable-success">
  <img src="https://img.shields.io/badge/Platform-Linux%20Mint-blue">
  <img src="https://img.shields.io/badge/Optimized-Home%20Server-orange">
  <img src="https://img.shields.io/badge/Language-EN%20-purple">
</p>

---

<table>
<tr>

<td width="50%" valign="top">

<h3>📁 File Server (Samba)</h3>

<ul>
<li>Automatic shared directory creation</li>
</ul>

<pre><code>/home/phobos/Server</code></pre>

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
<li>Fallback to VNC (x11vnc) on unsupported systems</li>
<li>Full remote desktop control</li>
</ul>

</td>

<td width="50%" valign="top">

<h3>💻 Web File Manager</h3>

<ul>
<li>Automatic File Browser installation</li>
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
    <li>Media tools</li>
    <li>Games and utilities</li>
  </ul>
</li>

<li>Disabled services:
  <ul>
    <li>Bluetooth</li>
    <li>CUPS (printing)</li>
    <li>Avahi daemon</li>
  </ul>
</li>

<li>Desktop optimizations:
  <ul>
    <li>Animations disabled</li>
    <li>Reduced visual effects</li>
  </ul>
</li>

<li>Memory tuning:
  <ul>
    <li>Swappiness set to 10</li>
  </ul>
</li>
</ul>
<br>
</td>

<td width="50%" valign="top">

<h3>⚙️ Kernel & Storage Tuning</h3>

<ul>
<li>CPU governor set to <code>schedutil</code></li>
<li>HDD I/O scheduler set to <code>deadline</code></li>
<li>Persistent configuration via systemd and udev rules</li>
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
<li>HDD spindown enabled (15 minutes idle)</li>
<li>Journald limited to RAM usage</li>
<li>Automatic log vacuum cleanup</li>
<li>ZRAM enabled for memory compression</li>
</ul>

</td>

<td width="50%" valign="top">

<h3>📊 Monitoring (Conky HUD)</h3>

<ul>
<li>CPU usage and frequency</li>
<li>RAM and swap usage</li>
<li>Disk usage (system and data drive)</li>
<li>Network IP address</li>
<li>CPU governor status</li>
<li>Disk scheduler status</li>
<li>ZRAM usage</li>
<li>FileBrowser status (online/offline)</li>
<li>Tailscale IP</li>
<li>System uptime</li>
</ul>

<p>Auto-starts on login with a lightweight overlay HUD.</p>
<br>
</td>

</tr>
</table>

---

<h2>🎯 Target Use Cases</h2>

<ul>
<li>Old laptops and desktops</li>
<li>Legacy 32-bit systems (i686)</li>
<li>Home NAS</li>
<li>Personal file server</li>
<li>Lightweight cloud storage</li>
<li>Remote access node</li>
<li>Always-on monitoring machine</li>
</ul>

---

<h2>📌 Access Points</h2>

<p><b>Samba (LAN)</b></p>

<pre><code>smb://SERVER_IP/server</code></pre>

<p><b>File Browser (Web UI)</b></p>

<pre><code>http://SERVER_IP:8080</code></pre>

<p><b>Remote Access</b></p>

<pre><code>Tailscale private network</code></pre>

<p><b>Remote Desktop</b></p>

<pre><code>AnyDesk / VNC</code></pre>

---

<h2>⚠️ Notes</h2>

<ul>
<li>AnyDesk compatibility may vary on legacy systems</li>
<li>Samba password setup is required during installation</li>
<li>Network interface names may vary (enp*, eth*, wlan*)</li>
<li>Designed for Ubuntu and Linux Mint</li>
<li>Optimized for low-resource environments</li>
<li>ZRAM is enabled automatically for memory pressure reduction</li>
</ul>

---

<p align="center">
Made for lightweight server enthusiasts. 🐧
</p>
