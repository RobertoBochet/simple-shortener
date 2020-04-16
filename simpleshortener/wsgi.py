import os

from webapp import WebApp


def gunicorn_entry():
    """
    Entry point for Gunicorn
    It retrieves the option from envs and return an initialized instance of WebApp

    :return an initialized instance of WebApp
    :rtype WebApp
    """

    env = {}

    env["url_file"] = os.getenv("SS_URL_FILE")
    env["url_file_expiration"] = os.getenv("SS_URL_EXPIRATION")
    env["redis_url"] = os.getenv("SS_REDIS_URL")
    env["redis_statistics"] = os.getenv("SS_REDIS_STATISTICS")
    env["statistics_expiration"] = os.getenv("SS_STATISTICS_EXPIRATION")
    env["log_level"] = os.getenv("SS_LOG_LEVEL")
    env["log_level_modules"] = os.getenv("SS_LOG_LEVEL_MODULES")

    # Remove None env
    env = {k: env[k] for k in env if env[k] is not None}

    # Return initialized WebApp
    return WebApp(**env)
