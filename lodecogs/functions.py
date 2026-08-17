import disnake


class EmbedBuilder(disnake.Embed):

    def __init__(self, bot, inter):
        super().__init__()
        self.bot = bot
        self.inter = inter

    @staticmethod
    async def embed_builder(
        inter,
        custom_color,
        custom_thumbnail,
        custom_title,
        description,
        fields,
        footer_icon,
        footer_text,
        status,
    ):
        color = None
        thumbnail = None
        title = None
        failure_color = disnake.Color(0xF00A0A)
        failure_thumbnail = "https://bg3.wiki/w/images/4/4f/Generic_Threat.webp"
        failure_title = "Apologies."
        success_color = disnake.Color(0x3B9DA5)
        success_thumbnail = "https://bg3.wiki/w/images/2/2e/Durable.webp"
        success_title = "Success."
        waiting_color = disnake.Color(0x7A7979)
        waiting_thumbnail = "https://bg3.wiki/w/images/5/5f/Slow.webp"
        waiting_title = "Please wait."
        if status == "failure":
            color = failure_color
            thumbnail = failure_thumbnail
            title = failure_title
        elif status == "success":
            color = success_color
            thumbnail = success_thumbnail
            title = success_title
        elif status == "waiting":
            color = waiting_color
            thumbnail = waiting_thumbnail
            title = waiting_title
        if custom_color is not None:
            color = custom_color
        if custom_thumbnail is not None:
            thumbnail = custom_thumbnail
        if custom_title is not None:
            title = custom_title
        if footer_icon is None:
            footer_icon = "https://cdn.discordapp.com/avatars/1534659821549391952/86c5bebf46a06ca9949d949e877ba765"
        if footer_text is None:
            footer_text = "Lodestar"
        embed = disnake.Embed(color=color, description=description, title=title)
        if fields is not None:
            for field in fields:
                embed.add_field(
                    inline=bool(field["inline"]),
                    name=field["name"],
                    value=field["value"],
                )
        if inter.author.guild_avatar is None:
            author_icon = inter.author.avatar.url
        elif inter.author.guild_avatar is not None:
            author_icon = inter.author.guild_avatar.url
        else:
            author_icon = warning_thumbnail
        embed.set_author(icon_url=author_icon, name=inter.author.name)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        embed.set_thumbnail(url=thumbnail)
        return embed
