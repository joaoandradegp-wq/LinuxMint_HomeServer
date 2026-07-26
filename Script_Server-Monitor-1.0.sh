#!/bin/bash
set -e

echo "=== Sevastolink Monitor Installer ==="

sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl

INSTALL_DIR="$HOME/SevastolinkMonitor"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install fastapi uvicorn psutil

cat > api.py <<'PYEOF'
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn, psutil, socket, subprocess, platform, os, time
from datetime import timedelta

app = FastAPI(title="Sevastolink Monitor")

def run(cmd):
    try:
        return subprocess.check_output(cmd,shell=True,text=True,stderr=subprocess.DEVNULL).strip()
    except:
        return ""

def svc(name):
    return "ONLINE" if run(f"systemctl is-active {name}")=="active" else "OFFLINE"

def cpu_model():
    return run("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d ':' -f2").strip()

def cpu_temp():
    try:
        for v in psutil.sensors_temperatures().values():
            for e in v:
                return round(e.current,1)
    except:
        pass
    return None

def iface():
    for n,s in psutil.net_if_stats().items():
        if s.isup and n!="lo" and not n.startswith("tailscale"):
            return n
    return ""

IFACE=iface()
old=psutil.net_io_counters(pernic=True)
oldt=time.time()

def speed():
    global old,oldt
    if IFACE not in psutil.net_io_counters(pernic=True): return (0,0)
    now=time.time()
    cur=psutil.net_io_counters(pernic=True)
    dt=max(now-oldt,0.001)
    d=(cur[IFACE].bytes_recv-old[IFACE].bytes_recv)/dt/1024/1024
    u=(cur[IFACE].bytes_sent-old[IFACE].bytes_sent)/dt/1024/1024
    old,oldt=cur,now
    return round(d,2),round(u,2)

def ip():
    for a in psutil.net_if_addrs().get(IFACE,[]):
        if a.family==socket.AF_INET:
            return a.address
    return "Offline"

def linkspeed():
    p=f"/sys/class/net/{IFACE}/speed"
    try:
        s=int(open(p).read().strip())
        return f"{s//1000} Gb/s" if s>=1000 else f"{s} Mb/s"
    except:
        return "Unknown"

@app.get("/api/rainmeter", response_class=PlainTextResponse)
def rain():
    cpu=psutil.cpu_percent(interval=0.5)
    mem=psutil.virtual_memory()
    sw=psutil.swap_memory()
    dk=psutil.disk_usage("/")
    down,up=speed()
    uptime=str(timedelta(seconds=int(time.time()-psutil.boot_time())))
    tsip=run("ip -4 addr show tailscale0 | grep inet | awk '{print $2}' | cut -d/ -f1") or "Offline"
    lines=[
        f"HOSTNAME={platform.node()}",
        f"CPU_MODEL={cpu_model()}",
        f"CPU_CORES={psutil.cpu_count(logical=False)}",
        f"CPU_THREADS={psutil.cpu_count(logical=True)}",
        f"CPU_FREQ={round(psutil.cpu_freq().current/1000,2)}",
        f"CPU_TEMP={cpu_temp()}",
        f"CPU_USAGE={cpu}",
        f"RAM_USED={round(mem.used/1024**3,2)}",
        f"RAM_TOTAL={round(mem.total/1024**3,2)}",
        f"RAM_PERCENT={mem.percent}",
        f"SWAP_USED={round(sw.used/1024**3,2)}",
        f"SWAP_TOTAL={round(sw.total/1024**3,2)}",
        f"SWAP_PERCENT={sw.percent}",
        f"DISK_USED={round(dk.used/1024**3,2)}",
        f"DISK_TOTAL={round(dk.total/1024**3,2)}",
        f"DISK_PERCENT={dk.percent}",
        f"LAN_IP={ip()}",
        f"DOWNLOAD={down}",
        f"UPLOAD={up}",
        f"LINK_SPEED={linkspeed()}",
        f"FILEBROWSER={svc('filebrowser')}",
        f"TAILSCALE={svc('tailscaled')}",
        f"TAILSCALE_IP={tsip}",
        f"UPTIME={uptime}"
    ]
    return "\n".join(lines)

if __name__=="__main__":
    uvicorn.run("api:app",host="0.0.0.0",port=8181)
PYEOF

PYTHON="$INSTALL_DIR/.venv/bin/python"

cat | sudo tee /etc/systemd/system/sevastolink.service >/dev/null <<EOF
[Unit]
Description=Sevastolink Monitor API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$PYTHON $INSTALL_DIR/api.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable sevastolink
sudo systemctl restart sevastolink

echo
echo "Instalação concluída!"
echo "Teste:"
echo "http://server:8181/api/rainmeter"
