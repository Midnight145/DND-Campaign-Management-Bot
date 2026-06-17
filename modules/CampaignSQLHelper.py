import asyncio
import sqlite3
import traceback
from typing import Union, Optional, TYPE_CHECKING

import discord

from .CampaignInfo import CampaignInfo
from .FakeMember import FakeMember

if TYPE_CHECKING:  # TYPE_CHECKING is always false, allows for type hinting without circular import
    from ..DNDBot import DNDBot


class CampaignSQLHelper:
    """
    WILL NEVER COMMIT TO DATABASE
    """

    def __init__(self, bot: 'DNDBot'):
        self.bot = bot

    def get_campaigns(self) -> list[dict]:
        return self.bot.db.execute("SELECT * FROM campaigns").fetchall()

    def create_campaign(self, vals: CampaignInfo) -> bool:
        """
        Adds a new campaign to the database
        :param vals: Campaign info created by SQLHelper
        :return: Whether we should commit to database
        """
        try:
            self.bot.db.execute(
                f"INSERT INTO campaigns (name, dm, role, category, information_channel, min_players, max_players, "
                f"current_players, status_message, location, playstyle, session_length, meeting_frequency, "
                f"meeting_day, meeting_time, meeting_date, system, new_player_friendly, timestamp, paused, "
                f"info_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (vals.name, vals.dm, vals.role, vals.category, vals.information_channel, vals.min_players,
                 vals.max_players, vals.current_players, vals.status_message, vals.location, vals.playstyle,
                 vals.session_length, vals.meeting_frequency, vals.meeting_day, vals.meeting_time, vals.meeting_date,
                 vals.system, vals.new_player_friendly, vals.timestamp, vals.paused, vals.info_message))
            return True
        except Exception:
            traceback.print_exc()
            return False

    def set_campaign_info(self, campaign: CampaignInfo, info: str) -> bool:
        try:
            self.bot.db.execute(f"UPDATE campaigns SET info_message = ? WHERE id = ?", (info, campaign.id))
            return True
        except Exception:
            traceback.print_exc()
            return False

    def set_campaign_field(self, campaign: CampaignInfo, field: str, value: str) -> bool:
        try:
            self.bot.db.execute(f"UPDATE campaigns SET {field} = ? WHERE id = ?", (value, campaign.id))
            return True
        except Exception:
            traceback.print_exc()
            return False

    def delete_campaign(self, campaign: Union[int, str]) -> bool:
        """
        Deletes a campaign from the database
        :param campaign: Either campaign name or campaign ID
        :return: Whether we should commit to database
        """

        try:
            # checks whether we passed ID or name
            if isinstance(campaign, int):
                self.bot.db.execute(f"DELETE FROM campaigns WHERE id = {campaign}")
                self.bot.db.execute(f"DELETE FROM players WHERE campaign = {campaign}")
            else:
                resp = self.select_campaign(campaign)
                self.bot.db.execute(f"DELETE FROM campaigns WHERE name LIKE {campaign}")
                self.bot.db.execute(f"DELETE FROM players WHERE campaign = {resp.id}")
            return True
        except Exception:
            traceback.print_exc()
            return False

    def set_campaign_status(self, campaign: CampaignInfo, status: int) -> bool:
        try:
            self.bot.db.execute(f"UPDATE campaigns SET locked = {status} WHERE id = {campaign.id}")
            return True
        except Exception:
            traceback.print_exc()
            return False

    def select_campaign(self, campaign: Union[int, str]) -> CampaignInfo | None:
        """
        Selects a row from the campaign table
        :param campaign: Either campaign name or campaign ID
        :return: Row corresponding to that campaign
        """
        # checks whether we passed ID or name
        if isinstance(campaign, int):
            campaign = self.bot.db.execute("SELECT * FROM campaigns WHERE id = ?", (campaign,)).fetchone()
            if campaign is None:
                return None
            else:
                return self.dict_to_campaign(campaign)
        else:
            campaign = self.bot.db.execute("SELECT * FROM campaigns WHERE name = ?", (campaign,)).fetchone()
            if campaign is None:
                return None
            else:
                return self.dict_to_campaign(campaign)

    def rename_campaign(self, campaign: CampaignInfo, new_name: str):
        try:
            # self.bot.db.execute(f"ALTER TABLE {self.__get_table_name(campaign.name)} RENAME TO "
            #                     f"{self.__get_table_name(new_name)}")
            self.bot.db.execute(f"UPDATE campaigns SET name = ? WHERE name LIKE ?", (new_name, campaign.name))
            return True
        except Exception:
            traceback.print_exc()
            return False

    def select_field(self, field) -> Optional[list[dict]]:
        """
        Selects a certain field from the main table
        :param field: the field to be selected
        :return: The rows found
        """
        return self.bot.db.execute(f"SELECT {field} FROM campaigns").fetchall()

    @staticmethod
    def dict_to_campaign(resp: Union[sqlite3.Row, dict]) -> CampaignInfo:
        """
        Converts a row: dict returned by SELECT to a CampaignInfo object
        :param resp: The dictionary to be converted
        :return: The created CampaignInfo object
        """
        if isinstance(resp, sqlite3.Row):
            resp = dict(zip(resp.keys(), resp))
        campaign = CampaignInfo()
        for key, value in resp.items():
            setattr(campaign, key, value)
        return campaign

    def add_player(self, campaign: CampaignInfo, player: discord.Member):
        try:
            is_waitlisted = self.bot.db.execute(f"SELECT waitlisted FROM players WHERE id = ? AND campaign = ?",
                                                (player.id, campaign.id)).fetchone()
            if is_waitlisted:
                self.__increment_players(campaign, 1)
                return self.unwaitlist(campaign, player)
            else:
                self.bot.db.execute(f"INSERT INTO players (id, campaign, waitlisted, name) VALUES ("
                                    f"?, ?, ?, ?)", (player.id, campaign.id, 0, player.display_name))
                self.__increment_players(campaign, 1)
                return True
        except Exception:
            traceback.print_exc()
            return False

    def waitlist_player(self, campaign: CampaignInfo, player: discord.Member):
        try:
            self.bot.db.execute(f"INSERT INTO players (id, campaign, waitlisted, name) VALUES ("
                                f"?, ?, ?, ?)", (player.id, campaign.id, 1, player.display_name))
            return True
        except Exception:
            traceback.print_exc()
            return False

    def unwaitlist(self, campaign: CampaignInfo, player: discord.Member):
        try:
            waitlisted = 0
            self.bot.db.execute(f"UPDATE players SET waitlisted = ? WHERE id = ? AND campaign = {campaign.id}",
                                (waitlisted, player.id))
            self.__increment_players(campaign, 1)
            return True
        except Exception:
            traceback.print_exc()
            return False

    def clear_waitlist(self, campaign: CampaignInfo):
        try:
            self.bot.db.execute(f"DELETE FROM players WHERE waitlisted = 1 AND campaign = {campaign.id}")
            return True
        except Exception:
            traceback.print_exc()
            return False

    def remove_player(self, campaign: CampaignInfo, player: Union[discord.Member, FakeMember]):
        try:
            self.bot.db.execute(f"DELETE FROM players WHERE id = {player.id} AND campaign = {campaign.id}")
            self.__increment_players(campaign, -1)
            return True
        except Exception:
            traceback.print_exc()
            return False

    def remove_waitlisted_player(self, campaign: CampaignInfo, player: Union[discord.Member, FakeMember]):
        try:
            self.bot.db.execute(f"DELETE FROM players WHERE id = {player.id} AND campaign = {campaign.id}")
            return True
        except Exception:
            traceback.print_exc()
            return False

    def set_max_players(self, campaign: CampaignInfo, amount: int):
        try:
            self.bot.db.execute(f"UPDATE campaigns SET max_players = {amount} WHERE id= {campaign.id}")
            return True
        except Exception:
            traceback.print_exc()
            return False

    def __increment_players(self, campaign: CampaignInfo, amount):
        try:
            self.bot.db.execute(f"UPDATE campaigns SET current_players = {campaign.current_players + amount} WHERE "
                                f"name LIKE ?", (campaign.name,))
            self.bot.connection.commit()
            return True
        except Exception:
            traceback.print_exc()
            return False

    def get_waitlist(self, campaign: CampaignInfo):
        try:
            return self.bot.db.execute("SELECT * FROM "
                                       f"players WHERE waitlisted = 1 AND campaign = {campaign.id}").fetchall()
        except Exception:
            traceback.print_exc()
            return None

    def get_waitlisted_players(self, campaign: CampaignInfo):
        return self.get_waitlist(campaign)

    def get_players(self, campaign: CampaignInfo):
        try:
            return self.bot.db.execute("SELECT id FROM "
                                       f"players WHERE waitlisted = 0 AND campaign = {campaign.id}").fetchall()
        except Exception:
            traceback.print_exc()
            return None

    def set_current_player_count(self, campaign: CampaignInfo, amount: int):
        try:
            self.bot.db.execute(f"UPDATE campaigns SET current_players = {amount} WHERE id= {campaign.id}")
            return True
        except Exception:
            traceback.print_exc()
            return False

    def pause_campaign(self, campaign: CampaignInfo):
        try:
            self.bot.db.execute(f"UPDATE campaigns SET paused = 1 WHERE id= {campaign.id}")
            return True
        except Exception:
            traceback.print_exc()
            return False

    def resume_campaign(self, campaign: CampaignInfo):
        try:
            self.bot.db.execute(f"UPDATE campaigns SET paused = 0 WHERE id= {campaign.id}")
            return True
        except Exception:
            traceback.print_exc()
            return False
