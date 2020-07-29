from enum import Enum
# ------------------------------------------------------------------------------


class Comparator(Enum):
    EQUAL       = ('equal',   'equal',       '==',     False, '!=',     'is not equal to'  )  # noqa: E241, E202, E501, E221
    NOT_EQUAL   = ('equal',   'not equal',   '!=',     True,  '==',     'is equal to'      )  # noqa: E241, E202, E501, E221
    SIMILAR     = ('similar', 'similar',     '~',      False, '!~',     'is not similar to')  # noqa: E241, E202, E501, E221
    NOT_SIMILAR = ('similar', 'not similar', '!~',     True,  '~',      'is similar to'    )  # noqa: E241, E202, E501, E221
    IN          = ('in_',     'in',          'in',     False, 'not in', 'is not in'        )  # noqa: E241, E202, E501, E221
    NOT_IN      = ('in_',     'not in',      'not in', True,  'in',     'is in'            )  # noqa: E241, E202, E501, E221

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
            message = self.get_message(
                comparator,
                a,
                b,
                a_val,
                b_val,
                attribute=attribute,
                delta=delta,
                epsilon=epsilon,
            )
        else:
            message = message.format(
                a=a,
                b=b,
                a_val=a_val,
                b_val=b_val,
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

    def get_message(self, comparator, a, b, a_val, b_val, attribute=None, delta=None, epsilon=None):
        message = f'{a} {comparator.message} {b}.'
        if attribute is not None:
            message = f'{attribute.capitalize()} of {a} {comparator.message} {attribute} of {b}.'

        if comparator is Comparator.SIMILAR:
            message += f' Delta {delta} is greater than epsilon {epsilon}.'
        elif comparator is Comparator.NOT_SIMILAR:
            message += f' Delta {delta} is not greater than epsilon {epsilon}.'
        else:
            message += f' {a_val} {comparator.negation_symbol} {b_val}.'

        return message

    def equal(self, a, b):
        return a == b

    def similar(self, difference, epsilon=0.01):
        return difference < epsilon

    def in_(self, a, b):
        return a in b

    def difference(self, a, b):
        return abs(a - b)

    def get_type(self, item):
        return item.__class__.__name__
