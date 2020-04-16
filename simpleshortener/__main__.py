#!/usr/bin/env python3
import argparse
import logging

from webapp import WebApp

if __name__ == "__main__":

    # Gets inline arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-n", "--host", dest="host", default="127.0.0.1",
                        help="the service host")
    parser.add_argument("-p", "--port", dest="port", type=int, default=7878,
                        help="the service port")

    parser.add_argument("-u", "--redis-url", dest="redis_url",
                        help="redis url for \"url\" in \"redis://{host}[:port]/{db}\" format")
    parser.add_argument("-s", "--redis-statistics", dest="redis_statistics",
                        help="redis url for \"statistics\" in \"redis://{host}[:port]/{db}\" format")
    parser.add_argument("-f", "--url-file", dest="url_file",
                        help="JSON file contains url. It can be also provided over http(s)")
    parser.add_argument("-k", "--url-file-expiration", dest="url_file_expiration", type=int,
                        help="url file expiration in hours")
    parser.add_argument("-e", "--statistics-expiration", dest="statistics_expiration", type=int,
                        help="expiration of the statistics")
    parser.add_argument("-d", "--flask-debug", dest="flask_debug", action="store_true",
                        help="expiration of the statistics")

    parser.add_argument("-v", dest="log_level", action="count", default=0,
                        help="number of -v specifics level of verbosity")
    parser.add_argument("--info", dest="log_level", action="store_const", const=2, help="equal to -vv")
    parser.add_argument("--debug", dest="log_level", action="store_const", const=3, help="equal to -vvv")

    # Parses args
    args = vars(parser.parse_args())
    # Removes None elements
    args = {k: args[k] for k in args if args[k] is not None}

    # Parses the verbosity level
    if "log_level" in args:
        try:
            args["log_level"] = {
                0: logging.ERROR,
                1: logging.WARNING,
                2: logging.INFO,
                3: logging.DEBUG
            }[args["log_level"]]

        except KeyError:
            args["log_level"] = logging.DEBUG

    # Gets flask options
    flask_options = {
        "host": args.pop("host"),
        "port": args.pop("port"),
        "debug": args.pop("flask_debug")
    }

    # Starts Flask app
    WebApp(**args).run(**flask_options)
