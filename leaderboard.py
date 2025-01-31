import os  
import discord  
from discord.ext import commands, tasks  
from discord import app_commands  
import aiohttp  

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Use environment variable for token  

# Server-specific configuration  
SERVER_ID = 1334260506327777314  # Replace with your server ID  
LEADERBOARD_CHANNEL_ID = 1334807752089927762  # The channel for leaderboard  

# Roblox Game Configuration  
GAMES = [  
    {  
        "name": "Flex Fight",  
        "universe_id": "2223968745",  
        "place_id": "6110766473",  
    },  
    {  
        "name": "Timebomb Duels",  
        "universe_id": "4049246711",  
        "place_id": "11379739543",  
    },  
    {  
        "name": "Czesk Chat",  
        "universe_id": "5879629203",  
        "place_id": "17169742580",  
    },  
    {  
        "name": "Obby Trials",  
        "universe_id": "5819548197",  
        "place_id": "16952725324",  
    },  
    {  
        "name": "Obby Race",  
        "universe_id": "5847461965",  
        "place_id": "17056666727",  
    },  
    {  
        "name": "Tower of Hell",  
        "universe_id": "703124385",  
        "place_id": "1962086868",  
    },  
    {  
        "name": "Mic Up",  
        "universe_id": "2626227051",  
        "place_id": "6884319169",  
    },  
]  

# Roblox API URLs  
SERVERS_API_URL_TEMPLATE = "https://games.roblox.com/v1/games/{}/servers/Public?sortOrder=Asc&limit=10"  

# Initialize bot  
intents = discord.Intents.default()  
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)  
tree = bot.tree  # Slash command tree  

@tree.command(name="version", description="Check the bot version information.")  
async def version(interaction: discord.Interaction):  
    embed = discord.Embed(  
        title="Version",  
        description="v0.91",  
        color=discord.Color.blue(),  
    )  
    embed.set_footer(text="Made by @doxkll")  
    await interaction.response.send_message(embed=embed)  

async def fetch_active_players(place_id):  
    """Fetch active players from the specified game's place."""  
    async with aiohttp.ClientSession() as session:  
        try:  
            async with session.get(SERVERS_API_URL_TEMPLATE.format(place_id)) as response:  
                if response.status == 200:  
                    return (await response.json()).get("data", [])  
        except Exception as e:  
            print(f"Error fetching active player data for place ID {place_id}: {e}")  
    return None  

@tasks.loop(minutes=1)  # Adjust the frequency as needed  
async def send_leaderboard():  
    """Send leaderboard based on active players to the specified channel."""  
    channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)  
    
    if channel:  
        leaderboard = []  

        for game in GAMES:  
            active_players_data = await fetch_active_players(game["place_id"])  
            if active_players_data:  
                total_players = sum(server.get("playing", 0) for server in active_players_data)  
                leaderboard.append((game["name"], total_players))  

        # Sort leaderboard by player count in descending order  
        leaderboard.sort(key=lambda x: x[1], reverse=True)  

        leaderboard_message = "🏆 **Active Players Leaderboard** 🏆\n"  
        for game_name, player_count in leaderboard:  
            leaderboard_message += f"{game_name}: {player_count} players\n"  

        await channel.send(leaderboard_message)  

@bot.event  
async def on_ready():  
    print(f"Bot is online as {bot.user}!")  
    try:  
        # Sync slash commands for the server  
        await tree.sync(guild=discord.Object(id=SERVER_ID))  
        print("Slash commands synced!")  
    except Exception as e:  
        print(f"Error syncing commands: {e}")  

    # Start the leaderboard task  
    send_leaderboard.start()  

# Run the bot  
bot.run(DISCORD_TOKEN)
