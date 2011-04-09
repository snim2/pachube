"""
Copyright (C) Sarah Mount, 2011.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Sarah Mount'
__date__ = 'April 2011'


# pylint: disable=W0613
# pylint: disable=E0611
# pylint: disable=F0401
# pylint: disable=E1101


from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson as json

from datetime import datetime
import logging

from keys import PACHUBE_KEY


class LaptopDatum(db.Model):
    timestamp = db.DateTimeProperty()
    temp = db.FloatProperty()
    critical_temp = db.FloatProperty()
    remaining = db.IntegerProperty()
    last_full_capacity = db.IntegerProperty()
    loadav = db.FloatProperty()
    running_procs = db.IntegerProperty()

    def parse_and_put(self, jsonfeed):
        ts = jsonfeed['updated'].split('.')[0]
        self.timestamp = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')

        for stream in jsonfeed['datastreams']:
            if stream['id'] == '0':
                self.temp = float(stream['current_value'])
            elif stream['id'] == '1':
                self.loadav = float(stream['current_value'])
            elif stream['id'] == '2':
                self.running_procs = int(stream['current_value'])
            elif stream['id'] == '3':
                self.remaining = int(stream['current_value'])
            elif stream['id'] == '4':
                self.last_full_capacity = int(stream['current_value'])
            elif stream['id'] == '5':
                self.critical_temp = float(stream['current_value'])
        self.put()


class FeedGrabber(webapp.RequestHandler):
    def get(self):
        url = "http://api.pachube.com/v2/feeds/22344.json"
        response = urlfetch.fetch(url=url,
                                  headers={'X-PachubeApiKey' : PACHUBE_KEY},
                                  method=urlfetch.GET,
                                  payload='')
        json_response = json.loads(response.content)
        logging.debug('Got the following from Pachube:\n' +
                      str(json_response))
        LaptopDatum().parse_and_put(json_response)
        return


application = webapp.WSGIApplication(
    [('/feedgrabber/', FeedGrabber),
     ],
    debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
