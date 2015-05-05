from .state_base_block import StateBase
from nio.common.block.attribute import Input
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import ExpressionProperty
from nio.metadata.properties import ExpressionProperty, StringProperty, \
    VersionProperty


@Input('setter')
@Input('getter')
@Discoverable(DiscoverableType.block)
class MergeState(StateBase):

    """
    If *state_sig* evaluates to True then the signal sets the state according
    to *state_expr*. Else, the signal gets assigned the state to the attribute
    *state_name*.

    """

    state_name = StringProperty(default='state', title="State Name")
    state_sig = ExpressionProperty(title="Is State Signal",
                                   default="{{ hasattr($, 'state') }}")
    version = VersionProperty(default='2.0.0', min_version='2.0.0')

    def _process_group(self, signals, group, to_notify):
        for signal in signals:
            try:
                is_state_sig = self.state_sig(signal)
            except:
                is_state_sig = False
                self._logger.exception("Failed determining state signal")

            # 2 choices - state setter, or trying to pass through
            if is_state_sig:
                self._logger.debug("Attempting to set state")
                self._process_state(signal, group)
            else:
                existing_state = self.get_state(group)
                self._logger.debug(
                    "Assigning state {} to signal".format(existing_state))
                setattr(signal, self.state_name, existing_state)
                to_notify.append(signal)

    def _process_setter_group(self, signals, group, to_notify):
        """ Process the signals for a group.

        Add any signals that should be passed through to the to_notify list
        """
        for signal in signals:
            self._logger.debug("Attempting to set state")
            self._process_state(signal, group)
