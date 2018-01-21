# -*- coding: utf-8 -*-
"""
    flask2.__main__
    ~~~~~~~~~~~~~~

    Alias for flask2.run for the command line.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""


if __name__ == '__main__':
    from .cli import main
    main(as_module=True)
