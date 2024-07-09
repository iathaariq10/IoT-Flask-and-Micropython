/* <=============================================Control Client====================================================> */
/* <=============================================Control Client====================================================> */

$(document).ready(function() {
    $('.on').click(function() {
        var client = $(this).data('client');
        var command = client + '_ON';
        sendCommand(client, command);
    });

    $('.off').click(function() {
        var client = $(this).data('client');
        var command = client + '_OFF';
        sendCommand(client, command);
    });

    function sendCommand(client, command) {
        $.ajax({
            url: '/controlClient1',
            method: 'POST',
            data: { client: client, command: command },
            success: function(response) {
                console.log(response);
            }
        });
    }
});

$(document).ready(function() {
    $('.on').click(function() {
        var client = $(this).data('client');
        var command = client + '_ON';
        sendCommand(client, command);
    });

    $('.off').click(function() {
        var client = $(this).data('client');
        var command = client + '_OFF';
        sendCommand(client, command);
    });

    function sendCommand(client, command) {
        $.ajax({
            url: '/controlClient2',
            method: 'POST',
            data: { client: client, command: command },
            success: function(response) {
                console.log(response);
            }
        });
    }
});

$(document).ready(function() {
    $('.on').click(function() {
        var client = $(this).data('client');
        var command = client + '_ON';
        sendCommand(client, command);
    });

    $('.off').click(function() {
        var client = $(this).data('client');
        var command = client + '_OFF';
        sendCommand(client, command);
    });

    function sendCommand(client, command) {
        $.ajax({
            url: '/controlClient3',
            method: 'POST',
            data: { client: client, command: command },
            success: function(response) {
                console.log(response);
            }
        });
    }
});

/* <=============================================Status Client====================================================> */
/* <=============================================Status Client====================================================> */

function updateClientStatus(client) {
            $.getJSON(`/statusClient${client}`, function(data) {
                $(`#status_client_${client}`).text(data.status);
                $(`#Data_client_${client}`).text(data.data_count);
            });
        }
        setInterval(function() { updateClientStatus(1); }, 1000);
        setInterval(function() { updateClientStatus(2); }, 1000);
        setInterval(function() { updateClientStatus(3); }, 1000);

/* <=============================================Report Sensor====================================================> */
/* <=============================================Report Sensor====================================================> */

