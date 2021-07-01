# -*- coding: utf-8 -*-


from webs.api.exceptions.customs import InvalidAPIRequest


class LengthChecker(object):
    """字段长度校验"""

    def __init__(self, sign, length):
        self.sign = sign
        self.length = length

    def __call__(self, verified):
        if verified is not None and len(verified) > self.length:
            raise InvalidAPIRequest(f'{self.sign}长度过长！')


class OneOf(object):
    """Validator which succeeds if ``value`` is a member of ``choices``"""

    def __init__(self, choices):
        self.choices = choices

    def __call__(self, verified):
        if verified not in self.choices:
            raise InvalidAPIRequest(f'请选择{self.choices}其中之一！')
