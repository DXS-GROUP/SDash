const ctxCPU = document.getElementById('cpuChart').getContext('2d');
const ctxRAM = document.getElementById('ramChart').getContext('2d');
const ctxDISK = document.getElementById('diskChart').getContext('2d');
const ctxNetRecv = document.getElementById('netRecvChart').getContext('2d');
const ctxNetSent = document.getElementById('netSentChart').getContext('2d');

const cpuChart = new Chart(ctxCPU, {
    type: 'doughnut',
    data: {
        labels: ['CPU Usage', 'Free'],
        datasets: [{
            label: 'CPU',
            data: [0, 100],
            backgroundColor: ['#e9bdbe', '#abd89b']
        }]
    },
    options: {
        plugins: {
            datalabels: {
                formatter: (value, context) => {
                    return context.chart.data.labels[context.dataIndex] + ': ' + value + '%';
                },
                color: 'black',
            }
        }
    }
});

const ramChart = new Chart(ctxRAM, {
    type: 'doughnut',
    data: {
        labels: ['RAM Usage', 'Free'],
        datasets: [{
            label: 'RAM',
            data: [0, 100],
            backgroundColor: ['#e9bdbe', '#abd89b']
        }]
    },
    options: {
        plugins: {
            datalabels: {
                formatter: (value, context) => {
                    return context.chart.data.labels[context.dataIndex] + ': ' + value + '%';
                },
                color: 'black',
            }
        }
    }
});

const diskChart = new Chart(ctxDISK, {
    type: 'doughnut',
    data: {
        labels: ['DISK Usage', 'Free'],
        datasets: [{
            label: 'DISK',
            data: [0, 100],
            backgroundColor: ['#e9bdbe', '#abd89b']
        }]
    },
    options: {
        plugins: {
            datalabels: {
                formatter: (value, context) => {
                    return context.chart.data.labels[context.dataIndex] + ': ' + value + '%';
                },
                color: 'black',
            }
        }
    }
});

const netRecvChart = new Chart(ctxNetRecv, {
    type: 'line',
    data: {
        labels: Array.from({ length: 60 }, (_, i) => i + 1),
        datasets: [{
            label: 'Download Speed (kbit/s)',
            data: Array(60).fill(0),
            borderColor: '#FF6384',
            fill: true
        }]
    },
    options: {
        plugins: {
            datalabels: {
                align: 'end',
                anchor: 'end',
                formatter: (value) => {
                    return value + ' kbit/s';
                },
                color: 'black',
            }
        }
    }
});

const netSentChart = new Chart(ctxNetSent, {
    type: 'line',
    data: {
        labels: Array.from({ length: 60 }, (_, i) => i + 1),
        datasets: [{
            label: 'Upload Speed (kbit/s)',
            data: Array(60).fill(0),
            borderColor: '#36A2EB',
            fill: true
        }]
    },
    options: {
        plugins: {
            datalabels: {
                align: 'end',
                anchor: 'end',
                formatter: (value) => {
                    return value + ' kbit/s';
                },
                color: 'black',
            }
        }
    }
});

function updateCharts() {
    fetch('/usage')
        .then(response => response.json())
        .then(data => {
            cpuChart.data.datasets[0].data[0] = data.cpu_usage;
            cpuChart.data.datasets[0].data[1] = 100 - data.cpu_usage;
            cpuChart.update();

            ramChart.data.datasets[0].data[0] = data.ram_usage;
            ramChart.data.datasets[0].data[1] = 100 - data.ram_usage;
            ramChart.update();

            diskChart.data.datasets[0].data[0] = data.disk_usage;
            diskChart.data.datasets[0].data[1] = 100 - data.disk_usage;
            diskChart.update();

            netRecvChart.data.datasets[0].data.shift();
            netRecvChart.data.datasets[0].data.push(data.net_recv);
            netRecvChart.update();

            netSentChart.data.datasets[0].data.shift();
            netSentChart.data.datasets[0].data.push(data.net_sent);
            netSentChart.update();

            document.getElementById("summary_data").textContent = "CPU: " + data.cpu_usage.toFixed(2) + "% RAM: " + data.ram_usage.toFixed(2) + "% Disk: " + data.disk_usage.toFixed(2) + "%";
            document.getElementById("summary_net_data").textContent = "Upload: " + data.net_sent.toFixed(2) + " kbit/s Download: " + data.net_recv.toFixed(2) + " kbit/s";
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



setInterval(updateCharts, 1000);
setInterval(updateSystemInfo, 1000);

