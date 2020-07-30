from typing import Any, List, Optional, Set, Tuple, Union

from enum import Enum
# ------------------------------------------------------------------------------


'''
The enforce module contains the Enforce class which is used for faciltating
inline testing, inside of function defitions and test definitions.
'''


class Comparator(Enum):
    '''
    Enum for comparison operators used by Enforce.

    Includes:

        * EQ
        * NOT_EQ
        * GT
        * GTE
        * LT
        * LTE
        * SIMILAR
        * NOT_SIMILAR
        * IN
        * NOT_IN
        * INSTANCE_OF
        * NOT_INSTANCE_OF
    '''
    EQ              = ('eq',          'equal',            '==',             False, '!=',             'not equal to'    )  # noqa: E241, E202, E501, E221
    NOT_EQ          = ('eq',          'not equal',        '!=',             True,  '==',             'equal to'        )  # noqa: E241, E202, E501, E221
    GT              = ('gt',          'greater',          '>',              False, '<=',             'not greater than')  # noqa: E241, E202, E501, E221
    GTE             = ('gte',         'greater or equal', '>=',             False, '<',              'less than'       )  # noqa: E241, E202, E501, E221
    LT              = ('lt',          'lesser',           '<',              False, '>=',             'not less than'   )  # noqa: E241, E202, E501, E221
    LTE             = ('lte',         'lesser or equal',  '<=',             False, '>',              'greater than'    )  # noqa: E241, E202, E501, E221
    SIMILAR         = ('similar',     'similar',          '~',              False, '!~',             'not similar to'  )  # noqa: E241, E202, E501, E221
    NOT_SIMILAR     = ('similar',     'not similar',      '!~',             True,  '~',              'similar to'      )  # noqa: E241, E202, E501, E221
    IN              = ('in_',         'in',               'in',             False, 'not in',         'not in'          )  # noqa: E241, E202, E501, E221
    NOT_IN          = ('in_',         'not in',           'not in',         True,  'in',             'in'              )  # noqa: E241, E202, E501, E221
    INSTANCE_OF     = ('instance_of', 'instance of',      'isinstance',     False, 'not isinstance', 'not instance of' )  # noqa: E241, E202, E501, E221
    NOT_INSTANCE_OF = ('instance_of', 'not instance of',  'not isinstance', True,  'isinstance',     'instance of'     )  # noqa: E241, E202, E501, E221

    def __init__(
        self, function, text, symbol, negation, negation_symbol, message
    ):
        # type: (str, str, str, bool, str, str) -> None
        '''
        Constructs Comparator instance.

        Args:
            function (str): Enforce function name.
            text (str): Comparator as text.
            symbol (str): Comparator as symbol.
            negation (bool): Function is a negation.
            negation_symbol (str): Negated comparator as symbol.
            message  (str): Error message fragment.
        '''
        self.function = function
        self.text = text
        self.symbol = symbol
        self.negation = negation
        self.negation_symbol = negation_symbol
        self.message = message

    @property
    def canonical(self):
        # type: () -> str
        '''
        str: Canonical name of Comparator
        '''
        return self.name.lower()

    @staticmethod
    def from_string(string):
        # type: (str) -> Comparator
        '''
        Constructs Comparator from given string.

        Args:
            string (str): Comparator name.

        Returns:
            Comparator: Comparator.
        '''
        lut = {}
        for val in Comparator.__members__.values():
            lut[val.text] = val
            lut[val.symbol] = val
        return lut[string.lower()]


class EnforceError(Exception):
    '''
    Enforce error class.
    '''
    pass
# ------------------------------------------------------------------------------


