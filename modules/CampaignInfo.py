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
    :param timestamp: When the campaign was created
    """

    name: str = ""
    role: int = 0
    category: int = 0
    information_channel: int = 0
    dm: int = 0
    min_players: int = 0
    max_players: int = 0
    current_players: int = 0
    status_message: int = 0
    id: int = 0
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
    new_player_friendly: int = 0
    timestamp: int = 0
    paused: int = 0
