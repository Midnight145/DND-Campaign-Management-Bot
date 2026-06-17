import datetime
import json
import typing

import discord
from fastapi import Response, status, APIRouter

from DNDBot import DNDBot
from modules.api.Permissions import permissions, Permissions
from .CampaignActionHandler import ActionEmbedCreator
from .returned_structs import UserInfo
from .structs import CampaignApplication, PartialCampaignInfo, CampaignActionRequest, UserUpdateRequest, \
    UserUpdateManyRequest
from .. import CampaignInfo, CampaignSQLHelper

router = APIRouter()
# noinspection PyTypeChecker
guild: discord.Guild = None


def init_guild():
    global guild
    if guild is None:
        guild = DNDBot.instance.get_guild(DNDBot.instance.config["server"])


async def get_user_helper(user_id: int) -> (str, int):
    user = await guild.fetch_member(user_id)
    user_info = DNDBot.instance.db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user_info is None:
        user_info = {"first_name": "", "last_name": "", "unt_email": "", "unt_student": 0, "playstyle": ""}

    resp = UserInfo()
    resp.id = user.id
    resp.name = user.name
    resp.discriminator = user.discriminator
    resp.nickname = user.display_name
    resp.campaigns_player = []
    resp.campaigns_dm = []
    resp.warnings = {}
    resp.first_name = user_info["first_name"]
    resp.last_name = user_info["last_name"]
    resp.unt_email = user_info["unt_email"]
    resp.unt_student = bool(user_info["unt_student"])
    resp.playstyle = user_info["playstyle"]

    res = DNDBot.instance.db.execute("select id, reason from warns where member = ?", (user.id,)).fetchall()
    for i in res:
        # resp["warnings"][str(i["id"])] = i["reason"]
        resp.warnings[i["id"]] = i["reason"]

    if user is None:
        user = DNDBot.instance.get_user(user_id)
        if user is None:
            return json.dumps({"error": "User not found"}), 404

        return json.dumps(resp.__dict__)
        # resp = {"id": user.id, "name": user.name, "discriminator": user.discriminator, "nickname": user.display_name,
        #         "in_discord": False, "officer": False, "developer": False, "verified": False, "guest": False,
        #         "player": False, "dm": False, "banned_player": False, "banned_dm": False, "joined": "",
        #         "campaigns_player": [], "campaigns_dm": [], "warnings": {}, "first_name": user_info["first_name"],
        #         "last_name": user_info["last_name"], "unt_email": user_info["unt_email"],
        #         "unt_student": bool(user_info["unt_student"]),
        #         "playstyle": user_info["playstyle"], user_info["bio"]: "", user_info["pronouns"]: "",
        #         user_info["image"]: "", user_info["position"]: ""
        #         }
        # return json.dumps(resp)

    officer_role = guild.get_role(DNDBot.instance.config["officer_role"])
    developer_role = guild.get_role(DNDBot.instance.config["developer_role"])
    verified_role = guild.get_role(DNDBot.instance.config["verified_role"])
    guest_role = guild.get_role(DNDBot.instance.config["guest_role"])
    player_role = guild.get_role(DNDBot.instance.config["member_role"])
    dm_role = guild.get_role(DNDBot.instance.config["dm_role"])
    banned_player_role = guild.get_role(DNDBot.instance.config["banned_player_role"])
    banned_dm_role = guild.get_role(DNDBot.instance.config["banned_dm_role"])

    resp.in_discord = True
    resp.officer = officer_role in user.roles
    resp.developer = developer_role in user.roles
    resp.verified = verified_role in user.roles
    resp.guest = guest_role in user.roles
    resp.player = player_role in user.roles
    resp.dm = dm_role in user.roles
    resp.banned_player = banned_player_role in user.roles
    resp.banned_dm = banned_dm_role in user.roles
    resp.joined = user.joined_at.isoformat()

    # resp = {"id": user.id, "name": user.name, "discriminator": user.discriminator, "nickname": user.display_name,
    #         "in_discord": True, "officer": officer_role in user.roles, "developer": developer_role in user.roles,
    #         "verified": verified_role in user.roles, "guest": guest_role in user.roles,
    #         "player": player_role in user.roles, "dm": dm_role in user.roles,
    #         "banned_player": banned_player_role in user.roles, "banned_dm": banned_dm_role in user.roles,
    #         "joined": user.joined_at.isoformat(), "campaigns_player": [], "campaigns_dm": [], "warnings": {},
    #         "first_name": user_info["first_name"],
    #         "last_name": user_info["last_name"], "unt_email": user_info["unt_email"],
    #         "unt_student": bool(user_info["unt_student"]), "playstyle": user_info["playstyle"]}

    res = DNDBot.instance.db.execute("select * from campaigns where dm = ?", (user.id,)).fetchall()
    for i in res:
        # resp["campaigns_dm"].append(i["id"])
        resp.campaigns_dm.append(i["id"])
    res = DNDBot.instance.db.execute("select * from players where id = ? and waitlisted = 0", (user.id,)).fetchall()
    for i in res:
        # resp["campaigns_player"].append(i["campaign"])
        resp.campaigns_player.append(i["campaign"])

    return json.dumps(resp.__dict__), 200


