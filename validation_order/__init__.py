from . import validation_order
from pylint.lint import PyLinter

__all__ = ['validation_order', 'register']


def register(linter):
    """
    :type linter: PyLinter
    """
    linter.register_checker(validation_order.ValidationOrderChecker(linter))
