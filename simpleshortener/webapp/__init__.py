import logging
from os.path import join, dirname, abspath
from typing import Union, Tuple

import simplejson as simplejson
from flask import Flask, abort, request, Response, render_template
from werkzeug.utils import redirect

from cooldown.exceptions import CooldownError
from log import LoggerSetup
from simpleshortener.simpleshortener import SimpleShortener

# Retrieves logger
_logger = logging.getLogger(__name__)


class WebApp(Flask):
    def __init__(self,
                 log_level: Union[int, str] = logging.ERROR,
                 log_level_modules: Union[int, str] = logging.ERROR,
                 **kwargs):
        super(WebApp, self).__init__("simpleshortener",
                                     template_folder=join(dirname(abspath(__file__)), 'templates'),
                                     static_folder=join(dirname(abspath(__file__)), 'static'))

        # Init log
        LoggerSetup(["webapp", "simpleshortener"], log_level, log_level_modules=log_level_modules)

        # Init UUS
        self._ss = SimpleShortener(**kwargs)

        # Sets url rules for api
        self.add_url_rule("/api/v2/sync", "sync", view_func=self._sync)
        self.add_url_rule("/api/v2/url_list", "url_list", view_func=self._url_list)
        self.add_url_rule("/api/v2/metrics", "get_metrics", view_func=self._get_metrics, methods=["GET", "POST"])

        # Sets special pages
        self.add_url_rule("/statistics", "statistics", view_func=self._statistics)

        # Sets a 404 for the favicon and robots.txt
        self.add_url_rule("/favicon.ico", "favicon.ico", view_func=lambda: abort(404))
        self.add_url_rule("/robots.txt", "robots.txt", view_func=lambda: abort(404))

        # Sets short url
        self.add_url_rule("/<path:url>", "redirect", view_func=self._redirect)

        _logger.info("The web app is ready")

    def _sync(self) -> Union[str, Tuple[str, int]]:
        # Tries to sync the url db
        try:
            self._ss.sync()
            return "Done"

        except CooldownError:
            return "Too many requests in a short period", 503

        except SyntaxError as e:
            return "An error has occurred ({})".format(e.__class__.__name__), 503

    def _url_list(self):
        return Response(
            response=simplejson.dumps(self._ss.get_url_list()),
            status=200,
            mimetype="application/json")

    def _get_metrics(self):
        if request.json is not None and "url" in request.json:
            return Response(
                response=simplejson.dumps(self._ss.get_metrics(request.json["url"])),
                mimetype="application/json")

        if request.args is not None and  "url" in request.args:
            return Response(
                response=simplejson.dumps(self._ss.get_metrics(request.args["url"])),
                mimetype="application/json")

        return abort(403)

    def _redirect(self, url: str):
        try:
            u = self._ss.get_url(url)

            # TODO: Move statistics update to another thread
            self._ss.update_url_statistics(url, user_agent=request.headers.get('User-Agent'))

            return redirect(u)
        except:
            return abort(404)

    def _statistics(self):
        return self.send_static_file('statistics.html')