@router.get("/images/{cid}")
async def get_image(cid: str):
    with open(f"/home/ryan/Development/CAGBot/images/{cid}.png", "rb") as file:
        return Response(file.read(), media_type="image/png")


@router.get("/campaigns")
@permissions(Permissions.CAMPAIGN_READ)
async def get_campaigns(auth: str, response: Response):
    init_guild()
    campaigns = DNDBot.instance.CampaignSQLHelper.get_campaigns()
    for val in campaigns:
        dm = guild.get_member(val["dm"])
        if dm is None:
            val["dm_username"] = "Unknown"
            val["dm_nickname"] = "Unknown"
        else:
            val["dm_username"] = dm.name
            val["dm_nickname"] = dm.display_name
        players = DNDBot.instance.db.execute(f"SELECT * FROM players WHERE campaign = ?",
                                             (val["id"],)).fetchall()
        val["players"] = [i["id"] for i in players if i["waitlisted"] == 0]
        val["waitlist"] = [i["id"] for i in players if i["waitlisted"] == 1]
        val["date_created"] = val["timestamp"]
    return json.dumps(campaigns)


@router.get("/campaigns/getmany/{id_list}")
@permissions(Permissions.CAMPAIGN_READ)
async def get_many_campaign(id_list: str, auth: str, response: Response):
    init_guild()
    if '[' in id_list:
        id_list = id_list[1:-1]
    if id_list == "":
        return json.dumps({})
    try:
        campaign_ids = [int(i) for i in id_list.split(",")]
    except ValueError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return json.dumps({"error": "IDs must be valid integers."})
    campaigns = []
    for campaign_id in campaign_ids:
        resp = DNDBot.instance.db.execute(f"SELECT * FROM campaigns WHERE id = {campaign_id}").fetchone()
        if resp is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return json.dumps({"error": f"Campaign {campaign_id} not found"})
        players = DNDBot.instance.db.execute(f"SELECT * FROM players WHERE campaign = ?", (resp["id"],)).fetchall()
        resp["players"] = [i["id"] for i in players if i["waitlisted"] == 0]
        resp["waitlist"] = [i["id"] for i in players if i["waitlisted"] == 1]
        dm = guild.get_member(resp["dm"])
        if dm is None:
            resp["dm_username"] = "Unknown"
            resp["dm_nickname"] = "Unknown"
        else:
            resp["dm_username"] = dm.name
            resp["dm_nickname"] = dm.display_name
        resp["new_player_friendly"] = resp["new_player_friendly"]
        resp["date_created"] = resp["timestamp"]
        campaigns.append(resp)
    return json.dumps(campaigns)


