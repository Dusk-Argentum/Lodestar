import disnake
from disnake import Forbidden, HTTPException, InteractionResponded, NotFound
from disnake.ext import commands

from lodecogs.functions import EmbedBuilder

import os

import random

import re

import sqlite3
from sqlite3 import OperationalError

import uuid


class Functions:
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def collision_check(inter, name, total, priority, combatants):
        collision_check = {"name": False, "priority": False}
        names_list = []
        for _, combatant in combatants.items():
            names_list.append(combatant["name"])
        for name_entry in names_list:
            if name == name_entry:
                count_check = re.search(r" \((\d{1,2})\)$", name)
                if count_check is not None:
                    count = 2
                    while name in names_list:
                        if count >= 52:
                            break
                        count += 1
                        name = re.sub(r" \((\d{1,2})\)$", f" ({count})", name)
                    if count >= 52:
                        failure = await EmbedBuilder.embed_builder(
                            inter=inter,
                            custom_color=None,
                            custom_thumbnail=None,
                            custom_title=None,
                            description="Unresolvable name collision. Please use a new name.",
                            fields=None,
                            footer_icon=None,
                            footer_text="50 attempts were made to append a new number.",
                            status="failure",
                        )
                        name, total, priority, collision_check = (
                            failure,
                            failure,
                            failure,
                            failure,
                        )
                        return name, total, priority, collision_check
                elif count_check is None:
                    name = name + " (2)"
                    if len(name) > 19:
                        failure = await EmbedBuilder.embed_builder(
                            inter=inter,
                            custom_color=None,
                            custom_thumbnail=None,
                            custom_title=None,
                            description="Unresolvable name collision. Please use a new name.",
                            fields=None,
                            footer_icon=None,
                            footer_text="Maximum name length: 19 characters.",
                            status="failure",
                        )
                        name, total, priority, collision_check = (
                            failure,
                            failure,
                            failure,
                            failure,
                        )
                        return name, total, priority, collision_check
                    if name in names_list:
                        count = 2
                        while name in names_list:
                            if count >= 52:
                                break
                            count += 1
                            name = re.sub(r" \((\d{1,2})\)$", f" ({count})", name)
                        if count >= 52:
                            failure = await EmbedBuilder.embed_builder(
                                inter=inter,
                                custom_color=None,
                                custom_thumbnail=None,
                                custom_title=None,
                                description="Unresolvable name collision. Please use a new name.",
                                fields=None,
                                footer_icon=None,
                                footer_text="50 attempts were made to append a new number.",
                                status="failure",
                            )
                            name, total, priority, collision_check = (
                                failure,
                                failure,
                                failure,
                                failure,
                            )
                            return name, total, priority, collision_check
                collision_check.update({"name": True})
                break
        totals_list = []
        for _, combatant in combatants.items():
            totals_list.append(combatant["total"])
        if total in totals_list:
            priorities_list = []
            for _, combatant in combatants.items():
                if combatant["total"] == total:
                    priorities_list.append(combatant["priority"])
            if priority in priorities_list:
                count = 1
                while priority in priorities_list:
                    if count >= 51:
                        break
                    priority = random.randint(1, 99)
                    count += 1
                if count >= 51:
                    failure = await EmbedBuilder.embed_builder(
                        inter=inter,
                        custom_color=None,
                        custom_thumbnail=None,
                        custom_title=None,
                        description="Unresolvable priority collision. Please use a new total.",
                        fields=None,
                        footer_icon=None,
                        footer_text="50 attempts were made to generate a new random priority.",
                        status="failure",
                    )
                    name, total, priority, collision_check = (
                        failure,
                        failure,
                        failure,
                        failure,
                    )
                    return name, total, priority, collision_check
                collision_check.update({"priority": True})
        return name, total, priority, collision_check

    @staticmethod
    async def combatant_autocomplete(inter, input_: str):
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            combatant_name = initiative
            return combatant_name
        init_uuid = initiative[0][0]
        combatants = await Functions.init_build(inter=inter, init_uuid=init_uuid)
        combatants = combatants[0]
        combatants_list = []
        for _, combatant_ in combatants.items():
            if combatant_["uuid"] == "INITIATOR":
                continue
            combatants_list.append(combatant_["name"])
        return [
            combatant for combatant in combatants_list if input_.lower() in combatant
        ]

    @staticmethod
    async def connection(inter, database):
        try:
            con = sqlite3.connect(f"{database}.db", timeout=30)
        except OperationalError:
            con = await Functions.connection_failure(inter=inter)
        return con

    @staticmethod
    async def connection_failure(inter):
        failure = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="Sorry, I ran into a problem with my database; please try again later.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="failure",
        )
        return failure

    @staticmethod
    async def init_build(inter, init_uuid):
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            combatants, initiator, pin, round_ = con, con, con, con
            return combatants, initiator, pin, round_
        cur = con.cursor()
        cur.execute("SELECT * FROM init_list")
        initiative = cur.fetchall()
        cur.execute(
            "SELECT id, total, priority FROM init_list WHERE uuid = 'INITIATOR'"
        )
        init_metadata = cur.fetchall()[0]
        initiator = init_metadata[0]
        pin = init_metadata[1]
        round_ = init_metadata[2]
        combatants = {}
        for count, combatant in enumerate(initiative):
            current_combatant_attrs = {}
            cur.execute(
                f"SELECT uuid FROM init_list WHERE uuid = ?", [f"{combatant[0]}"]
            )
            current_combatant_attrs.update({"uuid": cur.fetchall()[0][0]})
            cur.execute(f"SELECT id FROM init_list WHERE uuid = ?", [f"{combatant[0]}"])
            current_combatant_attrs.update({"id": cur.fetchall()[0][0]})
            cur.execute(
                f"SELECT name FROM init_list WHERE uuid = ?", [f"{combatant[0]}"]
            )
            current_combatant_attrs.update({"name": cur.fetchall()[0][0]})
            cur.execute(
                f"SELECT total FROM init_list WHERE uuid = ?", [f"{combatant[0]}"]
            )
            current_combatant_attrs.update({"total": cur.fetchall()[0][0]})
            cur.execute(
                f"SELECT priority FROM init_list WHERE uuid = ?", [f"{combatant[0]}"]
            )
            current_combatant_attrs.update({"priority": cur.fetchall()[0][0]})
            cur.execute(
                f"SELECT turn FROM init_list WHERE uuid = ?", [f"{combatant[0]}"]
            )
            current_combatant_attrs.update({"turn": cur.fetchall()[0][0]})
            combatants.update({str(count): current_combatant_attrs})
        con.close()
        return combatants, initiator, pin, round_

    @staticmethod
    async def init_check_combatant(inter, init_uuid, name):
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            combatant = con
            return combatant
        cur = con.cursor()
        cur.execute(f"SELECT * FROM init_list WHERE name = ?", [f"{name}"])
        combatant = cur.fetchall()
        con.close()
        if not combatant:
            combatant = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description=f"No combatant named {name} in this combat.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
        return combatant

    @staticmethod
    async def init_check_exists(inter):
        con = await Functions.connection(inter=inter, database="init_master")
        if isinstance(con, disnake.Embed):
            initiative = con
            return initiative
        cur = con.cursor()
        cur.execute(
            f"SELECT * FROM init_master WHERE guild = ? AND channel = ?",
            [inter.guild.id, inter.channel.id],
        )
        initiative = cur.fetchall()
        con.close()
        if not initiative:
            initiative = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="This channel is not in combat.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
        return initiative

    @staticmethod
    async def init_check_owned(inter, init_uuid, player, name):
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            owned = con
            return owned
        cur = con.cursor()
        cur.execute(
            f"SELECT * FROM init_list WHERE id = ? AND name = ?", [player, f"{name}"]
        )
        player = cur.fetchall()
        con.close()
        if not player:
            player = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="No combatant with that name under your control.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
        return player

    @staticmethod
    async def init_check_player(inter, init_uuid, player):
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            player = con
            return player
        cur = con.cursor()
        cur.execute(f"SELECT * FROM init_list WHERE id = ?", [f"{player}"])
        combatant = cur.fetchall()
        con.close()
        if not combatant:
            player = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="No combatants under your control in this combat.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
        return player

    @staticmethod
    async def init_sort(combatants, initiator):
        init_order = dict(
            sorted(
                combatants.items(),
                key=lambda x: (
                    -x[1]["total"],
                    x[1]["id"] != initiator,
                    x[1]["priority"],
                ),
            )
        )
        init_sorted = {}
        count = 0
        for _, combatant in init_order.items():
            init_sorted.update({f"{count}": combatant})
            count += 1
        return init_sorted

    @staticmethod
    async def init_turns(self, init_sorted, initiator, round_):
        init_list = []
        for _, combatant in init_sorted.items():
            if combatant["uuid"] == "INITIATOR":
                continue
            symbol = ""
            if combatant["id"] == initiator:
                symbol = "-"
            elif combatant["id"] != initiator and combatant["turn"] != 1:
                symbol = "+"
            if combatant["turn"] == 1:
                symbol = "*"
            name_space = " " * (19 - len(combatant["name"]))
            total_space = " " * (2 - len(str(combatant["total"])))
            priority_space = " " * (2 - len(str(combatant["priority"])))
            turn_builder = f"""{symbol} {combatant["name"]}{name_space} [{combatant["total"]}{total_space} | \
{priority_space}{combatant["priority"]}]"""
            init_list.append(turn_builder)
        init_list = "\n".join(init_list)
        initiator = await self.bot.fetch_user(initiator)
        init_turns = f"### Round: {round_} | Initiator: {initiator.mention}\n```diff\n{init_list}\n```"
        return init_turns


