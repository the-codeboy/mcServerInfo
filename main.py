import os

from mcstatus import MinecraftServer
import time
from discord_webhook import DiscordWebhook
import json

fileName = "data.json"

global server
global webhookUrl

if os.path.exists(fileName):
    with open(fileName) as json_file:
        data = json.load(json_file)
        if "serverName" in data and "url" in data:
            serverName = data["serverName"]
            webhookUrl = data["url"]
else:
    serverName = input("please enter the ip of the server")
    webhookUrl = input("please enter the url of the discord webhook")
    data = {"serverName": serverName, "url": webhookUrl}
    with open(fileName, 'w') as outfile:
        json.dump(data, outfile)
print(F"server ip: {serverName}")
print(F"webhook url: {webhookUrl}")
server = MinecraftServer.lookup(serverName)

playersOnline = 0
playerSample = []
online = False
try:
    status = server.status()
    playersOnline = status.players.online
    playerSample = status.players.sample
    online = True
    print(f"player online: {playersOnline}")
except:
    print("can not connect to server")


def sendWebhook(text, player=None):
    if player is None:
        print(text)
        webhook = DiscordWebhook(url=webhookUrl, content=text, rate_limit_retry=True)
    else:
        print(player.name + text)
        webhook = DiscordWebhook(url=webhookUrl, content=text, rate_limit_retry=True, username=player.name,
                                 avatar_url="https://minotar.net/bust/" + player.id)
    webhook.execute()


def sendPlayerJoinOrLeave(player, message):
    sendWebhook(message, player=player)


def sendPlayerChange(newPlayers):
    global playerSample
    if newPlayers is not None:
        for player in newPlayers:
            online = False
            if playerSample is not None:
                for oldPlayer in playerSample:
                    if oldPlayer.id == player.id:
                        online = True
        if not online:
            sendPlayerJoinOrLeave(player, " has joined the server")
    if playerSample is not None:
        for player in playerSample:
            online = False
            if newPlayers is not None:
                for newPlayer in newPlayers:
                    if newPlayer.id == player.id:
                        online = True
            if not online:
                sendPlayerJoinOrLeave(player, " has left the server")
    playerSample = newPlayers

while True:
    try:
        status = server.status()
        players = status.players.online
        playersOnline = players
        sendPlayerChange(status.players.sample)
        if players != playersOnline:
            print(f"player online: {players}")
        # if not online:
        #  sendWebhook("server online again")
        time.sleep(5)
        online = True
    except:
        print("connecting failed")
        # if online:
        #  sendWebhook("server offline")
        online = False
        time.sleep(5)
