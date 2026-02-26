from typing import Any, Callable  # noqa F401
# ------------------------------------------------------------------------------


class InfixBase:
    '''
    InfixBase is used for declaring a mapping between infix operators and class
    methods, using _infix_lookup.
    '''
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Construct Infix instance.
        '''
        self._infix_lookup = {}  # type: dict[str, str]

    def _get_infix_function(self, symbol):
        # type: (str) -> Callable
        '''
        Get infix function from lookup table.

        Args:
            symbol (str): Lookup table symbol.

        Returns:
            callable: Infix function.
        '''
        name = self._infix_lookup.get(symbol, '')
        try:
            return getattr(self, name)
        except AttributeError:
            msg = f"Method not implemented for '{symbol}'."
            if name != '':
                msg = f"Method {name} not implemented for '{symbol}'."
            raise NotImplementedError(msg)


class ArithmeticInfix(InfixBase):
    '''
    Infix class for infix operators: +, -, *, /
    '''
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Construct ArithmeticInfix instance.
        '''
        super().__init__()
        self._infix_lookup.update({
            '+': '',   # add
            'r+': '',  # add
            '-': '',   # subtract
            'r-': '',  # subtract
            '*': '',   # multiply
            'r*': '',  # multiply
            '/': '',   # divide
            'r/': '',  # divide
        })

    def __add__(self, value):
        # type: (Any) -> Any
        '''
        Add (+).

        Args:
            value (object): Value.

        Returns:
            object: Self ADD value.
        '''
        return self._get_infix_function('+')(value)

    def __radd__(self, value):
        # type: (Any) -> Any
        '''
        Add (+).

        Args:
            value (object): Value.

        Returns:
            object: Value ADD self.
        '''
        return self._get_infix_function('r+')(value)

    def __sub__(self, value):
        # type: (Any) -> Any
        '''
        Subtract (-).

        Args:
            value (object): Value.

        Returns:
            object: Self SUBTRACT value.
        '''
        return self._get_infix_function('-')(value)

    def __rsub__(self, value):
        # type: (Any) -> Any
        '''
        Subtract (-).

        Args:
            value (object): Value.

        Returns:
            object: Value SUBTRACT self.
        '''
        return self._get_infix_function('r-')(value)

    def __mul__(self, value):
        # type: (Any) -> Any
        '''
        Multiply (*).

        Args:
            value (object): Value.

        Returns:
            object: Self MULTIPLY value.
        '''
        return self._get_infix_function('*')(value)

    def __rmul__(self, value):
        # type: (Any) -> Any
        '''
        Multiply (*).

        Args:
            value (object): Value.

        Returns:
            object: Value MULTIPLY self.
        '''
        return self._get_infix_function('r*')(value)

    def __truediv__(self, value):
        # type: (Any) -> Any
        '''
        Divide (/).

        Args:
            value (object): Value.

        Returns:
            object: Self DIVIDE value.
        '''
        return self._get_infix_function('/')(value)

    def __rtruediv__(self, value):
        # type: (Any) -> Any
        '''
        Divide (/).

        Args:
            value (object): Value.

        Returns:
            object: Value DIVIDE self.
        '''
        return self._get_infix_function('r/')(value)


