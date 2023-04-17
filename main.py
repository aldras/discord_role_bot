import discord
import os
import requests
import json
import random

client = discord.Client(intents=discord.Intents.default())

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]

starter_encouragements = [
  "Cheer up!", "Hang in there.", "You are a great person / bot!"
]

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]["q"] + " -" + json_data[0]["a"]
  return (quote)


def update_encouragements(encouraging_message):
  if "encouragements" in db.keys():
    encouragements = db["encouragements"]
    encouragements.append(encouraging_message)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [encouraging_message]


def delete_encouragment(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
  db["encouragements"] = encouragements


@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))
  channel = client.get_channel(1088833580832145500)
  text = "React to me!"
  message = await channel.send(text)
  await message.add_reaction('🏃')

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if msg.startswith("$inspire"):
    quote = get_quote()
    await message.channel.send(quote)

  if db["responding"]:
    options = starter_encouragements
    if "encouragements" in db.keys():
      options = options + db["encouragements"]

    if any(word in msg for word in sad_words):
      await message.channel.send(random.choice(options))

  if msg.startswith("$new"):
    encouraging_message = msg.split("$new ", 1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("New encouraging message added.")

  if msg.startswith("$del"):
    encouragements = []
    if "encouragements" in db.keys():
      index = int(msg.split("$del", 1)[1])
      delete_encouragment(index)
      encouragements = db["encouragements"]
    await message.channel.send(encouragements)

  if msg.startswith("$list"):
    encouragements = []
    if "encouragements" in db.keys():
      encouragements = db["encouragements"]
    await message.channel.send(encouragements)

  if msg.startswith("$responding"):
    value = msg.split("$responding ", 1)[1]

    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on.")
    else:
      db["responding"] = False
      await message.channel.send("Responding is off.")

@client.event
async def on_reaction_add(reaction, user):
    print("on_reaction_add called")
    channel = client.get_channel(1088833580832145500)
    if reaction.message.channel.id != channel.id:
        return
    if user.id == client.user.id:
      return
    if reaction.emoji == "🏃":
      print("Role add request from {0.user}".format(client))
      role = discord.utils.get(user.guild.roles, name="Administrator")
      await user.add_roles(role)

@client.event
async def on_reaction_remove(reaction, user):
    print("on_reaction_remove called")
    channel = client.get_channel(1088833580832145500)
    if reaction.message.channel.id != channel.id:
      return
    if reaction.emoji == "🏃":
      print("Role remove request from {0.user}".format(client))
      role = discord.utils.get(user.guild.roles, name="Administrator")
      await user.remove_roles(role)

@client.event
async def on_raw_reaction_add(payload):
    print("on_raw_reaction_add called")

@client.event
async def on_raw_reaction_remove(payload):
    print("on_raw_reaction_remove called")
    message_id = payload.message_id

    #get the server name from the payload
    guild = client.get_guild(int(payload.guild_id))
    channel = client.get_channel(int(payload.channel_id))

  
    channel_bot = client.get_channel(1088833580832145500)
    if channel.id != channel_bot.id:
      print("Channel id mis-match")
      return
    if payload.user_id == client.user.id:
      return
    if payload.emoji.name == "🏃":
      print("Role remove request from {0.user}".format(client))
      role = discord.utils.get(guild.roles, name="Administrator")

      if role is not None:
        # payload.member is not availible for REACTION_REMOVE event type
        member = await guild.fetch_member(payload.user_id)
        if member is not None:
          await member.remove_roles(role)
          print("done")
        else:
          print("member not found")
      else:
        print("role not found.")
    else:
      print("emoji does not match")
    
client.run(os.getenv("TOKEN"))
