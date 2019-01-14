import astroid

from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker


class ValidationOrderChecker(BaseChecker):
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
        self._current_function = None  # type: astroid.nodes.FunctionDef
        self._current_if = None  # type: astroid.nodes.If

    def visit_functiondef(self, node):
        self._current_function = node

    def leave_functiondef(self, node):
        self._current_function = None

    def visit_if(self, node):
        """Visit only if's that have a single `raise` statement.

        :type node: astroid.nodes.If
        """
        self._current_if = node

    def leave_if(self, node):
        self._current_if = None

    def visit_raise(self, node):
        """
        :type node: astroid.nodes.Raise
        """

        if node.parent == self._current_if \
                and len(self._current_if.body) == 1:
            self._check_validation_order(node)

    def _check_validation_order(self, node):
        """
        :type node: astroid.nodes.Raise
        """
        # skip if:
        # - if the current if is the first statement in the current function
        if self._current_function.body[0] == self._current_if:
            return

        current_if_variables = self._get_variables(self._current_if.test)
        # current_function_variables = self._get_variables(self._current_function.args)

        # - if there are no variables in current if
        if current_if_variables:
            # otherwise, for each statement before the current if...
            valid_case = False
            for stmt in self._current_function.body:
                if stmt == self._current_if:
                    break
                # we must check if there were any assign ops before
                if isinstance(stmt, astroid.Assign):
                    stray_vars = self._get_variables(stmt.targets)
                    if hasattr(stmt.value, "args"):
                        stray_vars.update(self._get_variables(stmt.value.args))
                    for stray_var in stray_vars:
                        if stray_var in current_if_variables:
                            valid_case = True
            if not valid_case:
                self.add_message('validation-order-error',
                                 confidence=60,
                                 node=node,
                                 line=self._current_if.lineno)

    def _get_variables(self, node):
        """
        :rtype: set
        """
        if isinstance(node, list):
            l = list()
            for n in node:
                if hasattr(n, 'attrname'):
                    l.append(n.attrname)
                elif hasattr(n, 'name'):
                    l.append(n.name)
                # else:
                #     print("UH!")
            return set(l)

        if hasattr(node, 'args'):
            l = [x.name for x in node.args]
            return set(l)

        t = set()
        names = list(node.nodes_of_class(astroid.nodes.Name))
        for n in names:
            if hasattr(n.parent, 'args'):
                if n in n.parent.args:
                    t.add(n.name)
            elif hasattr(n, 'name'):
                t.add(n.name)
            # else:
            #     print("UH!")
        return t
