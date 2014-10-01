from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.string import StringProperty
from .state_mixin import StateMixin, NoState


@Discoverable(DiscoverableType.block)
class MergeState(StateMixin, Block):
    '''
    If *state_sig* evaluates to True then the signal sets the state according
    to *state_expr*. Else, the signal gets assigned the state to the attribute
    *state_name*. If no signal has been set, then *state_name* is set to None.

    '''

    state_name = StringProperty(default='state', title="State Name")
    state_sig = ExpressionProperty(title="Is State Signal",
                                   default="{{hasattr($, 'state')}}")

    def process_signals(self, signals):
        signal_list = []
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
                if self._state is not NoState:
                    self._logger.debug(
                        "Assigning state to signal: {}".format(self._state)
                    )
                    setattr(signal, self.state_name, self._state)
                    signal_list.append(signal)
                else:
                    setattr(signal, self.state_name, None)
                    signal_list.append(signal)
                    self._logger.debug(
                        "State assigned to None as it has not been set yet"
                    )
        self.notify_signals(signal_list)
