const bg = "#1e1e2d";
const fg = "#d5d9d6";
const color1 = "#abd89b";
const color2 = "#e9bdbe";
const color3 = "#c4a3f1";
const color4 = "#7e9cd8";

function updateIndicators() {
    fetch('/usage')
      .then(response => response.json())
      .then(data => {
        const cpuProgress = document.getElementById('cpu-progress');
        const ramProgress = document.getElementById('ram-progress');
        const diskProgress = document.getElementById('disk-progress');
  
        cpuProgress.style.width = `${data.cpu_usage}%`;
        document.getElementById('cpu-value').textContent = `CPU: ${data.cpu_usage.toFixed(2)}%`;
  
        ramProgress.style.width = `${data.ram_usage}%`;
        document.getElementById('ram-value').textContent = `RAM: ${(data.ram_used / 1024 / 1024 / 1024).toFixed(1)}GB / ${(data.ram_total / 1024 / 1024 / 1024).toFixed(1)}GB - ${data.ram_usage.toFixed(1)}%`;
  
        diskProgress.style.width = `${data.disk_usage}%`;
        document.getElementById('disk-value').textContent = `Disk: ${(data.disk_used / 1024 / 1024 / 1024).toFixed(1)}GB / ${(data.disk_total / 1024 / 1024 / 1024).toFixed(1)}GB - ${data.disk_usage.toFixed(2)}%`;

        document.getElementById('summary_data_cpu_text').innerHTML = 'CPU USAGE: ' + data.cpu_usage + '%'
        document.getElementById('summary_data_ram_text').innerHTML = 'RAM USAGE: ' + data.ram_usage + '%'
        document.getElementById('summary_data_disk_text').innerHTML = 'DISK USAGE: ' + data.disk_usage + '%'

        document.getElementById('upload_speed').innerHTML = 'UPLOAD SPEED: ' + data.net_sent.toFixed(2) + 'kb/s'
        document.getElementById('download_speed').innerHTML = 'DOWNLOAD SPEED: ' + data.net_recv.toFixed(2) + 'kb/s'
      });
}

function updateSystemInfo() {
    fetch('/system_info')
        .then(response => response.json())
        .then(data => {
            document.getElementById('device_uptime').innerText = 'Uptime: ' + data.device_uptime;
            document.getElementById('device_ip').innerText = 'IP: ' + data.device_ip;
            document.getElementById('platform').innerText = 'Platform: ' + data.sys_platform;
            document.getElementById('device_name').innerText = 'Device: ' + data.device_name;
            document.getElementById('model').innerText = 'Host: ' + data.sys_model;
            document.getElementById('cpu').innerText = 'CPU: ' + data.sys_cpu;
            document.getElementById('gpu').innerText = 'GPU: ' + data.sys_gpu;
        });
}

setInterval(updateIndicators, 1000);
setInterval(updateSystemInfo, 1000);
