from dataclasses import dataclass


@dataclass
class CampaignInfo:
    """
    Holds the information about a given campaign, normally created by CampaignSQLHelper from a row. Can be
    initialized to  and filled manually, or can be filled via constructor.
    :param name: The campaign's name
    :param role: The campaign's role
    :param category: The campaign's category channel
    :param information_channel: The "global" information channel
    :param dm: Dungeon master
    :param dm_username: The DM's username
    :param dm_nickname: The DM's nickname
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
    :param meeting_day: The campaign's meeting day, used for recurring campaigns
    :param meeting_time: The campaign's meeting time
    :param meeting_date: The campaign's meeting date, used for one-shot campaigns
    :param system: The campaign's system
    :param new_player_friendly: Whether the campaign is new player friendly
    :param paused: Whether the campaign is paused
    :param date_created: When the campaign was created
    :param players: List of players
    :param waitlist: List of waitlisted players
    """

    name: str = ""
    role: int = 0
    category: int = 0
    information_channel: int = 0
    dm: int = 0
    dm_username: str = ""
    dm_nickname: str = ""
    min_players: int = 0
    max_players: int = 0
    current_players: int = 0
    status_message: int = 0
    id: str = ""
    locked: str = ""
    info_message: str = ""
    location: str = ""
    playstyle: str = ""
    session_length: str = ""
    meeting_frequency: str = ""
    meeting_day: str = ""
    meeting_time: str = ""
    meeting_date: str = ""
    system: str = ""
    new_player_friendly: str = ""
    date_created: int = 0
    paused: int = 0
    players: list[int] = None
    waitlist: list[int] = None


@dataclass
class UserInfo:
    """
    Holds information for any queried user
    :param id: The user's ID
    :param name: The user's name
    :param discriminator: The user's discriminator
    :param nickname: The user's nickname
    :param officer: Whether the user is an officer
    :param developer: Whether the user is a developer
    :param verified: Whether the user is verified
    :param guest: Whether the user is a guest
    :param player: Whether the user is a player
    :param dm: Whether the user is a DM
    :param banned_player: Whether the user is a banned player
    :param banned_dm: Whether the user is a banned DM
    :param joined: When the user joined
    :param campaigns_player: List of campaigns the user is a player in
    :param campaigns_dm: List of campaigns the user is a DM in
    :param warnings: List of warnings. Keys are the warning IDs, values are the warning reasons
    :param bio: User's bio
    :param pronouns: User's pronouns
    :param image: User's image
    :param position: User's position
    """
    id: int = 0
    name: str = ""
    discriminator: str = ""
    nickname: str = ""
    in_discord: bool = False
    officer: bool = False
    developer: bool = False
    verified: bool = False
    guest: bool = False
    player: bool = False
    dm: bool = False
    banned_player: bool = False
    banned_dm: bool = False
    joined: str = ""
    campaigns_player: list[int] = None
    campaigns_dm: list[int] = None
    warnings: dict[str, str] = None  # json doesn't support int keys, so you have to typecast to int before use
    first_name: str = ""
    last_name: str = ""
    unt_email: str = ""
    unt_student: bool = False
    playstyle: str = ""
    bio: str = ""
    pronouns: str = ""
    image: str = ""
    position: str = ""


def generate_struct(dict_: dict, cls: type):
    """
    Generates a struct from a dict
    Usage: generate_struct({"name": "test"}, CampaignInfo) --> CampaignInfo(name="test")
    Usage: generate_struct({"name": "test"}, UserInfo) --> UserInfo(name="test")
    :param dict_: The dict to generate from
    :param cls: The class to generate
    :return: The generated struct
    """
    obj = cls()
    for key, value in dict_.items():
        setattr(obj, key, value)
    return obj
