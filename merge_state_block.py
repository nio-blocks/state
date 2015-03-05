from .state_base_block import StateBase
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import ExpressionProperty
from nio.metadata.properties import StringProperty


@Discoverable(DiscoverableType.block)
class MergeState(StateBase):

    """
    If *state_sig* evaluates to True then the signal sets the state according
    to *state_expr*. Else, the signal gets assigned the state to the attribute
    *state_name*.

    """

    state_name = StringProperty(default='state', title="State Name")
    state_sig = ExpressionProperty(title="Is State Signal",
                                   default="{{hasattr($, 'state')}}")

    def _process_group(self, signals, group, to_notify):
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
            else:
                existing_state = self.get_state(group)
                self._logger.debug(
                    "Assigning state {} to signal".format(existing_state))
                setattr(signal, self.state_name, existing_state)
                to_notify.append(signal)
