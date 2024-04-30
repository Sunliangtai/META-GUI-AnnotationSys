from typing import List, Union


Sexp = Union[str, List["Sexp"]]  # type: ignore # Recursive type
Lispress = Sexp

LEFT_PAREN = "("
RIGHT_PAREN = ")"
ESCAPE = "\\"
DOUBLE_QUOTE = '"'
META = "^"
READER = "#"

# node label used for external references
EXTERNAL_LABEL = "ExternalReference"
# for `render_pretty`
NUM_INDENTATION_SPACES = 2
# keyword for introducing variable bindings
LET = "let"
# keyword for sequencing programs that have multiple statements
SEQUENCE = "do"
SEQUENCE_SEXP: List[Sexp] = [SEQUENCE]  # to help out mypy
# variables will be named `x0`, `x1`, etc., in the order they are introduced.
VAR_PREFIX = "x"
# named args are given like `(fn :name1 arg1 :name2 arg2 ...)`
NAMED_ARG_PREFIX = ":"
# values are rendered as `#(MySchema "json_dump_of_my_value")`
VALUE_CHAR = "#"
META_CHAR = "^"


def _is_beginning_control_char(nextC):
    return (
        nextC.isspace()
        or nextC == LEFT_PAREN
        or nextC == RIGHT_PAREN
        or nextC == DOUBLE_QUOTE
        or nextC == READER
        or nextC == META
    )


def parse_sexp(s: str) -> Sexp:
    offset = 0

    # eoi = end of input
    def is_eoi():
        nonlocal offset
        return offset == len(s)

    def peek():
        nonlocal offset
        return s[offset]

    def next_char():
        # pylint: disable=used-before-assignment
        nonlocal offset
        cn = s[offset]
        offset += 1
        return cn

    def skip_whitespace():
        while (not is_eoi()) and peek().isspace():
            next_char()

    def skip_then_peek():
        skip_whitespace()
        return peek()

    def read() -> Sexp:
        skip_whitespace()
        c = next_char()
        if c == LEFT_PAREN:
            return read_list()
        elif c == DOUBLE_QUOTE:
            return read_string()
        elif c == META:
            meta = read()
            expr = read()
            return [META, meta, expr]
        elif c == READER:
            return [READER, read()]
        else:
            out_inner = ""
            if c != "\\":
                out_inner += c

            # TODO: is there a better loop idiom here?
            if not is_eoi():
                next_c = peek()
                escaped = c == "\\"
                while (not is_eoi()) and (
                    escaped or not _is_beginning_control_char(next_c)
                ):
                    if (not escaped) and next_c == "\\":
                        next_char()
                        escaped = True
                    else:
                        out_inner += next_char()
                        escaped = False
                    if not is_eoi():
                        next_c = peek()
            return out_inner

    def read_list():
        out_list = []
        while skip_then_peek() != RIGHT_PAREN:
            out_list.append(read())
        next_char()
        return out_list

    def read_string():
        out_str = ""
        while peek() != '"':
            c_string = next_char()
            out_str += c_string
            if c_string == "\\":
                out_str += next_char()
        next_char()
        return f'"{out_str}"'

    out = read()
    skip_whitespace()
    assert offset == len(
        s
    ), f"Failed to exhaustively parse {s}, maybe you are missing a close paren?"
    return out


def parse_lispress(s: str) -> Lispress:
    """
    Parses a Lispress string into a Lispress object.
    Inverse of `render_pretty` or `render_compact`.
    E.g.:
    >>> s = \
    "(describe" \
    "  (:start" \
    "    (findNextEvent" \
    "      (Constraint[Event]" \
    "        :attendees (attendeeListHasRecipientConstraint" \
    "          (recipientWithNameLike" \
    "            (Constraint[Recipient])" \
    '            #(PersonName "Elaine")))))))'
    >>> parse_lispress(s)
    ['describe', [':start', ['findNextEvent', ['Constraint[Event]', ':attendees', ['attendeeListHasRecipientConstraint', ['recipientWithNameLike', ['Constraint[Recipient]'], '#', ['PersonName', '"Elaine"']]]]]]]
    """
    return parse_sexp(s)


