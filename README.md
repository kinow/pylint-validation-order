# PyLint Validation Order

A PyLint plugin that tries to locate `if` statements, where validation
is being performed after unnecessary variable declaration.

Uses `astroid` to parse the script AST.

## Usage

In development mode:

```bash
PYTHONPATH=. pylint --errors-only --load-plugins validation_order $SCRIPT_PATH
```

For more, check PyLint's [documentation](http://pylint.pycqa.org/en/latest/how_tos/plugins.html)
on plugins.

## TODO:

- Investigate if it is worth to check other statements besides `raise`
- Check if besides variable declaration, we could also warn over other
statements used