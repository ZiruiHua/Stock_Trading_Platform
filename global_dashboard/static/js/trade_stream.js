/**
 * This defines the behavior of a consumer that listens to the trade_stream channel group.
 * Whenever there's a new trade record in the channel group, this consumer gets the message
 * and inserts it to the top of the list.
 *
 */
$(function() {
    var ws_path = "/data-api/trade-stream/";
    console.log("Connecting to " + ws_path);
    // use the WebSocket wrapper provided by Django Channels to simplify the calls
    var webSocketBridge = new channels.WebSocketBridge();
    webSocketBridge.connect(ws_path);  // open a WebSocket connection to the backend
    webSocketBridge.listen(function(data) {  // listen for update data
        console.log("Got new records: " + data);
        // Create the inner content of the record row
        var content = data.html;
        // See if there's a div to replace it in, or if we should add a new one
        var existing = $("tr[data-record-id=" + data.id + "]");
        if (existing.length) {
            existing.html(content);
        } else {
            var newRow = $("<tr data-record-id='" + data.id + "'>" + content + "</tr>");
            $("#trade-stream").prepend(newRow);
        }
    });

    // debugging info
    webSocketBridge.socket.onopen = function() { console.log("Connected to notification socket"); }
    webSocketBridge.socket.onclose = function() { console.log("Disconnected to notification socket"); }
});
