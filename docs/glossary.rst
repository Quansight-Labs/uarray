.. currentmodule:: uarray

Glossary
========

Multimethod
-----------

A method, possibly with a default/reference implementation, that can
have other implementations provided by different backends.

If a multimethod does not have an implementation, a
:obj:`BackendNotImplementedError` is raised.

Backend
-------

A backend is an entity that can provide implementations for different
functions. It can also (optionally) receive some options from the user
about how to process the implementations. A backend can be set permanently
or temporarily.

.. _DomainGlossary:

Domain
------

A domain is a collection or grouping of multimethods. A domain's string,
by convention (although not by force), is the name of the module that provides
the multimethods.

Dispatching
-----------

Dispatching is the process of forwarding a function call to an implementation
in a backend.

Conversion
----------

A backend might have different object types compared to the reference
implementation, or it might require some other conversions of objects.
Conversion is the process of converting any given object into a
library's native form.

Coercion
^^^^^^^^

Coercions are conversions that may take a long time, usually those
involving copying or moving of data. As a rule of thumb, conversions
longer than ``O(log n)`` (where ``n`` is the size of the object  in
memory) should be made into coercions.

.. _MarkingGlossary:

Marking
-------

Marking is the process of telling the backend what convertor to use for
a given argument.
