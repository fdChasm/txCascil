import time

from twisted.internet import reactor

from cascil import ServerServiceFactory
from cascil.permissions.functionality import Functionality
from cascil.permissions.permission_resolver import PermissionResolver
from cascil.events import EventSubscriptionFulfiller


config = {
    'interface': '127.0.0.1',
    'port': 29000,
    'transport': 'netstring',
    'packing': 'json',
    'authentication': {
        'type': 'cube2crypto',
        "credentials": {
            "example.com": {
                "bob": {
                    "groups": ["spyd.gep.bob"],
                    "pubkey": "+619da5dd56cefee9ee35091d27490d78b19d0d884f1fc7b5"
                }
            }
        }
    },
}

class PingMessageHandler(object):
    msgtype = 'ping'
    execute = Functionality(msgtype)

    @classmethod
    def handle_message(cls, context, client_controller, message):
        server_time = int(time.time() * 1000000)
        client_time = message['time']
        client_controller.send({'msgtype': 'pong', 'client_time': client_time, 'server_time': server_time}, message.get('reqid'))

message_handlers = {
    'ping': PingMessageHandler,
}

permission_dictionary = {
    "spyd.gep.bob": {
        "allows": ["*"]
    }
}
permission_resolver = PermissionResolver.from_dictionary(permission_dictionary)
event_subscription_fulfiller = EventSubscriptionFulfiller()


def publish_clock_tick_event():
    event_subscription_fulfiller.publish('clock_tick', int(time.time()))
    reactor.callLater(1, publish_clock_tick_event)

reactor.callLater(1, publish_clock_tick_event)

context = {}

service_factory = ServerServiceFactory()
cascil_service = service_factory.build_service(context, config, message_handlers, permission_resolver, event_subscription_fulfiller)

cascil_service.startService()
reactor.run()
