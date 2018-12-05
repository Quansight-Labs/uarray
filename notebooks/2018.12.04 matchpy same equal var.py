# If you include two wildcards twice in an expression, will it match when they are equal?

from matchpy import *

replacer = ManyToOneReplacer()


ManyThings = Operation.new("ManyThings", Arity(0, False))

w = Wildcard.dot("w")
replacer.add(ReplacementRule(Pattern(ManyThings(w, w)), lambda w: w))

print(replacer.replace(ManyThings(Symbol("hi"), Symbol("hi"))))
# yep it does! this is Symbol("hi")
