const colors = {
    bg: "#282A36",
    fg: "#F8F8F2",
    color1: "#abd89b",
    color2: "#e9bdbe",
    color3: "#c4a3f1",
    color4: "#7e9cd8"
};

const updateIndicators = async () => {
    try {
        const [usage, cpuTemp] = await Promise.all([
            fetch('/api/usage').then(response => response.json()),
            fetch('/api/cpu_temp').then(response => response.json())
        ]);

        updateProgressBars(usage);
        updateSummaryTexts(usage);
        updateNetworkSpeeds(usage);
        updateCpuTemperature(cpuTemp);
    } catch (error) {
        console.error('Error updating indicators:', error);
    }
};

const updateProgressBars = (usage) => {
    const progressElements = {
        cpu: document.getElementById('cpu-progress'),
        ram: document.getElementById('ram-progress'),
        disk: document.getElementById('disk-progress')
    };

    progressElements.cpu.style.width = `${usage.cpu_usage}%`;
    if (usage.cpu_usage > 90) {
        progressElements.cpu.style.backgroundColor = "#FF5555";
    } else if (usage.cpu_usage > 70) {
        progressElements.cpu.style.backgroundColor = "#FFB86C";
    } else {
        progressElements.cpu.style.backgroundColor = "#50FA7B";
    }

    progressElements.ram.style.width = `${usage.ram_usage}%`;
    if (usage.ram_usage > 90) {
        progressElements.ram.style.backgroundColor = "#FF5555";
    } else if (usage.ram_usage > 80) {
        progressElements.ram.style.backgroundColor = "#FFB86C";
    } else {
        progressElements.ram.style.backgroundColor = "#50FA7B";
    }

    progressElements.disk.style.width = `${usage.disk_usage}%`;
    if (usage.disk_usage > 90) {
        progressElements.disk.style.backgroundColor = "#FF5555";
    } else if (usage.disk_usage > 80) {
        progressElements.disk.style.backgroundColor = "#FFB86C";
    } else {
        progressElements.disk.style.backgroundColor = "#50FA7B";
    }

};

const updateSummaryTexts = (usage) => {
    document.getElementById('cpu-value').textContent = `CPU: ${usage.cpu_usage.toFixed(2)}%`;
    document.getElementById('ram-value').textContent = `RAM: ${(usage.ram_used / (1024 ** 3)).toFixed(1)}GB / ${(usage.ram_total / (1024 ** 3)).toFixed(1)}GB - ${usage.ram_usage.toFixed(1)}%`;
    document.getElementById('disk-value').textContent = `Disk: ${(usage.disk_used / (1024 ** 3)).toFixed(1)}GB / ${(usage.disk_total / (1024 ** 3)).toFixed(1)}GB - ${usage.disk_usage.toFixed(2)}%`;
    document.getElementById('summary_data_cpu_text').innerHTML = `CPU USAGE: <br>${usage.cpu_usage}%`;
    document.getElementById('summary_data_ram_text').innerHTML = `RAM USAGE: <br>${usage.ram_usage}%`;
    document.getElementById('summary_data_disk_text').innerHTML = `DISK USAGE: <br>${usage.disk_usage}%`;
};

const updateNetworkSpeeds = (usage) => {
    document.getElementById('upload_speed').innerHTML = `UPLOAD SPEED: ${usage.net_sent.toFixed(2)}kb/s`;
    document.getElementById('download_speed').innerHTML = `DOWNLOAD SPEED: ${usage.net_recv.toFixed(2)}kb/s`;
};

const updateCpuTemperature = (cpuTemp) => {
    document.getElementById('summary_data_cpu_temp_text').innerHTML = `CPU: ${cpuTemp.cpu_temp.toFixed(1)}°C - ${(cpuTemp.cpu_freq / 1000).toFixed(1)}GHz`;
    if (cpuTemp.cpu_temp.toFixed(0) > 45) {
        document.getElementById('summary_data_cpu_temp_text').style.color = "#FFB86C";
    } else if (cpuTemp.cpu_temp.toFixed(0) > 60) {
        document.getElementById('summary_data_cpu_temp_text').style.color = "#FF5555";
    } else {
      document.getElementById('summary_data_cpu_temp_text').style.color = ""; // reset to default color
    }
};

const updateSystemInfo = async () => {
    try {
        const data = await fetch('/api/system_info').then(response => response.json());
        const systemInfoElements = {
            uptime: document.getElementById('device_uptime'),
            ip: document.getElementById('device_ip'),
            platform: document.getElementById('platform'),
            deviceName: document.getElementById('device_name'),
            model: document.getElementById('model'),
            cpu: document.getElementById('cpu'),
            gpu: document.getElementById('gpu')
        };

        systemInfoElements.uptime.innerText = data.device_uptime;
        systemInfoElements.ip.innerText = data.device_ip;
        systemInfoElements.platform.innerText = data.sys_platform;
        systemInfoElements.deviceName.innerText = data.device_name;
        systemInfoElements.model.innerText = data.sys_model;
        systemInfoElements.cpu.innerText = data.sys_cpu;
        systemInfoElements.gpu.innerText = data.sys_gpu;
    } catch (error) {
        console.error('Error updating system info:', error);
    }
};

const fetchBatteryStatus = async () => {
    try {
        const response = await fetch('/api/battery');
        const data = await response.json();
        const chargeElement = document.getElementById('charge');
        const batteryProgress = document.getElementById('battery-progress');

        if (data.charge !== null) {
            const status = data.plugged ? "Charging" : "Not Charging";
            chargeElement.innerHTML = `BATTERY USAGE: <br>${data.charge.toFixed(2)}% - ${status}`;
            batteryProgress.style.width = `${data.charge}%`;

            if (data.charge.toFixed(0) < 15) {
                batteryProgress.style.backgroundColor = "#FF5555";
            } else if (data.charge.toFixed(0) < 30) {
                batteryProgress.style.backgroundColor = "#FFB86C";
            } else {
                batteryProgress.style.backgroundColor = "#50FA7B";
            }
        } else {
            chargeElement.innerHTML = "No battery detected <br> None";
        }
    } catch (error) {
        console.error('Error fetching battery status:', error);
    }
};

const fetchServices = async () => {
    const servicesBody = document.getElementById('services-body');
    const contextMenu = document.getElementById('context-menu');
    let selectedService = '';

    try {
        const response = await fetch('/api/services');
        const data = await response.json();
        servicesBody.innerHTML = '';

        data.forEach(service => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${service.name}</td>
                <td>${service.status}</td>
                <td>${service.error || 'None'}</td>
            `;
            row.addEventListener('contextmenu', function(event) {
                event.preventDefault();
                selectedService = service.name;
                contextMenu.style.display = 'block';
                contextMenu.style.left = `${event.pageX}px`;
                contextMenu.style.top = `${event.pageY}px`;
            });
            servicesBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching services:', error);
    }
};

setInterval(fetchBatteryStatus, 1000);
setInterval(updateIndicators, 1000);
setInterval(updateSystemInfo, 1000);
setInterval(fetchServices, 1000);
