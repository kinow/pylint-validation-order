import astroid

from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker


class ValidationOrderChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'validation-order'
    priority = -1
    msgs = {
        'W0001': (
            'Validation order could be different.',
            'validation-order-error',
            'The validation logic could be done sooner.'
        ),
    }
    options = (
        # (
        #     'ignore-ints',
        #     {
        #         'default': False, 'type': 'yn', 'metavar' : '<y_or_n>',
        #         'help': 'Allow returning non-unique integers',
        #     }
        # ),
    )

    def __init__(self, linter=None):
        BaseChecker.__init__(self, linter)
        self._initialize()

    def _initialize(self):
        print("Validation Order Checker Initialized!")

    def visit_ifexp(self, node):
        print("Node: " + str(node))

