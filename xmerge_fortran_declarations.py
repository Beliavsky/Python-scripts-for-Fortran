#!/usr/bin/env python3
"""
xmerge_fortran_declarations.py

Consolidate consecutive, uncommented Fortran declarations that share the same
type/spec (text before '::') into one declaration statement, wrapping with
continuation lines using '&' when a line would exceed a chosen width.

Important fixes vs naive versions:
- Joins free-form continuation lines into a single logical statement before parsing,
  so wrapped declarations are handled correctly.
- Wraps lines to maximize fill while reserving space for the trailing ', &' on
  continued lines (uses a small backtrack step).

Rules:
- Only merges consecutive declarations with identical lhs (before ::), after
  normalizing whitespace/case.
- Does not touch lines with '!' anywhere (full-line or inline comments).
- Leaves non-declaration statements unchanged.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional, Tuple


DECL_RE = re.compile(r"^(\s*)(.+?)\s*::\s*(.+?)\s*$")


def _has_comment_anywhere(line: str) -> bool:
    # conservative: if '!' appears anywhere, treat as comment and do not touch
    return "!" in line


def _is_blank_or_full_comment(line: str) -> bool:
    s = line.strip()
    return s == "" or s.startswith("!")


def _normalize_lhs(lhs: str) -> str:
    lhs = lhs.strip().lower()
    lhs = re.sub(r"\s+", " ", lhs)
    lhs = re.sub(r"\s*,\s*", ", ", lhs)
    lhs = re.sub(r"\s*\(\s*", "(", lhs)
    lhs = re.sub(r"\s*\)\s*", ")", lhs)
    return lhs


def _split_decl_tail(tail: str) -> List[str]:
    """
    Split text after '::' into top-level comma-separated items.
    Respects parentheses and quotes.
    """
    items: List[str] = []
    buf: List[str] = []
    depth = 0
    in_sq = False
    in_dq = False

    i = 0
    while i < len(tail):
        ch = tail[i]

        if ch == "'" and not in_dq:
            in_sq = not in_sq
            buf.append(ch)
            i += 1
            continue
        if ch == '"' and not in_sq:
            in_dq = not in_dq
            buf.append(ch)
            i += 1
            continue

        if not in_sq and not in_dq:
            if ch == "(":
                depth += 1
            elif ch == ")":
                if depth > 0:
                    depth -= 1
            elif ch == "," and depth == 0:
                item = "".join(buf).strip()
                if item:
                    items.append(item)
                buf = []
                i += 1
                continue

        buf.append(ch)
        i += 1

    last = "".join(buf).strip()
    if last:
        items.append(last)
    return items


def _gather_logical_statements(lines: List[str]) -> List[dict]:
    """
    Convert physical lines into logical statements (free-form continuation).
    For safety, we refuse to join (and later refuse to rewrite) anything that
    contains '!' in any involved line.
    """
    stmts: List[dict] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        if _is_blank_or_full_comment(line) or _has_comment_anywhere(line):
            stmts.append({"text": line.rstrip("\n"), "phys": [line], "safe": False})
            i += 1
            continue

        phys = [line]
        safe = True

        buf = line.rstrip("\n")
        # join while trailing '&'
        while buf.rstrip().endswith("&"):
            buf = buf.rstrip()
            buf = buf[:-1].rstrip()  # drop trailing '&'

            i += 1
            if i >= n:
                break

            nxt = lines[i]
            # if continuation line has comments/blank, do not attempt to rewrite this stmt
            if _is_blank_or_full_comment(nxt) or _has_comment_anywhere(nxt):
                safe = False
                break

            phys.append(nxt)
            nxt_txt = nxt.rstrip("\n")

            # remove optional leading '&' after whitespace
            s = nxt_txt.lstrip()
            if s.startswith("&"):
                s = s[1:].lstrip()

            buf = buf + " " + s

        stmts.append({"text": buf, "phys": phys, "safe": safe})
        i += 1

    return stmts


def _parse_decl_stmt(stmt_text: str) -> Optional[Tuple[str, str, str, List[str]]]:
    """
    Returns (indent, lhs_exact, lhs_norm, items) if stmt_text is a declaration.
    stmt_text must be a full logical statement (no inline comments).
    """
    m = DECL_RE.match(stmt_text)
    if not m:
        return None
    indent, lhs_exact, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
    lhs_norm = _normalize_lhs(lhs_exact)
    items = _split_decl_tail(tail)
    if not items:
        return None
    return indent, lhs_exact, lhs_norm, items


def _wrap_decl(
    indent: str,
    lhs_exact: str,
    items: List[str],
    width: int = 80,
    cont_extra_indent: int = 3,
) -> List[str]:
    """
    Wrap a declaration to width, maximizing fill on each continued line.
    Continued physical lines end with ', &' and are followed by a continuation line.
    """
    first_prefix = f"{indent}{lhs_exact} :: "
    cont_prefix = indent + (" " * cont_extra_indent)

    out_lines: List[str] = []
    remaining = items[:]
    first = True

    while remaining:
        prefix = first_prefix if first else cont_prefix

        line_items: List[str] = []
        # greedily add items based on content width (without ', &')
        while remaining:
            candidate_items = line_items + [remaining[0]]
            candidate = prefix + ", ".join(candidate_items)
            if len(candidate) <= width or not line_items:
                # accept if fits, or if it's the first item on the line (even if too long)
                line_items.append(remaining.pop(0))
                # if we just accepted an overlong single item, stop
                if len(prefix + ", ".join(line_items)) > width and len(line_items) == 1:
                    break
            else:
                break

        line = prefix + ", ".join(line_items)

        # if more items remain, we must add ', &' to this line; backtrack if needed
        if remaining:
            cont_suffix = ", &"
            if len(line) + len(cont_suffix) > width:
                # move items from the end of this line to the front of remaining
                while len(line_items) > 1 and len(line) + len(cont_suffix) > width:
                    remaining.insert(0, line_items.pop())
                    line = prefix + ", ".join(line_items)
            line = line + cont_suffix

        out_lines.append(line)
        first = False

    return out_lines


def consolidate_fortran(lines: List[str], width: int = 80) -> List[str]:
    stmts = _gather_logical_statements(lines)
    out: List[str] = []

    run_indent: Optional[str] = None
    run_lhs_exact: Optional[str] = None
    run_lhs_norm: Optional[str] = None
    run_items: List[str] = []

    def flush_run() -> None:
        nonlocal run_indent, run_lhs_exact, run_lhs_norm, run_items
        if run_lhs_exact is None:
            return
        new = _wrap_decl(run_indent or "", run_lhs_exact, run_items, width=width)
        out.extend([s + "\n" for s in new])
        run_indent = None
        run_lhs_exact = None
        run_lhs_norm = None
        run_items = []

    for st in stmts:
        text = st["text"]
        phys = st["phys"]
        safe = st["safe"]

        if not safe:
            flush_run()
            out.extend(phys)
            continue

        parsed = _parse_decl_stmt(text)
        if parsed is None:
            flush_run()
            out.extend(phys)
            continue

        indent, lhs_exact, lhs_norm, items = parsed

        if run_lhs_norm is None:
            run_indent = indent
            run_lhs_exact = lhs_exact
            run_lhs_norm = lhs_norm
            run_items = items[:]
            continue

        if lhs_norm == run_lhs_norm:
            run_items.extend(items)
        else:
            flush_run()
            run_indent = indent
            run_lhs_exact = lhs_exact
            run_lhs_norm = lhs_norm
            run_items = items[:]

    flush_run()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="Fortran source file to process")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output file (default: stdout)")
    ap.add_argument("--width", type=int, default=80, help="Maximum line width (default: 80)")
    ap.add_argument("--inplace", action="store_true", help="Overwrite input file")
    args = ap.parse_args()

    text = args.input.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(True)  # keep '\n'
    new_lines = consolidate_fortran(lines, width=args.width)
    out_text = "".join(new_lines)

    if args.inplace:
        args.input.write_text(out_text, encoding="utf-8")
        return

    if args.output is not None:
        args.output.write_text(out_text, encoding="utf-8")
    else:
        print(out_text, end="")


if __name__ == "__main__":
    main()
