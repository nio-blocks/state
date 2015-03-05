from .state_base_block import StateBase
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.signal.base import Signal
from nio.metadata.properties import BoolProperty


@Discoverable(DiscoverableType.block)
class StateChange(StateBase):

    """ Notifies a signal on *state* change.

    Maintains a *state*. When *state* changes, a signal is notified
    that containes the *state* and *prev_state*.

    *state* is set by the *state_expr* property. It is an expression
    property that evalues to *state*. If the expression fails,
    then the *state* remains unmodified.

    *state* changing from None to not None does not count as a state change.
    This makes is so that setting the initial state does not trigger
    a notification Signal.
    """

    exclude = BoolProperty(default=True, title="Exclude Existing Fields")

    def _process_group(self, signals, group, to_notify):
        """ Process the signals for a group.

        Add any signals that should be passed through to the to_notify list
        """
        for signal in signals:
            state_change = self._process_state(signal, group)
            if state_change is not None:

                # If we are excluding existing fields we want to add
                # the states and previous states to an empty signal
                if self.exclude:
                    signal = Signal()

                setattr(signal, 'prev_state', state_change[0])
                setattr(signal, 'state', state_change[1])
                to_notify.append(signal)
