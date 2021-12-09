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
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS prefixes (id INTEGER PRIMARY KEY, prefix VARCHAR(10))""")

    def remove_guild_prefix(self, guild_id: int):
        self.cursor.execute(f"""DELETE FROM prefixes WHERE id = {guild_id}""")

    def add_guild_prefix(self, guild_id: int, prefix: str):
        self.remove_guild_prefix(guild_id)
        self.cursor.execute(f"""INSERT INTO prefixes VALUES({guild_id}, \"{prefix}\")""")

    def get_guild_prefix(self, guild_id: int):
        self.cursor.execute(f"""SELECT prefix FROM prefixes WHERE id = {guild_id}""")
        try:
            result = self.cursor.fetchone()[0]
            return result if result else self.bot.default_prefix
        except Exception as e:
            if isinstance(e, TypeError):
                return self.bot.default_prefix
            else:
                # TODO: Log error to file
                print(type(e).__name__, e)
                return self.bot.default_prefix
