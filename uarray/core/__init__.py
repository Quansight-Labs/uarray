"""
Core data types and operations. Roughly based on Cartesian Categories.

Best practices:

* If you are doing a bunch of fixed point function operations (with compose)
  consider moving the logic into it's own operation and then wrapping in a `Function`.
  This is a little more sane to understand and program. Also, we see this function
  as a coherent chunk in the AST for longer (until application) so maybe will make
  that more sensible as well?
  Con is that we don't see body till evaluation time. So if we wanna process/replace
  accumlated functions before applying, this makes that impossible.
"""


from .unify import *  # NOQA
