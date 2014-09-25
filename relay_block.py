from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.modules.threading import Lock
from .state_mixin import StateMixin

@Discoverable(DiscoverableType.block)
class Relay(StateMixin, Block):
    '''
    When the state obtained from State Expression is true, signals are allowed through.
    Else signals are blocked
    '''
    def __init__(self):
        super().__init__()
        self._safe_lock = Lock()

    def process_signals(self, signals):
        signal_list = []
        with self._safe_lock:
            for signal in signals:
                self._process_state(signal)
                if self._state:
                    signal_list.append(signal)
        self.notify_signals(signal_list)

    #def _state_change_error(self, e):
        ## silence errors during state changes that are bad
        #pass
