from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import InputPeerEmpty
import configparser

# Read API credentials from a config file
config = configparser.ConfigParser()
config.read('config.ini')

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
phone = config['Telegram']['phone']

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Function to search for channels
async def search_channels(keyword):
    await client.start(phone)
    
    result = await client(SearchRequest(
        q=keyword,
        limit=50,
        hash=0
    ))
    
    channels = []
    
    for chat in result.chats:
        if chat.broadcast:  # This ensures we are only getting channels
            channels.append(chat.username)
    
    return channels

# Main function
if __name__ == '__main__':
    import asyncio
    
    keyword = input("Enter the topic to search for Telegram channels: ")
    channels = asyncio.run(search_channels(keyword))
    
    with open('telegram_channels_list.txt', 'w') as f:
        for channel in channels:
            if channel:
                f.write(f"https://t.me/{channel}\n")
    
    print("Channels list saved to telegram_channels_list.txt")

