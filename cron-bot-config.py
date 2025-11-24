import bot_backbone
from bot_backbone import client, servers_object, file_locale, bot_setup

debug = False
debug_channel = 0
command_prefix = '%'

@client.event
async def on_ready():
  if servers_object != {}:
    print("Config mode enabled.")
    #for value in servers_object.values():
    #  await client.get_channel(value).send("That was a good nap. Config mode active. Lemme know what you need, boss.")

@client.event
async def on_message(message):
  global debug
  global debug_channel
  global command_prefix
  global isAdmin
  global servers_object
  
  isAdmin = message.author.guild_permissions.administrator

  if (not (message.author == client.user)) & (isAdmin) & (bot_backbone.command_check(message,command_prefix)):
    if (debug) & (message.channel.id != debug_channel):
      await message.channel.send("Sorry, I'm in debug mode for a different location. I'm locked in on that channel and won't accept any other commands at this time. Thank you.")
    
    elif bot_backbone.command_check(message,command_prefix+'debug'):
      debug = not debug
      debug_channel = message.channel.id
      if debug: await message.channel.send("Got it. Activating debug mode. I'll only be looking at messages in this channel now.")
      else: await message.channel.send("Got it. Deactivating debug mode. Listening on all open channels.")
    
    elif bot_backbone.command_check(message,command_prefix+'quit'):
      await message.channel.send("Understood. Just some testing? See you around.")
      for value in servers_object.values():
        if value != message.channel.id:
          await client.get_channel(value).send("Got a message from a different location to shut down. See ya!")
      quit()
    
    elif bot_backbone.command_check(message,command_prefix+'savechannel'):
      bot_backbone.set_server_file_value(str(message.guild.id), message.channel.id)
      await message.channel.send("Roger roger! I stored this channel for later.")

    elif bot_backbone.command_check(message,command_prefix+'setmode'):
      response_message = bot_backbone.setmode_handler(full_message_text=message.content.lower())
      servers_object = bot_backbone.servers_object
      await message.channel.send(f"{response_message}")
    
    elif bot_backbone.command_check(message,command_prefix+'serverlist') & debug:
      message_text = '```'
      for key in servers_object.keys():
        message_text += '\n'+client.get_guild(int(key)).name + ' : ' + client.get_channel(servers_object[key]).name + ' (server id: ' + key + ', channel id: ' + str(servers_object[key]) + ')'
      message_text += '```'
      await message.channel.send(message_text)

    else:
      await message.channel.send("Sorry, that doesn't seem like one of the commands I know... Maybe try something else? Or put me in debug mode.")

client.run(bot_setup['DISCORD_BOT_CLIENT_ID'])