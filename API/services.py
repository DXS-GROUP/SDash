import psutil

def get_services():
    services = []
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        services.append({
            "name": proc.info['name'],
            "status": proc.info['status'],
            "error": None
        })
    return services
