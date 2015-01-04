# -*- coding: utf-8 -*-


class ValidationError(ValueError):

    _UNDEFINED = object()

    def __init__(self, msg, value=_UNDEFINED):
        self.msg = msg
        self.value = value

        super(ValidationError, self).__init__(str(self))

    def __str__(self):
        return self.to_s()

    def to_s(self):
        if self.value != self._UNDEFINED:
            return 'Invalid value %s (%s): %s'\
                   % (repr(self.value),
                      self.value.__class__.__name__,
                      self.msg)

        return self.msg


class Validator(object):

    def validate(self, value):
        """Check if ``value`` is valid.

        Adaptors should return the adapted value in this method.

        @param value: The value to validate and to adapt

        @raise ValidationError: If ``value`` is invalid.
        """
        raise NotImplementedError

    def is_valid(self, value):
        """Check if the value is valid.

        @return: ``True`` if the value is valid, ``False`` if invalid.
        """
        try:
            self.validate(value)

            return True
        except (ValidationError, ValueError):
            return False

    def error(self, value):
        """Helper method that can be called when ``value`` is deemed invalid.
        Can be overriden to provide customized :py:exc:`ValidationError` subclasses.
        """
        raise ValidationError("must be %s" % self.humanized_name, value)

    @property
    def humanized_name(self):
        """Return a human-friendly string name for this validator."""
        return getattr(self, 'name', self.__class__.__name__)


# Default validators
class Callable(Validator):
    """A validator that accepts a callable.

    Attributes:
        - callable: The callable
    """
    def __init__(self, callable_):
        """
        @param callable_: The callable
        @type callable_: callable
        """
        if not callable(callable_):
            raise TypeError('"callable" argument is not callable')

        self.callable = callable_

    def validate(self, value):
        try:
            return self.callable(value)
        except (TypeError, ValueError) as e:
            raise ValidationError(str(e))


class Enum(Validator):
    """A validator that accepts only a finite set of values.

    Attributes:
        - values: The collection of valid values.
    """

    values = ()

    def __init__(self, values=None):
        super(Enum, self).__init__()

        if values is None:
            values = self.values

        try:
            self.values = set(values)
        except TypeError:
            self.values = list(values)

    def validate(self, value):
        try:
            if value in self.values:
                return value
        except TypeError:
            pass

        self.error(value)

    @property
    def humanized_name(self):
        return "one of {%s}" % ", ".join(map(repr, self.values))


Choice = Enum


class Boolean(Validator):
    """A validator that accepts booleans

    Accepted values are 1, true, yes, y, on
    and their negatives or native boolean types (True, False).
    """

    name = 'boolean'

    def validate(self, value):
        if isinstance(value, str):
            value_ = value.lower()

            if value_ in ['1', 'true', 'yes', 'y', 'on']:
                return True
            if value_ in ['0', 'false', 'no', 'n', 'off']:
                return False

            self.error(value)
        elif not isinstance(value, bool):
            self.error(value)

        return value


class Integer(Validator):
    """A validator that accepts integers
    """

    name = 'integer'

    def validate(self, value):
        try:
            return int(value)
        except ValueError:
            self.error(value)


class Float(Validator):
    """A validator that accepts floats
    """

    name = 'float'

    def validate(self, value):
        try:
            return float(value)
        except ValueError:
            self.error(value)


class Range(Validator):
    """A validator that restricts a value to be in a specified range.

    The range can be of anything that can be compared to the specified value,
    like integers, floats or string.
    """

    name = 'range'

    def __init__(self, min=None, max=None,
                 include_min=True, include_max=True,
                 validator=Integer()):
        self.min = min
        self.max = max
        self.include_min = include_min
        self.include_max = include_max
        self.validator = validator

    def validate(self, value):
        if self.validator:
            value = self.validator.validate(value)

        if self.min is not None:
            if value < self.min \
                or (value == self.min
                    and self.include_min is False):
                self.error(value)

        if self.max is not None:
            if value > self.max \
                or (value == self.max
                    and self.include_max is False):
                self.error(value)

        return value

    @property
    def humanized_name(self):
        left_boundary = '[' if self.include_min else ']'
        right_boundary = ']' if self.include_max else '['

        return "in range %s%s, %s%s"\
               % (left_boundary,
                  repr(self.min), repr(self.max),
                  right_boundary)
