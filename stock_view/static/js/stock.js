

// get the stock symbol; notice it can be an empty string
var stock_symbol = document.getElementById("stock_symbol").getAttribute("data-symbol").toUpperCase();

function buyStock() {
    var input = $("#buy-amount");
    var amount = input.val();
    $.post("/stock/buy/", {"amount": amount, "stock_symbol": stock_symbol})
        .done(function() {
            input.val("");  // clear user input
            alert("Bought successful!");
            var update = parseInt(amount);
            updateMax(update);
            updateCurrentHold(update);
            updateBuyingPower();
        })
        .fail(function(xhr, status, error) {  // xhr refers to XMLHttpRequest
            alert("Bought failed!");
            console.log(status);
            console.log(error);
            console.log(xhr)
        });
}

function sellStock() {
    var input = $("#sell-amount");
    var amount = input.val();
    $.post("/stock/sell/", {"amount": amount, "stock_symbol": stock_symbol})
        .done(function() {
            input.val("");  // clear user input
            alert("Sold successful!");
            var update = - parseInt(amount);
            updateMax(update);
            updateCurrentHold(update);
            updateBuyingPower();
        })
        .fail(function(xhr, status, error) {  // xhr refers to XMLHttpRequest
            alert("Sold failed!");
            console.log(status);
            console.log(error);
        });
}

function updateCurrentPrice() {
    $.get("/data-api/get-current-price/" + stock_symbol)
        .done(function (data){
            if (!isNaN(data)) {  // if it's not an error string
                $("#stock_price").html(data);
            }
        });
}

// Author: ZJ

// Get company description
function loadDes() {
    var get_url = "/data-api/get-company-info/" + stock_symbol;
    $.ajax({
        url: get_url,
        type: 'GET',
        success: function (data) {
            console.log("In loadDes");
            //var company_description = $('#stock-description');
            var company_description = document.getElementById('stock-description');
            company_description.innerHTML = data + '...';
        }
    });

}

// Update max available
function updateMax(update) {
    console.log("In updateMax");
    //var max = $('#max-available');
    var max = document.getElementById('max-available');
    var new_max = parseInt(max.innerHTML) - update;
    max.innerHTML = new_max;
}

// Update current stock holdings
function updateCurrentHold(update) {
    console.log("In updateCurrentHold");
    //var curr = $("#current-share");
    var curr = document.getElementById('current-share');
    var new_curr = parseInt(curr.innerHTML) + update;
    curr.innerHTML = new_curr;
}

function updateBuyingPower() {
    console.log("In updateBuyingPower");
    //var buy_power = $("#buying-power");
    var buy_power = document.getElementById('buying-power');
    var get_url = "/stock/buying-power/";
    $.ajax({
        url: get_url,
        type: 'GET',
        success: function (data) {
            buy_power.innerHTML = '$' + data;
        }
    })

}

function subscribe() {
    var watch = document.getElementById('watch-stock');
    console.log(watch);
    var form_data = { "stock_symbol": stock_symbol };
    if (watch.innerHTML === 'Watch') {
        var post_url = "/stock/subscribe/";
    } else {
        var post_url = "/stock/unsubscribe/";
    }
    $.ajax({
        url: post_url,
        type: 'POST',
        data: form_data,
        success: function (data) {
            if (watch.innerHTML === 'Watch') {
                watch.innerHTML = "Unwatch";
            } else {
                watch.innerHTML = "Watch";
            }
        }
    })
}
// draw stock price line chart
function drawLineChart(prices, dates) {
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
/**
 * Initializations after the page is loaded.
 */
$(document).ready(function() {
    // add event-handlers
    $('#buy-stock').click(buyStock);
    $('#sell-stock').click(sellStock);
    $('#watch-stock').click(subscribe);

    loadDes();
    updateCurrentPrice();  // update the latest closing price of this stock

    // periodically update the latest price indicator every 1 minute (same as the API data update rate)
    window.setInterval(function() {
        updateCurrentPrice();
        }, 60000);

    $.getJSON(
        "/global/get-history-price/" + stock_symbol,
        function (data) {
            if (data) {
                drawLineChart(data.p, data.d, data.s);
            }
        }
    );
    // -- pass CSRF token in every POST request using jQuery ----------------------
    // source: https://docs.djangoproject.com/en/1.11/ref/csrf/#ajax

    // acquire the token
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    // then set the token on the AJAX request
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});
