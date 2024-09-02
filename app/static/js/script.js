const colors = {
    bg: "#181926",
    fg: "#cad3f5",
    accent: "#24273a",
    accent_hover: "#ca9ee6",
    critical: "#ed8796",
    warning: "#e5c890",
    normal: "#a6da95"
};

const updateIndicators = async () => {
    try {
        const [usage, cpuTemp, gpuTemp, userIP] = await Promise.all([
            fetch('/api/usage').then(response => response.json()),
            fetch('/api/cpu_temp').then(response => response.json()),
            fetch('/api/gpu_temp').then(response => response.json()),
            fetch('/api/user_ip').then(response => response.json())
        ]);

        updateProgressBars(usage);
        updateSummaryTexts(usage);
        updateNetworkSpeeds(usage);
        updateCpuTemperature(cpuTemp);
        updateGpuTemperature(gpuTemp);
        getUserIp(userIP);
    } catch (error) {
        console.error('Error updating indicators:', error);
    }
};

const getUserIp = (userIP) => {
    const user_ip = userIP.ip;

    console.debug("User IP: " + user_ip);
};

const updateProgressBars = (usage) => {
    const progressElements = {
        cpu: document.getElementById('cpu-progress'),
        ram: document.getElementById('ram-progress'),
        disk: document.getElementById('disk-progress')
    };

    progressElements.cpu.style.width = `${usage.cpu_usage}%`;
    if (usage.cpu_usage > 90) {
        progressElements.cpu.style.backgroundColor = colors.critical;
    } else if (usage.cpu_usage > 70) {
        progressElements.cpu.style.backgroundColor = colors.warning;
    } else {
        progressElements.cpu.style.backgroundColor = colors.normal;
    }

    progressElements.ram.style.width = `${usage.ram_usage}%`;
    if (usage.ram_usage > 90) {
        progressElements.ram.style.backgroundColor = colors.critical;
    } else if (usage.ram_usage > 80) {
        progressElements.ram.style.backgroundColor = colors.warning;
    } else {
        progressElements.ram.style.backgroundColor = colors.normal;
    }

    progressElements.disk.style.width = `${usage.disk_usage}%`;
    if (usage.disk_usage > 90) {
        progressElements.disk.style.backgroundColor = colors.critical;
    } else if (usage.disk_usage > 80) {
        progressElements.disk.style.backgroundColor = colors.warning;
    } else {
        progressElements.disk.style.backgroundColor = colors.normal;
    }
};

const updateSummaryTexts = (usage) => {
    document.getElementById('cpu-value').textContent = `CPU: ${usage.cpu_usage.toFixed(2)}%`;
    document.getElementById('ram-value').textContent = `RAM: ${(usage.ram_used / (1024 ** 3)).toFixed(1)}GB / ${(usage.ram_total / (1024 ** 3)).toFixed(1)}GB - ${usage.ram_usage.toFixed(1)}%`;
    document.getElementById('disk-value').textContent = `Disk: ${(usage.disk_used / (1024 ** 3)).toFixed(1)}GB / ${(usage.disk_total / (1024 ** 3)).toFixed(1)}GB - ${usage.disk_usage.toFixed(2)}%`;
    document.getElementById('summary_data_cpu_text').innerHTML = `CPU USAGE: <br>${usage.cpu_usage}%`;
    document.getElementById('summary_data_ram_text').innerHTML = `RAM USAGE: <br>${usage.ram_usage}%`;
    document.getElementById('summary_data_disk_text').innerHTML = `DISK USAGE: <br>${usage.disk_usage}%`;

    console.debug("CPU USAGE: " + usage.cpu_usage);
    console.debug("RAM USAGE: " + usage.ram_usage);
    console.debug("DISK USAGE: " + usage.disk_usage);
};

const updateNetworkSpeeds = (usage) => {
    document.getElementById('upload_speed').innerHTML = `UPLOAD SPEED: ${usage.net_sent.toFixed(2)}kb/s`;
    document.getElementById('download_speed').innerHTML = `DOWNLOAD SPEED: ${usage.net_recv.toFixed(2)}kb/s`;
};

