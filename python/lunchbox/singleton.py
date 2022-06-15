class Singleton:
    '''
    A super class for creating singleton classes.
    '''
    def __new__(cls, *args, **kwargs):
        '''
        __new__ is called before __init__. Normaly __new__ fetches an object and
        __init__ initilaizes it.

        In this class, __new__ checks the class body for an instance of a class,
        returns it if it already exists, and creates, assigns and returns it if
        it does not.

        Returns:
            object: Singular instance of class.
        '''
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance
