## Solution Description

[**solution.py**](./solution.py) : Module facilitating parsing of command line arguments.

Supports positional and optional arguments, and more features, like:
- Arguments can be added with specific attributes:
    - `alias` (to add short name for argument)
    - `required` (to make argument compulsory)
    - `type` (to specify type of value for argument)
    - `nvals` (to specify number of values for argument)
    - `set_value` (to specify value to be set on argument use)
- Multiple values can be passed for argument
- Values passed on call can be accessed as ordered or simple dictionary in:
    - Long form (all arguments)
    - Short form (excluding arguments with none value)
- Values can be printed in JSON format

[**solution_test.py**](./solution_test.py) : Tests for solution module.
