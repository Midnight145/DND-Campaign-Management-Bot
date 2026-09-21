import discord

from DNDBot import DNDBot
from modules import CampaignInfo
from modules.api.structs import CampaignActionRequest


class ActionEmbedCreator:
    # todo: add campaign id to embed

    @staticmethod
    def leave(campaign_action: CampaignActionRequest, campaign: CampaignInfo) -> discord.Embed:
        embed = discord.Embed(
            title="Campaign Action Request - Leave Campaign",
            color=discord.Color.red(),
        )
        embed.add_field(name="First Name", value=campaign_action.first_name)
        embed.add_field(name="Last Name", value=campaign_action.last_name)
        embed.add_field(name="Discord ID", value=campaign_action.id)
        embed.add_field(name="Campaign Name", value=campaign.name)
        if campaign_action.reasons:
            embed.add_field(name="Reasons", value="\n".join(campaign_action.reasons))
        if campaign_action.elaboration:
            embed.add_field(name="Elaboration", value=campaign_action.elaboration)
        return embed

    @staticmethod
    def end(campaign_action: CampaignActionRequest, campaign: CampaignInfo) -> discord.Embed:
        embed = discord.Embed(
            title="Campaign Action Request - End Campaign",
            color=discord.Color.red(),
        )
        embed.add_field(name="First Name", value=campaign_action.first_name)
        embed.add_field(name="Last Name", value=campaign_action.last_name)
        embed.add_field(name="Discord ID", value=campaign_action.id)
        embed.add_field(name="Campaign Name", value=campaign.name)
        if campaign_action.reasons:
            embed.add_field(name="Reasons", value="\n".join(campaign_action.reasons))
        if campaign_action.elaboration:
            embed.add_field(name="Elaboration", value=campaign_action.elaboration)
        return embed

    @staticmethod
    def pause(campaign_action: CampaignActionRequest, campaign: CampaignInfo) -> discord.Embed:
        embed = discord.Embed(
            title="Campaign Action Request - Pause Campaign",
            color=discord.Color.red(),
        )
        embed.add_field(name="First Name", value=campaign_action.first_name)
        embed.add_field(name="Last Name", value=campaign_action.last_name)
        embed.add_field(name="Discord ID", value=campaign_action.id)
        embed.add_field(name="Campaign Name", value=campaign.name)
        if campaign_action.reasons:
            embed.add_field(name="Reasons", value="\n".join(campaign_action.reasons))
        if campaign_action.elaboration:
            embed.add_field(name="Elaboration", value=campaign_action.elaboration)
        return embed

    @staticmethod
    def resume(campaign_action: CampaignActionRequest, campaign: CampaignInfo) -> discord.Embed:
        embed = discord.Embed(
            title="Campaign Action Request - Resume Campaign",
            color=discord.Color.red(),
        )
        embed.add_field(name="First Name", value=campaign_action.first_name)
        embed.add_field(name="Last Name", value=campaign_action.last_name)
        embed.add_field(name="Discord ID", value=campaign_action.id)
        embed.add_field(name="Campaign Name", value=campaign.name)
        if campaign_action.reasons:
            embed.add_field(name="Reasons", value="\n".join(campaign_action.reasons))
        if campaign_action.elaboration:
            embed.add_field(name="Elaboration", value=campaign_action.elaboration)
        return embed

    @staticmethod
    def lock(campaign_action: CampaignActionRequest, campaign: CampaignInfo) -> discord.Embed:
        embed = discord.Embed(
            title="Campaign Action Request - Lock Campaign",
            color=discord.Color.red(),
        )
        embed.add_field(name="First Name", value=campaign_action.first_name)
        embed.add_field(name="Last Name", value=campaign_action.last_name)
        embed.add_field(name="Discord ID", value=campaign_action.id)
        embed.add_field(name="Campaign Name", value=campaign.name)
        if campaign_action.reasons:
            embed.add_field(name="Reasons", value="\n".join(campaign_action.reasons))
        if campaign_action.elaboration:
            embed.add_field(name="Elaboration", value=campaign_action.elaboration)
        return embed

    @staticmethod
    def unlock(campaign_action: CampaignActionRequest, campaign: CampaignInfo) -> discord.Embed:
        embed = discord.Embed(
            title="Campaign Action Request - Unlock Campaign",
            color=discord.Color.red(),
        )
        embed.add_field(name="First Name", value=campaign_action.first_name)
        embed.add_field(name="Last Name", value=campaign_action.last_name)
        embed.add_field(name="Discord ID", value=campaign_action.id)
        embed.add_field(name="Campaign Name", value=campaign.name)
        if campaign_action.reasons:
            embed.add_field(name="Reasons", value="\n".join(campaign_action.reasons))
        if campaign_action.elaboration:
            embed.add_field(name="Elaboration", value=campaign_action.elaboration)
        return embed

    @staticmethod
    def update(campaign_action: CampaignActionRequest, campaign: CampaignInfo) -> discord.Embed:
        embed = discord.Embed(
            title="Campaign Action Request - Update Campaign",
            color=discord.Color.red(),
        )
        embed.add_field(name="First Name", value=campaign_action.first_name)
        embed.add_field(name="Last Name", value=campaign_action.last_name)
        embed.add_field(name="Discord ID", value=campaign_action.id)
        embed.add_field(name="Campaign Name", value=campaign.name)
        embed.add_field(name="New Player Count", value=campaign_action.new_player_count)
        if campaign_action.reasons:
            embed.add_field(name="Reasons", value="\n".join(campaign_action.reasons))
        if campaign_action.elaboration:
            embed.add_field(name="Elaboration", value=campaign_action.elaboration)
        return embed