class Enforce:
    '''
    Faciltates inline testing. Super class for Enforcer subclasses.

    Example:

        >>> class Foo:
                def __init__(self, value):
                    self.value = value
                def __repr__(self):
                    return '<Foo>'
        >>> class Bar:
                def __init__(self, value):
                    self.value = value
                def __repr__(self):
                    return '<Bar>'

        >>> Enforce(Foo(1), '==', Foo(2), 'type_name')
        >>> Enforce(Foo(1), '==', Bar(2), 'type_name')
        EnforceError: type_name of <Foo> is not equal to type_name of <Bar>. \
Foo != Bar.

        >>> class EnforceFooBar(Enforce):
            def get_value(self, item):
                return item.value
        >>> EnforceFooBar(Foo(1), '==', Bar(1), 'value')
        >>> EnforceFooBar(Foo(1), '==', Bar(2), 'value')
        EnforceError: value of <Foo> is not equal to value of <Bar>. 1 != 2.
        >>> EnforceFooBar(Foo(1), '~', Bar(5), 'value', epsilon=2)
        EnforceError: value of <Foo> is not similar to value of <Bar>. Delta 4 \
is greater than epsilon 2.

        >>> msg = '{a} is not like {b}. Please adjust your epsilon,: {epsilon}, '
        >>> msg += 'to be higher than {delta}. '
        >>> msg += 'A value: {a_val}. B value: {b_val}.'
        >>> EnforceFooBar(Foo(1), '~', Bar(5), 'value', epsilon=2, message=msg)
        <Foo> is not like <Bar>. Please adjust your epsilon: 2, to be higher \
than 4. A value: 1. B value: 5.
    '''
    def __init__(
        self,
        a,
        comparator,
        b,
        attribute=None,
        message=None,
        epsilon=0.01
    ):
        # type: (Any, str, Any, Optional[str], Optional[str], float) -> None
        '''
        Validates predicate specified in constructor.

        Args:
            a (object): First object to be tested.
            comparator (str): String representation of Comparator.
            b (object): Second object.
            attribute (str, optional): Attribute name of a and b. Default: None.
            message (str, optional): Custom error message. Default: None.
            epsilon (float, optional): Error threshold for a/b difference.
                Default: 0.01.

        Raises:
            EnforceError: If predicate fails.

        Returns:
            Enforce: Enforce instance.
        '''
        # resolve everything
        comp = Comparator.from_string(comparator)  # type: Comparator
        func = getattr(self, comp.function)
        a_val = a
        b_val = b
        if attribute is not None:
            getter = getattr(self, 'get_' + attribute)
            a_val = getter(a)
            if comp in [comp.IN, comp.NOT_IN]:
                b_val = [getter(x) for x in b]
            else:
                b_val = getter(b)

        # get delta
        flag = comp.function == 'similar'
        delta = None
        if flag:
            delta = self.difference(a_val, b_val)

        # create error message
        if message is None:
            message = self._get_message(attribute, comp)
        message = message.format(
            comparator=comp,
            a=a,
            b=b,
            a_val=a_val,
            b_val=b_val,
            attribute=attribute,
            delta=delta,
            epsilon=epsilon,
        )

        if flag:
            a_val = delta
            b_val = epsilon

        # test a and b with func
        result = func(a_val, b_val)
        if comp.negation:
            result = not result
        if result is False:
            raise EnforceError(message)

    def _get_message(self, attribute, comparator):
        # type: (Optional[str], Comparator) -> str
        '''
        Creates an unformatted error message given an attribute name and
        comparator.

        Args:
            attribute (str or None): Attribute name.
            comparator (Comparator): Comparator instance.

        Returns:
            str: Error message.
        '''
        message = '{a} is {comparator.message} {b}.'
        if attribute is not None:
            message = '{attribute} of {a} is {comparator.message} {attribute} of {b}.'

        skip = [
            Comparator.IN,
            Comparator.NOT_IN,
            Comparator.INSTANCE_OF,
            Comparator.NOT_INSTANCE_OF,
        ]
        if comparator in skip:
            pass
        elif comparator is Comparator.SIMILAR:
            message += ' Delta {delta} is greater than epsilon {epsilon}.'
        elif comparator is Comparator.NOT_SIMILAR:
            message += ' Delta {delta} is not greater than epsilon {epsilon}.'
        else:
            message += ' {a_val} {comparator.negation_symbol} {b_val}.'

        return message

    # COMPARATORS---------------------------------------------------------------
    def eq(self, a, b):
        # type: (Any, Any) -> bool
        '''
        Determines if a and b are equal.

        Args:
            a (object): First object.
            b (object): Second object.

        Returns:
            bool: True if a equals b.
        '''
        return a == b

    def gt(self, a, b):
        # type: (Any, Any) -> bool
        '''
        Determines if a is greater than b.

        Args:
            a (object): First object.
            b (object): Second object.

        Returns:
            bool: True if a is greater than b.
        '''
        return a > b

    def gte(self, a, b):
        # type: (Any, Any) -> bool
        '''
        Determines if a is greater than or equal to b.

        Args:
            a (object): First object.
            b (object): Second object.

        Returns:
            bool: True if a is greater than or equal to b.
        '''
        return a >= b

    def lt(self, a, b):
        # type: (Any, Any) -> bool
        '''
        Determines if a is lesser than b.

        Args:
            a (object): First object.
            b (object): Second object.

        Returns:
            bool: True if a is lesser than b.
        '''
        return a < b

    def lte(self, a, b):
        # type: (Any, Any) -> bool
        '''
        Determines if a is lesser than or equal to b.

        Args:
            a (object): First object.
            b (object): Second object.

        Returns:
            bool: True if a is lesser than or equal to b.
        '''
        return a <= b

    def similar(self, difference, epsilon=0.01):
        # type: (Union[int, float], float) -> bool
        '''
        Determines if a/b difference given error threshold episilon.

        Args:
            difference (int or float): Difference between a and b.
            epsilon (float, optional): Error threshold. Default: 0.01.

        Returns:
            bool: True if difference is less than epsilon.
        '''
        return difference < epsilon

    def in_(self, a, b):
        # type: (Any, Union[List, Set, Tuple]) -> bool
        '''
        Determines if a is in b.

        Args:
            a (object): Member object.
            b (list or set or tuple): Container object.

        Returns:
            bool: True if a is in b.
        '''
        return a in b

    def instance_of(self, a, b):
        # type: (Any, Any) -> bool
        '''
        Determines if a is instance of b.

        Args:
            a (type or list[type]): Instance object.
            b (object): Class object.

        Returns:
            bool: True if a is instance of b.
        '''
        if not isinstance(b, (tuple, list)):
            b = [b]
        if isinstance(b, list):
            b = tuple(b)
        return isinstance(a, b)

    def difference(self, a, b):
        # type: (Any, Any) -> float
        '''
        Calculates difference between a and b.

        Args:
            a (object): First object.
            b (object): Second object.

        Returns:
            float: Difference between a and b.
        '''
        return abs(a - b)

    # ATTRIBUTE-GETTERS---------------------------------------------------------
    def get_type_name(self, item):
        # type: (Any) -> str
        '''
        Gets __class__.__name__ of given item.

        Args:
            item (object): Item.

        Returns:
            str: item.__class__.__name__
        '''
        return item.__class__.__name__
