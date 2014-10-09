from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.expression import ExpressionProperty
from nio.modules.threading import Lock
from .state_mixin import StateMixin, NoState

@Discoverable(DiscoverableType.block)
class Relay(StateMixin, Block):
    '''
    If *state_sig* evaluates to True then the signal sets the state according
    to *state_expr*. Else, the signal gets notified if the state is True.

    state starts as False.

    '''

    state_sig = ExpressionProperty(title="Is State Signal",
                                   default="{{hasattr($, 'state')}}")

    def __init__(self):
        super().__init__()
        self._safe_lock = Lock()
       
    def configure(self, context):
        super().configure(context)
        self._state = False # deletes persistence. Makes sure _state starts as False

    def process_signals(self, signals):
        signal_list = []
        with self._safe_lock:
            for signal in signals:
                try:
                    is_state_sig = self.state_sig(signal)
                except Exception as e:
                    is_state_sig = False
                    self._logger.error(
                        "Failed determining state signal: {}".format(e)
                    )
                if is_state_sig:
                    self._logger.debug("Attempting to set state")
                    self._process_state(signal)
                else:
                    if self._state:
                        self._logger.debug("State is True")
                        signal_list.append(signal)
                    else:
                        self._logger.debug("State is False")
        self.notify_signals(signal_list)

