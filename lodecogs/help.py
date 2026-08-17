from lodecogs.functions import EmbedBuilder
from lodestar import VERSION

from disnake.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Shows a list of all commands.", name="help")
    @commands.contexts(guild=True)
    async def help(self, inter):
        field_count = 0
        fields = []
        for cog in self.bot.cogs:
            cog_name = cog
            if cog == "Events":
                continue
            elif cog == "Help":
                continue
            commands_list = []
            for command in self.bot.get_cog(cog).get_slash_commands():
                command = inter.guild.get_command_named(command.name)
                commands_list.append(
                    f"</{command.name}:{command.id}> | {command.description}"
                )
                next_command = next(iter(self.bot.get_cog(cog).get_slash_commands()))
                command = inter.guild.get_command_named(next_command.name)
                next_command_append = (
                    f"</{command.name}:{command.id}> | {command.description}"
                )
                if (len(str(commands_list)) + len(str(next_command_append))) > 1024:
                    fields.append(
                        {
                            "inline": False,
                            "name": f"{cog_name}",
                            "value": f"{'\n'.join(commands_list)}",
                        }
                    )
                    commands_list = []
                    field_count += 1
                    cog_name = ""
                    continue
            fields.append(
                {
                    "inline": False,
                    "name": f"{cog_name}",
                    "value": f"{'\n'.join(commands_list)}",
                }
            )
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=self.bot.user.avatar.url,
            custom_title=f"{self.bot.user.name}: Commands",
            description="Click on a command for more details.",
            fields=fields,
            footer_icon="https://cdn.discordapp.com/emojis/1288585929090400257.webp?size=160",
            footer_text=f"Made by @dusk_argentum! | {VERSION}",
            status="success",
        )
        await inter.response.send_message(delete_after=300, embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
