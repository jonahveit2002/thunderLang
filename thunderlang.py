import re

KEYWORDS = {
    'Shai': 'PRINT',
    'Chet': 'INPUT',
    'Joe': '+',  # String concatenation
    'Jaylin': '-',
    'Wiggins': '*',
    'IHart': '/',
    'Mark': 'INT_DECLARATION',
    'Presti': 'STRING_DECLARATION',
    'Holmgren': 'REVERSE_STRING',
}

variables = {}

def parse_expr(expr):
    operator_map = {
        'Joe': '+',
        'Jaylin': '-',
        'Wiggins': '*',
        'IHart': '/',
    }

    for name, op in operator_map.items():
        expr = expr.replace(name, op)
    return expr

def eval_expr(expr):
    expr = expr.strip()

    # Handle Holmgren reverse syntax
    if expr.startswith("Holmgren "):
        inner = expr[len("Holmgren "):].strip()
        reversed_value = eval_expr(inner)
        return reversed_value[::-1] if isinstance(reversed_value, str) else reversed_value

    seen = set()  # prevent circular reference loops

    while True:
        if expr in seen:
            print(f"[ERROR] Detected circular reference in: {expr}")
            return None
        seen.add(expr)

        # Variable reference
        if expr in variables:
            expr = str(variables[expr])
            continue

        # Replace variables with values
        for var in sorted(variables, key=len, reverse=True):
            value = variables[var]
            if isinstance(value, str) and not value.isdigit():
                value = f'"{value}"'
            expr = expr.replace(var, str(value))

        try:
            result = eval(expr)

            # Recursively evaluate if result is another expression
            if isinstance(result, str) and any(op in result for op in ['+', '-', '*', '/']):
                return eval_expr(result)

            return result

        except TypeError as te:
            if "can only concatenate str" in str(te):
                expr = re.sub(r'(?<!")(\b\d+\b)(?!")', r'"\1"', expr)
                continue
            return expr

        except Exception:
            return expr

def execute_line(line):
    tokens = line.strip().split()

    if not tokens:
        return

    if tokens[0] == 'Shai':
        expr = ' '.join(tokens[1:])
        if expr in variables:
            value = variables[expr]
            if isinstance(value, str) and any(op in value for op in ['+', '-', '*', '/']):
                value = eval_expr(value)
            print(value)
        else:
            expr = parse_expr(expr)
            result = eval_expr(expr)
            if result is not None:
                print(result)

    elif tokens[0] == 'Chet':
        if len(tokens) >= 2:
            var = tokens[1]
            user_input = input(f"Enter value for {var}: ")
            variables[var] = user_input
        else:
            print("Error: 'Chet' missing variable name")

    elif tokens[0] == 'Mark':
        if len(tokens) >= 3:
            var = tokens[1]
            expr = ' '.join(tokens[2:])
            expr = parse_expr(expr)
            result = eval_expr(expr)
            if result is not None:
                try:
                    variables[var] = int(result)
                except ValueError:
                    print(f"[ERROR] Mark expected an integer but got: {result}")
        else:
            print("Error: 'Mark' declaration missing variable name or value")

    elif tokens[0] == 'Presti':
        if len(tokens) >= 3:
            var = tokens[1]
            value = ' '.join(tokens[2:])

            result = value
            prev_result = None

            while result != prev_result:
                prev_result = result
                result = eval_expr(parse_expr(str(result)))

            variables[var] = str(result)

    elif '=' in tokens:
        var = tokens[0]
        expr = ' '.join(tokens[2:])
        expr = parse_expr(expr)
        result = eval_expr(expr)
        if result is not None:
            variables[var] = result
    else:
        print(f"[ERROR] Unrecognized statement: {line.strip()}")

def run(filename):
    with open(filename, 'r') as file:
        for line in file:
            execute_line(line)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python thunderlang.py <filename>")
    else:
        run(sys.argv[1])
