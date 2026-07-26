from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn
import psutil
import socket
import subprocess
import platform
import os
import time
from datetime import timedelta

app = FastAPI(title="Sevastolink Monitor")


# ---------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------

def run_command(cmd):
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except:
        return ""


def service_status(service):
    status = run_command(f"systemctl is-active {service}")
    return "ONLINE" if status == "active" else "OFFLINE"


def get_cpu_model():
    model = run_command("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d ':' -f2")
    return model.strip()


def get_cpu_temp():

    temps = psutil.sensors_temperatures()

    if not temps:
        return None

    for sensor in temps.values():
        for entry in sensor:
            if entry.current:
                return round(entry.current, 1)

    return None


def detect_network_interface():

    stats = psutil.net_if_stats()

    for name, st in stats.items():

        if not st.isup:
            continue

        if name == "lo":
            continue

        if name.startswith("tailscale"):
            continue

        return name

    return None


NETWORK_INTERFACE = detect_network_interface()

old_net = psutil.net_io_counters(pernic=True)
old_time = time.time()


def get_network_speed():

    global old_net
    global old_time

    if NETWORK_INTERFACE is None:
        return 0, 0

    now = time.time()

    current = psutil.net_io_counters(pernic=True)

    if NETWORK_INTERFACE not in current:
        return 0, 0

    elapsed = now - old_time

    down = (
        current[NETWORK_INTERFACE].bytes_recv -
        old_net[NETWORK_INTERFACE].bytes_recv
    ) / elapsed

    up = (
        current[NETWORK_INTERFACE].bytes_sent -
        old_net[NETWORK_INTERFACE].bytes_sent
    ) / elapsed

    old_net = current
    old_time = now

    return down / 1024 / 1024, up / 1024 / 1024


def get_ip():

    if NETWORK_INTERFACE is None:
        return "Offline"

    addrs = psutil.net_if_addrs()

    if NETWORK_INTERFACE not in addrs:
        return "Offline"

    for addr in addrs[NETWORK_INTERFACE]:

        if addr.family == socket.AF_INET:
            return addr.address

    return "Offline"


def get_link_speed():

    if NETWORK_INTERFACE is None:
        return "Unknown"

    path = f"/sys/class/net/{NETWORK_INTERFACE}/speed"

    if not os.path.exists(path):
        return "Unknown"

    try:

        speed = int(open(path).read().strip())

        if speed >= 1000:
            return f"{speed//1000} Gb/s"

        return f"{speed} Mb/s"

    except:
        return "Unknown"


def get_tailscale_ip():

    ip = run_command("ip -4 addr show tailscale0 | grep inet | awk '{print $2}' | cut -d/ -f1")

    if ip == "":
        return "Offline"

    return ip


def format_bytes(value):

    gb = value / (1024 ** 3)

    return round(gb, 2)


# ---------------------------------------------------------------------
# API
# ---------------------------------------------------------------------

@app.get("/")
def root():

    return {
        "application": "Sevastolink Monitor",
        "version": "1.0",
        "endpoint": "/api/status"
    }


@app.get("/api/status")
def status():

    cpu_percent = psutil.cpu_percent(interval=0.5)

    memory = psutil.virtual_memory()

    swap = psutil.swap_memory()

    disk = psutil.disk_usage("/")

    down, up = get_network_speed()

    uptime = timedelta(seconds=int(time.time() - psutil.boot_time()))

    return {

        "hostname": platform.node(),

        "cpu": {

            "model": get_cpu_model(),

            "cores": psutil.cpu_count(logical=False),

            "threads": psutil.cpu_count(logical=True),

            "frequency": round(psutil.cpu_freq().current / 1000, 2),

            "temperature": get_cpu_temp(),

            "usage": cpu_percent

        },

        "memory": {

            "used_gb": format_bytes(memory.used),

            "total_gb": format_bytes(memory.total),

            "percent": memory.percent

        },

        "swap": {

            "used_gb": format_bytes(swap.used),

            "total_gb": format_bytes(swap.total),

            "percent": swap.percent

        },

        "disk": {

            "mount": "/",

            "used_gb": format_bytes(disk.used),

            "total_gb": format_bytes(disk.total),

            "percent": disk.percent

        },

        "network": {

            "interface": NETWORK_INTERFACE,

            "ip": get_ip(),

            "download_mb_s": round(down, 2),

            "upload_mb_s": round(up, 2),

            "link_speed": get_link_speed()

        },

        "filebrowser": {

            "status": service_status("filebrowser")

        },

        "tailscale": {

            "status": service_status("tailscaled"),

            "ip": get_tailscale_ip()

        },

        "system": {

            "uptime": str(uptime)

        }

    }

@app.get("/api/rainmeter", response_class=PlainTextResponse)
def rainmeter():

    data = status()

    return "\n".join([
        f"HOSTNAME={data['hostname']}",
        f"CPU_MODEL={data['cpu']['model']}",
        f"CPU_CORES={data['cpu']['cores']}",
        f"CPU_THREADS={data['cpu']['threads']}",
        f"CPU_FREQ={data['cpu']['frequency']}",
        f"CPU_TEMP={data['cpu']['temperature']}",
        f"CPU_USAGE={data['cpu']['usage']}",

        f"RAM_USED={data['memory']['used_gb']}",
        f"RAM_TOTAL={data['memory']['total_gb']}",
        f"RAM_PERCENT={data['memory']['percent']}",

        f"SWAP_USED={data['swap']['used_gb']}",
        f"SWAP_TOTAL={data['swap']['total_gb']}",
        f"SWAP_PERCENT={data['swap']['percent']}",

        f"DISK_USED={data['disk']['used_gb']}",
        f"DISK_TOTAL={data['disk']['total_gb']}",
        f"DISK_PERCENT={data['disk']['percent']}",

        f"LAN_IP={data['network']['ip']}",
        f"DOWNLOAD={data['network']['download_mb_s']}",
        f"UPLOAD={data['network']['upload_mb_s']}",
        f"LINK_SPEED={data['network']['link_speed']}",

        f"FILEBROWSER={data['filebrowser']['status']}",

        f"TAILSCALE={data['tailscale']['status']}",
        f"TAILSCALE_IP={data['tailscale']['ip']}",

        f"UPTIME={data['system']['uptime']}"
    ])

if __name__ == "__main__":

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8181,
        reload=False
    )
