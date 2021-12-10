from datetime import datetime


class Logger:

    def __init__(self, logfile):
        self.logfile = logfile
        self.log = open(logfile, 'a')
        self.log_info("Logger initialized")

    def log_error(self, error: Exception, file: str):
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        error_message = f"{dt_string} | {file} | ERROR | {type(error).__name__} | {error}"
        self.log.write(error_message + "\n")

    def log_info(self, info: str, file="N/A"):
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        info_message = f"{dt_string} | {file} | INFO | {info}"
        self.log.write(info_message + "\n")
