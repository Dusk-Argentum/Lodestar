import disnake
from disnake.ext import commands

import os

DESCRIPTION = """A bot used for tracking Pathfinder 2e initiatives, made for the Crotopian Enterprises group. \
Made by @dusk_argentum."""
GUILD = 348897377400258560
TESTS = []
TOKEN = os.environ.get("Lodestar_TOKEN")
VERSION = "1.0.4"


if TOKEN == os.environ.get("Lodestar_BETA_TOKEN"):
    GUILD = 348897377400258560
    TESTS = [348897377400258560]
elif TOKEN == os.environ.get("Lodestar_TOKEN"):
    GUILD = 1519881344375853176
    TESTS = [348897377400258560, 1519881344375853176]


command_sync_flags = commands.CommandSyncFlags.default()


intents = disnake.Intents.default()


bot = commands.InteractionBot(
    command_sync_flags=command_sync_flags,
    intents=intents,
    test_guilds=TESTS,
    owner_id=97153790897045504,
)


bot.load_extension("lodecogs.events")
bot.load_extension("lodecogs.help")
bot.load_extension("lodecogs.initiative")


if __name__ == "__main__":
    bot.run(TOKEN)