const updateCpuTemperature = (cpuTemp) => {
    document.getElementById('summary_data_cpu_temp_text').innerHTML = `CPU: ${cpuTemp.cpu_temp.toFixed(1)}°C - ${(cpuTemp.cpu_freq / 1000).toFixed(1)}GHz`;
    if (cpuTemp.cpu_temp.toFixed(0) > 45) {
        document.getElementById('summary_data_cpu_temp_text').style.color = colors.warning;
    } else if (cpuTemp.cpu_temp.toFixed(0) > 60) {
        document.getElementById('summary_data_cpu_temp_text').style.color = colors.critical;
    } else {
        document.getElementById('summary_data_cpu_temp_text').style.color = "";
    }

    console.debug(`CPU TEMP: ${cpuTemp.cpu_temp.toFixed(1)}°C - ${(cpuTemp.cpu_freq / 1000).toFixed(1)}GHz`);
};

const updateGpuTemperature = (gpuTemp) => {
    if (gpuTemp.gpu_temp != "None") {
        document.getElementById('summary_data_gpu_temp_text').innerHTML = "GPU: " + gpuTemp.gpu_temp + "°C - " + gpuTemp.gpu_freq + "MHz";
        if (gpuTemp.gpu_temp > 45) {
            document.getElementById('summary_data_gpu_temp_text').style.color = colors.warning;
        } else if (gpuTemp.gpu_temp > 60) {
            document.getElementById('summary_data_gpu_temp_text').style.color = colors.critical;
        } else {
            document.getElementById('summary_data_gpu_temp_text').style.color = "";
        }
    }
    else {
        document.getElementById('summary_data_gpu_temp_text').style.display = "None";
    }

    console.debug("GPU: " + gpuTemp.gpu_temp + "°C - " + gpuTemp.gpu_freq + "MHz");
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
            cpuArch: document.getElementById('cpu_arch'),
            gpu: document.getElementById('gpu'),
        };

        systemInfoElements.platform.innerText = data.sys_platform;
        systemInfoElements.uptime.innerHTML = data.device_uptime;
        systemInfoElements.ip.innerText = data.device_ip;
        systemInfoElements.deviceName.innerText = data.device_name;
        systemInfoElements.model.innerText = data.sys_model;
        systemInfoElements.cpu.innerText = data.sys_cpu;
        systemInfoElements.gpu.innerText = data.sys_gpu;
        systemInfoElements.cpuArch.innerText = data.cpu_arch;
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
        const imgElement = document.querySelector('#battery-status img');

        if (data.charge !== null) {
            const charge = data.charge.toFixed(2);
            console.debug(`BATTERY: ${charge}%`);

            chargeElement.innerHTML = `BATTERY USAGE: <br>${charge}%`;
            batteryProgress.style.width = `${charge}%`;

            if (data.plugged) {
                batteryProgress.style.backgroundColor = colors.accent_hover;
                imgElement.src = "../static/icons/battery-bolt.svg";
            } else {
                setBatteryStatus(charge, batteryProgress, imgElement);
            }
        } else {
            chargeElement.innerHTML = "No battery detected <br> None";
        }
    } catch (error) {
        console.error('Error fetching battery status:', error);
    }
}

const setBatteryStatus = (charge, batteryProgress, imgElement) => {
    let backgroundColor;
    let imgSrc = "../static/icons/battery_full.svg";

    if (charge < 15) {
        backgroundColor = colors.critical;
        imgSrc = "../static/icons/battery-exclamation.svg";
    } else if (charge < 20) {
        backgroundColor = colors.warning;
    } else {
        backgroundColor = colors.normal;
    }

    batteryProgress.style.backgroundColor = backgroundColor;
    imgElement.src = imgSrc;
}

setInterval(fetchBatteryStatus, 1000);
setInterval(updateIndicators, 1000);
setInterval(updateSystemInfo, 1000);
