from cascil.server.central_message_handler import CentralMessageHandler
from cascil.client.client_controller import ClientController


class ClientControllerFactory(object):
    def __init__(self, context, message_handlers):
        self._context = context
        self._message_handlers = message_handlers

    def build(self, client_addr, protocol, authentication_controller):
        central_message_handler = CentralMessageHandler(self._message_handlers)
        return ClientController(self._context, client_addr, protocol, central_message_handler, authentication_controller)