@router.get("/campaigns/{campaign_id}")
@permissions(Permissions.CAMPAIGN_READ)
async def get_campaign(campaign_id: typing.Union[int, str], auth: str, response: Response):
    init_guild()
    try:
        campaign_id = int(campaign_id)
    except ValueError:
        pass
    try:
        if isinstance(campaign_id, int):
            resp = DNDBot.instance.db.execute(f"SELECT * FROM campaigns WHERE id = {campaign_id}").fetchone()
        else:
            resp = DNDBot.instance.db.execute(f"SELECT * FROM campaigns WHERE name LIKE ?", (campaign_id,)).fetchone()

        players = DNDBot.instance.db.execute(f"SELECT * FROM players WHERE campaign = ?", (resp["id"],)).fetchall()
        resp["players"] = [i["id"] for i in players if i["waitlisted"] == 0]
        resp["waitlist"] = [i["id"] for i in players if i["waitlisted"] == 1]
    except TypeError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return json.dumps({"error": "Campaign not found"})
    dm = guild.get_member(resp["dm"])
    if dm is None:
        resp["dm_username"] = "Unknown"
        resp["dm_nickname"] = "Unknown"
    else:
        resp["dm_username"] = dm.name
        resp["dm_nickname"] = dm.display_name
    resp["new_player_friendly"] = resp["new_player_friendly"]
    resp["date_created"] = resp["timestamp"]
    return json.dumps(resp)


@router.get("/campaigns/{campaign_id}/players")
@permissions(Permissions.USER_READ)
async def get_players(campaign_id: typing.Union[int, str], auth: str, response: Response):
    try:
        campaign_id = int(campaign_id)
    except ValueError:
        pass
    campaign = DNDBot.instance.CampaignSQLHelper.select_campaign(campaign_id)
    if campaign is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return json.dumps({"error": "Campaign not found"})
    resp = DNDBot.instance.CampaignSQLHelper.get_players(campaign)

    return json.dumps(resp)


@router.post("/campaigns/create")
@permissions(Permissions.CAMPAIGN_CREATE)
async def create_campaign(auth: str, campaign: PartialCampaignInfo, response: Response):
    init_guild()
    if DNDBot.instance.CampaignSQLHelper.select_campaign(campaign.name):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return json.dumps({"error": "Campaign with this name already exists"})
    text_based = False
    if "text-based" in campaign.location.lower():
        text_based = True
    if (not campaign.meeting_date and not campaign.meeting_day) and not text_based:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return json.dumps({"error": "Meeting date or day must be specified"})
    embed = discord.Embed(
        title="New Campaign Sign-Up! (Website)",
    )
    embed.add_field(name="First Name", value=campaign.dm.first_name, inline=True)
    embed.add_field(name="Last Name", value=campaign.dm.last_name, inline=True)
    embed.add_field(name="UNT Email", value=campaign.dm.unt_email, inline=True)
    embed.add_field(name="Discord Username", value=campaign.dm.discord_tag, inline=True)
    embed.add_field(name="Discord ID", value=campaign.dm.discord_id, inline=True)
    embed.add_field(name="DM Experience", value=campaign.dm.dm_experience, inline=True)
    embed.add_field(name="Playstyle", value=campaign.playstyle, inline=False)
    embed.add_field(name="Campaign Name", value=campaign.name, inline=True)
    embed.add_field(name="Description", value=campaign.info_message, inline=False)
    embed.add_field(name="System", value=campaign.system, inline=True)
    embed.add_field(name="Location", value=campaign.location, inline=True)
    if not text_based:
        embed.add_field(name="Meeting Frequency", value=campaign.meeting_frequency, inline=True)
        if campaign.meeting_day:
            embed.add_field(name="Meeting Day", value=campaign.meeting_day, inline=True)
        elif campaign.meeting_date:
            embed.add_field(name="Meeting Date", value=campaign.meeting_date, inline=True)
        embed.add_field(name="Meeting Time", value=campaign.meeting_time, inline=True)
        embed.add_field(name="Session Length", value=campaign.session_length, inline=True)
    embed.add_field(name="Min Players", value=campaign.min_players, inline=True)
    embed.add_field(name="Max Players", value=campaign.max_players, inline=True)
    embed.add_field(name="New Player Friendly", value=campaign.new_player_friendly, inline=True)

    channel = DNDBot.instance.get_channel(DNDBot.instance.config["dm_receipts"])
    DNDBot.instance.db.execute("UPDATE users SET playstyle = ? WHERE id = ?",
                               (campaign.playstyle, campaign.dm.discord_id))
    DNDBot.instance.connection.commit()
    message = await channel.send(embed=embed)
    if not message:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return json.dumps({"error": "Failed to create campaign"})
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    return json.dumps({"success": True})


