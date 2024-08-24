const ctxCPU = document.getElementById('cpuChart').getContext('2d');
const ctxRAM = document.getElementById('ramChart').getContext('2d');
const ctxDISK = document.getElementById('diskChart').getContext('2d');
const ctxNetRecv = document.getElementById('netRecvChart').getContext('2d');
const ctxNetSent = document.getElementById('netSentChart').getContext('2d');

const netRecvChart = new Chart(ctxNetRecv, {
    type: 'line',
    data: {
        labels: Array.from({ length: 60 }, (_, i) => i + 1), // последние 60 секунд
        datasets: [{
            label: 'Скорость загрузки (КБ/с)',
            data: Array(60).fill(0),
            borderColor: '#FF6384',
            fill: false
        }]
    }
});

const netSentChart = new Chart(ctxNetSent, {
    type: 'line',
    data: {
        labels: Array.from({ length: 60 }, (_, i) => i + 1), // последние 60 секунд
        datasets: [{
            label: 'Скорость выгрузки (КБ/с)',
            data: Array(60).fill(0),
            borderColor: '#36A2EB',
            fill: false
        }]
    }
});


const cpuChart = new Chart(ctxCPU, {
    type: 'doughnut',
    data: {
        labels: ['Usage CPU', 'Free'],
        datasets: [{
            label: 'CPU',
            data: [0, 100],
            backgroundColor: ['#e9bdbe', '#abd89b']
        }]
    }
});

const ramChart = new Chart(ctxRAM, {
    type: 'doughnut',
    data: {
        labels: ['Usage RAM', 'Free'],
        datasets: [{
            label: 'RAM',
            data: [0, 100],
            backgroundColor: ['#e9bdbe', '#abd89b']
        }]
    }
});

const diskChart = new Chart(ctxDISK, {
    type: 'doughnut',
    data: {
        labels: ['Usage DISK', 'Free'],
        datasets: [{
            label: 'DISK',
            data: [0, 100],
            backgroundColor: ['#e9bdbe', '#abd89b']
        }]
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
        });
}

function updateSystemInfo() {
    fetch('/system_info')
        .then(response => response.json())
        .then(data => {
            document.getElementById('platform').innerText = 'Platform: ' + data.sys_platform;
            document.getElementById('model').innerText = 'Model: ' + data.sys_model;
            document.getElementById('cpu').innerText = 'CPU: ' + data.sys_cpu;
            document.getElementById('gpu').innerText = 'GPU: ' + data.sys_gpu;
        });
}


setInterval(updateCharts, 100);
setInterval(updateSystemInfo, 1000);
