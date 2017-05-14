#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import functools
import time


def class_params_check(*types, **kwtypes):
    """
       check the parameters of a class function, usage: @class_params_check(int, str, (int, str), key1=list, key2=(list, tuple))
    """

    def _decoration(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            result = [isinstance(_param, _type) for _param, _type in zip(args[1:], types)]
            assert all(result), "params_chack: invalid parameters in " + func.__name__
            result = [isinstance(kwargs[_param], kwtypes[_param]) for _param in kwargs if _param in kwtypes]
            # print result
            assert all(result), "params_chack: invalid parameters in " + func.__name__
            return func(*args, **kwargs)

        return _inner

    return _decoration


def params_check(*types, **kwtypes):
    """
    check the parameters of a function, usage: @params_chack(int, str, (int, str), key1=list, key2=(list, tuple))
    """

    def _decoration(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            result = [isinstance(_param, _type) for _param, _type in zip(args, types)]
            assert all(result), "params_chack: invalid parameters in " + func.__name__
            result = [isinstance(kwargs[_param], kwtypes[_param]) for _param in kwargs if _param in kwtypes]
            # print result
            assert all(result), "params_chack: invalid parameters in " + func.__name__
            return func(*args, **kwargs)

        return _inner

    return _decoration


def get_time(raw=False):
    if raw:
        return time.time()
    return int(time.time())


def main():
    pass


if __name__ == '__main__':
    main()
