"""Field declarations."""

import abc
import copy


class BaseField(object, metaclass=abc.ABCMeta):
    """
    Base class for all fields.

    Subclasses should override `transform_to_storage` and
    `transform_from_storage`. They may optionally also override `validate`,
    but should call `super().validate` if doing so.
    """

    def __init__(self, null=False, default=None):
        """
        Construct the field.

        If `null=True`, None is not permitted in this field. The naming is for
        consistency with the equivalent concept in relational algebra and ORMs.

        `default` does what it says on the tin.
        """
        self.null = null
        self.default = default

    @abc.abstractmethod
    def transform_to_storage(self, value):
        raise NotImplementedError()

    @abc.abstractmethod
    def transform_from_storage(self, value):
        raise NotImplementedError()

    def validate(self, raw_value):
        if not self.null and raw_value is None:
            raise ValueError("%s is not nullable" % self.name)

    def __get__(self, obj, owner):
        if obj is None:
            return self

        try:
            raw_value = obj._fields[self.name]
        except KeyError:
            return self.default

        return self.transform_from_storage(raw_value)

    def __set__(self, obj, value):
        if value is None:
            obj._fields[self.name] = None
        else:
            obj._fields[self.name] = self.transform_to_storage(value)

        if obj.session:
            obj.session.mark_instance_dirty(obj)

    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name


class TextField(BaseField):
    def transform_to_storage(self, value):
        return str(value)

    def transform_from_storage(self, value):
        return value


class JSONField(BaseField):
    def transform_to_storage(self, value):
        return copy.deepcopy(value)

    def transform_from_storage(self, value):
        return copy.deepcopy(value)
