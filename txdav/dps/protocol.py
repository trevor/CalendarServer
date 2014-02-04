##
# Copyright (c) 2014 Apple Inc. All rights reserved.
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

from twext.who.idirectory import RecordType
from twisted.protocols import amp
from twisted.internet.defer import inlineCallbacks, returnValue
from twext.python.log import Logger

import cPickle as pickle

log = Logger()



class RecordWithShortNameCommand(amp.Command):
    arguments = [
        ('recordType', amp.String()),
        ('shortName', amp.String()),
    ]
    response = [
        ('fields', amp.String()),
    ]


class DirectoryProxyAMPProtocol(amp.AMP):
    """
    Server side of directory proxy
    """

    def __init__(self, directory):
        """
        """
        amp.AMP.__init__(self)
        self._directory = directory


    @RecordWithShortNameCommand.responder
    @inlineCallbacks
    def recordWithShortName(self, recordType, shortName):
        recordType = recordType.decode("utf-8")
        shortName = shortName.decode("utf-8")
        log.debug("RecordWithShortName: {r} {n}", r=recordType, n=shortName)
        record = (yield self._directory.recordWithShortName(
            RecordType.lookupByName(recordType), shortName)
        )
        fields = {}
        for field, value in record.fields.iteritems():
            # print("%s: %s" % (field.name, value))
            valueType = self._directory.fieldName.valueType(field)
            # TODO: handle other value types like NamedConstants
            if valueType is unicode:
                fields[field.name] = value

        response = {
            "fields": pickle.dumps(fields),
        }
        log.debug("Responding with: {response}", response=response)
        returnValue(response)