class ActionHandler:

    @staticmethod
    async def leave(bot: DNDBot, channel: discord.TextChannel, campaign: int, embed: discord.Embed) -> bool:
        try:
            member = channel.guild.get_member(int(embed.fields[2].value))
            await bot.CampaignPlayerManager.remove_player(channel, member, campaign)

            return True
        except Exception as e:
            await channel.send(f"Failed to leave campaign: {e}")
            return False

    @staticmethod
    async def end(bot: DNDBot, channel: discord.TextChannel, campaign: int, embed: discord.Embed) -> bool:
        try:
            if len(embed.fields) >= 5:
                reason = embed.fields[4].value
                await bot.CampaignManager.delete_campaign(channel, campaign, reason)
            else:
                await bot.CampaignManager.delete_campaign(channel, campaign)
            campaign = await bot.CampaignSQLHelper.select_campaign(channel, campaign)
            dm = channel.guild.get_member(campaign.dm)
            await dm.send(f"This is a notification that your request to end a campaign has been processed. The "
                          f"campaign will be deleted and the players will be notified. Campaign: {campaign.name}.")
            return True

        except Exception as e:
            await channel.send(f"Failed to end campaign: {e}")
            return False

    @staticmethod
    async def pause(bot: DNDBot, channel: discord.TextChannel, campaign: int, embed: discord.Embed) -> bool:
        campaign_info = await bot.CampaignSQLHelper.select_campaign(channel, campaign)
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
    async def resume(bot: DNDBot, channel: discord.TextChannel, campaign: int, embed: discord.Embed) -> bool:
        campaign_info = await bot.CampaignSQLHelper.select_campaign(channel, campaign)
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
    async def lock(bot: DNDBot, channel: discord.TextChannel, campaign: int, embed: discord.Embed) -> bool:
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
    async def unlock(bot: DNDBot, channel: discord.TextChannel, campaign: int, embed: discord.Embed) -> bool:
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
    async def update(bot: DNDBot, channel: discord.TextChannel, campaign: int, embed: discord.Embed) -> bool:
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
