const colors = {
    bg: "#232634",
    fg: "#c6d0f5",
    accent: "#303446",
    accent_hover: "#ca9ee6",
    critical: "#e78284",
    warning: "#e5c890",
    normal: "#a6d189"
};

const system_colors = {
    manjaro: "#50FA7B",
    arch: "#8BE9FD",
    kali: "#6272A4",
    endevaour: "##BD93F9",
    centos: "#F1FA8C",
    debian: "#FF5555",
    ubuntu: "#FFB86C",
    suse: "#50FA7B"
}

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
    document.getElementById('summary_data_gpu_temp_text').innerHTML = "GPU: " + gpuTemp.gpu_temp + "°C - " + gpuTemp.gpu_freq + "MHz";
    if (gpuTemp.gpu_temp > 45) {
        document.getElementById('summary_data_gpu_temp_text').style.color = colors.warning;
    } else if (gpuTemp.gpu_temp > 60) {
        document.getElementById('summary_data_gpu_temp_text').style.color = colors.critical;
    } else {
        document.getElementById('summary_data_gpu_temp_text').style.color = "";
    }

    console.debug("GPU: " + gpuTemp.gpu_temp.toFixed(1) + "°C - " + gpuTemp.gpu_freq.toFixed(1) + "MHz");
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
        const batteryBlock = document.getElementById('battery-status');

        if (data.charge !== null) {
            console.debug(`BATTERY: ${data.charge.toFixed(2)}% `);

            const status = data.plugged ? "Charging" : "Not Charging";
            chargeElement.innerHTML = `BATTERY USAGE: <br>${data.charge.toFixed(2)}%`;
            batteryProgress.style.width = `${data.charge}%`;

            if (data.plugged) {
                batteryProgress.style.backgroundColor = colors.accent_hover;
                imgElement.src = "../static/icons/battery-bolt.svg";
            }
            else {
                if (data.charge.toFixed(0) < 15) {
                    batteryProgress.style.backgroundColor = colors.critical;
                    imgElement.src = "../static/icons/battery-exclamation.svg";
                } else if (data.charge.toFixed(0) < 20) {
                    batteryProgress.style.backgroundColor = colors.warning;
                    imgElement.src = "../static/icons/battery-exclamation.svg";
                } else if (data.charge.toFixed(0) > 90) {
                    batteryProgress.style.backgroundColor = colors.normal;
                    imgElement.src = "../static/icons/battery_full.svg";
                } else {
                    batteryProgress.style.backgroundColor = colors.normal;
                    imgElement.src = "../static/icons/battery_full.svg";
                }
            }
        } else {
            chargeElement.innerHTML = "No battery detected <br> None";
            // batteryBlock.style.display = 'none';
        }
    } catch (error) {
        console.error('Error fetching battery status:', error);
    }
};

fetch('/get_os')
    .then(response => response.json())
    .then(data => {
        const main_block = document.getElementsByClassName('html')[0];

        if (main_block) {
            var osName = data.os_name;
            var logoColor = 'gray';

            if (osName.toLowerCase().includes('arch')) {
                logoColor = system_colors.arch;
            } else if (osName.toLowerCase().includes('debian')) {
                logoColor = system_colors.debian;
            } else if (osName.toLowerCase().includes('ubuntu')) {
                logoColor = system_colors.ubuntu;
            } else if (osName.toLowerCase().includes('suse')) {
                logoColor = system_colors.suse;
            } else if (osName.toLowerCase().includes('manjaro')) {
                logoColor = system_colors.manjaro;
            } else if (osName.toLowerCase().includes('centos')) {
                logoColor = system_colors.centos;
            } else if (osName.toLowerCase().includes('kali')) {
                logoColor = system_colors.kali;
            } else if (osName.toLowerCase().includes('endeavour')) {
                logoColor = system_colors.endevaour;
            }

            const backgroundStyle = "radial-gradient(circle at 5% 5%," + logoColor + " 1%,transparent 15.5%)fixed,radial-gradient(circle at 100% 90%," + logoColor + " 30%," + colors.bg + " 40.5%)";

            main_block.style.background = backgroundStyle;
        } else {
            console.error("Element with class 'html' not found.");
        }
    })
    .catch(error => console.error(error))

setInterval(fetchBatteryStatus, 1000);
setInterval(updateIndicators, 1000);
setInterval(updateSystemInfo, 1000);