class MathInfix(InfixBase):
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Infix class for infix operators: %, //, **, @
        '''
        super().__init__()
        self._infix_lookup.update({
            '%': '',    # modulo
            'r%': '',   # modulo
            '//': '',   # floor divide
            'r//': '',  # floor divide
            '**': '',   # exponentiate
            'r**': '',  # exponentiate
            '@': '',    # matrix multiply
            'r@': '',   # matrix multiply
        })

    def __mod__(self, value):
        # type: (Any) -> Any
        '''
        Modulo (%).

        Args:
            value (object): Value.

        Returns:
            object: Self MODULO value.
        '''
        return self._get_infix_function('%')(value)

    def __rmod__(self, value):
        # type: (Any) -> Any
        '''
        Modulo (%).

        Args:
            value (object): Value.

        Returns:
            object: Value MODULO self.
        '''
        return self._get_infix_function('r%')(value)

    def __floordiv__(self, value):
        # type: (Any) -> Any
        '''
        Floor divide (//).

        Args:
            value (object): Value.

        Returns:
            object: Self FLOOR DIVIDE value.
        '''
        return self._get_infix_function('//')(value)

    def __rfloordiv__(self, value):
        # type: (Any) -> Any
        '''
        Floor divide (//).

        Args:
            value (object): Value.

        Returns:
            object: Value FLOOR DIVIDE self.
        '''
        return self._get_infix_function('r//')(value)

    def __pow__(self, value):
        # type: (Any) -> Any
        '''
        Exponentiate (**).

        Args:
            value (object): Value.

        Returns:
            object: Self EXPONENTIATE value.
        '''
        return self._get_infix_function('**')(value)

    def __rpow__(self, value):
        # type: (Any) -> Any
        '''
        Exponentiate (**).

        Args:
            value (object): Value.

        Returns:
            object: Value EXPONENTIATE self.
        '''
        return self._get_infix_function('r**')(value)

    def __matmul__(self, value):
        # type: (Any) -> Any
        '''
        Matrix multiply (@).

        Args:
            value (object): Value.

        Returns:
            object: Self MATRIX MULTIPLY value.
        '''
        return self._get_infix_function('@')(value)

    def __rmatmul__(self, value):
        # type: (Any) -> Any
        '''
        Matrix multiply (@).

        Args:
            value (object): Value.

        Returns:
            object: Value MATRIX MULTIPLY self.
        '''
        return self._get_infix_function('r@')(value)


class LogicInfix(InfixBase):
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Infix class for infix operators: &, |, ^
        '''
        super().__init__()
        self._infix_lookup.update({
            '&': '',   # and
            'r&': '',  # and
            '|': '',   # or
            'r|': '',  # or
            '^': '',   # exclusive or
            'r^': '',  # exclusive or
        })

    def __and__(self, value):
        # type: (Any) -> Any
        '''
        And (&).

        Args:
            value (object): Value.

        Returns:
            object: Self AND value.
        '''
        return self._get_infix_function('&')(value)

    def __rand__(self, value):
        # type: (Any) -> Any
        '''
        And (&).

        Args:
            value (object): Value.

        Returns:
            object: Value AND self.
        '''
        return self._get_infix_function('r&')(value)

    def __or__(self, value):
        # type: (Any) -> Any
        '''
        Or (|).

        Args:
            value (object): Value.

        Returns:
            object: Self OR value.
        '''
        return self._get_infix_function('|')(value)

    def __ror__(self, value):
        # type: (Any) -> Any
        '''
        Or (|).

        Args:
            value (object): Value.

        Returns:
            object: Value OR self.
        '''
        return self._get_infix_function('r|')(value)

    def __xor__(self, value):
        # type: (Any) -> Any
        '''
        Exclusive or (^).

        Args:
            value (object): Value.

        Returns:
            object: Self EXCLUSIVE value.
        '''
        return self._get_infix_function('^')(value)

    def __rxor__(self, value):
        # type: (Any) -> Any
        '''
        Exclusive or (^).

        Args:
            value (object): Value.

        Returns:
            object: Value EXCLUSIVE self.
        '''
        return self._get_infix_function('r^')(value)


class ComparisonInfix(InfixBase):
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Infix class for infix operators: <, <=, >, >=
        '''
        super().__init__()
        self._infix_lookup.update({
            '<': '',   # less than
            '<=': '',  # less than or equal
            '>': '',   # greater than
            '>=': '',  # greater than or equal
        })

    def __lt__(self, value):
        # type: (Any) -> Any
        '''
        Less than (<).

        Args:
            value (object): Value.

        Returns:
            object: Self LESS THAN value.
        '''
        return self._get_infix_function('<')(value)

    def __le__(self, value):
        # type: (Any) -> Any
        '''
        Less than or equal (.

        Args:
            value (object): Value.

        Returns:
            object: Self LESS THAN OR EQUAL TO value.
        '''
        return self._get_infix_function('<=')(value)

    def __gt__(self, value):
        # type: (Any) -> Any
        '''
        Greater than (>).

        Args:
            value (object): Value.

        Returns:
            object: Self GREATER THAN value.
        '''
        return self._get_infix_function('>')(value)

    def __ge__(self, value):
        # type: (Any) -> Any
        '''
        Greater than or equa.

        Args:
            value (object): Value.

        Returns:
            object: Self GREATER THAN OR EQUAL TO value.
        '''
        return self._get_infix_function('>=')(value)


class BitwiseInfix(InfixBase):
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Infix class for infix operators: <<, >>
        '''
        super().__init__()
        self._infix_lookup.update({
            '>>': '',   # right bit shift
            'r>>': '',  # right bit shift
            '<<': '',   # left bit shift
            'r<<': '',  # left bit shift
        })

    def __rshift__(self, value):
        # type: (Any) -> Any
        '''
        Right bit shift (>>).

        Args:
            value (object): Value.

        Returns:
            object: Value RIGHT BIT SHIFT self.
        '''
        return self._get_infix_function('>>')(value)

    def __rrshift__(self, value):
        # type: (Any) -> Any
        '''
        Right bit shift (>>).

        Args:
            value (object): Value.

        Returns:
            object: Value RIGHT BIT SHIFT self.
        '''
        return self._get_infix_function('r>>')(value)

    def __lshift__(self, value):
        # type: (Any) -> Any
        '''
        Left bit shift (<<).

        Args:
            value (object): Value.

        Returns:
            object: Self LEFT BIT SHIFT value.
        '''
        return self._get_infix_function('<<')(value)

    def __rlshift__(self, value):
        # type: (Any) -> Any
        '''
        Left bit shift (<<).

        Args:
            value (object): Value.

        Returns:
            object: Value LEFT BIT SHIFT self.
        '''
        return self._get_infix_function('r<<')(value)


class ItemInfix(InfixBase):
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Infix class for infix operators: [], [] =, del [], [missing]
        '''
        super().__init__()
        self._infix_lookup.update({
            '[]': '',      # get item
            '[] =': '',    # set item
            '[missing]': '',     # missing item
            'del []': '',  # delete item
        })

    def __getitem__(self, key):
        # type: (Any) -> Any
        '''
        Get item ([]).

        Args:
            key (object): Key.

        Returns:
            object: Self GET ITEM key.
        '''
        try:
            return self._get_infix_function('[]')(key)
        except KeyError:
            return self.__missing__(key)

    def __setitem__(self, key, value):
        # type: (Any, Any) -> Any
        '''
        Set item (x[key] = value).

        Args:
            key (object): Key.
            value (object): Value.

        Returns:
            object: Self SET ITEM value.
        '''
        return self._get_infix_function('[] =')(key, value)

    def __missing__(self, key):
        # type: (Any) -> Any
        '''
        Missing item ([]). When __getitem__ looks for a non-existent key.

        Args:
            key (object): Key.

        Returns:
            object: Self MISSING key.
        '''
        return self._get_infix_function('[missing]')(key)

    def __delitem__(self, key):
        # type: (Any) -> Any
        '''
        Delete item (del x[key]).

        Args:
            key (object): Key.

        Returns:
            object: Self DELETE key.
        '''
        return self._get_infix_function('del []')(key)


class UnaryInfix(InfixBase):
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Infix class for unary operators: ~, -, +
        '''
        super().__init__()
        self._infix_lookup.update({
            '~': '',   # invert
            'x-': '',  # negative
            'x+': '',  # positive
        })

    def __invert__(self):
        # type: () -> Any
        '''
        Invert (~).

        Returns:
            object: INVERT self.
        '''
        return self._get_infix_function('~')()

    def __neg__(self):
        # type: () -> Any
        '''
        Negative (-).

        Returns:
            object: NEGATIVE self.
        '''
        return self._get_infix_function('x-')()

    def __pos__(self):
        '''
        Positive (+).

        Returns:
            object: POSITIVE self.
        '''
        return self._get_infix_function('x+')()


class EqualityInfix(InfixBase):
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Infix class for infix operators: ==, !=
        '''
        super().__init__()
        self._infix_lookup.update({
            '==': '',  # equal
            '!=': '',  # not equal
        })

    def __eq__(self, value):
        # type: (Any) -> Any
        '''
        Equal (==).

        Args:
            value (object): Value.

        Returns:
            object: Self EQUAL value.
        '''
        return self._get_infix_function('==')(value)

    def __ne__(self, value):
        # type: (Any) -> Any
        '''
        Not equal (!=).

        Args:
            value (object): Value.

        Returns:
            object: Self NOT EQUAL value.
        '''
        return self._get_infix_function('!=')(value)


class AssignmentInfix(InfixBase):
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Infix class for assignment operators: +=, -=, *=, /=, %=, //=, **=, @=,
        &=, |=, ^=, >>=, <<=
        '''
        super().__init__()
        self._infix_lookup.update({
            '+=': '',   # add and assign
            '-=': '',   # subtract and assign
            '*=': '',   # multiply and assign
            '/=': '',   # divide and assign
            '%=': '',   # modulo and assign
            '//=': '',  # floor divide and assign
            '**=': '',  # pow and assign
            '@=': '',   # matrix multiply and assign
            '&=': '',   # and and assign
            '|=': '',   # or and assign
            '^=': '',   # exclusive or and assign
            '>>=': '',  # right bit shift and assign
            '<<=': '',  # left bit shift and assign
        })

    def __iadd__(self, value):
        # type: (Any) -> Any
        '''
        Add and assign (+=).

        Args:
            value (object): Value.

        Returns:
            object: Assign self ADD value.
        '''
        return self._get_infix_function('+=')(value)

    def __isub__(self, value):
        # type: (Any) -> Any
        '''
        Subtract and assign (-=).

        Args:
            value (object): Value.

        Returns:
            object: Assign self SUBTRACT value.
        '''
        return self._get_infix_function('-=')(value)

    def __imul__(self, value):
        # type: (Any) -> Any
        '''
        Multiply and assign (*=)

        Args:
            value (object): Value.

        Returns:
            object: Assign self MULTIPLY value.
        '''
        return self._get_infix_function('*=')(value)

    def __itruediv__(self, value):
        # type: (Any) -> Any
        '''
        Divide and assign (/=).

        Args:
            value (object): Value.

        Returns:
            object: Assign self DIVIDE value.
        '''
        return self._get_infix_function('/=')(value)

    def __imod__(self, value):
        # type: (Any) -> Any
        '''
        Modulo and assign (%=).

        Args:
            value (object): Value.

        Returns:
            object: Assign self MODULO value.
        '''
        return self._get_infix_function('%=')(value)

    def __ifloordiv__(self, value):
        # type: (Any) -> Any
        '''
        Floor divide and assign (//=).

        Args:
            value (object): Value.

        Returns:
            object: Assign self FLOOR value.
        '''
        return self._get_infix_function('//=')(value)

    def __ipow__(self, value):
        # type: (Any) -> Any
        '''
        Exponentiate and assign (**=).

        Args:
            value (object): Value.

        Returns:
            object: Assign self EXPONENTIATE value.
        '''
        return self._get_infix_function('**=')(value)

    def __imatmul__(self, value):
        # type: (Any) -> Any
        '''
        Matrix multiply and assign (@=).

        Args:
            value (object): Value.

        Returns:
            n (@object: Assign self MATRIX MULTIPLY value.
        '''
        return self._get_infix_function('@=')(value)

    def __iand__(self, value):
        # type: (Any) -> Any
        '''
        And and assign (&=).

        Args:
            value (object): Value.

        Returns:
            object: Assign self AND value.
        '''
        return self._get_infix_function('&=')(value)

    def __ior__(self, value):
        # type: (Any) -> Any
        '''
        Or and assign (|=).

        Args:
            value (object): Value.

        Returns:
            object: Assign self OR value.
        '''
        return self._get_infix_function('|=')(value)

    def __ixor__(self, value):
        # type: (Any) -> Any
        '''
        Exclusive or and assign (^=).

        Args:
            value (object): Value.

        Returns:
            n (^object: Assign self EXCLUSIVE value.
        '''
        return self._get_infix_function('^=')(value)

    def __irshift__(self, value):
        # type: (Any) -> Any
        '''
        Right bit shift and assign (>>=).

        Args:
            value (object): Value.

        Returns:
            n (>>object: Assign self RIGHT value.
        '''
        return self._get_infix_function('>>=')(value)

    def __ilshift__(self, value):
        # type: (Any) -> Any
        '''
        Left bit shift and assign (<<=).

        Args:
            value (object): Value.

        Returns:
             (<object: Assign self LEFT value.
        '''
        return self._get_infix_function('<<=')(value)


class MiscInfix(InfixBase):
    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        '''
        Infix class for operators: del x.attr, in
        '''
        super().__init__()
        self._infix_lookup.update({
            'del .': '',  # delete attribute
            'in': '',     # contains
        })

    def __delattr__(self, value):
        # type: (Any) -> Any
        '''
        Delete attribute (del x.attr).

        Args:
            value (object): Value.

        Returns:
            object: Self DELETE value.
        '''
        return self._get_infix_function('del .')(value)

    def __contains__(self, value):
        # type: (Any) -> Any
        '''
        Contains (in).

        Args:
            value (object): Value.

        Returns:
            object: Value CONTAINS self.
        '''
        return self._get_infix_function('in')(value)


class AllInfix(
    ArithmeticInfix,
    MathInfix,
    LogicInfix,
    ComparisonInfix,
    BitwiseInfix,
    ItemInfix,
    UnaryInfix,
    EqualityInfix,
    AssignmentInfix,
    MiscInfix,
):
    pass


class UtiltyInfix(
    ArithmeticInfix,
    MathInfix,
    LogicInfix,
    ComparisonInfix,
    BitwiseInfix,
    ItemInfix,
    UnaryInfix,
):
    pass
