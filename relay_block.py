from .state_base_block import StateBase
from nio.block.terminals import input, Output
from nio.common.versioning.dependency import DependsOn
from nio.util.discovery import discoverable
from nio.properties import Property, VersionProperty


@input('setter')
@input('getter')
@output('false')
@output('true')
@DependsOn("nio", "1.5.2")
@discoverable
class Relay(StateBase):

    """ Passthrough *getter* signals if the state is True.

    *getter* signals pass through to the *true* output if the last *setter*
    signal set the state to True. Else, the signals to *getter* pass through
    to the *false* output.
    """
    version = VersionProperty(default='4.0.0')

    def _process_group(self, signals, group, to_notify):
        """ Process the signals from the default/getter input for a group.

        Add any signals that should be passed through to the to_notify list
        """
        for signal in signals:
            if self.get_state(group):
                self.logger.debug("State is True")
                to_notify['true'].append(signal)
            else:
                self.logger.debug("State is False")
                to_notify['false'].append(signal)

    def _process_setter_group(self, signals, group, to_notify):
        """ Process the signals from the setter input for a group.

        Add any signals that should be passed through to the to_notify list
        """
        for signal in signals:
            self.logger.debug("Attempting to set state")
            self._process_state(signal, group)
