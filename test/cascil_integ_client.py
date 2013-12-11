import sys
import time

from twisted.internet import reactor

from txCascil import ClientServiceFactory


config = {
    'interface': '127.0.0.1',
    'port': 29000,
    'transport': 'netstring',
    'packing': 'json',
    'authentication': {
        'type': 'cube2crypto',
        'domain': 'example.com',
        'username': 'bob',
        'privkey': '81a838d411f32284ce4d9bfee2af62d62db0308fa73a6b2f',
    },
}

def display_ping(message):
    start_time = message['client_time']
    echo_time = message['server_time']
    now_time = int(time.time() * 1000000)

    cts = (echo_time - start_time) / 1000.0
    stc = (now_time - echo_time) / 1000.0
    rnd = (now_time - start_time) / 1000.0

    print "ping response: cts: {:.4f} ms, stc: {:.4f} ms, rnd: {:.4f} ms".format(cts, stc, rnd)

def display_error(failure):
    sys.stderr.write(str(failure))

class PongMessageHandler(object):
    @classmethod
    def handle_message(cls, context, client_controller, message):
        display_ping(message)

class PrintMessageHandler(object):
    @classmethod
    def handle_message(cls, context, client_controller, message):
        print message

class AuthenticatedMessageHandler(object):
    @classmethod
    def handle_message(cls, context, client_controller, message):
        print "Authenticated foo"
        client_controller.request({'msgtype': 'ping', 'time': int(time.time() * 1000000)})

message_handlers = {
    'authenticated': AuthenticatedMessageHandler,
    'pong': PongMessageHandler,
    'event': PrintMessageHandler,
    'status': PrintMessageHandler,
}

context = {}

client_service_factory = ClientServiceFactory()
client_service = client_service_factory.build_service(context, config, message_handlers)

# Messages queued before authentication may take a long time to be delivered
client_service.request({'msgtype': 'ping', 'time': int(time.time() * 1000000)}).addCallbacks(display_ping, display_error)
client_service.request({'msgtype': 'subscribe', 'event_stream': 'clock_tick'})

client_service.startService()
reactor.run()
