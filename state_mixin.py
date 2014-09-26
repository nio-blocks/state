from nio.common.signal.base import Signal
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.modules.scheduler import Job
from nio.modules.threading import Lock

# Default starting state
class NoState(Exception):
    pass

class StateMixin(object):
    """ A block mixin for keeping track of state
    use _process_state with the signal to determine if a state change is necessary"""
    state_expr = ExpressionProperty(title='State Expression', attr_default=NameError)
    backup_interval = TimeDeltaProperty(title='Backup Interval',
                                        default={'seconds': 600})

    def __init__(self):
        super().__init__()
        self._state = NoState
        self._backup_job = None
        self._state_lock = Lock()

    def configure(self, context):
        super().configure(context)
        self._state = self.persistence.load('state') or self._state

    def start(self):
        super().start()
        self._backup_job = Job(
            self._backup,
            self.backup_interval,
            True
        )

    def stop(self):
        self._backup_job.cancel()
        self._backup()

    def _process_state(self, signal):
        '''changes state from signal. If signal cannot be processed, state
        remains unchanged.

        returns a Signal on successful change. Returns None if state did not change
        '''
        with self._state_lock:
            prev_state = self._state
            state = self.state_expr(signal)
            if state is not NameError:
                self._state = state
            else:
                return
            if prev_state is not NoState and self._state != prev_state:
                # notify signal if there was a prev_state and
                # the state has changed.
                signal = Signal({
                    "state": self._state,
                    "prev_state": prev_state
                })
                return signal

    def _backup(self):
        ''' Persist the current state using the persistence module.

        '''
        self.persistence.store(
            "state",
            self._state
        )
        self.persistence.save()

    def log_error(self, e):
        self._logger.error("State Change failed: {}".format(str(e)))
