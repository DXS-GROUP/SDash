const ctx = document.getElementById('cpuTempChart').getContext('2d');
const cpuTempChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'CPU Temp (°C)',
            data: [],
            borderColor: '#abd89b',
            fill: true,
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                display: false,
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Temp (°C)'
                },
                min: 0,
                max: 100
            }
        }
    }
});

function updateCPUTempChart() {
    fetch('/cpu_temp')
        .then(response => response.json())
        .then(data => {
            const now = new Date().toLocaleTimeString();
            cpuTempChart.data.labels.push(now);
            cpuTempChart.data.datasets[0].data.push(data.cpu_temp);

            if (cpuTempChart.data.labels.length > 10) {
                cpuTempChart.data.labels.shift();
                cpuTempChart.data.datasets[0].data.shift();
            }

            cpuTempChart.update();

            document.getElementById("summary_temp_data").textContent = "CPU Temp: " + data.cpu_temp.toFixed(2) + "°C";
        });
}

setInterval(updateCPUTempChart, 1000); 
