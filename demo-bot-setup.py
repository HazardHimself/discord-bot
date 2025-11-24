import bot_backbone
from bot_backbone import client, bot_setup

@client.event
async def on_ready():
  await bot_backbone.send_timed_message_FILE('meme.jpg')
  quit()

client.run(bot_setup['DISCORD_BOT_CLIENT_ID'])