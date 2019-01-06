import astroid

from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker


class UniqueReturnChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'unique-returns'
    priority = -1
    msgs = {
        'W0001': (
            'Returns a non-unique constant.',
            'non-unique-returns',
            'All constants returned in a function should be unique.'
        ),
    }
    options = (
        (
            'ignore-ints',
            {
                'default': False, 'type': 'yn', 'metavar' : '<y_or_n>',
                'help': 'Allow returning non-unique integers',
            }
        ),
    )


def register(linter):
    linter.register_checker(UniqueReturnChecker(linter))
