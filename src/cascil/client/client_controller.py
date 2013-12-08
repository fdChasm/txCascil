import itertools

from cascil.exceptions import AuthenticationHardFailure
import traceback


class ClientController(object):
    def __init__(self, context, client_addr, protocol, central_message_handler, authentication_controller):
        self._context = context
        self._client_addr = client_addr
        self._protocol = protocol
        self._authentication_controller = authentication_controller
        self._central_message_handler = central_message_handler
        self._request_id_counter = itertools.count()

    def send(self, message, respid=None):
        if respid is not None:
            message['respid'] = respid
        self._protocol.send(message)

    @property
    def is_authenticated(self):
        return self._authentication_controller.is_authenticated

    def receive(self, message):
        if self.is_authenticated:
            self._receive_authenticated(message)
        else:
            self._receive_not_authenticated(message)

    def connection_established(self):
        self._authentication_controller.connection_established()

    def disconnected(self):
        pass

    def _receive_not_authenticated(self, message):
        try:
            self._authentication_controller.receive(message)
            if self.is_authenticated:
                self._receive_authenticated({'msgtype': 'authenticated'})
        except AuthenticationHardFailure as e:
            self.send({"msgtype": "error", 'type': e.type, "message": "Authentication failure"}, message.get('reqid', None))
            self._protocol.disconnect()

    def _receive_authenticated(self, message):
        try:
            self._central_message_handler.handle_message(self._context, self, message)
        except Exception as e:
            traceback.print_exc()
            self.send({"msgtype": "error", 'type': e.type, "message": e.message}, message.get('reqid', None))
