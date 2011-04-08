"""
Instant messanger bot, tied to imified.com.

Copyright (C) Sarah Mount, 2010.

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
__date__ = 'September 2010'

from google.appengine.ext import db
from google.appengine.ext import webapp

from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import urlfetch

import base64
import logging
import urllib

import xml.dom.minidom as minidom

### imified.com details
BOTKEY = '153885E3-4190-450C-ADC7873170752670'
USER = 's.mount@wlv.ac.uk'
PASSWORD = 'f00bar'

    
class IMBot(webapp.RequestHandler):

    @classmethod
    def imified(cls, form_fields):
        """Call an imified.com API method and handle response.
        """
        url = 'https://www.imified.com/api/bot/'
        base64string = base64.encodestring('%s:%s' % (USER, PASSWORD))[:-1]
        authString = 'Basic %s' % base64string
        form_data = urllib.urlencode(form_fields)
        # POST form.
        response = urlfetch.fetch(url=url,
                                  payload=form_data,
                                  method=urlfetch.POST,
                                  headers={'AUTHORIZATION' : authString})
        # Log IMIFIED response.
        if response.status_code == 200:
            logging.info('%s OK: %s' % (form_fields['apimethod'], response.content))
        else:
            logging.debug('%s FAILED<%s>: %s' %
                          (form_fields['apimethod'],
                           str(response.status_code),
                           response.content))
        return response
    
    @classmethod
    def get_user(cls, userkey):
        form_fields = {'botkey':BOTKEY,
                       'apimethod':'getuser',
                       'userkey':userkey}
        response = IMBot.imified(form_fields)
        if response.status_code == 200:
            xml = minidom.parseString(response.content)
            details = {}
            user = xml.getElementsByTagName('user')[0]
            # <rsp ...><user>...<user>screen_name</user></user>...</rsp>
            details['user'] = str(user.getElementsByTagName('user')[0].firstChild.nodeValue)
            details['channel'] = str(user.getElementsByTagName('network')[0].firstChild.nodeValue).lower()
            details['key'] = str(user.getElementsByTagName('userkey')[0].firstChild.nodeValue).lower()
            return details
        else:
            return None

    @classmethod
    def get_all_users(cls, network=None):
        form_fields = {'botkey':BOTKEY,
                       'apimethod':'getAllUsers',
                       'userkey':userkey}
        if network is not None:
            form_fields['network':network]
        response = IMBot.imified(form_fields)
        if response.status_code == 200:
            xml = minidom.parseString(response.content)
            users = xml.getElementsByTagName('user')
            usernames = []
            # <rsp ...><user>...<user>screen_name</user></user>...</rsp>
            for user in users[::2]:
                details = {}
                details['user'] = str(user.getElementsByTagName('user')[0].firstChild.nodeValue)
                details['channel'] = str(user.getElementsByTagName('network')[0].firstChild.nodeValue).lower()
                details['key'] = str(user.getElementsByTagName('userkey')[0].firstChild.nodeValue).lower()
                usernames.append(details)
            return usernames
        else:
            return None

    @classmethod
    def update_status(cls, message, channel):
        """Update the status of this bot.
        """
        form_fields = {'botkey':BOTKEY,
                       'apimethod':'updateStatus',
                       'network':channel}
        response = IMBot.imified(form_fields)
        return # Response only contains success / fail information.
    
    @classmethod
    def send_im(cls, user, messsage, channel):
        """Send an IM message which is NOT part of a BOT conversation.

        user: Userkey for required channel.
        message: Text to send
        channel: IM network to use. Must be in:
                 set(['twitter', 'jabber', 'msn', 'gTalk', 'aim', 'yahoo'])  
        """
        form_fields = {'botkey':BOTKEY,
                       'apimethod':'send',
                       'userkey':user.get_network_id(channel),
                       'network':channel}
        response = IMBot.imified(form_fields)
        return # Response only contains success / fail information.
    
    def post(self):
        """Conversational part of BOT goes here.
        """
        req_data = []
        for arg in self.request.arguments():
            req_data.append(arg + '=' + self.request.get(arg))
        logging.debug('Got following request data: ' +
                      ' '.join(req_data))
        self.response.out.write("Hello from Sarah's laptop!")

    def get(self):
        msg = 'Working on something for our 5CS006 students...watch this space!'
        IMBot.update_status('jabber', msg)


application = webapp.WSGIApplication(
    [('/bot/', IMBot),
     ],
    debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()

