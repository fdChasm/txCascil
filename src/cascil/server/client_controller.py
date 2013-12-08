from cascil.exceptions import AuthenticationHardFailure


class ClientController(object):
    def __init__(self, context, client_addr, protocol, authentication_controller, central_message_handler, permission_resolver):
        self._context = context
        self._client_addr = client_addr
        self._protocol = protocol
        self._authentication_controller = authentication_controller
        self._central_message_handler = central_message_handler
        self._permission_resolver = permission_resolver

        self.event_subscriptions = []

    def send(self, message, respid=None):
        if respid is not None:
            message['respid'] = respid
        self._protocol.send(message)

    @property
    def is_authenticated(self):
        return self._authentication_controller.is_authenticated

    def get_group_names(self):
        return self._authentication_controller.groups

    def allowed(self, functionality):
        group_names = self.get_group_names()
        return self._permission_resolver.groups_allow(group_names, functionality)

    def connection_established(self):
        pass

    def receive(self, message):
        if self.is_authenticated:
            self._receive_authenticated(message)
        else:
            self._receive_not_authenticated(message)

    def disconnected(self):
        for event_subscription in self.event_subscriptions:
            event_subscription.unsubscribe()

    def _receive_not_authenticated(self, message):
        try:
            self._authentication_controller.receive(message)
        except AuthenticationHardFailure:
            self.send({"msgtype": "error", "message": "Authentication failure"}, message.get('reqid', None))
            self._protocol.disconnect()

    def _receive_authenticated(self, message):
        try:
            self._central_message_handler.handle_message(self._context, self, message)
        except Exception as e:
            self.send({"msgtype": "error", "message": e.message}, message.get('reqid', None))

    def on_subscribed_event(self, event_stream, data):
        self.send({"msgtype": "event", "event_stream": event_stream, "event_data": data})
