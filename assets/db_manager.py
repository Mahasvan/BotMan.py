import os
import sqlite3
import time


class DbManager:

    def __init__(self, bot, db_file=None, auto_backup=True, max_backups=10):
        self.bot = bot
        self.db_file = db_file
        if not self.db_file:
            self.db_file = os.path.join("assets", "storage.db")
        if db_file:
            self.db = sqlite3.connect(db_file, isolation_level=None)
            self.cursor = self.db.cursor()
            self.setup_table()
        else:
            self.first_setup()

        self.auto_backup = auto_backup
        self.max_backups = max_backups

    """Basic setup of the database"""

    def first_setup(self):
        open(self.db_file, "w").close()
        self.db = sqlite3.connect(self.db_file)
        self.cursor = self.db.cursor()
        self.setup_table()

    def setup_table(self):
        try:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS prefixes 
            (id INTEGER PRIMARY KEY, prefix VARCHAR(10))""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS games_channels 
            (guild_id INTEGER PRIMARY KEY, channel_id INTEGER NOT NULL)""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS cookies 
            
            (user_id INTEGER PRIMARY KEY, cookies_count INTEGER)""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS weather
            
            (user_id INTEGER PRIMARY KEY, city VARCHAR(50))""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS timezones 
            (user_id INTEGER PRIMARY KEY, timezone VARCHAR(50), offset varchar(15))""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS reminders
            
            (user_id INTEGER, now_time VARCHAR(50),  reminder_time VARCHAR(50), reminder_text VARCHAR(500))""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS links 
            
            (guild_id INTEGER, link_title VARCHAR(50), link_url VARCHAR(255), creator_id INTEGER)""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS tags
            (guild_id INTEGER, tag_name VARCHAR(50), tag_text VARCHAR(500), creator_id INTEGER)""")

        except Exception as e:
            self.bot.logger.log_error(e, "setup_table")

    """Guild prefix functions"""

    def remove_guild_prefix(self, guild_id: int):
        try:
            self.cursor.execute(f"""DELETE FROM prefixes WHERE id = (?)""", (guild_id,))
        except Exception as e:
            self.bot.logger.log_error(e, "remove_guild_prefix")

    def add_guild_prefix(self, guild_id: int, prefix: str):
        self.remove_guild_prefix(guild_id)
        try:
            self.cursor.execute(f"""INSERT INTO prefixes VALUES((?), (?))""", (guild_id, prefix))
        except Exception as e:
            self.bot.logger.log_error(e, "add_guild_prefix")

    def get_guild_prefix(self, guild_id: int):
        self.cursor.execute(f"""SELECT prefix FROM prefixes WHERE id = (?)""", (guild_id,))
        try:
            result = self.cursor.fetchone()[0]
            return result if result else self.bot.default_prefix
        except Exception as e:
            if isinstance(e, TypeError):
                return self.bot.default_prefix
            else:
                self.bot.logger.log_error(e, "get_guild_prefix")
                return self.bot.default_prefix

    """MadLibs functions"""

    def set_games_channel(self, guild_id: int, channel_id: int):
        try:
            self.remove_games_channel(guild_id)
            self.cursor.execute(f"""INSERT INTO games_channels VALUES((?), (?))""", (guild_id, channel_id))
        except Exception as e:
            self.bot.logger.log_error(e, "add_madlib_channel")

    def remove_games_channel(self, guild_id: int):
        try:
            self.cursor.execute(f"""DELETE FROM games_channels WHERE guild_id = (?)""", (guild_id,))
        except Exception as e:
            self.bot.logger.log_error(e, "remove_madlib_channel")

    def get_games_channel(self, guild_id: int):
        self.cursor.execute(f"""SELECT channel_id FROM games_channels WHERE guild_id = (?)""", (guild_id,))
        try:
            result = self.cursor.fetchone()[0]
            return result if result else None
        except Exception as e:
            self.bot.logger.log_error(e, "get_madlib_channel")

    """Cookies functions"""

    def add_cookie(self, user_id: int):
        try:
            self.cursor.execute(f"""SELECT cookies_count FROM cookies WHERE user_id = (?)""", (user_id,))
            result = self.cursor.fetchone()
            if result:
                self.cursor.execute(f"""UPDATE cookies SET cookies_count = (?) WHERE user_id = (?)""",
                                    (result[0] + 1, user_id))
            else:
                self.cursor.execute(f"""INSERT INTO cookies VALUES((?), 1)""", (user_id,))
        except Exception as e:
            self.bot.logger.log_error(e, "add_cookie")

    def get_cookies_count(self, user_id: int):
        try:
            self.cursor.execute(f"""SELECT cookies_count FROM cookies WHERE user_id = ?""", (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            self.bot.logger.log_error(e, "get_cookies_count")

    """Weather functions"""

    def set_weather_city(self, user_id: int, city: str):
        try:
            result = self.get_weather_city(user_id)
            if result:
                self.cursor.execute(f"""UPDATE weather SET city = (?) WHERE user_id = (?)""", (city, user_id))
            else:
                self.cursor.execute(f"""INSERT INTO weather VALUES((?), (?))""", (user_id, city))
        except Exception as e:
            self.bot.logger.log_error(e, "set_city")

    def get_weather_city(self, user_id: int):
        self.cursor.execute(f"""SELECT city FROM weather WHERE user_id = (?)""", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def remove_weather_city(self, user_id: int):
        try:
            self.cursor.execute(f"""DELETE FROM weather WHERE user_id = (?)""", (user_id,))
        except Exception as e:
            self.bot.logger.log_error(e, "remove_weather_city")

    """Time functions"""

    def get_timezone(self, user_id: int):
        self.cursor.execute(f"""SELECT timezone FROM timezones WHERE user_id = (?)""", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_offset(self, user_id: int):
        self.cursor.execute(f"""SELECT offset FROM timezones WHERE user_id = (?)""", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def set_timezone_null_values(self, user_id: int):
        try:
            self.cursor.execute(f"""UPDATE timezones SET timezone = NULL, offset = NULL 
            WHERE user_id = (?)""", (user_id,))
        except Exception as e:
            self.bot.logger.log_error(e, "set_timezone_null_values")

    def set_timezone(self, user_id: int, timezone: str):
        try:
            self.set_timezone_null_values(user_id)
            self.cursor.execute(f"""UPDATE timezones SET timezone = (?) WHERE user_id = (?)""", (timezone, user_id))
        except Exception as e:
            self.bot.logger.log_error(e, "set_timezone")

    def set_offset(self, user_id: int, offset: str):
        try:
            self.set_timezone_null_values(user_id)
            self.cursor.execute(f"""UPDATE timezones SET offset = (?), timezone = (?) WHERE user_id = (?)""",
                                (offset, None, user_id))
        except Exception as e:
            self.bot.logger.log_error(e, "set_offset")

    def remove_timezone(self, user_id: int):
        try:
            self.cursor.execute(f"""UPDATE timezones SET timezone = (?) WHERE user_id = (?)""", (None, user_id))
        except Exception as e:
            self.bot.logger.log_error(e, "remove_timezone")

    def remove_offset(self, user_id: int):
        try:
            self.cursor.execute(f"""UPDATE timezones SET offset = (?) WHERE user_id = (?)""", (None, user_id))
        except Exception as e:
            self.bot.logger.log_error(e, "remove_offset")

    """Reminder functions"""

    def get_completed_reminders(self):
        current_time = time.time()
        try:
            self.cursor.execute(f"""SELECT user_id, now_time, reminder_time, reminder_text
             FROM reminders WHERE reminder_time <= (?)""", (current_time,))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            self.bot.logger.log_error(e, "get_completed_reminders")

    def get_all_reminders(self):
        try:
            self.cursor.execute(f"""SELECT user_id, reminder_time, reminder_text
             FROM reminders""")
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            self.bot.logger.log_error(e, "get_all_reminders")

    def set_reminder(self, user_id: int, now_time: int, reminder_time: int, reminder_text: str):
        try:
            self.cursor.execute(f"""INSERT INTO reminders VALUES((?), (?), (?), (?))""",
                                (user_id, now_time, reminder_time, reminder_text))
        except Exception as e:
            self.bot.logger.log_error(e, "set_reminder")

    def remove_reminder(self, user_id: int, reminder_time):
        try:
            self.cursor.execute(f"""DELETE FROM reminders WHERE user_id = (?) AND reminder_time <= (?)""",
                                (user_id, reminder_time))
        except Exception as e:
            self.bot.logger.log_error(e, "remove_reminder")

    def prune_reminders(self):
        now_time = time.time()
        try:
            self.cursor.execute(f"""DELETE FROM reminders WHERE reminder_time <= (?)""", (now_time,))
        except Exception as e:
            self.bot.logger.log_error(e, "prune_reminders")

    """Links and Tags"""

    def fetch_link(self, guild_id: int, link_name: str):
        try:
            self.cursor.execute(
                f"""SELECT link_title, link_url, creator_id FROM links WHERE guild_id = (?) and link_title = (?)""",
                (guild_id, link_name,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            self.bot.logger.log_error(e, "fetch_link")

    def fetch_all_guild_links(self, guild_id: int):
        try:
            self.cursor.execute(f"""SELECT link_title, link_url FROM links WHERE guild_id = (?)""", (guild_id,))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            self.bot.logger.log_error(e, "fetch_all_guild_links")

    def fetch_tag(self, guild_id: int, tag_name: str):
        try:
            self.cursor.execute(
                f"""SELECT tag_name, tag_text, creator_id FROM tags WHERE guild_id = (?) and tag_name = (?)""",
                (guild_id, tag_name,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            self.bot.logger.log_error(e, "fetch_tag")

    def fetch_all_guild_tags(self, guild_id: int):
        try:
            self.cursor.execute(f"""SELECT tag_name, tag_text FROM tags WHERE guild_id = (?)""", (guild_id,))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            self.bot.logger.log_error(e, "fetch_all_guild_tags")

    def add_link(self, guild_id: int, link_title: str, link_url: str, creator_id: int):
        try:
            prev_link = self.fetch_link(guild_id, link_title)
            if prev_link is None:
                self.cursor.execute(f"""INSERT INTO links VALUES((?), (?), (?), (?))""",
                                    (guild_id, link_title, link_url, creator_id))
            else:
                self.cursor.execute(
                    f"""UPDATE links SET link_url = (?), creator_id = (?) WHERE guild_id = (?) and link_title = (?)""",
                    (link_url, creator_id, guild_id, link_title))
        except Exception as e:
            self.bot.logger.log_error(e, "set_link")

    def remove_link(self, guild_id: int, link_title: str):
        try:
            self.cursor.execute(f"""DELETE FROM links WHERE guild_id = (?) and link_title = (?)""",
                                (guild_id, link_title,))
        except Exception as e:
            self.bot.logger.log_error(e, "remove_link")

    def add_tag(self, guild_id: int, tag_name: str, tag_text: str, creator_id: int):
        try:
            prev_tag = self.fetch_tag(guild_id, tag_name)
            if prev_tag is None:
                self.cursor.execute(f"""INSERT INTO tags VALUES((?), (?), (?), (?))""",
                                    (guild_id, tag_name, tag_text, creator_id))
            else:
                self.cursor.execute(
                    f"""UPDATE tags SET tag_text = (?), creator_id = (?) WHERE guild_id = (?) and tag_name = (?)""",
                    (tag_text, creator_id, guild_id, tag_name))
        except Exception as e:
            self.bot.logger.log_error(e, "set_tag")

    def remove_tag(self, guild_id: int, tag_name: str):
        try:
            self.cursor.execute(f"""DELETE FROM tags WHERE guild_id = (?) and tag_name = (?)""",
                                (guild_id, tag_name,))
        except Exception as e:
            self.bot.logger.log_error(e, "remove_tag")
