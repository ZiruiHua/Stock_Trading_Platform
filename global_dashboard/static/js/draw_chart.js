$(document).ready(function () {
    // date selector
    $.getJSON(
        "/global/get-recommendation/",
        function (data) {
            if (data) {
                for (var i = 0; i < data.symbols.length; i += 1) {
                    var s = data.symbols[i];
                    $.getJSON(
                        "/global/get-history-price/" + s,
                        function (data) {
                            if (data) {
                                drawLineChart(data.p, data.d, data.s);
                            }
                        }
                    );
                }
            }
        }
    );
});

function drawLineChart(prices, dates, symbol) {
    'use strict';
    // Main Template Color
    var brandPrimary = '#33b35a';
    var LINECHART = $('#chart-' + symbol);
    var myLineChart = new Chart(LINECHART, {
        type: 'line',
        options: {
            legend: {
                display: false
            }
        },
        data: {
            labels: dates,
            datasets: [
                {
                    label: "My First dataset",
                    fill: false,
                    lineTension: 0.3,
                    backgroundColor: "rgba(77, 193, 75, 0.4)",
                    borderColor: brandPrimary,
                    borderCapStyle: 'butt',
                    borderDash: [],
                    borderDashOffset: 0.0,
                    borderJoinStyle: 'miter',
                    borderWidth: 1,
                    pointBorderColor: brandPrimary,
                    pointBackgroundColor: "#fff",
                    pointBorderWidth: 1,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: brandPrimary,
                    pointHoverBorderColor: "rgba(220,220,220,1)",
                    pointHoverBorderWidth: 2,
                    pointRadius: 1,
                    pointHitRadius: 0,
                    data: prices,
                    spanGaps: false
                }
            ]
        }
    });
}