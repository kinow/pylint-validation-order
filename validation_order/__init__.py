from . import validation_order

__all__ = ['validation_order', 'register']


def register(linter):
    linter.register_checker(validation_order.ValidationOrderChecker(linter))
