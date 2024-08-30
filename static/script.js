const colors = {
  bg: "#1e1e2d",
  fg: "#d5d9d6",
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

      const cpuProgress = document.getElementById('cpu-progress');
      const ramProgress = document.getElementById('ram-progress');
      const diskProgress = document.getElementById('disk-progress');

      cpuProgress.style.width = `${usage.cpu_usage}%`;
      document.getElementById('cpu-value').textContent = `CPU: ${usage.cpu_usage.toFixed(2)}%`;

      ramProgress.style.width = `${usage.ram_usage}%`;
      document.getElementById('ram-value').textContent = `RAM: ${(usage.ram_used / 1024 / 1024 / 1024).toFixed(1)}GB / ${(usage.ram_total / 1024 / 1024 / 1024).toFixed(1)}GB - ${usage.ram_usage.toFixed(1)}%`;

      diskProgress.style.width = `${usage.disk_usage}%`;
      document.getElementById('disk-value').textContent = `Disk: ${(usage.disk_used / 1024 / 1024 / 1024).toFixed(1)}GB / ${(usage.disk_total / 1024 / 1024 / 1024).toFixed(1)}GB - ${usage.disk_usage.toFixed(2)}%`;

      document.getElementById('summary_data_cpu_text').innerHTML = 'CPU USAGE: <br>' + usage.cpu_usage + '%';
      document.getElementById('summary_data_ram_text').innerHTML = 'RAM USAGE: <br>' + usage.ram_usage + '%';
      document.getElementById('summary_data_disk_text').innerHTML = 'DISK USAGE: <br>' + usage.disk_usage + '%';

      document.getElementById('upload_speed').innerHTML = 'UPLOAD SPEED: <br>' + usage.net_sent.toFixed(2) + 'kb/s';
      document.getElementById('download_speed').innerHTML = 'DOWNLOAD SPEED: <br>' + usage.net_recv.toFixed(2) + 'kb/s';

      document.getElementById('summary_data_cpu_temp_text').innerHTML = 'CPU: ' + cpuTemp.cpu_temp.toFixed(1) + '°C - ' + (cpuTemp.cpu_freq / 1000).toFixed(1) + 'GHz';
  } catch (error) {
      console.error('Error updating indicators:', error);
  }
};

const updateSystemInfo = async () => {
  try {
      const data = await fetch('/api/system_info').then(response => response.json());

      document.getElementById('device_uptime').innerText = data.device_uptime;
      document.getElementById('device_ip').innerText = data.device_ip;
      document.getElementById('platform').innerText = data.sys_platform;
      document.getElementById('device_name').innerText = data.device_name;
      document.getElementById('model').innerText = data.sys_model;
      document.getElementById('cpu').innerText = data.sys_cpu;
      document.getElementById('gpu').innerText = data.sys_gpu;
  } catch (error) {
      console.error('Error updating system info:', error);
  }
};

function fetchBatteryStatus() {
    fetch('/api/battery')
        .then(response => response.json())
        .then(data => {
            const chargeElement = document.getElementById('summary_data_battery_text');

            if (data.charge !== null) {
                chargeElement.textContent = data.charge.toFixed(2) + "%" + '<br>' + data.plugged ? "Charging" : "Not Charging";
            } else {
                chargeElement.textContent = "No battery detected";
                statusElement.textContent = "None";
            }
        })
        .catch(error => {
            console.error('Error fetching battery status:', error);
        });
}

document.addEventListener('DOMContentLoaded', function() {
  const servicesBody = document.getElementById('services-body');
  const contextMenu = document.getElementById('context-menu');
  let selectedService = '';

  function fetchServices() {
      fetch('/api/services')
          .then(response => response.json())
          .then(data => {
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
          });
  }

  fetchServices();
});

setInterval(fetchBatteryStatus, 1000);
setInterval(updateIndicators, 1000);
setInterval(updateSystemInfo, 1000);
