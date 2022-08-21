// Chart IDs
let gChartConsumption = null
let gChartUsage = null
let gChartDashboard = null
let gChartHistoryDetails = null

// Colors
const COLOR_PRODUCTION_FED_IN = "#2980b9";
const COLOR_PRODUCTION_SELF_CONSUMED = "#27ae60";

const COLOR_CONSUMED_FROM_GRID = "#c0392b";
const COLOR_CONSUMED_FROM_PV = "#8e44ad";

const COLOR_PRODUCED = "#f1c40f";
const COLOR_CONSUMED = "#d35400";


// Creates a chart showing the consumption distribution
function createConsumptionChart(canvasId, gridPercentage, pvPercentage) {
    var xValues = [getChartString("chart_from_grid"), getChartString("chart_from_pv")];
    var yValues = [gridPercentage, pvPercentage];
    var barColors = [
        COLOR_CONSUMED_FROM_GRID,
        COLOR_CONSUMED_FROM_PV
    ];
    if (gChartConsumption != null) gChartConsumption.destroy();
    gChartConsumption = new Chart(canvasId, {
        type: "doughnut",
        data: {
            labels: xValues,
            datasets: [{
                backgroundColor: barColors,
                data: yValues
            }]
        },
        options: {
            rotation: 180,
            maintainAspectRatio: false,
            title: {
                display: false
            },
            plugins: {
                labels: {
                    // render 'label', 'value', 'percentage', 'image' or custom function, default is 'percentage'
                    render: 'percentage',
                    fontSize: 16,
                    fontColor: '#ffffff',
                    textShadow: true
                }
            }
        }
    });
}

// Creates a chart showing the power consumption distribution
function createUsageChart(canvasId, fedInPercentage, selfPercentage) {
    var xValues = [getChartString("chart_fed_in"), getChartString("chart_self_consumed")];
    var yValues = [fedInPercentage, selfPercentage];
    var barColors = [
        COLOR_PRODUCTION_FED_IN,
        COLOR_PRODUCTION_SELF_CONSUMED
    ];
    if (gChartUsage != null) gChartUsage.destroy();
    gChartUsage = new Chart(canvasId, {
        type: "doughnut",
        data: {
            labels: xValues,
            datasets: [{
                backgroundColor: barColors,
                data: yValues
            }]
        },
        options: {
            rotation: 180,
            maintainAspectRatio: false,
            title: {
                display: false
            },
            plugins: {
                labels: {
                    // render 'label', 'value', 'percentage', 'image' or custom function, default is 'percentage'
                    render: 'percentage',
                    fontSize: 16,
                    fontColor: '#ffffff',
                    textShadow: true
                }
            }
        }
    });
}

// Creates a chart for the dashboard view
function createDashboardChart(canvasId, data) {

    const labels = [];
    const chart_data = {
        labels: labels,
        datasets: [{
            label: getChartString("chart_produced_kwh"),
            data: [],
            fill: false,
            borderColor: COLOR_PRODUCTION_SELF_CONSUMED,
            backgroundColor: COLOR_PRODUCTION_SELF_CONSUMED,
            borderWidth: 2
        },
        {
            label: getChartString("chart_consumed_kwh"),
            data: [],
            fill: false,
            borderColor: COLOR_CONSUMED_FROM_GRID,
            backgroundColor: COLOR_CONSUMED_FROM_GRID,
            borderWidth: 2
        },
        {
            label: getChartString("chart_fed_in_kwh"),
            data: [],
            fill: false,
            borderColor: COLOR_PRODUCTION_FED_IN,
            backgroundColor: COLOR_PRODUCTION_FED_IN,
            borderWidth: 2
        }]
    };

    for (index = 0; index < data.length; index++) {
        labels.push(data[index][1]); // Element 1 = time
        chart_data.datasets[0].data.push(data[index][2]);
        chart_data.datasets[1].data.push(data[index][3]);
        chart_data.datasets[2].data.push(data[index][4]);
    }

    if (gChartDashboard != null) gChartDashboard.destroy();
    gChartDashboard = new Chart(canvasId, {
        type: "line",
        responsive: true,
        data: chart_data,
        options: {
            maintainAspectRatio: false,
            title: {
                display: false
            },
            elements: {
                point: {
                    radius: 0
                }
            }
        }
    });
}

// Creates a chart showing history details
function createHistoryDetailsChart(canvasId, data) {

    const labels = [];
    const chart_data = {
        labels: labels,
        datasets: [{
            label: getChartString("chart_produced_self_kwh"),
            data: [],
            borderColor: COLOR_PRODUCTION_SELF_CONSUMED,
            backgroundColor: COLOR_PRODUCTION_SELF_CONSUMED,
            borderWidth: 2,
            stack: 'Stack 0'
        },
        {
            label: getChartString("chart_produced_grid_kwh"),
            data: [],
            borderColor: COLOR_PRODUCTION_FED_IN,
            backgroundColor: COLOR_PRODUCTION_FED_IN,
            borderWidth: 2,
            stack: 'Stack 0'
        },
        {
            label: getChartString("chart_consumed_pv_kwh"),
            data: [],
            borderColor: COLOR_CONSUMED_FROM_PV,
            backgroundColor: COLOR_CONSUMED_FROM_PV,
            borderWidth: 2,
            stack: 'Stack 1'
        },
        {
            label: getChartString("chart_consumed_grid_kwh"),
            data: [],
            borderColor: COLOR_CONSUMED_FROM_GRID,
            backgroundColor: COLOR_CONSUMED_FROM_GRID,
            borderWidth: 2,
            stack: 'Stack 1'
        }]
    };

    for (index = 0; index < data.length; index++) {
        labels.push(data[index]["date"]); // Element 1 = time
        chart_data.datasets[0].data.push(data[index]["produced_self"]);
        chart_data.datasets[1].data.push(data[index]["produced_feed_in"]);
        chart_data.datasets[2].data.push(data[index]["consumed_from_pv"]);
        chart_data.datasets[3].data.push(data[index]["consumed_from_grid"]);
    }

    if (gChartHistoryDetails != null) gChartHistoryDetails.destroy();
    gChartHistoryDetails = new Chart(canvasId, {
        type: "bar",
        responsive: true,
        data: chart_data,
        options: {
            maintainAspectRatio: false,
            title: {
                display: false
            },
            plugins: {
                labels: false
            },
            interaction: {
                intersect: false,
            },
            scales: {
                x: {
                    stacked: true,
                },
                y: {
                    stacked: true
                }
            }
        }
    });
}