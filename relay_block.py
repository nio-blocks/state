from .state_base_block import StateBase
from nio.common.block.attribute import Input, Output
from nio.common.versioning.dependency import DependsOn
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import ExpressionProperty, VersionProperty


@Input('setter')
@Input('getter')
@Output('false')
@Output('true')
@DependsOn("nio", "1.5.2")
@Discoverable(DiscoverableType.block)
class Relay(StateBase):

    """ Passthrough *getter* signals if the state is True.

    *getter* signals are pass through the block if the last *setter* signal set
    the state to True. Else, the signals to *getter* are filtered out.
    """
    version = VersionProperty(default='4.0.0')

    def _process_group(self, signals, group, to_notify):
        """ Process the signals from the default/getter input for a group.

        Add any signals that should be passed through to the to_notify list
        """
        for signal in signals:
            if self.get_state(group):
                self._logger.debug("State is True")
                to_notify['true'].append(signal)
            else:
                self._logger.debug("State is False")
                to_notify['false'].append(signal)

    def _process_setter_group(self, signals, group, to_notify):
        """ Process the signals from the setter input for a group.

        Add any signals that should be passed through to the to_notify list
        """
        for signal in signals:
            self._logger.debug("Attempting to set state")
            self._process_state(signal, group)
