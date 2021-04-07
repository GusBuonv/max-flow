from typing import Optional

class Null:
    def __init__(self, *args, **kwargs): raise RuntimeError('Call Null.instance() instead')
    def __call__(self, *args, **kwargs): return self
    def __repr__(self): return "Null(  )"
    def __nonzero__(self): return 0

    def __getattr__(self, name): return self
    def __setattr__(self, name, value): return self
    def __delattr__(self, name): return self

    _instance: Optional['Null'] = None

    @classmethod
    def instance(cls) -> 'Null':
        if cls._instance is not None:
            return cls._instance

        instance = cls.__new__(cls)
        cls._instance = instance
        return instance