function fetchSensorData(clientId, tableId) {
    const table = document.getElementById(tableId);

    fetch(`/get_sensor_data/${clientId}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = table.querySelector('tbody');
            tableBody.innerHTML = '';
            data.forEach(entry => {
                const row = document.createElement('tr');
                Object.values(entry).forEach(value => {
                    const cell = document.createElement('td');
                    cell.textContent = value;
                    row.appendChild(cell);
                });
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error:', error));
}

function updateSensorData() {
    fetchSensorData(1, 'client1Table');
    fetchSensorData(2, 'client2Table');
    fetchSensorData(3, 'client3Table');
}

updateSensorData();

setInterval(updateSensorData, 5000);

/* <=============================================Side Time Box====================================================> */
/* <=============================================Side Time Box====================================================> */

function updateDateTime() {
        var currentDate = new Date();

        var day = currentDate.getDate();
        var month = currentDate.getMonth() + 1; // Months are zero-based
        var year = currentDate.getFullYear();

        var hours = currentDate.getHours();
        var minutes = currentDate.getMinutes();
        var seconds = currentDate.getSeconds();

        day = day < 10 ? '0' + day : day;
        month = month < 10 ? '0' + month : month;
        hours = hours < 10 ? '0' + hours : hours;
        minutes = minutes < 10 ? '0' + minutes : minutes;
        seconds = seconds < 10 ? '0' + seconds : seconds;

        document.getElementById('side-date').innerHTML = day + ' / ' + month + ' / ' + year;
        document.getElementById('side-time').innerHTML = hours + ' : ' + minutes + ' : ' + seconds;
    }

    updateDateTime();
    setInterval(updateDateTime, 1000);

/* <======================================Update Data Sensor Client 1=============================================> */
/* <======================================Update Data Sensor Client 1=============================================> */

async function updateClient1Data() {
  try {
    const response = await fetch("/updateClient1");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.json();
    document.getElementById("S1_A").innerHTML = data.reading_S1_A.toFixed(2) + " °C";
    document.getElementById("S1_B").innerHTML = data.reading_S1_B.toFixed(2) + " %";
    document.getElementById("IP_1").innerHTML = data.ipAddress_1;
    document.getElementById("C1_A").innerHTML = '<strong>' + data.status_1 + '</strong>';
    document.getElementById("C1_B").innerHTML = '<strong>' + data.status_2 + '</strong>';

    if (data.reading_S1_A >= 30) {
      updateStopwatchS1A();
    } else {
      document.getElementById("T1_A").innerHTML = "00 : 00 : 00";
    }

    if (data.reading_S1_B >= 60) {
      updateStopwatchS1B();
    } else {
      document.getElementById("T1_B").innerHTML = "00 : 00 : 00";
    }

    setTimeout(updateClient1Data, 100);
  } catch (error) {
    console.error("Error fetching data:", error);
    setTimeout(updateClient1Data, 100);
  }
}

function updateStopwatchS1A() {
  let timeValue = document.getElementById("T1_A").innerHTML;
  let timeArray = timeValue.split(":");
  let seconds = parseInt(timeArray[2]) + 1;
  let minutes = parseInt(timeArray[1]);
  let hours = parseInt(timeArray[0]);

  if (seconds === 60) {
    seconds = 0;
    minutes += 1;
  }

  if (minutes === 60) {
    minutes = 0;
    hours += 1;
  }

  document.getElementById("T1_A").innerHTML =
    (hours < 10 ? "0" + hours : hours) + " : " +
    (minutes < 10 ? "0" + minutes : minutes) + " : " +
    (seconds < 10 ? "0" + seconds : seconds);

  setInterval(updateStopwatchS1A, 100000);
}

function updateStopwatchS1B() {
  let timeValue = document.getElementById("T1_B").innerHTML;
  let timeArray = timeValue.split(":");
  let seconds = parseInt(timeArray[2]) + 1;
  let minutes = parseInt(timeArray[1]);
  let hours = parseInt(timeArray[0]);

  if (seconds === 60) {
    seconds = 0;
    minutes += 1;
  }

  if (minutes === 60) {
    minutes = 0;
    hours += 1;
  }

  document.getElementById("T1_B").innerHTML =
    (hours < 10 ? "0" + hours : hours) + " : " +
    (minutes < 10 ? "0" + minutes : minutes) + " : " +
    (seconds < 10 ? "0" + seconds : seconds);

  setInterval(updateStopwatchS1B, 100000);
}

updateClient1Data();

/* <======================================Update Data Sensor Client 2=============================================> */
/* <======================================Update Data Sensor Client 2=============================================> */

let stopwatchIntervalS2A;
let stopwatchIntervalS2B;

async function updateClient2Data() {
  try {
    const response = await fetch("/updateClient2");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.json();
    document.getElementById("S2_A").innerHTML = data.reading_S2_A.toFixed(2) + " °C";
    document.getElementById("S2_B").innerHTML = data.reading_S2_B.toFixed(2) + " cm";
    document.getElementById("IP_2").innerHTML = data.ipAddress_2;
    document.getElementById("C2_A").innerHTML = '<strong>' + data.status_1 + '</strong>';
    document.getElementById("C2_B").innerHTML = '<strong>' + data.status_2 + '</strong>';

    if (data.reading_S2_A >= 40) {
      updateStopwatchS2A();
    } else {
      document.getElementById("T2_A").innerHTML = "00 : 00 : 00";
    }

    if (data.reading_S2_B <= 10) {
      updateStopwatchS2B();
    } else {
      document.getElementById("T2_B").innerHTML = "00 : 00 : 00";
    }

    setTimeout(updateClient2Data, 100);
  } catch (error) {
    console.error("Error fetching data:", error);
    setTimeout(updateClient2Data, 100);
  }
}

function updateStopwatchS2A() {
  let timeValue = document.getElementById("T2_A").innerHTML;
  let timeArray = timeValue.split(":");
  let seconds = parseInt(timeArray[2]) + 1;
  let minutes = parseInt(timeArray[1]);
  let hours = parseInt(timeArray[0]);

  if (seconds === 60) {
    seconds = 0;
    minutes += 1;
  }

  if (minutes === 60) {
    minutes = 0;
    hours += 1;
  }

  document.getElementById("T2_A").innerHTML =
    (hours < 10 ? "0" + hours : hours) + " : " +
    (minutes < 10 ? "0" + minutes : minutes) + " : " +
    (seconds < 10 ? "0" + seconds : seconds);

  setInterval(updateStopwatchS2A, 100000);
}

function updateStopwatchS2B() {
  let timeValue = document.getElementById("T2_B").innerHTML;
  let timeArray = timeValue.split(":");
  let seconds = parseInt(timeArray[2]) + 1;
  let minutes = parseInt(timeArray[1]);
  let hours = parseInt(timeArray[0]);

  if (seconds === 60) {
    seconds = 0;
    minutes += 1;
  }

  if (minutes === 60) {
    minutes = 0;
    hours += 1;
  }

  document.getElementById("T2_B").innerHTML =
    (hours < 10 ? "0" + hours : hours) + " : " +
    (minutes < 10 ? "0" + minutes : minutes) + " : " +
    (seconds < 10 ? "0" + seconds : seconds);

  setInterval(updateStopwatchS2B, 100000);
}

updateClient2Data();

/* <======================================Update Data Sensor Client 3=============================================> */
/* <======================================Update Data Sensor Client 3=============================================> */

let stopwatchIntervalS3A;
let stopwatchIntervalS3B;

async function updateClient3Data() {
  try {
    const response = await fetch("/updateClient3");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.json();
    document.getElementById("S3_A").innerHTML = data.reading_S3_A.toFixed(2) + " Amp";
    document.getElementById("S3_B").innerHTML = data.reading_S3_B.toFixed(2) + " Volt";
    document.getElementById("S3_C").innerHTML = data.reading_S3_C.toFixed(2) + " Watt";
    document.getElementById("S3_D").innerHTML = data.reading_S3_D.toFixed(2) + " KWh";
    document.getElementById("IP_3").innerHTML = data.ipAddress_3;
    document.getElementById("C3_A").innerHTML = '<strong>' + data.status_1 + '</strong>';
    document.getElementById("C3_B").innerHTML = '<strong>' + data.status_2 + '</strong>';

    // Update Stopwatch for T3_A
    if (data.reading_S3_A > 0) {
      updateStopwatchS3A();
    } else {
      clearInterval(stopwatchIntervalS3A);
      document.getElementById("T3_A").innerHTML = "00 : 00 : 00";
    }

    // Update Stopwatch for T3_B
    if (data.reading_S3_B >= 220) {
      updateStopwatchS3B();
    } else {
      clearInterval(stopwatchIntervalS3B);
      document.getElementById("T3_B").innerHTML = "00 : 00 : 00";
    }

    setTimeout(updateClient3Data, 100);
  } catch (error) {
    console.error("Error fetching data:", error);
    setTimeout(updateClient3Data, 100);
  }
}

function updateStopwatchS3A() {
  stopwatchIntervalS3A = setInterval(() => {
    let timeValue = document.getElementById("T3_A").innerHTML;
    let timeArray = timeValue.split(":");
    let seconds = parseInt(timeArray[2]) + 1;
    let minutes = parseInt(timeArray[1]);
    let hours = parseInt(timeArray[0]);

    if (seconds === 60) {
      seconds = 0;
      minutes += 1;
    }

    if (minutes === 60) {
      minutes = 0;
      hours += 1;
    }

    document.getElementById("T3_A").innerHTML =
      (hours < 10 ? "0" + hours : hours) + " : " +
      (minutes < 10 ? "0" + minutes : minutes) + " : " +
      (seconds < 10 ? "0" + seconds : seconds);
  }, 100000);
}

function updateStopwatchS3B() {
  stopwatchIntervalS3B = setInterval(() => {
    let timeValue = document.getElementById("T3_B").innerHTML;
    let timeArray = timeValue.split(":");
    let seconds = parseInt(timeArray[2]) + 1;
    let minutes = parseInt(timeArray[1]);
    let hours = parseInt(timeArray[0]);

    if (seconds === 60) {
      seconds = 0;
      minutes += 1;
    }

    if (minutes === 60) {
      minutes = 0;
      hours += 1;
    }

    document.getElementById("T3_B").innerHTML =
      (hours < 10 ? "0" + hours : hours) + " : " +
      (minutes < 10 ? "0" + minutes : minutes) + " : " +
      (seconds < 10 ? "0" + seconds : seconds);
  }, 100000);
}

updateClient3Data();


/* <==============================================Membuat Sidebar===================================================> */
/* <==============================================Membuat Sidebar===================================================> */

const menu = document.getElementById('menu-label');
const sidebar = document.getElementsByClassName('sidebar')[0];

menu.addEventListener('click', function() {
     sidebar.classList.toggle('hide');
})

/* <============================================Membuat Linechart===================================================> */
/* <============================================Membuat Linechart===================================================> */

// Fungsi untuk mengupdate data chart dan label
function updateChart(chart, firstDataArray, secondDataArray, thirdDataArray, label, isThirdDataArrayPresent) {
    if (chart.data.labels.length >= 30) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
        chart.data.datasets[1].data.shift();
        if (isThirdDataArrayPresent) {
            chart.data.datasets[2].data.shift();
        }
    }

    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(firstDataArray);
    chart.data.datasets[1].data.push(secondDataArray);
    if (isThirdDataArrayPresent) {
        chart.data.datasets[2].data.push(thirdDataArray);
    }
    chart.update();

    console.log("updateChart has been called!");
}

// Fungsi untuk membuat line chart
function createLineChart(chartId, firstLabel, secondLabel, thirdLabel) {
    const ctx = document.getElementById(chartId).getContext('2d');
    const datasets = [
        {
            label: firstLabel,
            data: [],
            borderColor: '#363062',
            backgroundColor: 'rgba(82, 114, 242, 0.2)',
            tension: 0.4,
            fill: true,
        },
        {
            label: secondLabel,
            data: [],
            borderColor: '#687EFF',
            backgroundColor: 'rgba(152, 228, 255, 0.2)',
            tension: 0.4,
            fill: true,
        }
    ];

    if (thirdLabel) {
        datasets.push({
            label: thirdLabel,
            data: [],
            borderColor: '#5050A0',
            backgroundColor: 'rgba(128, 128, 255, 0.2)',
            tension: 0.4,
            fill: true,
        });
    }

    const lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'category',
                    display: true,
                    grid: {
                        display: false,
                    },
                },
                y: {
                    display: true,
                    grid: {
                        display: true,
                    },
                },
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                },
            },
        },
    });

    return lineChart;
}

function startUpdatingChart() {
    const charts = [
        createLineChart('lineChart_1', 'Suhu Ruangan (°C)', 'Kelembapan Ruangan (% RH)'),
        createLineChart('lineChart_2', 'Suhu Air (°C)', 'Jarak (cm)'),
        createLineChart('lineChart_3', 'Arus Listrik (Amp)', 'Tegangan Listrik (Volt)', 'Daya (Watt)'),
    ];

    setInterval(async () => {
        const currentTime = moment().format('HH:mm');

        const clients = [
            { client: 'Client 1', getData_A: grafik_S1_A, getData_B: grafik_S1_B },
            { client: 'Client 2', getData_A: grafik_S2_A, getData_B: grafik_S2_B },
            { client: 'Client 3', getData_A: grafik_S3_A, getData_B: grafik_S3_B, getData_C: grafik_S3_C }
        ];

        const dataPromises = charts.map(async (chart, index) => {
            const client = clients[index];
            if (client.getData_C) {
                const [data1, data2, data3] = await Promise.all([
                    client.getData_A(),
                    client.getData_B(),
                    client.getData_C()
                ]);
                return [data1, data2, data3];
            } else {
                const [data1, data2] = await Promise.all([
                    client.getData_A(),
                    client.getData_B()
                ]);
                return [data1, data2, null];
            }
        });

        const chartData = await Promise.all(dataPromises);

        charts.forEach((chart, index) => {
            const [data1, data2, data3] = chartData[index];
            const isThirdDataArrayPresent = data3 !== null;
            updateChart(chart, data1, data2, isThirdDataArrayPresent ? data3 : [], currentTime, isThirdDataArrayPresent);
        });
    }, 60000);
}


/* <===========================================Update Chart Client==================================================> */

// CLIENT 1
async function grafik_S1_A() {
    const response = await fetch('/get_chart_data/1');
    const data = await response.json();
    return data.map(item => item.S1_A);
}

async function grafik_S1_B() {
    const response = await fetch('/get_chart_data/1');
    const data = await response.json();
    return data.map(item => item.S1_B);
}

/// CLIENT 2
async function grafik_S2_A() {
    const response = await fetch('/get_chart_data/2');
    const data = await response.json();
    return data.map(item => item.S2_A);
}

async function grafik_S2_B() {
    const response = await fetch('/get_chart_data/2');
    const data = await response.json();
    return data.map(item => item.S2_B);
}

/// CLIENT 3
async function grafik_S3_A() {
    const response = await fetch('/get_chart_data/3');
    const data = await response.json();
    return data.map(item => item.S3_A);
}

async function grafik_S3_B() {
    const response = await fetch('/get_chart_data/3');
    const data = await response.json();
    return data.map(item => item.S3_B);
}

async function grafik_S3_C() {
    const response = await fetch('/get_chart_data/3');
    const data = await response.json();
    return data.map(item => item.S3_C);
}

// Memulai pembaruan line chart
startUpdatingChart();
