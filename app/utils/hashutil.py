#!/usr/bin/env python
# -*- coding: utf-8 -*-


import hashlib


def hash_md5(s):
    return hashlib.md5(s).hexdigest()


def main():
    pass


if __name__ == '__main__':
    main()
