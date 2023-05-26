from search.logging.logs import logging_setup, log_process_time


class SearchProcess:
    def __init__(self, latitude: float, longitude: float, radius: int) -> None:
        super().__init__()
        self.log = logging_setup()
        self.latitude = latitude
        self.longitute = longitude
        self.radius = radius

    @log_process_time
    def process(self):
        self.log.info("coucou")