@router.post("/campaigns/{campaign_id}/action")
@permissions(Permissions.CAMPAIGN_CREATE)
async def campaign_action_request(auth: str, campaign_id, campaign_action: CampaignActionRequest, response: Response):
    init_guild()
    campaign = DNDBot.instance.CampaignSQLHelper.select_campaign(campaign_id)
    embed = getattr(ActionEmbedCreator, campaign_action.action.name)()
    channel = DNDBot.instance.get_channel(DNDBot.instance.config["campaign_action_channel"])
    to_react = await channel.send(embed=embed)
    await to_react.add_reaction("✅")
    await to_react.add_reaction("❌")


@router.post("/campaigns/apply")
@permissions(Permissions.USER_CREATE)
async def apply_to_campaigns(auth: str, application: CampaignApplication, response: Response):
    init_guild()
    for campaign in application.campaigns:
        if "(waitlist)" in campaign:
            campaign = campaign[:-11]
        campaign = DNDBot.instance.CampaignSQLHelper.select_campaign(campaign)
        if campaign is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return json.dumps({"error": "Campaign not found"})
    for i in application.campaigns:
        campaign = DNDBot.instance.CampaignSQLHelper.select_campaign(i)
        dm = guild.get_member(campaign.dm)
        embed = discord.Embed(
            title=f"New Application for {campaign.name}",
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Campaign", value=campaign.name, inline=False)
        embed.add_field(name="DM", value=str(dm), inline=False)
        embed.add_field(name="Name", value=f"{application.first_name} {application.last_name}", inline=False)
        embed.add_field(name="Discord", value=f"{str(guild.get_member(application.discord_id))}")
        embed.add_field(name="Discord ID", value=str(application.discord_id))
        embed.set_footer(text="React with a green checkmark to approve or a red X to deny.")

        channel = DNDBot.instance.get_channel(DNDBot.instance.config["applications_channel"])
        message = await channel.send(content=dm.mention, embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    return json.dumps({"success": True})


async def update_user_helper(user_id: int, user: UserUpdateRequest):
    exists = (await guild.fetch_member(user_id)) is None
    if exists:
        return json.dumps({"error": "User not found"}), 404
    exists = DNDBot.instance.db.execute("SELECT * from USERS where id = ?", (user_id,)).fetchone()
    if not exists:
        DNDBot.instance.db.execute(
            "INSERT INTO users (first_name, last_name, id, unt_email, unt_student, playstyle, bio, pronouns, "
            "image, position) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user.first_name, user.last_name, user.id,
             user.unt_email, int(user.unt_student), user.playstyle, user.bio,
             user.pronouns, user.image, user.position))
    else:
        DNDBot.instance.db.execute("UPDATE users SET first_name = ?, last_name = ?, id = ?, unt_email = ?, "
                                   "unt_student = ?, playstyle = ?, bio = ?, pronouns = ?, image = ?, position = ? "
                                   "WHERE id = ?",
                                   (user.first_name, user.last_name, user.id,
                                    user.unt_email, int(user.unt_student), user.playstyle, user.bio,
                                    user.pronouns, user.image, user.position, user.id))
    return json.dumps({"success": True}), 200


@router.get("/users/officers")
@permissions(Permissions.USER_READ)
async def get_officers(auth: str, response: Response):
    init_guild()
    members = [tuple(await get_user_helper(i.id))[0] for i in
               guild.get_role(DNDBot.instance.config["officer_role"]).members]
    return json.dumps(members)


@router.post("/users/updatemany")
@permissions(Permissions.USER_WRITE)
async def user_update_many(auth: str, request: UserUpdateManyRequest,  response: Response):
    init_guild()
    for i in request.users:
        ret, status_code = await get_user_helper(i.id)
        if status_code != 200:
            return ret, status_code
    DNDBot.instance.connection.commit()
    return json.dumps({"success": True})


@router.get("/users/{user_id}")
@permissions(Permissions.USER_READ)
async def get_user(user_id: int, auth: str, response: Response) -> str:
    init_guild()
    resp, status_ = await get_user_helper(user_id)
    response.status_code = status_
    return resp


@router.post("/users/{user_id}/update")
@permissions(Permissions.USER_CREATE)
async def update_user(user_id: int, auth: str, user: UserUpdateRequest, response: Response):
    init_guild()
    ret, status_ = await update_user_helper(user_id, user)
    if ret:
        response.status_code = status_
        return ret
    DNDBot.instance.connection.commit()


@router.get("/users/{user_id}/delete")
@permissions(Permissions.USER_CREATE)
async def delete_user(user_id: int, auth: str, response: Response):
    init_guild()
    exists = (await guild.fetch_member(user_id)) is None
    if exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return json.dumps({"error": "User not found"})
    DNDBot.instance.db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    DNDBot.instance.connection.commit()


@router.get("/users/{user_id}/warnings")
@permissions(Permissions.USER_READ)
async def get_user_warnings(user_id: int, auth: str, response: Response):
    warns = DNDBot.instance.db.execute("select * from warns where member = ?", (user_id,)).fetchall()
    resp = [{i["id"]: i["reason"]} for i in warns]
    return json.dumps(resp)


# async def campaign_creation_callback(instance: DNDBot, campaign_info: CampaignInfo):
async def campaign_creation_callback(*args, campaign: CampaignInfo = None):
    init_guild()
    text_based = False
    if "text-based" in campaign.location.lower():
        text_based = True
    oneshot = bool(campaign.meeting_date)
    name = campaign.name
    dungeon_master = await guild.fetch_member(campaign.dm)

    DNDBot.instance.connection.commit()
    channel = guild.get_channel(DNDBot.instance.config["notification_channel"])
    if not text_based:
        await channel.send(
            f"<@&{DNDBot.instance.config['new_campaign_role']}>: A new campaign has opened: "
            f"\"{campaign.name}\"! This {'one-shot' if oneshot else 'campaign'} will run using {campaign.system} by <@{campaign.dm}> on {campaign.meeting_date if oneshot else campaign.meeting_day}, for {campaign.session_length} starting at {campaign.meeting_time}! "
            f"Apply to join here: <https://www.untcriticalhit.org/campaigns#{campaign.id}>")
    else:
        await channel.send(
            f"<@&{DNDBot.instance.config['new_campaign_role']}>: A new campaign has opened: "
            f"\"{campaign.name}\"! This campaign will run using {campaign.system} by <@{campaign.dm}>. This is a text-based campaign, so it will likely be run entirely asynchronously on Discord with no vocal aspect. "
            f"Apply to join here: <https://www.untcriticalhit.org/campaigns#{campaign.id}>"
        )
    embed = discord.Embed(
        title="Campaign Created",
        description=f"Campaign {name} created.",
        timestamp=datetime.datetime.utcnow()
    )
    receipts = guild.get_channel(DNDBot.instance.config["dm_receipts"])
    embed.add_field(name="DM", value=f"{str(dungeon_master)} ({dungeon_master.id})")
    embed.add_field(name="Role", value=str(guild.get_role(campaign.role)))
    embed.add_field(name="Category", value=str(
        (await guild.fetch_channel(campaign.category)).name))
    embed.add_field(name="Max Players", value=f"{campaign.max_players}")
    await receipts.send(embed=embed)
