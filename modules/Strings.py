from enum import StrEnum


class Error(StrEnum):
    ERROR_CLOSED_DMS = ("Error: Could not DM {member.display_name} ({member.mention}). They likely have their DMs "
                        "closed.")
    """
    Requires member: discord.Member
    """
    ERROR_UNKNOWN_DMS = "An unknown error occurred: Could not DM {member.display_name} ({member.mention})"
    ERROR_UNK = "An unknown error occurred."

    ERROR_VERIFICATION_CLOSED_DMS = ("{member.mention}: I was unable to DM you. Please open your DMs to this server, "
                                     "as I will send campaign updates via DM in the future. Once you have done that, "
                                     "you will need to re-react to the verification reaction.")
    """
    Requires member: discord.Member
    """

    def __str__(self):
        return self.value


class Confirmation(StrEnum):
    CONFIRM_PLAYER_CAMPAIGN_PAUSE = ("{member.display_name}: This is a notification that a campaign you're in has been "
                                     "paused. The channels for the campaign will be locked, and the campaign will not "
                                     "hold any sessions until it is unpaused. Please reach out to your DM for more "
                                     "information. If you wish to leave the campaign at any time, you may do so "
                                     "through the Leave a Campaign form found in <#812549890227437588> or "
                                     "<#823698349243760670>. Campaign: {campaign.name}.")
    """
    Requires member: discord.Member, campaign: CampaignInfo
    """
    CONFIRM_DM_CAMPAIGN_PAUSE = ("{member.display_name}: This is a notification that your request to pause a campaign "
                                  "has been processed. The channels will be locked and the players will be notified. "
                                  "To unpause the campaign, please fill out the same form found in "
                                  "<#823698349243760670> in the Dungeon Masters category. Campaign: {campaign.name}.")
    """
    Requires member: discord.Member, campaign: CampaignInfo
    """
    CONFIRM_PLAYER_CAMPAIGN_RESUME = ("{member.display_name}: This is a notification that a campaign you’re in has "
                                      "been unpaused. The channels for the campaign are now unlocked, "
                                      "and the campaign may resume holding sessions. Please reach out to your DM for "
                                      "more information. If you wish to leave the campaign, you may do so through the "
                                      "Leave a Campaign form found in <#812549890227437588> or <#823698349243760670>. "
                                      "Campaign: {campaign.name}.")
    """
    Requires member: discord.Member, campaign: CampaignInfo
    """
    CONFIRM_DM_CAMPAIGN_RESUME = ("{member.display_name}: This is a notification that your request to unpause a "
                                  "campaign has been processed. The channels are now unlocked and the players will be "
                                  "notified. Please note that now that the campaign is unpaused, sessions should "
                                  "resume. To end the campaign, please fill out the same form found in "
                                  "<#823698349243760670> in the Dungeon Masters category. Campaign: {campaign.name}.")
    """
    Requires member: discord.Member, campaign: CampaignInfo
    """

    CONFIRM_PLAYER_CAMPAIGN_DELETE = ("{member.display_name}: You have been removed from a campaign due to it being "
                                      "ended by its DM or the President. Campaign: {campaign.name}. Reason: {reason}.")
    """
    Requires member: discord.Member, campaign: CampaignInfo, reason: str
    """

    CONFIRM_PLAYER_CAMPAIGN_REMOVE = ("{member.display_name}: This is a notification that you have been removed from "
                                      "the campaign {campaign.name}. Please contact the President or the Campaign "
                                      "Master if you think this was a mistake.")
    """
    Requires member: discord.Member, campaign: CampaignInfo
    """
    CONFIRM_DM_CAMPAIGN_REMOVE = ("{dm.mention}: This is a notification that {member.mention} has been removed from "
                                  "the campaign {campaign.name}. Please contact the President or the Campaign Master "
                                  "if you think this was a mistake.")
    """
    Requires dm: discord.Member, member: discord.Member, campaign: CampaignInfo
    """
    CONFIRM_PLAYER_CAMPAIGN_ADD = ("{member.display_name}: This is a notification that you have been approved and "
                                   "added to a campaign. If you ever wish to leave the campaign, please use the Leave "
                                   "a Campaign form found in <#812549890227437588>. Campaign: {campaign.name}.")
    """
    Requires member: discord.Member, campaign: CampaignInfo
    """

    CONFIRM_PLAYER_VERIFICATION_DENIED = (
        "Your verification has been denied due to your nickname not following the instructions as "
        "described in {channel.mention}. If you believe this to be a mistake, please contact the "
        "President.")
    """
    Requires channel: TextChannel
    """

    CONFIRM_PLAYER_CAMPAIGN_DENIED = ("{member.display_name}: You have been denied from {campaign.name}. This is an "
                                      "automated message. If you believe this to be a mistake, please contact the "
                                      "Campaign Master.")
    """
    Requires member: discord.Member, campaign: CampaignInfo
    """
    CONFIRM_DM_CAMPAIGN_DENIED = "{member.mention} application for the campaign {campaign.name} has been denied by the DM."
    """
    Requires member: discord.Member, campaign: CampaignInfo
    """
    CONFIRM_PLAYER_WAITLIST_DENY = ("{member.display_name}: You have been denied from {campaign.name}, which you were "
                                    "on the waitlist for. This is an automated message. If you believe this to be a "
                                    "mistake, please contact the Campaign Master.")
    """
    Requires member: discord.Member, campaign: CampaignInfo
    """
    CONFIRM_DM_WAITLIST_DENY = "{member.mention} waitlisted application for the campaign {campaign.name} has been denied by the DM."
    """
    Requires member: discord.Member, campaign: CampaignInfo
    """

    CONFIRM_DM_CAMPAIGN_LOCK = "{member.display_name}: This is a notification that your request to lock a campaign has been processed. While locked, no new applications can be made for the campaign. To unlock the campaign, please fill out the same form found in <#823698349243760670> in the Dungeon Masters category. Campaign: {campaign.name}"
    CONFIRM_DM_CAMPAIGN_UNLOCK = "{member.display_name}: This is a notification that your request to unlock a campaign has been processed. New applications can now be made for the campaign. Campaign: {campaign.name}"



    def __str__(self):
        return self.value


class New(StrEnum):
    NEW_CAMPAIGN_INFO_MESSAGE = (
        "Here is where the Dungeon Master can post important information regarding the campaign that players "
        "may need to refer back to. This information can include a description of the **location** the "
        "campaign takes place in, the **mission** the players are taking on, and a **map** of the land.")

    NEW_CAMPAIGN_NOTES_MESSAGE = (
        "This is where players and the DM can post notes that they want to remember. Meet an important "
        "character? Write it down! Don't wanna forget a tidbit of information a character gave you? Write it "
        "down! Keep in mind the DM may ask you not to write down notes if they choose to.")

    NEW_CAMPAIGN_PICS_MESSAGE = (
        "This is where anyone can post pictures of their characters, locations, etc. Be sure to label it so "
        "you can refer back to it later! ")

    NEW_CAMPAIGN_ANNOUNCEMENT_MESSAGE = (
        "Welcome to the **{campaign.name}** campaign category! This is where your Dungeon Master can post "
        "announcements, information, and other important information regarding the campaign. "
        "Players and the DM may also communicate in #lobby. If your sessions are virtual, "
        "they will be held through this category's voice channel. Let me know if you have any "
        "questions, and have fun!")
    """
    Requires campaign: CampaignInfo
    """
