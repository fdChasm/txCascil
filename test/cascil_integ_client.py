import time

from twisted.internet import reactor

from cascil.client.service_factory import ServiceFactory


client_service_factory = ServiceFactory()

config = {
    'interface': '127.0.0.1',
    'port': 29000,
    'transport': 'netstring',
    'packing': 'edn',
    'authentication': {
        'type': 'cube2crypto',
        'domain': 'example.com',
        'username': 'bob',
        'privkey': '81a838d411f32284ce4d9bfee2af62d62db0308fa73a6b2f',
    },
}

class AuthenticatedMessageHandler(object):
    msgtype = 'authenticated'

    @classmethod
    def handle_message(cls, context, client_controller, message):
        print "Authenticated foo"

class PongMessageHandler(object):
    msgtype = 'pong'

    @classmethod
    def handle_message(cls, context, client_controller, message):
        start_time = message['client_time']
        echo_time = message['server_time']
        now_time = int(time.time() * 1000000)

        cts = (echo_time - start_time) / 1000.0
        stc = (now_time - echo_time) / 1000.0
        rnd = (now_time - start_time) / 1000.0

        print "ping response: cts: {:.4f} ms, stc: {:.4f} ms, rnd: {:.4f} ms".format(cts, stc, rnd)

message_handlers = {
    'authenticated': AuthenticatedMessageHandler,
    'pong': PongMessageHandler,
}

context = {}

client_service = client_service_factory.build_service(context, config, message_handlers)

client_service.startService()

reactor.run()
