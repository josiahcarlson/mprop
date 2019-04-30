
In December 2013, Giampaolo asked if it was possble to do property-like things
in Python modules. It was. This was the result. Apparently a lot of Python folks
really liked this functionality, or functionality like it, because in 2017 there
were two PEPs that were put forward to add deferred attribute lookup to modules:
https://www.python.org/dev/peps/pep-0549/
https://www.python.org/dev/peps/pep-0562/

Ultimately the simpler of the two (PEP 562) won out, and if you are using Python
3.7 or later, you can use the PEP 562 deferred attributes. As such, unless there
is something major, this project is mostly for historical purposes.

Description
===========

This package intends to offer a mechanism to add properties to your modules.
The primary use-case of this functionality is to allow for the deferred
execution of expensive-to-compute module/package level globals without needing
to explicitly call a function.

Generally speaking, this module has two APIs that offer this functionality.
You can use either of them or both of them, and everything will work more or
less as you expect it to, as long as you follow the rules.

Note that this package supports the use of basically any descriptor at the
module-level, not just properties.

Usage
=====

The first method of using the package supports basically any descriptor being
used as a decorator in the standard way. We show the use of ``property`` for the
sake of brevity::

    @property
    def module_property(mod):
        '''mod is the module that this property was defined in'''

    import mprop; mprop.init()

.. warning: If you use properties or any of your own descriptors, you must
    call ``mprop.init()`` after defining all of your properties/descriptors.
    You *can* call ``mprop.init()`` multiple times if you need to add more
    properties/descriptors during runtime.

Because remembering to put the import/init call at the bottom of a module can
be annoying, we've got a special decorator that works just like the property
object, but handles the ``mprop.init()`` call for you::

    from mprop import mproperty

    @mproperty
    def module_property2(mod):
        '''I work exactly the same as the earlier module property, but you
        don't need to make a subsequent call to ``mprop.init()``'''

Regardless of which method you use, if the name of your module is ``mod`` those
that import the module can access the properties as normal::

    # example.py
    from mprop import mproperty

    @mproperty
    def prop(mod):
        return "I was called!"

    def fcn():
        # I can access the property via:
        print _pmodule.prop

    # test.py
    import example

    # the below should print "I was called!"
    print example.prop
    # this should also print "I was called!"
    example.fcn()

Referencing properties from within the module
=============================================

After initialization, your code may want to reference the global properties.
If you try to access the properties directly, you will get a NameError unless
you locally aliased the value, the initialization has not completed, or unless
someone else injected a value with that name into the globals.

If you would like to directly access properties in the module, from within the
module, you must reference them relative to the newly generated module. This is
available from within your functions defined in the module via ``_pmodule``,
which is the "property-enhanced module" that offers property access.

If you find it necessary to require access to the original module object
(which doesn't support properties), you can access ``_module`` from the global
namspace.

How it works
============

The short version: we replace the standard Python module instance in
``sys.modules`` during module import, which allows us to ensure that the module
is replaced everywhere it is used. We perform some magic to ensure that
everything available in the original module is available in the replacement
module (the replacement module's ``__dict__`` is the module's globals), and we
post-process everything in the module's global namespace to pull out
descriptors as necessary.

As of February 1, 2019, in order to offer proper ``@mproperty.setter/deleter``
support, we've started initializing the module after import via the system
profiler. More specifically, any time we get a call for ``@mproperty``, we see
if we've installed a system profiler to clean up after this module. In CPython
via the ``sys.setprofile()`` handler, we look for return calls from module
creation. These auto-nest, and auto-remove themselves, so by the time your final
mprop-using module is done initializing, our profilers are removed.

We used to inject a special ``__getattribute__`` method that auto-initializes on
first access, but it was being triggered in cases where I didn't expect.

Python magic that goes on
-------------------------

* Using ``sys.getframe()`` to pull calling frame objects to get module globals
  and subsequently the module object itself
* Replace ``sys.modules`` entries
* Replace an instance ``__dict__``
* Assign descriptors during runtime by modifying the base class of the
  replacement module
* Use the system profiler to discover when a module has finished loading, to
  start initialization
