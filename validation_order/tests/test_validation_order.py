import astroid

from pylint.testutils import CheckerTestCase, Message
from validation_order.validation_order import ValidationOrderChecker


class TestValidationOrder(CheckerTestCase):
    CHECKER_CLASS = ValidationOrderChecker

    def test_bad_validation_order(self):
        stmt = astroid.extract_node(
            '''
        def some_method(n):
            num = 1
            if n > 2:
                raise Exception("Invalid value for N!")
        '''
        )
        with self.assertAddsMessages(
                Message(
                    "validation-order-error",
                    line=4,
                    confidence=60
                )
        ):
            self.walk(stmt)