class Initiative(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Adds a new combatant.", name="add")
    @commands.contexts(guild=True)
    async def add(
        self,
        inter,
        name: str = commands.Param(
            description="The name of the combatant.",
            name="name",
            max_length=19,
            min_length=1,
        ),
        total: int = commands.Param(
            description="The total result of the Initiative roll.",
            name="total",
            max_value=99,
            min_value=-9,
        ),
        priority: int = commands.Param(
            default=1,
            description="For PCs, total ties are won by the lower number.",
            name="priority",
            max_value=99,
            min_value=-9,
        ),
    ):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = initiative[0][0]
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        if len(combatants) >= 50:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="Maximum combatants reached.",
                fields=None,
                footer_icon=None,
                footer_text="Max.: 50.",
                status="failure",
            )
            await inter.edit_original_response(embed=embed)
            return
        name, total, priority, collision_check = await Functions.collision_check(
            inter=inter,
            name=name,
            total=total,
            priority=priority,
            combatants=combatants,
        )
        if isinstance(name, disnake.Embed):
            await inter.edit_original_response(content=None, embed=name)
            return
        if len(name) > 19:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="Please choose a name that does not collide with other combatants.",
                fields=None,
                footer_icon=None,
                footer_text="Maximum name length: 19 characters.",
                status="failure",
            )
            await inter.edit_original_response(embed=embed)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(
            f"INSERT INTO init_list VALUES (?, ?, ?, ?, ?, ?)",
            [f"{str(uuid.uuid4())}", inter.author.id, f"{name}", total, priority, 0],
        )
        con.commit()
        con.close()
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator, round_=round_
        )
        description = f"{name} was added to initiative with total {total} and priority {priority}."
        name_command = inter.guild.get_command_named("name")
        priority_command = inter.guild.get_command_named("priority")
        if collision_check["name"] is True:
            description += f"""\n-# There was already a combatant by the name provided, so it has been changed for you. \
Use </{name_command.name}:{name_command.id}> to set a new one."""
        if collision_check["priority"] is True:
            description += f"""\n-# There was already a combatant with the priority provided in the total {total}, so \
it has been changed for you. Use </{priority_command.name}:{priority_command.id}> to set a new one."""
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description=description,
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(delete_after=300, embed=embed)
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(
                allowed_mentions=disnake.AllowedMentions(users=False),
                content=init_turns,
            )
            await pin.forward(inter.channel)
        except (NotFound, Forbidden, HTTPException):
            try:
                await inter.channel.send(
                    allowed_mentions=disnake.AllowedMentions(users=False),
                    content=init_turns,
                )
            except Forbidden:
                embed = await EmbedBuilder.embed_builder(
                    inter=inter,
                    custom_color=None,
                    custom_thumbnail=None,
                    custom_title="Command completed successfully. However:",
                    description="I don't have permission to send messages in this channel.",
                    fields=None,
                    footer_icon=None,
                    footer_text="Please update my permissions. I need Send Messages and Pin Messages.",
                    status="failure",
                )
                await inter.edit_original_response(content=None, embed=embed)

    @commands.slash_command(
        description="Starts a new initiative in the current channel.", name="begin"
    )
    @commands.contexts(guild=True)
    async def begin(self, inter):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if initiative is type(disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = uuid.uuid4()
        con = await Functions.connection(inter=inter, database="init_master")
        if con is type(disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(
            f"INSERT INTO init_master VALUES (?, ?, ?)",
            [f"{init_uuid}", inter.guild.id, inter.channel.id],
        )
        con.commit()
        con.close()
        add_command = inter.guild.get_command_named("add")
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail="",
            custom_title=f"Initiative started successfully.",
            description=f"Add combatants to initiative using </{add_command.name}:{add_command.id}>.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(embed=embed)
        try:
            pin = await inter.channel.send(
                content="Setting up the initiative list. Please wait.",
            )
        except Forbidden:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title="Command did not complete.",
                description="I don't have permission to send messages in this channel.",
                fields=None,
                footer_icon=None,
                footer_text="Please update my permissions. I need Send Messages and Pin Messages.",
                status="failure",
            )
            await inter.edit_original_response(content=None, embed=embed)
            return
        try:
            await pin.pin()
        except (Forbidden, HTTPException, NotFound):
            pass
        with sqlite3.connect(f"init_folder/{init_uuid}.db", timeout=30) as con:
            cur = con.cursor()
        cur.execute(
            """CREATE TABLE init_list (uuid TEXT NOT NULL PRIMARY KEY, id INTEGER, name TEXT, total INTEGER, \
priority INTEGER, turn INTEGER)"""
        )
        cur.execute(
            f"INSERT INTO init_list VALUES (?, ?, ?, ?, ?, ?)",
            ("INITIATOR", inter.author.id, None, pin.id, 0, 1),
        )
        con.commit()
        con.close()
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator, round_=round_
        )
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(
                allowed_mentions=disnake.AllowedMentions(users=False),
                content=init_turns.replace(
                    "```diff\n\n```", "```diff\nAwaiting combatants...\n```"
                ),
            )
        except (NotFound, Forbidden, HTTPException):
            try:
                await inter.channel.send(
                    allowed_mentions=disnake.AllowedMentions(users=False),
                    content=init_turns.replace(
                        "```diff\n\n```", "```diff\nAwaiting combatants...\n```"
                    ),
                )
            except Forbidden:
                embed = await EmbedBuilder.embed_builder(
                    inter=inter,
                    custom_color=None,
                    custom_thumbnail=None,
                    custom_title="Command completed successfully. However:",
                    description="I don't have permission to send messages in this channel.",
                    fields=None,
                    footer_icon=None,
                    footer_text="Please update my permissions. I need Send Messages and Pin Messages.",
                    status="failure",
                )
                await inter.edit_original_response(content=None, embed=embed)

    @commands.slash_command(
        description="Modify the person who controls the specified combatant.",
        name="controller",
    )
    @commands.contexts(guild=True)
    async def controller(
        self,
        inter,
        name: str = commands.Param(
            autocomplete=Functions.combatant_autocomplete,
            description="The name of the combatant you would like to modify.",
            name="name",
            max_length=19,
            min_length=1,
        ),
        controller: disnake.Member = commands.Param(
            description="The member you would like to make the controller.",
            name="controller",
        ),
    ):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = initiative[0][0]
        player = await Functions.init_check_player(
            inter=inter, init_uuid=init_uuid, player=inter.author.id
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        player = await Functions.init_check_owned(
            inter=inter, init_uuid=init_uuid, player=inter.author.id, name=name
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        combatant = await Functions.init_check_combatant(
            inter=inter, init_uuid=init_uuid, name=name
        )
        if isinstance(combatant, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatant)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute("SELECT id FROM init_list WHERE name = ?", [f"{name}"])
        old_controller = cur.fetchall()[0][0]
        con.close()
        if old_controller != inter.author.id:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="You are not the combat initiator.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
            await inter.edit_original_response(content=None, embed=embed)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(
            f"UPDATE init_list SET id = ? WHERE name = ?", [controller.id, f"{name}"]
        )
        con.commit()
        con.close()
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator, round_=round_
        )
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description=f"{controller.mention} is now the controller of {name}.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(content=None, embed=embed)
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(
                allowed_mentions=disnake.AllowedMentions(users=False),
                content=init_turns,
            )
        except (NotFound, Forbidden, HTTPException):
            pass

    @commands.slash_command(
        description="Ends initiative in the current channel.", name="end"
    )
    @commands.contexts(guild=True)
    async def end(self, inter):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        try:
            await inter.response.send_message(embed=embed)
        except InteractionResponded:
            await inter.edit_original_response(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = initiative[0][0]
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute("SELECT total FROM init_list WHERE uuid = 'INITIATOR'")
        pin = cur.fetchall()[0][0]
        con.close()
        if os.path.exists(f"init_folder/{init_uuid}.db"):
            os.remove(f"init_folder/{init_uuid}.db")
        else:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="Combat could not be ended.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
            await inter.edit_original_response(content=None, embed=embed)
            return
        con = await Functions.connection(inter=inter, database="init_master")
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(f"DELETE FROM init_master WHERE uuid = ?", [f"{init_uuid}"])
        con.commit()
        con.close()
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="Combat ended.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(content=None, embed=embed)
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.unpin()
        except (Forbidden, HTTPException, NotFound):
            pass

    @commands.slash_command(
        description="Sets a new combat initiator.", name="initiator"
    )
    @commands.contexts(guild=True)
    async def initiator(
        self,
        inter,
        initiator: disnake.Member = commands.Param(
            description="The member you would like to make the initiator.",
            name="initiator",
        ),
    ):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = initiative[0][0]
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute("SELECT id FROM init_list WHERE uuid = 'INITIATOR'")
        old_initiator = cur.fetchall()[0][0]
        con.close()
        if old_initiator != inter.author.id:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="You are not the combat initiator.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
            await inter.edit_original_response(content=None, embed=embed)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(
            f"UPDATE init_list SET id = ? WHERE uuid ='INITIATOR'", [initiator.id]
        )
        con.commit()
        con.close()
        combatants, initiator_, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator_
        )
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator_, round_=round_
        )
        initiator = await self.bot.fetch_user(initiator_)
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description=f"{initiator.mention} is now the initiator of this combat.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(content=None, embed=embed)
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(
                allowed_mentions=disnake.AllowedMentions(users=False),
                content=init_turns,
            )
        except (NotFound, Forbidden, HTTPException):
            pass

    @commands.slash_command(description="Jumps to a combatant.", name="jump")
    @commands.contexts(guild=True)
    async def jump(
        self,
        inter,
        name: str = commands.Param(
            autocomplete=Functions.combatant_autocomplete,
            description="The name of the combatant you would like to jump to.",
            name="name",
            max_length=19,
            min_length=1,
        ),
    ):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = initiative[0][0]
        player = await Functions.init_check_player(
            inter=inter, init_uuid=init_uuid, player=inter.author.id
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        combatant = await Functions.init_check_combatant(
            inter=inter, init_uuid=init_uuid, name=name
        )
        if isinstance(combatant, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatant)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute("SELECT priority FROM init_list WHERE uuid = 'INITIATOR'")
        round_ = cur.fetchall()[0][0]
        con.close()
        next_command = inter.guild.get_command_named("next")
        if round_ == 0:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description=f"Please first start combat with </{next_command.name}:{next_command.id}>.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
            await inter.edit_original_response(content=None, embed=embed)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(f"SELECT uuid FROM init_list WHERE name = ?", [f"{name}"])
        combatant = cur.fetchall()[0][0]
        cur.execute(f"UPDATE init_list SET turn = 0 WHERE turn = 1")
        cur.execute(f"UPDATE init_list SET turn = 1 WHERE uuid = ?", [f"{combatant}"])
        con.commit()
        con.close()
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator, round_=round_
        )
        jumped_combatant = None
        for _, combatant in init_sorted.items():
            if combatant["name"] == name:
                jumped_combatant = combatant
                break
        name_space = " " * (19 - len(jumped_combatant["name"]))
        total_space = " " * (2 - len(str(jumped_combatant["total"])))
        priority_space = " " * (2 - len(str(jumped_combatant["priority"])))
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description=f"""It is now {jumped_combatant["name"]}'s turn.
```diff\n* {jumped_combatant["name"]}{name_space} [{jumped_combatant["total"]}{total_space} | \
{priority_space}{jumped_combatant["priority"]}]```""",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(embed=embed)
        turn_mention = await self.bot.fetch_user(jumped_combatant["id"])
        try:
            mention = await inter.channel.send(turn_mention.mention)
        except Forbidden:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title="I could not ping the upcoming player.",
                description="I don't have permission to send messages in this channel.",
                fields=None,
                footer_icon=None,
                footer_text="Please update my permissions. I need Send Messages and Pin Messages.",
                status="failure",
            )
            await inter.edit_original_response(content=None, embed=embed)
            return
        await mention.delete()
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(
                allowed_mentions=disnake.AllowedMentions(users=False),
                content=init_turns,
            )
        except (NotFound, Forbidden, HTTPException):
            pass

    @commands.slash_command(
        description="Lists the current combatants in order.", name="list"
    )
    @commands.contexts(guild=True)
    async def list_(self, inter):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = initiative[0][0]
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator, round_=round_
        )
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="Built a new initiative list.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(delete_after=10, embed=embed)
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(init_turns)
            await pin.forward(inter.channel)
            return
        except (NotFound, Forbidden, HTTPException):
            try:
                await inter.channel.send(
                    allowed_mentions=disnake.AllowedMentions(users=False),
                    content=init_turns,
                )
            except Forbidden:
                embed = await EmbedBuilder.embed_builder(
                    inter=inter,
                    custom_color=None,
                    custom_thumbnail=None,
                    custom_title="Command completed successfully. However:",
                    description="I don't have permission to send messages in this channel.",
                    fields=None,
                    footer_icon=None,
                    footer_text="Please update my permissions. I need Send Messages and Pin Messages.",
                    status="failure",
                )
                await inter.edit_original_response(content=None, embed=embed)

    @commands.slash_command(description="Changes a combatant's name.", name="name")
    @commands.contexts(guild=True)
    async def name(
        self,
        inter,
        name: str = commands.Param(
            autocomplete=Functions.combatant_autocomplete,
            description="The name of the combatant you would like to change the name of.",
            name="name",
            max_length=19,
            min_length=1,
        ),
        new_name: str = commands.Param(
            description="The name you would like to be set instead.",
            name="new_name",
            max_length=19,
            min_length=1,
        ),
    ):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = initiative[0][0]
        player = await Functions.init_check_player(
            inter=inter, init_uuid=init_uuid, player=inter.author.id
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        player = await Functions.init_check_owned(
            inter=inter, init_uuid=init_uuid, player=inter.author.id, name=name
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        combatant = await Functions.init_check_combatant(
            inter=inter, init_uuid=init_uuid, name=name
        )
        if isinstance(combatant, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatant)
            return
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        total = None
        priority = None
        for _, combatant in combatants.items():
            if combatant["name"] == name:
                total = combatant["total"]
                priority = combatant["priority"]
        new_name, total, priority, collision_check = await Functions.collision_check(
            inter=inter,
            name=new_name,
            total=total,
            priority=priority,
            combatants=combatants,
        )
        if isinstance(new_name, disnake.Embed):
            await inter.edit_original_response(content=None, embed=new_name)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(
            f"UPDATE init_list SET name = ? WHERE id = ? AND name = ?",
            [f"{new_name}", inter.author.id, f"{name}"],
        )
        con.commit()
        con.close()
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator, round_=round_
        )
        description = f"The combatant's name was updated to {new_name}."
        name_command = inter.guild.get_command_named("name")
        if collision_check["name"] is True:
            description += f"""\n-# There was already a combatant by the name provided, so it has been changed for \
you. Use </{name_command.name}:{name_command.id}> to set a new one."""
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description=description,
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(embed=embed)
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(
                allowed_mentions=disnake.AllowedMentions(users=False),
                content=init_turns,
            )
        except (NotFound, Forbidden, HTTPException):
            pass

    @commands.slash_command(description="Advances initiative.", name="next")
    @commands.contexts(guild=True)
    async def next_(self, inter):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = initiative[0][0]
        player = await Functions.init_check_player(
            inter=inter, init_uuid=init_uuid, player=inter.author.id
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        if len(init_sorted) == 1:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="No combatants remain. Ending combat.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
            await inter.edit_original_response(embed=embed)
            await Initiative.end(interaction=inter, inter=inter)
            return
        first_combatant = init_sorted["1"]
        init_iter = iter(init_sorted)
        prev_combatant = None
        next_combatant = None
        increment_round = False
        for combatant in init_iter:
            if init_sorted[combatant]["turn"] == 1:
                prev_combatant = init_sorted[combatant]["uuid"]
                next_combatant = next(init_iter, "1")
                next_combatant = init_sorted[next_combatant]
                if next_combatant == first_combatant:
                    increment_round = True
                if next_combatant == "0":
                    next_combatant = init_sorted[first_combatant]
                break
        if round_ == 0:
            increment_round = True
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(
            f"UPDATE init_list SET turn = 0 WHERE uuid = ? AND turn = 1",
            [f"{prev_combatant}"],
        )
        cur.execute(
            f"UPDATE init_list SET turn = 1 WHERE uuid = ?",
            [f"{next_combatant['uuid']}"],
        )
        if increment_round:
            round_ += 1
            if round_ > 864000:
                embed = await EmbedBuilder.embed_builder(
                    inter=inter,
                    custom_color=None,
                    custom_thumbnail=None,
                    custom_title="Congratulations. You were in combat for 2 real-world months worth of rounds.",
                    description="Unfortunately, I have to cut you off now. Thanks for playing!",
                    fields=None,
                    footer_icon=None,
                    footer_text="Your combat will now be ended. Please feel free to start a new one.",
                    status="failure",
                )
                await inter.edit_original_response(embed=embed)
                con.close()
                await Initiative.end(interaction=inter, inter=inter)
                return
            cur.execute(
                f"UPDATE init_list SET priority = ? WHERE uuid = 'INITIATOR'", [round_]
            )
        con.commit()
        con.close()
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator, round_=round_
        )
        name_space = " " * (19 - len(next_combatant["name"]))
        total_space = " " * (2 - len(str(next_combatant["total"])))
        priority_space = " " * (2 - len(str(next_combatant["priority"])))
        next_turn_builder = f"""* {next_combatant["name"]}{name_space} [{next_combatant["total"]}{total_space} | \
{priority_space}{next_combatant["priority"]}]"""
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description=f"It is now {next_combatant['name']}'s turn.\n```diff\n{next_turn_builder}\n```",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        turn_mention = await self.bot.fetch_user(next_combatant["id"])
        try:
            await inter.channel.send(content=turn_mention.mention, embed=embed)
        except Forbidden:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title="I could not output the next player's turn.",
                description="I don't have permission to send messages in this channel.",
                fields=None,
                footer_icon=None,
                footer_text="Please update my permissions. I need Send Messages and Pin Messages.",
                status="failure",
            )
            await inter.edit_original_response(content=None, embed=embed)
            return
        await inter.delete_original_response()
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(
                allowed_mentions=disnake.AllowedMentions(users=False),
                content=init_turns,
            )
        except (NotFound, Forbidden, HTTPException):
            return

    @commands.slash_command(
        description="Modifies the initiative priority for the specified combatant."
    )
    @commands.contexts(guild=True)
    async def priority(
        self,
        inter,
        name: str = commands.Param(
            autocomplete=Functions.combatant_autocomplete,
            description="The name of the combatant you would like to modify.",
            name="name",
            max_length=19,
            min_length=1,
        ),
        priority: int = commands.Param(
            description="For PCs, total ties are won by the lower number.",
            name="priority",
            max_value=99,
            min_value=-1,
        ),
    ):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = initiative[0][0]
        player = await Functions.init_check_player(
            inter=inter, init_uuid=init_uuid, player=inter.author.id
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        player = await Functions.init_check_owned(
            inter=inter, init_uuid=init_uuid, player=inter.author.id, name=name
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        combatant = await Functions.init_check_combatant(
            inter=inter, init_uuid=init_uuid, name=name
        )
        if isinstance(combatant, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatant)
            return
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        total = None
        for _, combatant in combatants.items():
            if combatant["name"] == name:
                total = combatant["total"]
        _, total, priority, collision_check = await Functions.collision_check(
            inter=inter,
            name=name,
            total=total,
            priority=priority,
            combatants=combatants,
        )
        if isinstance(_, disnake.Embed):
            await inter.edit_original_response(content=None, embed=_)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(
            f"UPDATE init_list SET priority = ? WHERE id = ? AND name = ?",
            [priority, inter.author.id, f"{name}"],
        )
        con.commit()
        con.close()
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator, round_=round_
        )
        description = f"{name}'s priority was updated to {priority}."
        priority_command = inter.guild.get_command_named("priority")
        if collision_check["priority"] is True:
            description += f"""\n-# There was already a combatant with your priority at {total}, so it has been \
changed for you. Use </{priority_command.name}:{priority_command.id}> to set a new one."""
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description=description,
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(content=None, embed=embed)
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(
                allowed_mentions=disnake.AllowedMentions(users=False),
                content=init_turns,
            )
        except (NotFound, Forbidden, HTTPException):
            pass

    @commands.slash_command(description="Removes a combatant.", name="remove")
    @commands.contexts(guild=True)
    async def remove(
        self,
        inter,
        name: str = commands.Param(
            autocomplete=Functions.combatant_autocomplete,
            description="The name of the combatant you would like to remove.",
            name="name",
            max_length=19,
            min_length=1,
        ),
    ):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
            return
        init_uuid = initiative[0][0]
        player = await Functions.init_check_player(
            inter=inter, init_uuid=init_uuid, player=inter.author.id
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        combatant = await Functions.init_check_combatant(
            inter=inter, init_uuid=init_uuid, name=name
        )
        if isinstance(combatant, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatant)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(
            f"SELECT uuid, turn FROM init_list WHERE id = ? AND name = ?",
            [inter.author.id, f"{name}"],
        )
        combatant = cur.fetchall()
        con.close()
        if combatant[0][1] == 1:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="You cannot remove a combatant on their own turn.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
            await inter.edit_original_response(content=None, embed=embed)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        if isinstance(con, disnake.Embed):
            await inter.edit_original_response(content=None, embed=con)
            return
        cur = con.cursor()
        cur.execute(f"DELETE FROM init_list WHERE uuid = ?", [f"{combatant[0][0]}"])
        con.commit()
        con.close()
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        if len(init_sorted) == 1:
            embed = await EmbedBuilder.embed_builder(
                inter=inter,
                custom_color=None,
                custom_thumbnail=None,
                custom_title=None,
                description="No combatants remain. Ending combat.",
                fields=None,
                footer_icon=None,
                footer_text=None,
                status="failure",
            )
            await inter.edit_original_response(embed=embed)
            await Initiative.end(interaction=inter, inter=inter)
            return
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator, round_=round_
        )
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description=f"{name} was removed from combat.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(embed=embed)
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(
                allowed_mentions=disnake.AllowedMentions(users=False),
                content=init_turns,
            )
        except (NotFound, Forbidden, HTTPException):
            pass

    @commands.slash_command(
        description="Modifies the initiative total for the specified combatant.",
        name="total",
    )
    @commands.contexts(guild=True)
    async def total(
        self,
        inter,
        name: str = commands.Param(
            autocomplete=Functions.combatant_autocomplete,
            description="The name of the combatant you would like to modify.",
            name="name",
            max_length=19,
            min_length=1,
        ),
        total: int = commands.Param(
            description="The new total you would like to set.",
            name="total",
            max_value=99,
            min_value=-9,
        ),
    ):
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description="You should see changes shortly.",
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="waiting",
        )
        await inter.response.send_message(embed=embed)
        initiative = await Functions.init_check_exists(inter=inter)
        if isinstance(initiative, disnake.Embed):
            await inter.edit_original_response(content=None, embed=initiative)
        init_uuid = initiative[0][0]
        player = await Functions.init_check_player(
            inter=inter, init_uuid=init_uuid, player=inter.author.id
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        player = await Functions.init_check_owned(
            inter=inter, init_uuid=init_uuid, player=inter.author.id, name=name
        )
        if isinstance(player, disnake.Embed):
            await inter.edit_original_response(content=None, embed=player)
            return
        combatant = await Functions.init_check_combatant(
            inter=inter, init_uuid=init_uuid, name=name
        )
        if isinstance(combatant, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatant)
            return
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        if isinstance(combatants, disnake.Embed):
            await inter.edit_original_response(content=None, embed=combatants)
            return
        priority = None
        for _, combatant in combatants.items():
            if combatant["name"] == name:
                priority = combatant["priority"]
        _, total, priority, collision_check = await Functions.collision_check(
            inter=inter,
            name=name,
            total=total,
            priority=priority,
            combatants=combatants,
        )
        if isinstance(_, disnake.Embed):
            await inter.edit_original_response(content=None, embed=_)
            return
        con = await Functions.connection(
            inter=inter, database=f"init_folder/{init_uuid}"
        )
        cur = con.cursor()
        if collision_check["priority"] is True:
            cur.execute(
                f"UPDATE init_list SET total = ?, priority = ? WHERE id = ? AND name = ?",
                [total, priority, inter.author.id, f"{name}"],
            )
        elif collision_check["priority"] is False:
            cur.execute(
                f"UPDATE init_list SET total = ? WHERE id = ? AND name = ?",
                [total, inter.author.id, f"{name}"],
            )
        con.commit()
        con.close()
        combatants, initiator, pin, round_ = await Functions.init_build(
            inter=inter, init_uuid=init_uuid
        )
        init_sorted = await Functions.init_sort(
            combatants=combatants, initiator=initiator
        )
        init_turns = await Functions.init_turns(
            self=self, init_sorted=init_sorted, initiator=initiator, round_=round_
        )
        description = f"{name}'s total was updated to {total}."
        priority_command = inter.guild.get_command_named("priority")
        if collision_check["priority"] is True:
            description += f"""\n-# There was already a combatant with your priority at {total}, so it has been \
changed for you. Use </{priority_command.name}:{priority_command.id}> to set a new one."""
        embed = await EmbedBuilder.embed_builder(
            inter=inter,
            custom_color=None,
            custom_thumbnail=None,
            custom_title=None,
            description=description,
            fields=None,
            footer_icon=None,
            footer_text=None,
            status="success",
        )
        await inter.edit_original_response(content=None, embed=embed)
        try:
            pin = await inter.channel.fetch_message(pin)
            await pin.edit(
                allowed_mentions=disnake.AllowedMentions(users=False),
                content=init_turns,
            )
        except (NotFound, Forbidden, HTTPException):
            pass


def setup(bot):
    bot.add_cog(Initiative(bot))
