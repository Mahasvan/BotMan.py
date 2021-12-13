import sqlite3


class DbManager:

    def __init__(self, bot, db_file=None):
        self.bot = bot
        if db_file:
            self.db = sqlite3.connect(db_file, isolation_level=None)
            self.cursor = self.db.cursor()
            self.setup_table()
        else:
            self.first_setup()

    def first_setup(self):
        open("assets/storage.db", "w").close()
        self.db = sqlite3.connect("assets/storage.db")
        self.cursor = self.db.cursor()
        self.setup_table()

    def setup_table(self):
        try:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS prefixes 
            (id INTEGER PRIMARY KEY, prefix VARCHAR(10))""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS madlibs_channels 
            (guild_id INTEGER PRIMARY KEY, channel_id INTEGER NOT NULL)""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS cookies 
            (user_id INTEGER PRIMARY KEY, cookies_count INTEGER)""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS weather
            (user_id INTEGER PRIMARY KEY, city VARCHAR(50))""")
        except Exception as e:
            self.bot.logger.log_error(e, "setup_table")

    def remove_guild_prefix(self, guild_id: int):
        try:
            self.cursor.execute(f"""DELETE FROM prefixes WHERE id = {guild_id}""")
        except Exception as e:
            self.bot.logger.log_error(e, "remove_guild_prefix")

    def add_guild_prefix(self, guild_id: int, prefix: str):
        self.remove_guild_prefix(guild_id)
        try:
            self.cursor.execute(f"""INSERT INTO prefixes VALUES({guild_id}, \"{prefix}\")""")
        except Exception as e:
            self.bot.logger.log_error(e, "add_guild_prefix")

    def get_guild_prefix(self, guild_id: int):
        self.cursor.execute(f"""SELECT prefix FROM prefixes WHERE id = {guild_id}""")
        try:
            result = self.cursor.fetchone()[0]
            return result if result else self.bot.default_prefix
        except Exception as e:
            if isinstance(e, TypeError):
                return self.bot.default_prefix
            else:
                self.bot.logger.log_error(e, "get_guild_prefix")
                print(type(e).__name__, e)
                return self.bot.default_prefix

    def set_madlib_channel(self, guild_id: int, channel_id: int):
        try:
            self.remove_madlib_channel(guild_id)
            self.cursor.execute(f"""INSERT INTO madlibs_channels VALUES({guild_id}, {channel_id})""")
        except Exception as e:
            self.bot.logger.log_error(e, "add_madlib_channel")

    def remove_madlib_channel(self, guild_id: int):
        try:
            self.cursor.execute(f"""DELETE FROM madlibs_channels WHERE guild_id = {guild_id}""")
        except Exception as e:
            self.bot.logger.log_error(e, "remove_madlib_channel")

    def get_madlib_channel(self, guild_id: int):
        self.cursor.execute(f"""SELECT channel_id FROM madlibs_channels WHERE guild_id = {guild_id}""")
        try:
            result = self.cursor.fetchone()[0]
            return result if result else None
        except Exception as e:
            self.bot.logger.log_error(e, "get_madlib_channel")

    def add_cookie(self, user_id: int):
        try:
            self.cursor.execute(f"""SELECT cookies_count FROM cookies WHERE user_id = {user_id}""")
            result = self.cursor.fetchone()
            if result:
                self.cursor.execute(f"""UPDATE cookies SET cookies_count = {result[0] + 1} WHERE user_id = {user_id}""")
            else:
                self.cursor.execute(f"""INSERT INTO cookies VALUES({user_id}, 1)""")
        except Exception as e:
            self.bot.logger.log_error(e, "add_cookie")

    def get_cookies_count(self, user_id: int):
        try:
            self.cursor.execute(f"""SELECT cookies_count FROM cookies WHERE user_id = {user_id}""")
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            self.bot.logger.log_error(e, "get_cookies_count")

    def set_weather_city(self, user_id: int, city: str):
        try:
            result = self.get_weather_city(user_id)
            if result:
                self.cursor.execute(f"""UPDATE weather SET city = \"{city}\" WHERE user_id = {user_id}""")
            else:
                self.cursor.execute(f"""INSERT INTO weather VALUES({user_id}, \"{city}\")""")
        except Exception as e:
            self.bot.logger.log_error(e, "set_city")

    def get_weather_city(self, user_id: int):
        self.cursor.execute(f"""SELECT city FROM weather WHERE user_id = {user_id}""")
        result = self.cursor.fetchone()
        return result[0] if result else None
