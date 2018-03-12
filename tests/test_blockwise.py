# This file is part of the Python aiocoap library project.
#
# Copyright (c) 2012-2014 Maciej Wasilak <http://sixpinetrees.blogspot.com/>,
#               2013-2014 Christian Amsüss <c.amsuess@energyharvesting.at>
#
# aiocoap is free software, this file is published under the MIT license as
# described in the accompanying LICENSE file.

"""This tests advanced cases of blockwise transfer; simple sequential transfers
are covered in test_server.TestServer.test_replacing_resource."""

import asyncio

import unittest
import aiocoap
import aiocoap.defaults

from .test_server import WithTestServer, WithClient, no_warnings, asynctest

class TestBlockwise(WithTestServer, WithClient):
    # tracked as https://github.com/chrysn/aiocoap/issues/58; behavior can be successful more or less by chance
    @unittest.skip
    @no_warnings
    @asynctest
    async def test_sequential(self):
        """Test whether the client serializes simultaneous block requests"""

        pattern1 = b"01234 first pattern" + b"01" * 1024
        pattern2 = b"01234 second pattern" + b"02" * 1024

        request1 = aiocoap.Message(
                uri='coap://' + self.servernetloc + '/replacing/one',
                code=aiocoap.POST,
                payload=pattern1,
                )
        request2 = aiocoap.Message(
                uri='coap://' + self.servernetloc + '/replacing/one',
                code=aiocoap.POST,
                payload=pattern2,
                )

        responses = []
        for response in asyncio.as_completed([self.client.request(r).response for r in [request1, request2]]):
            response = await response
            self.assertTrue(response.code.is_successful(), "Simultaneous blockwise requests caused error.")
            responses.append(response.payload)

        self.assertSetEqual(set(responses), set(x.replace(b'0', b'O') for x in (pattern1, pattern2)))
