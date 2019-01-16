import astroid

from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker


class ValidationOrderException(Exception):

    def __init__(self,
                 node: astroid.node_classes.NodeNG = None,
                 lineno: int = 0,
                 confidence: int = 60):
        super().__init__()
        self.node = node
        self.lineno = lineno
        self.confidence = confidence


class ValidationOrderChecker(BaseChecker):
    """Checks the order of validation in the code."""
    __implements__ = IAstroidChecker

    name = 'validation-order'
    priority = -1
    msgs = {
        'E3331': (
            'Validation order could be different.',
            'validation-order-error',
            'The validation logic could be done sooner.'
        ),
    }

    def __init__(self, linter=None):
        """
        :param linter: PyLint linter
        :type linter: pylint.lint.PyLinter
        """
        BaseChecker.__init__(self, linter)
        self._current_function = None  # type: astroid.nodes.FunctionDef
        self._current_if = None  # type: astroid.nodes.If

    def visit_functiondef(self, node):
        """
        :type node: astroid.nodes.FunctionDef
        """
        self._current_function = node

    def leave_functiondef(self, node):
        """
        :type node: astroid.nodes.FunctionDef
        """
        self._current_function = None

    def visit_if(self, node):
        """Visit only if's that have a single `raise` statement.

        :type node: astroid.nodes.If
        """
        self._current_if = node

    def leave_if(self, node):
        """
        :type node: astroid.nodes.Raise
        """
        self._current_if = None

    def visit_raise(self, node):
        """
        :type node: astroid.nodes.Raise
        """
        if self._is_validation_node(node, self._current_if) \
           and not self._is_first_statement(self._current_if, self._current_function):
            if_variables = self._get_variables(self._current_if.test)
            if if_variables:
                self._check_validation_order(node, if_variables)

    # --- private methods ---

    @staticmethod
    def _is_validation_node(raise_node: astroid.Raise, if_node: astroid.If):
        return raise_node.parent == if_node \
               and len(if_node.body) == 1

    @staticmethod
    def _is_first_statement(if_node: astroid.If, function_def: astroid.FunctionDef):
        return function_def.body[0] == if_node

    @staticmethod
    def _get_variables(node):
        """
        Retrieve a set of variables for a given node, or list of nodes.

        :param node: a node
        :type node: astroid.node_classes.NodeNG
        :return: set of variables (strings)
        :rtype: set
        """
        variables = set()

        if isinstance(node, list):
            for single_node in node:
                if hasattr(single_node, "name"):
                    variables.add(single_node.name)
            return variables

        if hasattr(node, 'args'):
            for arg_node in node.args:
                if hasattr(arg_node, "name"):
                    variables.add(arg_node.name)
            return variables

        names = list(node.nodes_of_class(astroid.nodes.Name))
        for name_node in names:
            if hasattr(name_node.parent, 'args'):
                if name_node in name_node.parent.args:
                    variables.add(name_node.name)
            elif hasattr(name_node, 'name'):
                variables.add(name_node.name)

        return variables

    def _check_validation_order(self, node, if_variables):
        """
        Logic to check the validation order.

        :type node: astroid.nodes.Raise
        :type if_variables: set
        :raises: ValidationOrderException
        """
        for stmt in self._current_function.body:
            if stmt == self._current_if:
                break

            try:
                self._check_node(stmt, if_variables)
            except ValidationOrderException as e:
                self.add_message('validation-order-error',
                                 confidence=e.confidence,
                                 node=node,
                                 line=e.lineno)

    def _check_node(self, node, if_variables):
        """
        Logic to check the validation order of a single node.

        :type node: astroid.nodes.Raise
        :type if_variables: set
        :raises: ValidationOrderException
        """

        # we must check if there were any assign ops before
        if isinstance(node, astroid.Assign):
            # a, b = ..., a and b are targets
            stray_vars = self._get_variables(node.targets)
            if hasattr(node.value, "args"):
                # a, b = _do_something(c), c is in args
                stray_vars.update(self._get_variables(node.value.args))
            for stray_var in stray_vars:
                if stray_var in if_variables:
                    return

        raise ValidationOrderException(
            node=node,
            lineno=self._current_if.lineno)

        # we must check if it is an if
        # if isinstance(node, astroid.If):
        #     if_vars = self._get_variables(node.test)
        #     for if_var in if_vars:
        #         if if_var in if_variables:
        #             return
