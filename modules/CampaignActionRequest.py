import functools
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from ..DNDBot import DNDBot

class CampaignActionRequest(commands.Cog):
    def __init__(self, bot: 'DNDBot'):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != 955932420262232065:
            return

        if message.author.bot and message.embeds:
            embed = message.embeds[0]
            if not embed.title.startswith("Campaign Action Request"):
                return
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.channel_id != 955932420262232065:
            return
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if not message.embeds:
            return
        embed = message.embeds[0]
        if not embed.title.startswith("Campaign Action Request"):
            return
        roles = [self.bot.config["admin_role"], self.bot.config["developer_role"]]
        if not any(role in [role.id for role in payload.member.roles] for role in roles):
            await message.remove_reaction(payload.emoji, payload.member)

        first, last = embed.fields[0].value, embed.fields[1].value
        discord_user = embed.fields[2].value
        campaign = int(embed.fields[3].value)
        action = embed.fields[4].value
        reason = '\n'.join([i.value for i in embed.fields[7::]])
        campaign = await self.bot.CampaignSQLHelper.select_campaign(campaign)
        if action.startswith("End"):
            result = await ActionHandler.end(self.bot, message.channel, campaign.id, payload.member, reason)
        elif action.startswith("Leave"):
            result = await ActionHandler.leave(self.bot, message.channel, campaign.id, payload.member)
        elif action.startswith("Pause"):
            result = await ActionHandler.pause(self.bot, message.channel, campaign.id, payload.member)
        elif action.startswith("Resume"):
            result = await ActionHandler.resume(self.bot, message.channel, campaign.id, payload.member)
        elif action.startswith("Lock"):
            result = await ActionHandler.lock(self.bot, message.channel, campaign.id, payload.member)
        elif action.startswith("Unlock"):
            result = await ActionHandler.unlock(self.bot, message.channel, campaign.id, payload.member)
        elif action.startswith("Update"):
            result = await ActionHandler.update(self.bot, message.channel, campaign.id, payload.member)
        else:
            result = False
        if result:
            await message.edit(content=f"✅ {action} request for {first} {last} ({discord_user}) in campaign "
                                       f"{campaign.name} processed successfully.", embeds=[])
        else:
            await message.channel.send(f"Failed to process {action} request for {first} {last} ({discord_user}) in campaign "
                                       "{campaign.name}.")


def dm_check(func):
    @functools.wraps(func)
    async def wrapper(bot: 'DNDBot', channel: discord.TextChannel, campaign, member: discord.Member, *args, **kwargs):
        # look up campaign object for permission check, but call the wrapped function
        # with the original campaign identifier so existing methods keep working
        campaign_obj = await bot.CampaignSQLHelper.select_campaign(campaign)
        if member.id != campaign_obj.dm:
            await channel.send("Only the DM can request this, this request has been denied.")
            return False
        try:
            return await func(bot, channel, campaign, member, *args, **kwargs)
        except Exception as e:
            await channel.send(f"Failed to process request: {e}")
            return False

    return wrapper

