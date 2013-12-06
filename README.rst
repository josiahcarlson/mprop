
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
used as a decorator in the standard way. We show the use of `property` for the
sake of brevity::

    @property
    def module_property(mod):
        '''mod is the module that this property was defined in'''

    import mprop; mprop.init()

.. warning: If you use properties or any of your own descriptors, you must
    call `mprop.init()` after defining all of your properties/descriptors.
    You *can* call `mprop.init()` multiple times if you need to add more
    properties/descriptors during runtime.

Because remembering to put the import/init call at the bottom of a module can
be annoying, we've got a special decorator that works just like the property
object, but handles the `mprop.init()` call for you::

    from mprop import mproperty

    @mproperty
    def module_property2(mod):
        '''I work exactly the same as the earlier module property, but you
        don't need to make a subsequent call to `mprop.init()`'''

Regardless of which method you use, if the name of your module is `mod`, you
those that import the module can access the properties as normal::

    # example.py
    from mprop import mproperty

    @mproperty
    def prop(mod):
        return "I was called!"

    # test.py
    import example

    # the below should print "I was called!"
    print example.prop

Referencing properties from within the module
=============================================

After initialization, your code may want to reference the global properties.
If you try to access the properties directly, you will get a NameError unless
you locally aliased the value, the initialization has not completed, or unless
someone else injected a value with that name into the globals.

In order to reference properties from within the module, any module that has
been initialized with `mprop.init()` or has used the `mproperty` decorator
will have in its global namespace an object called `_pmodule`, which is the
"property-enhanced module" that offers property access.

If you find it necessary to require access to the original module object
(which doesn't support properties), you can access `_module` from the global
namspace.

How it works
============

The short version: we replace the standard Python module instance in
`sys.modules` during module import, which allows us to ensure that the module
is replaced everywhere it is used. We perform some magic to ensure that
everything available in the original module is available in the replacement
module (the replacement module's `__dict__` is the module's globals), and we
post-process everything in the module's global namespace to pull out
descriptors as necessary.

When using the `mproperty` decorator, much the same goes on, but we add a
special `__getattribute__` method that handles descriptor extraction on first
attribute access to the module.

Python magic that goes on
-------------------------

* Using `sys.getframe()` to pull calling frame objects to get module globals
  and subsequently the module object itself
* Replace `sys.modules` entries
* Replace an instance `__dict__`
* Assign descriptors during runtime by modifying the base class of the
  replacement module
* Assign and delete class-level `__getattribute__` methods
