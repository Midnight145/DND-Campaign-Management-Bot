import asyncio
import datetime
import time
import typing
import pytz

import discord
from discord.ext import commands


class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.db.execute("CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,"
                            " time INTEGER, repeat TEXT, channel_id INTEGER, message TEXT, dst INTEGER DEFAULT 0)")
        self.bot.connection.commit()
        self.tasks = {}

    @commands.command()
    async def schedule(self, context: commands.Context, day_sent: str, time_sent: str,
                       repeat: typing.Literal['none', 'daily', 'weekly', 'biweekly', 'monthly'],
                       channel: discord.TextChannel, *, message: str):
        date = datetime.datetime.strptime(day_sent, '%m/%d/%Y')
        am_pm = time_sent[-2:]
        time_sent = time_sent[:-2]
        hour, minute = map(int, time_sent.split(':'))
        if am_pm.lower() == 'pm':
            if hour != 12:
                hour += 12
        else:
            if hour == 12:
                hour = 0

        time_ = datetime.time(hour, minute)
        datetime_ = datetime.datetime.combine(date, time_)
        localized = pytz.timezone('America/Chicago').localize(datetime_)
        time_value = localized.timestamp()
        self.bot.db.execute("INSERT INTO schedule (user_id, channel_id, time, repeat, message, dst) VALUES (?, ?, ?, ?, ?, ?)",
                            (context.author.id, channel.id, time_value, repeat, message, time.daylight))
        self.bot.connection.commit()

        await context.send(f"Message scheduled for {day_sent} at {time_sent} {am_pm} in {channel.mention} with the message: {message}")
        message_id = self.bot.db.lastrowid
        self.tasks[message_id] = asyncio.create_task(self.message_task(
            {"id": message_id, "user_id": context.author.id, "channel_id": channel.id, "time": time_value, "repeat": repeat,
             "message": message, "dst": time.daylight}))

    @commands.command()
    async def list_schedules(self, context: commands.Context):
        messages = self.bot.db.execute("SELECT * FROM schedule WHERE user_id = ?", (context.author.id,)).fetchall()
        if not messages:
            await context.send("You have no scheduled messages!")
            return
        embed = discord.Embed(title="Your scheduled messages")
        for message in messages:
            value = (f"Time: {datetime.datetime.fromtimestamp(message['time'], pytz.timezone('America/Chicago'))}\n"
                     f"Repeat: {message['repeat']}\n"
                     f"Channel: <#{message['channel_id']}>\n"
                     f"Message: {message['message']}")
            if len(value) > 1024:
                words = value.split(" ")
                embed.add_field(name=f"Message {message['id']}",
                                value=' '.join(words[:len(words)//2]), inline=False)
                embed.add_field(name=f"Message {message['id']}",
                                value=' '.join(words[len(words)//2::]), inline=False)
            else:
                embed.add_field(name=f"Message {message['id']}",
                                value=value, inline=False)
        await context.send(embed=embed)


    @commands.command()
    async def delete_schedule(self, context: commands.Context, message_id: int):
        message = self.bot.db.execute("SELECT * FROM schedule WHERE id = ?", (message_id,)).fetchone()
        if not message:
            await context.send("Message not found!")
            return
        if message["user_id"] != context.author.id:
            await context.send("You can't delete someone else's message!")
            return
        self.bot.db.execute("DELETE FROM schedule WHERE id = ?", (message_id,))
        self.bot.connection.commit()
        self.tasks[message_id].cancel()
        del self.tasks[message_id]
        await context.send("Message deleted!")

    @commands.command()
    async def update_schedule_date(self, context: commands.Context, id_: int, day_sent: str, time_sent: str):
        date = datetime.datetime.strptime(day_sent, '%m/%d/%Y')
        am_pm = time_sent[-2:]
        time_sent = time_sent[:-2]
        hour, minute = map(int, time_sent.split(':'))
        if am_pm.lower() == 'pm':
            if hour != 12:
                hour += 12
        else:
            if hour == 12:
                hour = 0

        time_ = datetime.time(hour, minute)
        datetime_ = datetime.datetime.combine(date, time_)
        localized = pytz.timezone('America/Chicago').localize(datetime_)
        time_value = localized.timestamp()

        self.bot.db.execute("UPDATE schedule SET time = ? WHERE id = ?", (time_value, id_))
        self.bot.connection.commit()
        await context.send("date updated!")

    @commands.command()
    async def update_schedule_message(self, context: commands.Context, id_: int, message: str):
        self.bot.db.execute("UPDATE schedule SET message = ? WHERE id = ?", (message, id_))
        self.bot.connection.commit()
        await context.send("message updated!")

    # noinspection PyAsyncCall
    async def cog_load(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = {}
        messages = self.bot.db.execute("SELECT * FROM schedule").fetchall()
        for message in messages:
            print("loading message: " + message["message"])
            self.tasks[message['id']] = asyncio.create_task(self.message_task(message))
            print("created task")
        print("Done loading messages!")

    async def cog_unload(self):
        for task in self.tasks:
            task.cancel()
        print("Done unloading messages!")

    async def message_task(self, message):
        if message["dst"] != time.daylight:
            message["time"] += 3600 if message["dst"] == 1 else -3600
            self.bot.db.execute("UPDATE schedule SET time = ?, dst = ? WHERE id = ?",
                                (message["time"], time.daylight, message["id"]))
        print("Starting message task for " + str(message['id']))
        print("Message Info: " + str(message))
        channel = self.bot.get_channel(message["channel_id"])
        if channel is None:
            print("Channel not found for message " + str(message['id']))
            self.bot.db.execute("DELETE FROM schedule WHERE id = ?", (message["id"],))
            self.bot.connection.commit()
            return
        print("Sleeping until " + str(
            datetime.datetime.fromtimestamp(message["time"], pytz.timezone('America/Chicago'))) + " for " + message["message"])
        await discord.utils.sleep_until(datetime.datetime.fromtimestamp(message["time"], pytz.timezone('America/Chicago')))
        await channel.send(message['message'])
        if message["repeat"] == "none":
            self.bot.db.execute("DELETE FROM schedule WHERE id = ?", (message["id"],))
            self.bot.connection.commit()
            return
        offset = 86400
        if message["repeat"] == "daily":
            pass
        elif message["repeat"] == "weekly":
            offset *= 7
        elif message["repeat"] == "biweekly":
            offset *= 14
        elif message["repeat"] == "monthly":
            offset *= 28

        self.bot.db.execute("UPDATE schedule SET time = ? WHERE id = ?",
                            (message["time"] + offset, message["id"]))
        message["time"] += offset
        self.bot.connection.commit()
        print("Done sending message!")
        print("New time: " + str(datetime.datetime.fromtimestamp(message["time"], pytz.timezone('America/Chicago'))))
        print("New message info: " + str(message))
        self.tasks[message['id']] = asyncio.create_task(self.message_task(message))


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
