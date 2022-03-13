import asyncio
from datetime import datetime

import discord


class Logger:

    def __init__(self, bot, logfile_path):
        self.bot = bot
        self.logfile_path = logfile_path
        self.logfile = open(self.logfile_path, 'a')
        self.log_info("Logger initialized")
        self.logfile.write("\n")

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
        self.logfile.write(error_message + "\n")
        self.logfile.flush()
        if self.bot.log_channel and send_message:
            embed = discord.Embed(title="Error", description=error_message, color=0xFF0000)
            self.send_message(embed=embed)

    def log_info(self, info: str, file_or_command="N/A", send_message=True):
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        info_message = f"{dt_string} | {file_or_command} | INFO | {info}"
        self.logfile.write(info_message + "\n")
        self.logfile.flush()
        if self.bot.log_channel and send_message:
            embed = discord.Embed(title="Info", description=info_message, color=0xFFFF00)
            self.send_message(embed=embed)

    def clear_logfile(self, send_message=True):
        self.logfile.close()
        self.logfile = open(self.logfile_path, 'w')
        self.logfile.close()
        self.logfile = open(self.logfile_path, 'a')
        if self.bot.log_channel and send_message:
            embed = discord.Embed(title="Cleared logfile!", color=0x000000)
            self.send_message(embed=embed)

    def retrieve_log(self, message_count: int = 5):
        with open(self.logfile_path, 'r') as logfile:
            log_lines = logfile.readlines()
            log_lines.reverse()
        checking = True
        while checking:
            for line in range(len(log_lines)):
                if "|" not in str(log_lines[line]):
                    log_lines.pop(line)
                    break
                if log_lines[line].strip() == "\n":
                    log_lines.pop(line)
                    break
                if log_lines[line].strip() == "":
                    log_lines.pop(line)
                    break
            else:
                checking = False
        to_return = [line.strip("\n") for line in log_lines[:message_count][::-1]]
        return to_return
