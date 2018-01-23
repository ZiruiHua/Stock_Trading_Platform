from channels import route
from apis.consumers import connect_trade_stream, disconnect_trade_stream

# The channel routing defines what channels get handled by what consumers,
# including optional matching on message attributes. WebSocket messages of all
# types have a 'path' attribute, so we're using that to route the socket.
channel_routing = [
    # called when incoming WebSockets connect
    route("websocket.connect", connect_trade_stream, path=r'^/data-api/trade-stream/$'),
    # called when the client closes the socket
    route("websocket.disconnect", disconnect_trade_stream, path=r'^/data-api/trade-stream/$')
]
