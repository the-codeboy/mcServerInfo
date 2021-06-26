import json
import os
import time

from discord_webhook import DiscordWebhook
from mcstatus import MinecraftServer

file_name = "data.json"

global server
global webhook_url

if os.path.exists(file_name):
    with open(file_name) as json_file:
        data = json.load(json_file)
        if "serverName" in data and "url" in data:
            server_name = data["serverName"]
            webhook_url = data["url"]
else:
    server_name = input("please enter the ip of the server")
    webhook_url = input("please enter the url of the discord webhook")
    data = {"serverName": server_name, "url": webhook_url}
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)
print(F"server ip: {server_name}")
print(F"webhook url: {webhook_url}")
server = MinecraftServer.lookup(server_name)

players_online = 0
player_sample = []
online = False
try:
    status = server.status()
    players_online = status.players.online
    player_sample = status.players.sample
    online = True
    print(f"player online: {players_online}")
except Exception:
    print("can not connect to server")


def send_webhook(text, player=None):
    if player is None:
        print(text)
        webhook = DiscordWebhook(url=webhook_url, content=text, rate_limit_retry=True)
    else:
        print(player.name + text)
        webhook = DiscordWebhook(url=webhook_url, content=text, rate_limit_retry=True, username=player.name,
                                 avatar_url="https://minotar.net/bust/" + player.id)
    webhook.execute()


def send_player_join_or_leave(player, message):
    send_webhook(message, player=player)


def send_player_change(new_players):
    global player_sample
    if new_players is not None:
        for player in new_players:
            player_online = False
            if player_sample is not None:
                for oldPlayer in player_sample:
                    if oldPlayer.id == player.id:
                        player_online = True
            if not player_online:
                send_player_join_or_leave(player, " has joined the server")
    if player_sample is not None:
        for player in player_sample:
            player_online = False
            if new_players is not None:
                for newPlayer in new_players:
                    if newPlayer.id == player.id:
                        player_online = True
            if not player_online:
                send_player_join_or_leave(player, " has left the server")
    player_sample = new_players


while True:
    try:
        status = server.status()
        players = status.players.online
        players_online = players
        send_player_change(status.players.sample)
        if players != players_online:
            print(f"player online: {players}")
        # if not online:
        #  send_webhook("server online again")
        time.sleep(5)
        online = True
    except Exception:
        print("connecting failed")
        # if online:
        #  send_webhook("server offline")
        online = False
        time.sleep(5)
