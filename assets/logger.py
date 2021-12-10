from datetime import datetime


class Logger:

    def __init__(self, logfile):
        self.logfile = logfile
        self.log = open(logfile, 'a')
        self.log_info("Logger initialized")

    def log_error(self, error: Exception, file_or_command: str):
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        error_message = f"{dt_string} | {file_or_command} | ERROR | {type(error).__name__} | {error}"
        self.log.write(error_message + "\n")

    def log_info(self, info: str, file_or_command="N/A"):
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        info_message = f"{dt_string} | {file_or_command} | INFO | {info}"
        self.log.write(info_message + "\n")
