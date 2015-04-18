from .state_base_block import StateBase
from nio.common.block.attribute import Input
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import ExpressionProperty


@Input('setter')
@Discoverable(DiscoverableType.block)
class Relay(StateBase):

    """
    If *state_sig* evaluates to True then the signal sets the state according
    to *state_expr*. Else, the signal gets notified if the *state* is True.
    """

    state_sig = ExpressionProperty(
        title="Is State Signal", default="{{ hasattr($, 'state') }}")

    def _process_group(self, signals, group, to_notify):
        """ Process the signals for a group.

        Add any signals that should be passed through to the to_notify list
        """
        for signal in signals:
            try:
                is_state_sig = self.state_sig(signal)
            except:
                is_state_sig = False
                self._logger.exception("Failed determining state signal")

            # 3 choices - state setter, state is true, or state is false
            if is_state_sig:
                self._logger.debug("Attempting to set state")
                self._process_state(signal, group)
            elif self.get_state(group):
                self._logger.debug("State is True")
                to_notify.append(signal)
            else:
                self._logger.debug("State is False")

    def _process_setter_group(self, signals, group, to_notify):
        """ Process the signals for a group.

        Add any signals that should be passed through to the to_notify list
        """
        for signal in signals:
            self._logger.debug("Attempting to set state")
            self._process_state(signal, group)