class ActionHandler:

    @staticmethod
    async def leave(bot: 'DNDBot', channel: discord.TextChannel, campaign: int, member: discord.Member) -> bool:
        try:
            await bot.CampaignPlayerManager.remove_player(channel, member, campaign)

            return True
        except Exception as e:
            await channel.send(f"Failed to leave campaign: {e}")
            return False

    @staticmethod
    @dm_check
    async def end(bot: 'DNDBot', channel: discord.TextChannel, campaign: int, member: discord.Member, reason = "DM's request") -> bool:
        try:
            await bot.CampaignManager.delete_campaign(channel, campaign, reason)
            campaign = await bot.CampaignSQLHelper.select_campaign(channel, campaign)
            dm = channel.guild.get_member(campaign.dm)
            await dm.send(f"This is a notification that your request to end a campaign has been processed. The "
                          f"campaign will be deleted and the players will be notified. Campaign: {campaign.name}.")
            return True

        except Exception as e:
            await channel.send(f"Failed to end campaign: {e}")
            return False

    @staticmethod
    @dm_check
    async def pause(bot: 'DNDBot', channel: discord.TextChannel, campaign: int, member: discord.Member) -> bool:
        campaign_info = await bot.CampaignSQLHelper.select_campaign(campaign)
        category: discord.CategoryChannel = channel.guild.get_channel(campaign_info.category)
        campaign_role = channel.guild.get_role(campaign_info.role)

        commit = await bot.CampaignSQLHelper.pause_campaign(campaign)
        if commit:
            for i in category.channels:
                await i.set_permissions(campaign_role, send_messages=False)
            players = bot.CampaignSQLHelper.get_players(campaign)
            for i in players:
                member = channel.guild.get_member(i)
                await member.send(f"This is a notification that a campaign you’re in has been paused. The channels for "
                                  f"the campaign will be locked, and the campaign will not hold any sessions until it "
                                  f"is unpaused. Please reach out to your DM for more information. If you wish to "
                                  f"leave the campaign at any time, you may do so through the Leave a Campaign form "
                                  f"found in <#812549890227437588> or <#823698349243760670>. Campaign: "
                                  f"{campaign_info.name}.")
            dm = channel.guild.get_member(campaign_info.dm)
            await dm.send(f"This is a notification that your request to pause a campaign has been processed. The "
                          f"channels will be locked and the players will be notified. To unpause the campaign, please "
                          f"fill out the same form found in <#823698349243760670> in the Dungeon Masters category. "
                          f"Campaign: {campaign_info.name}.")
            await channel.send(f"Campaign {campaign_info.name} paused")
            return True
        else:
            await channel.send("Failed to pause campaign")
            return False

    @staticmethod
    @dm_check
    async def resume(bot: 'DNDBot', channel: discord.TextChannel, campaign: int, member: discord.Member) -> bool:
        campaign_info = await bot.CampaignSQLHelper.select_campaign(campaign)
        category: discord.CategoryChannel = channel.guild.get_channel(campaign_info.category)
        campaign_role = channel.guild.get_role(campaign_info.role)

        commit = await bot.CampaignSQLHelper.resume_campaign(campaign)
        if commit:
            for i in category.channels:
                await i.set_permissions(campaign_role, send_messages=True)
            players = bot.CampaignSQLHelper.get_players(campaign)
            for i in players:
                member = channel.guild.get_member(i)
                await member.send(f"This is a notification that a campaign you’re in has been resumed. The channels "
                                  f"for the campaign will be unlocked. Campaign: {campaign_info.name}.")
            dm = channel.guild.get_member(campaign_info.dm)
            await dm.send(f"This is a notification that your request to resume a campaign has been processed. The "
                          f"channels will be unlocked and the players will be notified. "
                          f"Campaign: {campaign_info.name}.")
            return True
        else:
            await channel.send("Failed to resume campaign")
            return False

    @staticmethod
    @dm_check
    async def lock(bot: 'DNDBot', channel: discord.TextChannel, campaign: int, member: discord.Member) -> bool:
        try:
            await bot.CampaignManager.update_lock_status(channel, campaign, 1)
            campaign_info = await bot.CampaignSQLHelper.select_campaign(channel, campaign)
            dm = channel.guild.get_member(campaign_info.dm)
            await dm.send(f"This is a notification that your request to lock a campaign has been processed. New "
                          f"players will not be able to apply until the campaign has been unlocked. "
                          f"Campaign: {campaign_info.name}.")
            return True
        except Exception as e:
            await channel.send(f"Failed to lock campaign: {e}")
            return False

    @staticmethod
    @dm_check
    async def unlock(bot: 'DNDBot', channel: discord.TextChannel, campaign: int, member: discord.Member) -> bool:
        try:
            await bot.CampaignManager.update_lock_status(channel, campaign, 0)
            campaign_info = await bot.CampaignSQLHelper.select_campaign(channel, campaign)
            dm = channel.guild.get_member(campaign_info.dm)
            await dm.send(f"This is a notification that your request to unlock a campaign has been processed. New "
                          f"players will be able to apply for the campaign. Campaign: {campaign_info.name}.")
            return True
        except Exception as e:
            await channel.send(f"Failed to unlock campaign: {e}")
            return False

    @staticmethod
    @dm_check
    async def update(bot: 'DNDBot', channel: discord.TextChannel, campaign: int, member: discord.Member) -> bool:
        try:
            await bot.CampaignPlayerManager.set_max_player_count(channel, campaign, int(embed.fields[4].value))
            campaign_info = await bot.CampaignSQLHelper.select_campaign(channel, campaign)
            dm = channel.guild.get_member(campaign_info.dm)
            await dm.send(f"This is a notification that your request to update the max player count for a campaign has "
                          f"been processed. Campaign: {campaign_info.name}.")
            return True
        except Exception as e:
            await channel.send(f"Failed to update campaign: {e}")
            return False
