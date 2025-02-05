import os
from datetime import datetime, timedelta
import psutil
import platform
import socket
import time

def get_personal_and_system_details():
    details = {}
    
    details['current_user'] = os.getlogin()
    details['current_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    details['home_directory'] = os.path.expanduser("~")
    details['path_variable'] = os.getenv('PATH')

    logged_in_users = psutil.users()
    details['logged_in_users'] = [
        {
            'user_name': user.name,
            'host': user.host,
            'start_time': datetime.fromtimestamp(user.started).strftime("%Y-%m-%d %H:%M:%S")
        }
        for user in logged_in_users
    ]

    details['hostname'] = socket.gethostname()
    details['system_platform'] = platform.system()
    details['platform_version'] = platform.version()
    details['platform_machine'] = platform.machine()

    details['cpu_logical_cores'] = psutil.cpu_count(logical=True)
    details['cpu_physical_cores'] = psutil.cpu_count(logical=False)
    details['cpu_frequency'] = psutil.cpu_freq().current

    memory_info = psutil.virtual_memory()
    details['total_memory'] = memory_info.total / (1024 ** 3)
    details['used_memory'] = memory_info.used / (1024 ** 3)
    details['available_memory'] = memory_info.available / (1024 ** 3)
    details['memory_usage'] = memory_info.percent

    swap_info = psutil.swap_memory()
    details['total_swap'] = swap_info.total / (1024 ** 3)
    details['used_swap'] = swap_info.used / (1024 ** 3)
    details['free_swap'] = swap_info.free / (1024 ** 3)

    disk_info = psutil.disk_usage('/')
    details['total_disk'] = disk_info.total / (1024 ** 3)
    details['used_disk'] = disk_info.used / (1024 ** 3)
    details['free_disk'] = disk_info.free / (1024 ** 3)

    network_info = psutil.net_if_addrs()
    private_ip_prefixes = ("192.168.", "10.", "172.")
    network_interfaces = []
    for interface, addrs in network_info.items():
        for addr in addrs:
            if any(addr.address.startswith(prefix) for prefix in private_ip_prefixes):
                network_interfaces.append({
                    'interface': interface,
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })
    details['network_interfaces'] = network_interfaces

    boot_time = psutil.boot_time()
    details['uptime'] = str(timedelta(seconds=time.time() - boot_time))

    battery_info = psutil.sensors_battery()
    if battery_info:
        details['battery_percentage'] = battery_info.percent
        details['battery_plugged_in'] = battery_info.power_plugged

    return details
