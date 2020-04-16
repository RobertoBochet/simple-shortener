import json
import logging
from collections import Counter
from datetime import date, timedelta
from typing import List, Tuple, Union
from urllib.parse import urlparse

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import escape
from redis import StrictRedis
from schema import Schema, SchemaError

from cooldown import CooldownMethod
from .exceptions import *
from .redis_key import *

# Retrieves logger
_logger = logging.getLogger(__package__)


class SimpleShortener:
    def __init__(self,
                 url_file: str = "./url.json",
                 url_file_expiration: int = 6,
                 redis_url: str = "redis://127.0.0.1:6379/0",
                 redis_statistics: str = "redis://127.0.0.1:6379/1",
                 statistics_expiration: Union[timedelta, int] = timedelta(weeks=3)
                 ):

        # Saves the position of the url file
        self._url_file = url_file

        # Saves statistics expiration
        self._statistics_expiration = statistics_expiration if isinstance(statistics_expiration,
                                                                          timedelta) else timedelta(
            days=statistics_expiration)

        # Init and test redis connection
        try:
            self._redis_url = StrictRedis.from_url(url=redis_url,
                                                   charset="utf-8",
                                                   decode_responses=True)
            self._redis_statistics = StrictRedis.from_url(url=redis_statistics,
                                                          charset="utf-8",
                                                          decode_responses=True)
            self._redis_url.ping()
            self._redis_statistics.ping()

        except ConnectionError as e:
            _logger.fatal("Redis error: {}".format(e.__str__()))
            raise

        try:
            # Updates the db
            self.sync()

        except SyncFailed:
            _logger.warning("An error occurred in an attempt to sync the db")

        # Creates background scheduler for update the db
        self._scheduler = BackgroundScheduler(daemon=True)

        self._scheduler.add_job(lambda: self.sync(), 'interval', hours=int(url_file_expiration))

        # Starts the scheduler
        self._scheduler.start()

    @CooldownMethod(60)
    def sync(self) -> None:
        """
        Tries to update the url db

        :raises UrlFileNotFound: if the local file wasn't found
        :raises UrlFileRecoveryFailed: if the remote file wasn't retrieved
        :raises UrlFileInvalidJSON: if the file was invalid JSON
        :raises UrlFileInvalidSchema: if the data didn't have the right scheme
        :raises SyncDbError: if an db error has occurred
        :raises SyncFailed: if sync was failed
        """
        _logger.info("Try to load url list...")

        try:
            # Check if the resource is remote
            if bool(urlparse(self._url_file).scheme):
                # Load the remote json
                response = requests.get(self._url_file)
                data = response.json()

            else:
                # Open the gyms file and load it as json
                with open(self._url_file, 'r') as f:
                    data = json.load(f)

        except FileNotFoundError:
            _logger.warning("Failed to load the url list: file not found")
            raise UrlFileNotFound

        except requests.exceptions.ConnectionError:
            _logger.warning("Failed to load the url list: an HTTP error has occurred")
            raise UrlFileRecoveryFailed

        except ValueError:
            _logger.warning("Failed to load the url list: failed to decode json")
            raise UrlFileInvalidJSON

        # tests the data schema
        schema = Schema([
            {
                "target": str,
                "short": [str]
            }
        ])
        try:
            data = schema.validate(data)

        except SchemaError:
            _logger.warning("Failed to load the url list: invalid schema of the json")
            raise UrlFileInvalidSchema

        p = self._redis_url.pipeline()
        p_s = self._redis_statistics.pipeline()
        p.flushdb()

        # Inserts the short and the target in the url db
        for u in data:
            t = escape(u["target"])
            for s in [escape(v) for v in u["short"]]:
                p.set(s, t)
                p_s.sadd(STATISTICS_TARGET.format(t), s)

        try:
            p.execute()
            p_s.execute()

        except:
            _logger.warning("Failed to load the url list: an db error has occurred")
            raise SyncDbError

        _logger.info("Sync was completed")

    def get_url(self, url: str) -> str:
        """
        Provided the short url returns the target url

        :param url: the short url without the root slash
        :type url: str
        :raises UrlNotFound: if the short url doesn't exist
        :return: the target url
        :rtype: str

        :example:

        >>> simpleshortener = UUS()
        >>> simpleshortener.get_url("gtlb")
        https://gitlab.org
        """

        url = escape(url)

        _logger.debug("try to found \"{}\"".format(url))

        if not self._redis_url.exists(url):
            _logger.debug("\"{}\" not found".format(url))
            raise UrlNotFound

        return self._redis_url.get(url)

    def update_url_statistics(self, short: str, user_agent: str = None) -> None:
        """
        Updates the statistics for the short url provided with count and operation system is used by the user

        :param short: a short url
        :type short: str
        :param user_agent: a user agent string, defaults to None
        :type user_agent: str, optional
        """

        s = escape(short)
        p = self._redis_statistics.pipeline()

        d = date.today().strftime("%Y-%m-%d")

        total_key = STATISTICS_DATE_TOTAL.format(short=s, date=d)
        p.incr(total_key)
        p.expire(total_key, self._statistics_expiration)

        if user_agent is not None:
            if "Windows" in user_agent:
                user_agent = "windows"
            elif "Macintosh" in user_agent:
                user_agent = "mac"
            elif "iPhone" in user_agent:
                user_agent = "ios"
            elif "Android" in user_agent:
                user_agent = "android"
            elif "Linux" in user_agent:
                user_agent = "linux"
            else:
                user_agent = "other"

            useragent_key = STATISTICS_USERAGENT.format(short=s, date=d, user_agent=user_agent)
            p.incr(useragent_key)
            p.expire(useragent_key, self._statistics_expiration)

        p.execute()

    def get_url_list(self) -> List[Tuple[str, List[str]]]:
        """
        Get a list of the url and their shorts

        :return: returns a list of the available url and their shorts
        :rtype: List[Tuple[str, List[str]]]
        """
        data = []

        for v in self._redis_statistics.keys(STATISTICS_TARGET_ALL):
            data.append((v[len(STATISTICS_TARGET_ROOT):], list(self._redis_statistics.smembers(v))))

        return data

    def get_metrics(self, url: str):
        """
        Returns complex struct includes the metrics for the url

        :param url: a target url or a short url
        :type url: str
        """
        data = {
            "period": {
                "start": None,
                "end": None,
                "length": None
            }
        }

        # Sets the period of the data
        data["period"]["start"] = (date.today() - self._statistics_expiration).strftime("%Y-%m-%d")
        data["period"]["end"] = date.today().strftime("%Y-%m-%d")
        data["period"]["length"] = self._statistics_expiration.days

        # Checks if the url is not a target url
        if not self._redis_statistics.exists(STATISTICS_TARGET.format(url)):
            # Returns metrics of the short url
            return dict(data, **(self._get_metrics_short(url)))

        # Prepares the struct
        data = dict(data, **{
            "url": url,
            "total": 0,
            "per-day": None,
            "user-agent": {},
            "date": {},
            "short": []
        })

        # For each short for the target url
        for s in self._redis_statistics.smembers(STATISTICS_TARGET.format(url)):
            # Gets the short metrics
            short_data = self._get_metrics_short(s)
            # Adds them to the list of the shorts metrics
            data["short"].append(short_data)

            # Updates total target
            data["total"] += short_data["total"]
            # Updates user agent target
            data["user-agent"] = dict(Counter(data["user-agent"]) + Counter(short_data["user-agent"]))

            # For each date for the short
            for d in short_data["date"]:
                # If there isn't yet, creates it for the target
                if d not in data["date"]:
                    data["date"][d] = {
                        "total": 0,
                        "user-agent": {}
                    }
                # Updates total for current date
                data["date"][d]["total"] += short_data["date"][d]["total"]
                # Updates user agent for current date
                data["date"][d]["user-agent"] = dict(Counter(data["date"][d]["user-agent"])
                                                     + Counter(short_data["date"][d]["user-agent"]))

        data["per-day"] = data["total"] / self._statistics_expiration.days

        return data

    def _get_metrics_short(self, url: str):
        data = {
            "url": url,
            "total": 0,
            "per-day": None,
            "user-agent": {},
            "date": {},
        }
        string_begin, string_end = STATISTICS_DATE_TOTAL.format(short=url, date="{date}").split("{date}")

        total = 0

        for k in self._redis_statistics.keys(STATISTICS_DATE_TOTAL.format(short=url, date="*")):
            d = k[len(string_begin):-len(string_end)]
            v = int(self._redis_statistics.get(k))
            data["date"][d] = {
                "total": v,
                "user-agent": {}
            }
            total += v

        data["total"] = total
        data["per-day"] = total / self._statistics_expiration.days

        for d in data["date"]:
            for k in self._redis_statistics.keys(STATISTICS_USERAGENT.format(short=url, date=d, user_agent="*")):
                ua = k[len(STATISTICS_USERAGENT.format(short=url, date=d, user_agent="")):]
                v = int(self._redis_statistics.get(k))

                data["user-agent"][ua] = data["user-agent"].get(ua, 0) + v

                data["date"][d]["user-agent"][ua] = v

        return data
