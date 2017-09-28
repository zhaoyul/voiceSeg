"""
This file is responsible for the input(wav, stdin etc.)
"""

from cutvoice.util import DataValidator

__all__ = ["StreamTokenizer"]

class StreamTokenizer():
    SILENCE = 0
    POSSIBLE_SILENCE = 1
    POSSIBLE_NOISE = 2
    NOISE = 3

    STRICT_MIN_LENGTH = 2
    DROP_TRAILING_SILENCE = 4
    DROP_TAILING_SILENCE = 4

    def __init__(self, validator,
                 min_length, max_length, max_continuous_silence,
                 init_min=0, init_max_silence=0,
                 mode=0):

        if not isinstance(validator, DataValidator):
            raise TypeError("wrong type")

        if max_length <= 0:
            raise ValueError("'max_length' should be > 0 (value={0})".format(max_length))

        if min_length <= 0 or min_length > max_length:
            raise ValueError("'min_length' should be > 0 and <= 'max_length' (value={0})".format(min_length))

        if max_continuous_silence >= max_length:
            raise ValueError("'max_continuous_silence' should be < 'max_length' (value={0})".format(max_continuous_silence))

        if init_min >= max_length:
            raise ValueError("'init_min' must be < 'max_length' (value={0})".format(max_continuous_silence))

        self.validator = validator
        self.min_length = min_length
        self.max_length = max_length
        self.max_continuous_silence = max_continuous_silence
        self.init_min = init_min
        self.init_max_silent = init_max_silence

        self._mode = None
        self.set_mode(mode)
        self._strict_min_length = (mode & self.STRICT_MIN_LENGTH) != 0
        self._drop_tailing_silence = (mode & self.DROP_TRAILING_SILENCE) != 0

        self._deliver = None
        self._tokens = None
        self._state = None
        self._data = None
        self._contiguous_token = False

        self._init_count = 0
        self._silence_length = 0
        self._start_frame = 0
        self._current_frame = 0

    def set_mode(self, mode):

        if not mode in [self.STRICT_MIN_LENGTH, self.DROP_TRAILING_SILENCE,
                        self.STRICT_MIN_LENGTH | self.DROP_TRAILING_SILENCE, 0]:

            raise ValueError("Wrong mode")

        self._mode = mode
        self._strict_min_length = (mode & self.STRICT_MIN_LENGTH) != 0
        self._drop_tailing_silence = (mode & self.DROP_TRAILING_SILENCE) != 0

    def get_mode(self):
        return self._mode

    def _reinitialize(self):
        self._contiguous_token = False
        self._data = []
        self._tokens = []
        self._state = self.SILENCE
        self._current_frame = -1
        self._deliver = self._append_token

    def tokenize(self, data_source, callback=None):

        self._reinitialize()

        if callback is not None:
            self._deliver = callback

        while True:
            frame = data_source.read()
            if frame is None:
                break
            self._current_frame += 1
            self._process(frame)

        self._post_process()

        if callback is None:
            _ret = self._tokens
            self._tokens = None
            return _ret

    def _process(self, frame):

        frame_is_valid = self.validator.is_valid(frame)

        if self._state == self.SILENCE:

            if frame_is_valid:
                self._init_count = 1
                self._silence_length = 0
                self._start_frame = self._current_frame
                self._data.append(frame)

                if self._init_count >= self.init_min:
                    self._state = self.NOISE
                    if len(self._data) >= self.max_length:
                        self._process_end_of_detection(True)
                else:
                    self._state = self.POSSIBLE_NOISE

        elif self._state == self.POSSIBLE_NOISE:

            if frame_is_valid:
                self._silence_length = 0
                self._init_count += 1
                self._data.append(frame)
                if self._init_count >= self.init_min:
                    self._state = self.NOISE
                    if len(self._data) >= self.max_length:
                        self._process_end_of_detection(True)

            else:
                self._silence_length += 1
                if self._silence_length > self.init_max_silent or \
                        len(self._data) + 1 >= self.max_length:
                    self._data = []
                    self._state = self.SILENCE
                else:
                    self._data.append(frame)

        elif self._state == self.NOISE:

            if frame_is_valid:
                self._data.append(frame)
                if len(self._data) >= self.max_length:
                    self._process_end_of_detection(True)

            elif self.max_continuous_silence <= 0:
                self._process_end_of_detection()
                self._state = self.SILENCE

            else:
                self._silence_length = 1
                self._data.append(frame)
                self._state = self.POSSIBLE_SILENCE
                if len(self._data) == self.max_length:
                    self._process_end_of_detection(True)

        elif self._state == self.POSSIBLE_SILENCE:

            if frame_is_valid:
                self._data.append(frame)
                self._silence_length = 0
                self._state = self.NOISE
                if len(self._data) >= self.max_length:
                    self._process_end_of_detection(True)

            else:
                if self._silence_length >= self.max_continuous_silence:
                    if self._silence_length < len(self._data):
                        self._process_end_of_detection()
                    else:
                        self._data = []
                    self._state = self.SILENCE
                    self._silence_length = 0
                else:
                    self._data.append(frame)
                    self._silence_length += 1
                    if len(self._data) >= self.max_length:
                        self._process_end_of_detection(True)

    def _post_process(self):
        if self._state == self.NOISE or self._state == self.POSSIBLE_SILENCE:
            if len(self._data) > 0 and len(self._data) > self._silence_length:
                self._process_end_of_detection()

    def _process_end_of_detection(self, truncated=False):

        if not truncated and self._drop_tailing_silence and self._silence_length > 0:
            self._data = self._data[0: - self._silence_length]

        if (len(self._data) >= self.min_length) or \
           (len(self._data) > 0 and
                not self._strict_min_length and self._contiguous_token):

            _end_frame = self._start_frame + len(self._data) - 1
            self._deliver(self._data, self._start_frame, _end_frame)

            if truncated:
                self._start_frame = self._current_frame + 1
                self._contiguous_token = True
            else:
                self._contiguous_token = False
        else:
            self._contiguous_token = False

        self._data = []

    def _append_token(self, data, start, end):
        self._tokens.append((data, start, end))
