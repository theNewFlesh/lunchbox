from enum import Enum
# ------------------------------------------------------------------------------


class Comparator(Enum):
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
        self.function = function
        self.text = text
        self.symbol = symbol
        self.negation = negation
        self.negation_symbol = negation_symbol
        self.message = message

    @property
    def canonical(self):
        return self.name.lower()

    @staticmethod
    def from_string(string):
        lut = {}
        for val in Comparator.__members__.values():
            lut[val.text] = val
            lut[val.symbol] = val
        return lut[string.lower()]


class EnforceError(Exception):
    pass
# ------------------------------------------------------------------------------


class Enforce:
    '''
    msg = 'foobar'
    Enforce(foo, 'not in', ['Bar', 'Baz'], 'type_name', msg)
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
        # resolve everything
        comparator = Comparator.from_string(comparator)
        func = getattr(self, comparator.function)
        a_val = a
        b_val = b
        if attribute is not None:
            getter = getattr(self, 'get_' + attribute)
            a_val = getter(a)
            b_val = getter(b)

        # get delta
        flag = comparator.function == 'similar'
        delta = None
        if flag:
            delta = self.difference(a_val, b_val)

        # create error message
        if message is None:
            message = self._get_message(attribute, comparator)
        message = message.format(
            comparator=comparator,
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
        if comparator.negation:
            result = not result
        if result is False:
            raise EnforceError(message)

    def _get_message(self, attribute, comparator):
        message = '{a} is {comparator.message} {b}.'
        if attribute is not None:
            message = '{attribute} of {a} is {comparator.message} {attribute} of {b}.'

        if comparator is Comparator.SIMILAR:
            message += ' Delta {delta} is greater than epsilon {epsilon}.'
        elif comparator is Comparator.NOT_SIMILAR:
            message += ' Delta {delta} is not greater than epsilon {epsilon}.'
        else:
            message += ' {a_val} {comparator.negation_symbol} {b_val}.'

        return message

    # COMPARATORS---------------------------------------------------------------
    def eq(self, a, b):
        return a == b

    def gt(self, a, b):
        return a > b

    def gte(self, a, b):
        return a >= b

    def lt(self, a, b):
        return a < b

    def lte(self, a, b):
        return a <= b

    def similar(self, difference, epsilon=0.01):
        return difference < epsilon

    def in_(self, a, b):
        return a in b

    def instance_of(self, a, b):
        return isinstance(a, b)

    def difference(self, a, b):
        return abs(a - b)

    # ATTRIBUTE-GETTERS---------------------------------------------------------
    def get_type_name(self, item):
        return item.__class__.__name__
