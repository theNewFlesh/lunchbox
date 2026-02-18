from typing import Any  # noqa F401

from enum import Enum, EnumMeta
# ------------------------------------------------------------------------------


class EnumBaseMeta(EnumMeta):
    def __repr__(self):
        '''
        str: String representation.
        '''
        return self.__name__


class EnumBase(Enum, metaclass=EnumBaseMeta):
    '''
    Base class for enums.
    '''
    @classmethod
    def from_string(cls, string):
        # type: (str) -> Any
        '''
        Returns enum from a given string.

        Args:
            string (str): String.

        Raises:
            ValueError: If illegal string is given.

        Returns:
            enum: Enum.
        '''
        try:
            return getattr(cls, string.upper())
        except AttributeError:
            c = cls.__name__
            options = ', '.join(cls.options())
            msg = f'{string} is not a legal {c} string. '
            msg += f'Legal options: {options}.'
            raise ValueError(msg)

    @classmethod
    def to_dict(cls):
        # type: () -> dict
        '''
        Convert enum to a dictionary.

        Returns:
            dict: (name, value) dictionary.
        '''
        return {x.name: x.value for x in cls.__members__.values()}

    @classmethod
    def members(cls):
        # type: () -> list[Any]
        '''
        Returns list of enum members.

        Returns:
            list[Any]: List of enum members.
        '''
        return list(cls.__members__.values())

    @classmethod
    def options(cls):
        # type: () -> list[Any]
        '''
        Returns list of enum options.

        Returns:
            list[Any]: List of enum options.
        '''
        vals = list(cls.__members__.values())
        if isinstance(vals[0].value, list | tuple):
            return [x.value[0] for x in vals]
        return [x.value for x in vals]

    def __repr__(self):
        # type: () -> str
        '''
        str: String representation.
        '''
        return self.__str__()
