import enum
import typing

from pydantic import BaseModel


class DMInfo(BaseModel):
    first_name: str
    last_name: str
    discord_tag: str
    discord_id: int
    unt_email: typing.Optional[str]
    dm_experience: str


class PartialCampaignInfo(BaseModel):
    """
    Class that holds all basic information about a given campaign
    :param name: Name of the campaign
    :param dm: DM ID of the campaign
    :param min_players: Minimum number of players for the campaign
    :param max_players: Maximum number of players for the campaign
    :param info_message: Information message sent in the information channel
    :param location: Location of the campaign
    :param playstyle: Playstyle of the campaign
    :param session_length: The campaign's session length
    :param meeting_frequency: The campaign's meeting frequency
    :param meeting_time: The campaign's meeting time
    :param meeting_day: The campaign's meeting day. Can be None if campaign is a one-shot
    :param meeting_date: The campaign's meeting date. Will only be used if campaign is a one-shot
    :param system: The campaign's system
    :param new_player_friendly: Whether the campaign is new player friendly
    """
    name: str
    dm: DMInfo
    min_players: int
    max_players: int
    info_message: str
    location: str
    playstyle: str
    session_length: str
    meeting_frequency: str
    meeting_time: str
    meeting_day: typing.Optional[str]
    meeting_date: typing.Optional[str]
    system: str
    new_player_friendly: typing.Literal["Yes", "No"]


class CampaignInfo(BaseModel):
    """
    Holds the information about a given campaign, normally created by CampaignSQLHelper from a row. Can be
    initialized to and filled manually, or can be filled via constructor.
    :param name: The campaign's name
    :param role: The campaign's role
    :param category: The campaign's category channel
    :param information_channel: The "global" information channel
    :param dm: Dungeon master
    :param min_players: Minimum players required
    :param max_players: Maximum players allowed
    :param current_players: Current players
    :param status_message: The status message
    :param id: The campaign's ID
    :param locked: Whether the campaign is locked
    :param info_message: The campaign's info message
    :param location: The campaign's location
    :param playstyle: The campaign's playstyle
    :param session_length: The campaign's session length
    :param meeting_frequency: The campaign's meeting frequency
    :param meeting_time: The campaign's meeting time
    :param system: The campaign's system
    :param new_player_friendly: Whether the campaign is new player friendly
    """
    name: str
    role: int
    category: int
    information_channel: int
    dm: int
    min_players: int
    max_players: int
    current_players: int
    status_message: int
    id: str
    locked: str
    info_message: str
    location: str
    playstyle: str
    session_length: str
    meeting_frequency: str
    meeting_time: str
    system: str
    new_player_friendly: typing.Literal["Yes", "No"]


class CampaignApplication(BaseModel):
    """
    Holds the information about a given campaign application
    :param campaigns: List of campaigns the user is applying to
    :param first_name: First name of the user
    :param last_name: Last name of the user
    :param discord_tag: Discord tag of the user
    :param discord_id: Discord ID of the user
    :param unt_email: UNT email of the user
    """
    campaigns: list[str]
    first_name: str
    last_name: str
    discord_tag: str
    discord_id: int
    unt_email: typing.Optional[str]


class CampaignFetchMany(BaseModel):
    campaign_ids: list[int]


class CampaignAction(enum.Enum):
    leave = "Leave a campaign as a player"
    end = "End a campaign as a Dungeon Master"
    pause = "Pause a campaign as a Dungeon Master"
    resume = "Resume a campaign as a Dungeon Master"
    lock = "Lock a campaign as a Dungeon Master"
    unlock = "Unlock a campaign as a Dungeon Master"
    update = "Update Max Player Count as a Dungeon Master"


class CampaignActionRequest(BaseModel):
    first_name: str
    last_name: str
    id: int
    action: CampaignAction
    reasons: typing.Optional[list[str]]
    elaboration: typing.Optional[str]
    new_player_count: typing.Optional[int]
    campaign_name: str


class UserCreationRequest(BaseModel):
    first_name: str
    last_name: str
    id: int
    unt_email: typing.Optional[str]
    unt_student: bool
    playstyle: typing.Optional[str] = ""
    bio: typing.Optional[str] = ""
    pronouns: typing.Optional[str] = ""
    image: typing.Optional[str] = ""
    position: typing.Optional[str] = ""


class UserUpdateRequest(UserCreationRequest):
    pass


class UserUpdateManyRequest(BaseModel):
    users: typing.List[UserUpdateRequest]