def render_pretty(lispress: Lispress, max_width: int = 60) -> str:
    """
    Renders the expression on one or more lines, with adaptive linebreaks and
    standard lisp indentation.
    Attempts to keep lines below `max_width` when possible.
    Right inverse of `parse_lispress` (I.e. `parse_lispress(render_pretty(p)) == p`).
    E.g.:
    >>> lispress = ['describe', [':start', ['findNextEvent', ['Constraint[Event]', ':attendees', ['attendeeListHasRecipientConstraint', ['recipientWithNameLike', ['Constraint[Recipient]'], '#', ['PersonName', '"Elaine"']]]]]]]
    >>> print(render_pretty(lispress))
    (describe
      (:start
        (findNextEvent
          (Constraint[Event]
            :attendees (attendeeListHasRecipientConstraint
              (recipientWithNameLike
                (Constraint[Recipient])
                #(PersonName "Elaine")))))))
    """
    result = "\n".join(_render_lines(sexp=lispress, max_width=max_width))
    return result


def _render_lines(sexp: Lispress, max_width: int) -> List[str]:
    """Helper function for `render_pretty`."""
    compact = render_compact(sexp)
    if isinstance(sexp, str) or len(sexp) <= 1 or len(compact) <= max_width:
        return [compact]
    else:
        fn, *args = sexp
        if fn == VALUE_CHAR:
            assert len(args) == 1, "# Value expressions must have one argument"
            lines = _render_lines(args[0], max_width=max_width)
            lines[0] = VALUE_CHAR + lines[0]
            return lines
        elif fn == META_CHAR:
            assert len(args) == 2, "^ Meta expressions must have one argument"
            lines = _render_lines(args[0], max_width=max_width)
            lines.extend(_render_lines(args[1], max_width=max_width))
            lines[0] = META_CHAR + lines[0]
            return lines
        else:
            prefix = " " * NUM_INDENTATION_SPACES
            fn_lines = _render_lines(fn, max_width=max_width)
            arg_lines = _group_named_args(
                [
                    line
                    for arg in args
                    for line in _render_lines(arg, max_width=max_width)
                ]
            )
            lines = fn_lines + [prefix + line for line in arg_lines]
            lines[0] = LEFT_PAREN + lines[0]
            lines[-1] = lines[-1] + RIGHT_PAREN
            return lines


def _group_named_args(lines: List[str]) -> List[str]:
    """
    Helper function for `_render_lines`.
    Joins `:name` and `argument` lines into a single line.
    """
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _is_named_arg(line):
            result.append(" ".join(lines[i : i + 2]))
            i += 2
        else:
            result.append(line)
            i += 1
    return result


def _is_named_arg(name: str) -> bool:
    return name.startswith(NAMED_ARG_PREFIX)


def render_compact(lispress: Lispress) -> str:
    """
    Renders Lispress on a single line. Right inverse of `parse_lispress`.
    E.g.:
    >>> lispress = ['describe', [':start', ['findNextEvent', ['Constraint[Event]', ':attendees', ['attendeeListHasRecipientConstraint', ['recipientWithNameLike', ['Constraint[Recipient]'], '#', ['PersonName', '"Elaine"']]]]]]]
    >>> print(render_compact(lispress))
    (describe (:start (findNextEvent (Constraint[Event] :attendees (attendeeListHasRecipientConstraint (recipientWithNameLike (Constraint[Recipient]) #(PersonName "Elaine")))))))
    """
    return sexp_to_str(lispress)


def sexp_to_str(sexp: Sexp) -> str:
    """ Generates string representation from S-expression """
    # Note that some of this logic is repeated in lispress.render_pretty
    if isinstance(sexp, list):
        if len(sexp) == 3 and sexp[0] == META:
            (_meta, type_expr, underlying_expr) = sexp
            return META + sexp_to_str(type_expr) + " " + sexp_to_str(underlying_expr)
        elif len(sexp) == 2 and sexp[0] == READER:
            (_reader, expr) = sexp
            return READER + sexp_to_str(expr)
        else:
            return "(" + " ".join(sexp_to_str(f) for f in sexp) + ")"
    else:
        if sexp.startswith('"') and sexp.endswith('"'):
            return sexp
        else:
            return _escape_symbol(sexp)


def _escape_symbol(symbol: str) -> str:
    out = []
    for c in symbol:
        if _is_beginning_control_char(c):
            out.append("\\")
        out.append(c)
    return "".join(out)


def render(lispress):
    lispress = parse_lispress(lispress)
    lispress = render_pretty(lispress)
    return lispress
