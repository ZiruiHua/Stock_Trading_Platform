"""
Here are some self-defined exceptions classes used in the project.
"""


class Http400Error(Exception):
    message = ''

    def __init__(self, message, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.message = message


class Http404Error(Exception):
    message = ''

    def __init__(self, message, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.message = message
