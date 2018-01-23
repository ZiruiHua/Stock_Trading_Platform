// run update function on first refresh

// update function which retrieves 50 stocks
function updateList(filter) {
    var page = $("#page-no").html();
    var get_url = "/search/list/" + (parseInt(page) - 1);
    if (filter) {
        var filter_cat = $("#select-filter option:selected").text().toLowerCase();
        var filter_terms = $("#filter-terms").val().toString().split(" ").join("+");
        var get_url = "/search/filter/" + (parseInt(page) - 1) + "/" + filter_cat + "/" + filter_terms;
    }
    var stock_list = $("#stock-list");
    stock_list.empty();

    $.ajax({
        url: get_url,
        type: 'GET',
        success: function (data) {
            $.each(data.stocks, function () {
                var row_id = this.symbol + "-row";
                var stock_link = location.origin + "/stock/" + this.symbol;
                var stock_row = `<tr id=${row_id}><td><a href="${stock_link}">${this.symbol}</a></td><td><a href="${stock_link}">${this.name}</a></td><td>${this.sector}</td><td class="stock-price" id="${this.symbol}">$</td></tr>`;
                stock_list.append(stock_row);
            });         
        },
    }).done(function () {
        setInterval(refreshPrice(), 60000);
    });

}

// page change functions
function nextPage() {
    var next_page = parseInt($("#page-no").html()) + 1;
    $("#page-no").text(next_page);
    updateList();
    modifyPagination(next_page);
}

function prevPage() {
    var prev_page = parseInt($("#page-no").html()) - 1;
    $("#page-no").text(prev_page);
    updateList();
    modifyPagination(prev_page);
}

function setPage(pn) {
    $("#page-no").text(pn);
    updateList();
    modifyPagination(pn);
}

// modify pagination to reflect current page
function modifyPagination(pn) {
    var page_list = $("#pages");
    page_list.html("");
    var disabled = pn == 1 ? "disabled" : "";
    var prev = `<li class="page-item ${disabled}">
        <a class="page-link" href="#" aria-label="Previous" onclick="prevPage()">
        <span aria-hidden="true">&laquo;</span>
        <span class="sr-only">Previous</span>
        </a>
        </li>`;
    console.log(prev);

    var next = `<li class="page-item">
        <a class="page-link" href="#" aria-label="Next" onclick="nextPage()">
        <span aria-hidden="true">&raquo;</span>
        <span class="sr-only">Next</span>
        </a>
        </li>`;

    var pages = '';
    if (pn > 2) {
        pages += '<li class="page-item"><a class="page-link" href="#">...</a></li>';
    }
    for (i = pn - 1; i <= pn + 1; i++) {
        if (i > 0) {
            var active = i == pn ? "active" : "";
            pages += `<li class="page-item ${active}"><a class="page-link" href="#" onclick="setPage(${i})">${i}</a></li>`;
        }
    }
    pages += '<li class="page-item"><a class="page-link" href="#">...</a></li>';
    page_list.append(prev + pages + next);
}

// refresh stock prices every minute
function refreshPrice() {
    $(".stock-price").each(function (i, stock) {
        var get_url = "/search/price/" + stock.id;
        $.ajax({
            url: get_url,
            type: 'GET',
            success: function (data) {
                stock.innerHTML = "$" + data;
            },
            error: function (data) {
                stock.innerHTML = "NA"; // TODO: delete rows
                var row_id = stock.id + "-row";
                $(row_id).remove();
            }
        });

    });
}

$(document).ready(function () {
    updateList(false);
});
