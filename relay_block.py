from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.signal.base import Signal
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.modules.scheduler import Job
from nio.modules.threading import Lock

from .state_change import state_change_block

# We aren't even going to create a volatile one for now.
# class RelayVolatile(state_change_block.StateChangeVolatile):

@Discoverable(DiscoverableType.block)
class Relay(state_change_block.StateChange):
    """ Notifies a signal on *state* change.

    Maintains a *state*. When the state is True, signals pass through. When the state is
    False, signals are blocked

    *state* is set by the *state_expr* property. It is an expression
    property that evalues to *state*. If the expression fails,
    then the *state* remains unmodified.

    When state has not been set, this Block will block signals (equivalent to state == False)
    """
    def process_signals(self, signals):
        signals = []
        with self._safe_lock:
            for signal in signals:
                self._process_state(signal)
                if self._state:
                    signals.append(signal)
        self.notify_signals(signal)

    def process_signals(self, signals):
        super().process_signals(signals)
        if self._state:
            self.notify_signals(signals)

    def _state_change_error(self, e):
        # silence errors during state changes
        pass
