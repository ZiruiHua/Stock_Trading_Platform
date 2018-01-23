/*global $, document, Chart, LINECHART, data, options, window*/
$(document).ready(function () {
    // date selector
    $.getJSON(
        "/personal/get-holdings/",
        function (data) {
            if (data) {
                // drawHoldingTable(data.symbol_list, data.share_list);
                drawPieChart(data.symbol_list, data.value_list);
                get_total_asset(data.total_asset);
                draw_indicator(data.symbol_list, data.indicator_list);
            } else {
                // if the user doesn't have any holdings
                console.log("No holdings");
                get_total_asset(data.total_asset);
            }
        }
    );
    $.getJSON(
        "/personal/get-transactions/",
        function (data) {
            if (data) {
                get_transactions(data);
            }
        }
    );
    $.getJSON(
        "/personal/get-trend/",
        function (data) {
            if (data) {
                drawLineChart(data.dates, data.assets);
            }
        }
    );
    $('#btn_date').click(function () {
        var date = $('#datepicker').val();
        $.getJSON(
            "get-transactions-by-date/" + date,
            function (date) {
                $('#transactions').empty();
                get_transactions(date)
            }
        )
    })
});

function drawLineChart(dates, assets) {
    'use strict';

    // Main Template Color
    var brandPrimary = '#33b35a';
    var LINECHART = $('#lineChart');
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
                    fill: true,
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
                    data: assets,
                    spanGaps: false
                }
            ]
        }
    });
}

function drawPieChart(symbols, values) {
    'use strict';
    // Main Template Color
    var brandPrimary = '#33b35a';
    var PIECHART = $('#pieChart');
    var myPieChart = new Chart(PIECHART, {
        type: 'doughnut',
        data: {
            labels: symbols,
            datasets: [
                {
                    data: values,
                    borderWidth: [1, 1, 1],
                    backgroundColor: [
                        brandPrimary,
                        "rgba(75,192,192,1)",
                        "#FFCE56"
                    ],
                    hoverBackgroundColor: [
                        brandPrimary,
                        "rgba(75,192,192,1)",
                        "#FFCE56"
                    ]
                }]
        }
    });
}

function drawHoldingTable(symbols, shares) {
    for (var i = 0; i < symbols.length; i += 1) {
        $("#tbody").prepend(" <tr>\n" +
            "      <td>" + symbols[i] + "</td>\n" +
            "      <td>" + shares[i] + "</td>\n" +
            "    </tr>"
        );
    }
}

function get_transactions(data) {
    if (data.length > 0) {
        for (var i = 0; i < data.length; i += 1) {
            var name = data[i]['fields']['stock'];
            var type = data[i]['fields']['type'];
            var price = data[i]['fields']['price'];
            var shares = data[i]['fields']['shares'];
            var date = data[i]['fields']['date'].substr(0, 10);
            if (type) {
                $('#transactions').append(
                    "<li class=\"d-flex justify-content-between\">\n" +
                    "                                        <div class=\"left-col d-flex\">\n" +
                    "                                                <div class=\"icon\"><i class=\"fa fa-plus-square\" aria-hidden=\"true\"></i>\n" +
                    "                                                </div>\n" +
                    "\n" +
                    "                                            <div class=\"title\"><strong>" + name + "</strong>\n" +
                    "                                                <p>" + price + " per share, " + shares + " shares in total</p>\n" +
                    "                                            </div>\n" +
                    "                                        </div>\n" +
                    "                                        <div class=\"right-col text-right\">\n" +
                    "                                            <div class=\"month\">" + date + "<span\n" +
                    "                                        </div>\n" +
                    "                                    </li>"
                )
            } else {
                $('#transactions').append(
                    "<li class=\"d-flex justify-content-between\">\n" +
                    "                                        <div class=\"left-col d-flex\">\n" +
                    "                                                <div class=\"icon\"><i class=\"fa fa-minus-square\" aria-hidden=\"true\"></i>\n" +
                    "                                                </div>\n" +
                    "\n" +
                    "                                            <div class=\"title\"><strong>" + name + "</strong>\n" +
                    "                                                <p>" + price + " per share, " + shares + " shares in total</p>\n" +
                    "                                            </div>\n" +
                    "                                        </div>\n" +
                    "                                        <div class=\"right-col text-right\">\n" +
                    "                                            <div class=\"month\">" + date + "<span\n" +
                    "                                        </div>\n" +
                    "                                    </li>"
                )
            }

        }

    }
}

function get_total_asset(data) {
    if (data) {
        var myDiv = document.getElementById("total-asset");
        myDiv.innerHTML = "$" + data;
    }
}

function draw_indicator(symbols, indicators) {
    if (symbols && indicators) {
        for (var i = 0; i < symbols.length; i += 1) {
            var id = "tr-" + symbols[i];
            tr = $('#' + id);
            if (indicators[i] > 0) {
                tr.append("<td><i class=\"fa fa-arrow-up\" aria-hidden=\"true\"></i>\n</td>");
            } else if (indicators[i] < 0) {
                tr.append("<td><i class=\"fa fa-arrow-down\" aria-hidden=\"true\"></i>\n</td>");
            } else {
                tr.append("<td><i class=\"fa fa-arrow-right\" aria-hidden=\"true\"></i>\n</td>");
            }
        }
    }

}
