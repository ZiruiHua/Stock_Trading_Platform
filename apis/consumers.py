"""
Defines how consumers (those who listen to the channel) interacts with the
trade stream channel.

Author: Stephen Xie
"""
from channels import Group


def connect_trade_stream(message):
    """
    When the user opens a WebSocket to a leaderboard stream, adds them to the
    group for that stream so they receive new trade notifications.

    The notifications are actually sent in the Trade model on save.
    """
    # accept the incoming connection
    message.reply_channel.send({'accept': True})
    # add the reply_channel of this connection to the trade_stream group,
    # so that it can receive updates sent to the group (all group members
    # will be able to get the same message)
    Group('trade_stream').add(message.reply_channel)


def disconnect_trade_stream(message):
    """
    Removes the user from the trade_stream group when they disconnect.

    Channels will auto-cleanup eventually, but it can take a while, and having old
    entries cluttering up the group will reduce performance.
    """
    Group('trade_stream').discard(message.reply_channel)
