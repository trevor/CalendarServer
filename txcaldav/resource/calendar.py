##
# Copyright (c) 2010 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

"""
CalDAV resources.
"""

__all__ = [
    "CalDAVResource",
    "CalendarHomeResource",
    "CalendarCollectionResource",
    "CalendarObjectResource",
    "ScheduleInboxResource",
    "ScheduleOutboxResource",
]


import urllib

from twext.python.log import LoggingMixIn
from twext.web2.http_headers import MimeType
from twext.web2.http import RedirectResponse, Response
from twext.web2.stream import MemoryStream

from twistedcaldav import config
from twistedcaldav.extensions import DAVResource


class CalDAVResource(DAVResource, LoggingMixIn):
    """
    CalDAV resource.
    """
    def davComplianceClasses(self):
        return (
            tuple(super(CalDAVResource, self).davComplianceClasses())
            + config.CalDAVComplianceClasses
        )


class CalendarHomeResource(CalDAVResource):
    """
    Calendar home resource.

    This resource is backed by an L{ICalendarHome} implementation.
    """


class CalendarCollectionResource(CalDAVResource):
    """
    Calendar collection resource.

    This resource is backed by an L{ICalendar} implementation.
    """
    def render(self, request):
        if config.EnableMonolithicCalendars:
            #
            # Send listing instead of iCalendar data to HTML agents
            # This is mostly useful for debugging...
            #
            # FIXME: Add a self-link to the dirlist with a query string so
            #     users can still download the actual iCalendar data?
            #
            # FIXME: Are there better ways to detect this than hacking in
            #     user agents?
            #
            # FIXME: In the meantime, make this a configurable regex list?
            #
            agent = request.headers.getHeader("user-agent")
            if agent is not None and (
                agent.startswith("Mozilla/") and agent.find("Gecko") != -1
            ):
                renderAsHTML = True
            else:
                renderAsHTML = False
        else:
            renderAsHTML = True

        if not renderAsHTML:
            # Render a monolithic iCalendar file
            if request.path[-1] != "/":
                # Redirect to include trailing '/' in URI
                return RedirectResponse(request.unparseURL(path=urllib.quote(urllib.unquote(request.path), safe=':/')+'/'))

            def _defer(data):
                response = Response()
                response.stream = MemoryStream(str(data))
                response.headers.setHeader("content-type", MimeType.fromString("text/calendar"))
                return response

            d = self.iCalendarRolledup(request)
            d.addCallback(_defer)
            return d

        return super(CalDAVResource, self).render(request)


class CalendarObjectResource(CalDAVResource):
    """
    Calendar object resource.

    This resource is backed by an L{ICalendarObject} implementation.
    """


class ScheduleInboxResource(CalDAVResource):
    """
    Schedule inbox resource.

    This resource is backed by an XXXXXXX implementation.
    """


class ScheduleOutboxResource(CalDAVResource):
    """
    Schedule outbox resource.

    This resource is backed by an XXXXXXX implementation.
    """
