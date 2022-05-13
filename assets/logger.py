import asyncio
import json
from datetime import datetime

import discord


class Logger:

    def __init__(self, bot, logfile_path="botman.log", logfile_json_path="botman.json"):
        self.bot = bot
        self.logfile_path = logfile_path
        self.logfile_json_path = logfile_json_path
        self.logfile = open(self.logfile_path, 'a')
        self.log_to_channel = True

        try:
            self.json_log_object = json.load(open(logfile_json_path, 'r'))
        except:
            self.json_log_object = {}
        self.logfile_json = open(logfile_json_path, 'w')

        self.log_info("Logger initialized")

    def send_message(self, message=None, embed=None):
        if not self.bot.log_channel:
            return
        if not message and not embed:
            return
        if message:
            asyncio.create_task(self.bot.log_channel.send(message))
        if embed:
            asyncio.create_task(self.bot.log_channel.send(embed=embed))

    def log_error(self, error: Exception, file_or_command: str = "N/A", send_message=True):
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        error_message = f"{dt_string} | {file_or_command} | ERROR | {type(error).__name__} | {error}"
        error_dict = {
            "type": "error",
            "timestamp": dt_string,
            "file_or_command": file_or_command,
            "error_type": type(error).__name__,
            "message": str(error)
        }
        self.logfile.write(error_message + "\n")
        self.logfile.flush()
        self.json_log_object[dt_string] = error_dict
        self.clear_logfile_json(send_message=False)  # clear out the file because it doesn't overwrite the previous data
        json.dump(self.json_log_object, self.logfile_json, indent=4)
        self.logfile_json.flush()
        if self.bot.log_channel and send_message and self.log_to_channel:
            embed = discord.Embed(title=f"Error: {file_or_command}", description=error, color=0xFF0000)
            embed.set_footer(text=dt_string)
            self.send_message(embed=embed)

    def log_info(self, info: str, file_or_command="N/A", send_message=True):
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        info_message = f"{dt_string} | {file_or_command} | INFO | {info}"
        self.logfile.write(info_message + "\n")
        self.logfile.flush()
        info_dict = {
            "type": "info",
            "timestamp": dt_string,
            "file_or_command": file_or_command,
            "message": str(info)
        }
        self.json_log_object[dt_string] = info_dict
        self.clear_logfile_json(send_message=False)  # clear out the file because it doesn't overwrite the previous data
        json.dump(self.json_log_object, self.logfile_json, indent=4)
        self.logfile_json.flush()
        if self.bot.log_channel and send_message and self.log_to_channel:
            embed = discord.Embed(title=f"Info: {file_or_command}", description=info, color=0xFFFF00)
            embed.set_footer(text=dt_string)
            self.send_message(embed=embed)

    def clear_logfile(self, send_message=True):
        self.logfile.close()
        self.logfile = open(self.logfile_path, 'w')
        self.logfile.close()
        self.logfile = open(self.logfile_path, 'a')
        if self.bot.log_channel and send_message and self.log_to_channel:
            embed = discord.Embed(title="Cleared logfile!", color=0x000000)
            self.send_message(embed=embed)

    def clear_logfile_json(self, send_message=True):
        self.logfile_json.close()
        self.logfile_json = open(self.logfile_json_path, 'w')
        self.logfile_json.close()
        self.logfile_json = open(self.logfile_json_path, 'w')
        if self.bot.log_channel and send_message and self.log_to_channel:
            embed = discord.Embed(title="Cleared JSON logfile!", color=0x000000)
            self.send_message(embed=embed)

    def retrieve_log_json(self, message_count: int = 5, log_type="all"):
        """Accepted values of log_type: all, error, info"""
        to_return = []
        time_list = sorted(list(self.json_log_object.keys()))
        time_list.reverse()
        try:
            for time in time_list[:message_count]:
                details = self.json_log_object[time]
                if details["type"] == log_type or log_type == "all":
                    to_return.append(details)
        except TypeError:  # no logs found
            return to_return
        return to_return
