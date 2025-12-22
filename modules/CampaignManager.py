import functools
import sys
import typing

import discord
from discord.ext import commands
import datetime
from typing import Union, TYPE_CHECKING

from .CampaignInfo import CampaignInfo
from .errorhandler import TracebackHandler
import shlex
from .Strings import Error, Confirmation

if TYPE_CHECKING:  # TYPE_CHECKING is always false, allows for type hinting without circular import
    from ..DNDBot import DNDBot
    from . import CampaignSQLHelper, CampaignBuilder


def deprecated(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        await args[0].send("This command is deprecated. It should still work, but it might not.")
        return await args[1](*args, **kwargs)

    return wrapper


class CampaignManager(commands.Cog):
    def __init__(self, bot: 'DNDBot'):
        self.bot = bot
        self.CampaignBuilder: CampaignBuilder = self.bot.CampaignBuilder
        self.CampaignSQLHelper: CampaignSQLHelper = self.bot.CampaignSQLHelper
        self.bot.CampaignManager = self

    @commands.command()
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    @deprecated
    async def set_campaign_info(self, context: commands.Context, campaign: Union[int, str], *, info: str):
        """
        :param context: Command context
        :param campaign: Either campaign name or campaign ID
        :param info: The info to set
        :return: None
        """
        if "\n" in info:
            info.replace("\n", """
""")
        async with self.bot.mutex:
            campaign = self.CampaignSQLHelper.select_campaign(campaign)
            commit = self.CampaignSQLHelper.set_campaign_info(campaign, info)
            if commit:
                self.bot.connection.commit()
                # await self.bot.CampaignPlayerManager.update_status(campaign)
                await context.send("Campaign info set.")
            else:
                await context.send("Error setting campaign info")

    @commands.command()
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def delete_category(self, context: commands.Context, category: discord.CategoryChannel):
        """
        :param context: Command context
        :param category: Category to delete
        :return: None
        """
        for i in category.channels:
            await i.delete()
        await category.delete()
        await context.send(f"Category {category.name} deleted.")

    @commands.command()
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    @deprecated
    async def set_campaign_field(self, context: commands.Context, campaign: Union[int, str], field: str, *, value: str):
        """
        :param context: Command context
        :param campaign: Either campaign name or campaign ID
        :param field: The field to set
        :param value: The value to set the field to
        :return: None
        """
        if "\n" in value:
            value.replace("\n", """
""")
        async with self.bot.mutex:
            campaign = self.CampaignSQLHelper.select_campaign(campaign)
            commit = self.CampaignSQLHelper.set_campaign_field(campaign, field, value)
            if commit:
                self.bot.connection.commit()
                # await self.bot.CampaignPlayerManager.update_status(campaign)
            else:
                await context.send("Error setting campaign field")

    @commands.command(aliases=['delete_campaign'])
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def delete_campaign_command(self, context: commands.Context, campaign: Union[int, str], *,
                                      reason="Campaign deleted"):
        """
        :param context: Command context
        :param campaign: Either campaign name (wrapped in quotes) or campaign ID
        :param reason: The reason the campaign was deleted, DM'd to the members of the campaign.
        :return: None
        """
        resp = self.CampaignSQLHelper.select_campaign(campaign)
        if resp is None:
            await channel.send(f"Could not find campaign {campaign}")
            return
        async with self.bot.mutex:
            await context.send(f"Are you sure you want to delete campaign {resp.name} ({resp.id})? (yes/no)")
            try:
                message = await self.bot.wait_for("message", check=lambda m: m.author.id == context.author.id, timeout=60)
            except asyncio.TimeoutError:
                await context.send("Timed out.")
                return
            if message.content.lower() not in ["yes", "y"]:
                await context.send("Cancelled.")
                return
            await context.send("Deleting campaign...")
            await self.delete_campaign(context.channel, resp, reason)

    async def delete_campaign(self, channel: discord.TextChannel, campaign: CampaignInfo, reason="Campaign deleted"):


        members = [i["id"] for i in self.CampaignSQLHelper.get_players(campaign)]

        commit = self.CampaignSQLHelper.delete_campaign(campaign.id)

        commit2 = await self.CampaignBuilder.delete_campaign(campaign)

        status_channel = channel.guild.get_channel(self.bot.config["status_channel"])
        try:
            status_message = await status_channel.fetch_message(campaign.status_message)
            await status_message.delete()
        except Exception:
            pass
        if commit:
            await channel.send(f"Campaign \"{campaign.name}\" deleted.")
            self.bot.connection.commit()
        else:
            await channel.send(f"There was an error deleting \"{campaign.name}\"")
            await self.handle_error()

            return

        if commit2 is None:
            await channel.send(f"There was an error deleting \"{campaign.name}\".")
            return

        for member_id in members:
            member = channel.guild.get_member(member_id)
            if member is None:
                await channel.send(f"Member {member_id} not found, likely left the server")
                continue
            await self.bot.try_send_message(member, channel, Confirmation.CONFIRM_PLAYER_CAMPAIGN_DELETE.format(member=member, campaign=campaign, reason=reason))

    @commands.command()
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def rename_campaign(self, context: commands.Context, campaign: Union[int, str], *, name: str):
        """
        :param context: Command context
        :param campaign: Either campaign name (wrapped in quotes) or campaign ID
        :param name: New campaign name
        :return: None
        """
        async with self.bot.mutex:
            resp = self.CampaignSQLHelper.select_campaign(campaign)
            commit = self.CampaignSQLHelper.rename_campaign(resp, name)

            if commit:
                await context.send(f"Campaign \"{resp.name}\" renamed to \"{name}\".")
                self.bot.connection.commit()
                category: discord.CategoryChannel = context.guild.get_channel(resp.category)
                await category.edit(name=name)

            else:
                await context.send(f"There was an error renaming \"{resp.name}\"")
                await self.handle_error()

    @commands.command()
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def message_players_campaign_deleted(self, context: commands.Context, role: discord.Role):
        for member in role.members:
            self.bot.try_send_message(member, context, f'You have been removed from a campaign due to it being ended by its DM or the '
                                  f'President. Campaign: {role.name}.')
        await context.send("Players messaged.")
        await role.delete()
        await context.send(f"Role {role.name} deleted.")

    @commands.command()
    @commands.has_any_role(809567701735440469, 812785919727894539)
    async def drop_campaign(self, context: commands.Context, campaign: Union[int, str]):
        """
        Will drop a campaign from the database without deleting any channels
        :param context: Command context
        :param campaign: Either campaign name or campaign ID
        :return: None
        """
        async with self.bot.mutex:
            if self.CampaignSQLHelper.delete_campaign(campaign):
                await context.send(f"Campaign {campaign} deregistered.")
                self.bot.connection.commit()

    @commands.command()
    async def list_campaigns(self, context: commands.Context):
        """
        :param context: Command context
        :return: None
        """
        for role in context.author.roles:
            if role.id in [1050188024287338567, 873734392458145912, 809567701735440469]:  # dev, admin, officer
                query = "SELECT * FROM campaigns"
                break
            elif role.id == 812785919727894539:
                # this is dangerous! :D
                query = f"SELECT * FROM campaigns WHERE dm={context.author.id}"

        message_content = ""
        async with self.bot.mutex:
            resp = self.bot.db.execute(query).fetchall()
        for row in resp:
            message_content += f"{row['id']}: {row['name']}, DM: {str(context.guild.get_member(row['dm']))}, " \
                               f"{row['current_players']}/{row['max_players']} {'Locked' if row['locked'] else ''}\n"

        if len(message_content) <= 2000:
            await context.send("```\n" + message_content + "```")
            return
        else:
            campaigns = message_content.split("\n")
            message_1 = campaigns[:len(campaigns) // 2]
            message_2 = campaigns[len(campaigns) // 2:]
            await context.send("```\n" + '\n'.join(message_1) + "```")
            await context.send("```\n" + '\n'.join(message_2) + "```")

    @commands.command(aliases=["lock"])
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def lock_campaign(self, context: commands.Context, campaign: Union[int, str]):
        """
        :param context: Command context
        :param campaign: Either campaign name or campaign ID
        :return: None
        """
        async with self.bot.mutex:
            await self.update_lock_status(context.channel, campaign, 1)

    @commands.command(aliases=["unlock"])
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def unlock_campaign(self, context: commands.Context, campaign: Union[int, str]):
        """
        :param context: Command context
        :param campaign: Either campaign name or campaign ID
        :return: None
        """
        async with self.bot.mutex:
            await self.update_lock_status(context.channel, campaign, 0)

    async def update_lock_status(self, channel: discord.TextChannel, campaign: Union[int, str], status: int):
        campaign = self.CampaignSQLHelper.select_campaign(campaign)
        campaign.locked = status
        commit = self.CampaignSQLHelper.set_campaign_status(campaign, status)  # unlock
        if commit:
            self.bot.connection.commit()
            await channel.send(f"Campaign {campaign.name} {'un' if status == 0 else ''}locked.")
            if (member := channel.guild.get_member(campaign.dm)) != None:
                to_send = getattr(Confirmation, "CONFIRM_DM_CAMPAIGN_" + "LOCK" if status else "UNLOCK").value
                await self.bot.try_send_message(member, channel, to_send)
        else:
            print(f"Error {'un' if status == 0 else ''}locking campaign")

    @commands.command()
    async def list_players(self, context: commands.Context, campaign: Union[int, str]):
        admin = False
        dm = False
        for role in context.author.roles:
            if role.id in [1050188024287338567, 873734392458145912, 809567701735440469]:  # dev, admin, officer
                admin = True
                # we don't care if they are also a dm, they can see all campaigns
                break
            elif role.id == 812785919727894539:
                # they might also be an admin so we dont break here
                dm = True
        if not admin and not dm:
            return

        async with self.bot.mutex:
            campaign = self.CampaignSQLHelper.select_campaign(campaign)
            if (not admin) and dm and (campaign.dm != context.author.id):
                return
            players = self.CampaignSQLHelper.get_players(campaign)
            if players is None:
                await context.send("An error occurred.")
                return
            message = ""
            for i in players:
                if (member := context.guild.get_member(i["id"])) is not None:
                    message += f"{member.display_name} ({member.id})\n"
                else:
                    message += f"Could not resolve user {i['id']} -- Perhaps they left?\n"

            await context.send(message)

    async def handle_error(self):
        exc_type, exc_name, exc_traceback = sys.exc_info()
        channel = self.bot.get_channel(self.bot.config["staff_botspam"])
        err_code = 255
        for i in range(len(self.bot.traceback) + 1):
            if i in self.bot.traceback:
                continue
            err_code = i
        original = getattr(exc_traceback, '__cause__', exc_traceback)
        handler = TracebackHandler(err_code, f"{exc_type.__name__}: {str(exc_name)}", original)
        self.bot.traceback[err_code] = handler
        await channel.send(f"An error occurred. Error code: {str(err_code)}")

    @commands.command()
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def fix_perms(self, context: commands.Context, campaign_id: int):
        async with self.bot.mutex:
            campaign = self.CampaignSQLHelper.select_campaign(campaign_id)
            channel: discord.CategoryChannel = context.guild.get_channel(campaign.category)
            guild = channel.guild
            role = guild.get_role(campaign.role)
            dm = guild.get_member(campaign.dm)
            overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                          role: discord.PermissionOverwrite(send_messages=True, read_messages=True),
                          dm: discord.PermissionOverwrite(manage_channels=True, manage_permissions=True,
                                                          send_messages=True, manage_messages=True)
                          }
            await channel.edit(overwrites=overwrites)
            for i in channel.channels:
                await i.edit(overwrites=overwrites)
            await context.send(f"Permissions have been fixed for {campaign.name}")

    @commands.command()
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def update_campaign(self, context: commands.Context, campaign: int = None, *, kwargs = None):
        if campaign == None or kwargs == None or "=" not in kwargs:
            message = """Usage: `>update_campaign <campaign_id> <field1=value> <field2=value> ...`
Example: `>update_campaign 1 name="New Campaign Name" min_players=3 max_players=6`

Valid Fields:
```
name: str
min_players: int
max_players: int
info_message: str
location: str
playstyle: str
session_length: str
meeting_frequency: [Once every other week, Once every week, Once (one-shot)]
meeting_day: str
meeting_time: HH:MM (24hr)
meeting_date: YYYY-MM-DD
system: str
new_player_friendly: [Yes, No]
```
"""
            await context.send(message)
            return
        async with self.bot.mutex:
            campaign = self.CampaignSQLHelper.select_campaign(campaign)
            kwargs = kwargs.replace("“", "\"").replace("”", "\"")  # replace smart quotes with normal quotes
            args = shlex.split(kwargs)
            print(args)
            fields = []
            values = []
            for arg in args:
                print(arg)
                key, value = arg.split("=")
                fields.append(key)
                values.append(value)
                self.CampaignSQLHelper.set_campaign_field(campaign, key, value)
            self.bot.connection.commit()
            await context.send(
                "Campaign updated with\n" + "\n".join([f"{fields[i]}={values[i]}" for i in range(len(fields))]))

    @commands.command()
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def pause_campaign(self, context: commands.Context, campaign_id: int):
        campaign = self.bot.CampaignSQLHelper.select_campaign(campaign_id)
        await self.pause_resume_campaign(context, campaign, "pause")



    @commands.command(aliases=["unpause_campaign"])
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def resume_campaign(self, context: commands.Context, campaign_id: int):
        campaign = self.bot.CampaignSQLHelper.select_campaign(campaign_id)
        await self.pause_resume_campaign(context, campaign, "resume")

    async def pause_resume_campaign(self, context: commands.Context, campaign: CampaignInfo, action: str):
        if not getattr(self.bot.CampaignSQLHelper, action + "_campaign")(campaign):
            await context.send(f"There was an error while trying to {action} {campaign.name}")
            return
        category: discord.CategoryChannel = context.guild.get_channel(campaign.category)
        campaign_role = context.guild.get_role(campaign.role)
        for i in category.text_channels:
            overwrites = i.overwrites
            overwrites[campaign_role] = discord.PermissionOverwrite(send_messages=True if action == "resume" else False)
            await i.edit(overwrites=overwrites)

        player_confirm_enum = getattr(Confirmation, "CONFIRM_PLAYER_CAMPAIGN_" + action.upper())
        dm = context.guild.get_member(campaign.dm)

        players = [i["id"] for i in self.CampaignSQLHelper.get_players(campaign)]
        for player in players:
            member = context.guild.get_member(player)
            player_confirm_str = player_confirm_enum.value.format(member=member, campaign=campaign)
            if member == None:
                await context.send(f"Error: player {player} not found")
                continue
            await self.bot.try_send_message(member, context, player_confirm_str)

        dm_confirm_enum = getattr(Confirmation, "CONFIRM_DM_CAMPAIGN_" + action.upper())
        dm_confirm_str = dm_confirm_enum.value.format(member=dm, campaign=campaign)

        dm = context.guild.get_member(campaign.dm)
        await self.bot.try_send_message(dm, context, dm_confirm_str)
        await context.send(f"Campaign {campaign.name} {action}d succsesfully.")


    @commands.command()
    @commands.has_any_role(1050188024287338567, 873734392458145912, 809567701735440469)  # dev, admin, officer
    async def verify_dms(self, context: commands.Context):
        async with self.bot.mutex:
            async with context.typing():
                response = ""
                campaigns = self.CampaignSQLHelper.get_campaigns()
                for campaign in campaigns:
                    dm = context.guild.get_member(campaign["dm"])
                    if dm is None:
                        response += f"Could not resolve user {campaign['dm']} for campaign {campaign['name']}\n"
                await context.send(response)

    @commands.command()
    @commands.is_owner()
    async def create_dummy_campaign(self, context: commands.Context):
        await self.bot.CampaignBuilder.create_campaign(context.guild, "Test Campaign", context.author)
        await context.send("done")

async def setup(bot):
    await bot.add_cog(CampaignManager(bot))
