import asyncio

from datetime import datetime, timezone

import disnake
from disnake import InteractionResponded
from disnake.ext import commands
from disnake.ext.commands import CommandInvokeError

from lodecogs.functions import EmbedBuilder


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if inter.author.id == self.bot.owner_id:
            await inter.author.send(f"{error}")
        raw_error = error
        if isinstance(error, CommandInvokeError):
            error = "Incorrect invocation. Please re-examine the command in `/help`."
        else:
            error = f"Unhandled error.\nPlease let the developer know you saw this!"
        channel = self.bot.get_channel(1534741941940387921)
        timestamp = int(
            (
                datetime.strptime(
                    str(datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)),
                    "%Y-%m-%d %H:%M:%S",
                )
                - datetime.strptime("1970-01-01", "%Y-%m-%d")
            ).total_seconds()
        )
        value = f"""A command invoked by {inter.author.mention} (`{inter.author.id}`) on \
<t:{timestamp}:F> in {f"{inter.channel.mention} (`{inter.channel.id}`)" if
        inter.channel.type == disnake.ChannelType.text else f"a DM with {inter.author.mention} (`{inter.author.id}`)"} \
caused the error detailed below."""
        fields = [
            {"inline": False, "name": "Source:", "value": value},
            {"inline": False, "name": "Raw Error:", "value": raw_error},
            {"inline": False, "name": "Message Sent:", "value": error},
            {
                "inline": False,
                "name": "Message Context:",
                "value": f"`/{inter.application_command.name} {str(inter.filled_options)}`",
            },
        ]
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="An exception was caught.",
            fields=fields,
            footer_icon=None,
            footer_text=None,
            status="failure",
        )
        await channel.send(embed=embed)
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=self.bot.user.avatar.url,
            custom_title=None,
            description=f"I'm sorry, I ran into an error.\nError: {error}",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="failure",
        )
        try:
            await inter.response.send_message(
                delete_after=300, embed=embed, ephemeral=True
            )
        except InteractionResponded:
            await inter.edit_original_response(content=None, embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(1)
        print(f"{self.bot.user.name} online. Awaiting commands.")
        await self.bot.change_presence(
            activity=disnake.Game("Tracking initiative. | /help")
        )


def setup(bot):
    bot.add_cog(Events(bot))
