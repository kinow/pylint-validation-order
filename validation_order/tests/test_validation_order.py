import astroid
from astroid.node_classes import NodeNG
from pylint.testutils import CheckerTestCase, Message

from validation_order.validation_order import ValidationOrderChecker


class TestValidationOrder(CheckerTestCase):
    CHECKER_CLASS = ValidationOrderChecker

    def test_good_validation_order_0(self):
        stmt = astroid.extract_node(
            '''
        def some_method():
            n = get_n_value()
            if n > 2:
                raise Exception("Invalid value for N!")
        '''
        )
        with self.assertNoMessages():
            self.walk(stmt)

    def test_good_validation_order_1(self):
        stmt = astroid.extract_node(
            '''
        def some_method(self):
            if self.today_date > 2:
                raise Exception("Invalid value for N!")
        '''
        )
        with self.assertNoMessages():
            self.walk(stmt)

    def test_good_validation_order_2(self):
        stmt = astroid.extract_node(
            '''
        def some_method():
            n = do_something(today_date)
            if today_date > 2:
                raise Exception("Invalid value for N!")
        '''
        )
        with self.assertNoMessages():
            self.walk(stmt)

    def test_good_validation_order_3(self):
        stmt = astroid.extract_node(
            '''
        def some_method(today_date):
            tomorrow_date = today_date + 1
            if tomorrow_date > 2:
                raise Exception("Invalid value for tomorrow_date!")
        '''
        )
        with self.assertNoMessages():
            self.walk(stmt)

    def test_good_validation_order_4(self):
        stmt = astroid.extract_node(
            '''
        def some_method(today_date):
            if today_date:
                tomorrow_date = 10
            if tomorrow_date > 2:
                raise Exception("Invalid value for tomorrow_date!")
        '''
        )
        with self.assertNoMessages():
            self.walk(stmt)

    def test_bad_validation_order_dangling_variable(self):
        stmt = astroid.extract_node(
            '''
        def some_method(n):
            num = 1
            if n > 2:
                raise Exception("Invalid value for N!")
        '''
        )  # type: astroid.node_classes.NodeNG
        node = list(stmt.nodes_of_class(astroid.node_classes.Raise))[0]
        with self.assertAddsMessages(
                Message(
                    "validation-order-error",
                    line=4,
                    confidence=60,
                    node=node
                )
        ):
            self.walk(stmt)
