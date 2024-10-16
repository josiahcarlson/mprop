
# Copyright 2024 Josiah Carlson <josiah.carlson@gmail.com>
# Released under the LGPL 2.1 license
# Honestly, you shouldn't be using this, you should upgrade to Python 3.7+
# and use module properties.

import sys
import threading
import types

__all__ = ['init', 'mproperty']
PY3 = sys.version_info[:2] >= (3, 0)
_dtypes = type if PY3 else (type, types.ClassType)

def isdescriptor(v):
    # shortcut for the most common descriptor in Python land
    if isinstance(v, property):
        return True

    # omit descriptor/property definitions
    if isinstance(v, _dtypes):
        return False

    # check for the descriptor protocol
    for attr in ('__get__', '__set__', '__delete__'):
        if hasattr(v, attr):
            return True

    return False

def _cleanup(Module, glbls):
    items = glbls.items()
    if PY3:
        items = list(items)

    # Directly assign the properties to the Module class so that they behave
    # like properties, and remove them from the globals so that they don't
    # alias themselves.
    tf = type(_cleanup)
    for k, v in items:
        if isinstance(v, mproperty):
            v = property(v.fget, v.fset, v.fdel, v.doc)
        if isinstance(v, tf):
            del glbls[k]
            setattr(Module, k, staticmethod(v))
        elif isdescriptor(v):
            del glbls[k]
            setattr(Module, k, v)

def init(glbls=None):
    '''
    Initialize the module-level properties/descriptors for the module that
    this function is being called from. Or, if a globals dictionary is passed,
    initialize the module-level properties/descriptors for the module that
    those globals came from.

    See the readme for more documentation.
    '''
    # Pull the module context in which the init function was called.
    init = glbls is None
    if init:
        glbls = sys._getframe(1).f_globals
    name = glbls['__name__']

    module = sys.modules[name]
    if isinstance(sys.modules[name], types.ModuleType):
        # Every module must have a new class to ensure that the module itself
        # has its own unique properties.
        class Module(object):
            def __repr__(self):
                return "<Module %r>"%(self.__name__,)

        module = Module()

        # Give the Module object and the Python module the same namespace.
        module.__dict__ = glbls

        # Keep a reference to the Module so that non-module properties can
        # reference properties via _pmodule.PROPERTY .
        module._pmodule = module

        # Keep a reference to the original module so the original module isn't
        # cleaned up after we've replaced the sys.modules entry (cleanup
        # mangles the module globals).
        module._module = sys.modules[name]

        # Replace the original module with this one.
        sys.modules[name] = module
    else:
        # Assume that module is one of our Module classes, fetch it here just
        # in case someone is using both init() and @mproperty together
        Module = type(module)

    # Handle property assignment and global namespace cleanup
    _cleanup(Module, glbls)

    return module

class auto_init(object):
    '''
    New magic, uses the system profiler to handle module property cleanup after
    module initialization.
    '''
    __slots__ = 'op', 'gl'
    def __init__(self):
        self.op = None
        self.gl = {}

    def add(self, gl):
        if id(gl) not in self.gl:
            # don't know about this module / globals yet

            if not self.gl:
                # install the profiler / cleanup handler, but keep the old one
                self.op = sys.getprofile()
                sys.setprofile(self)

            # keep the reference for later
            self.gl[id(gl)] = gl

    def __call__(self, f, e, a):
        if e == 'return' and \
            f.f_code.co_name == '<module>' and \
            id(f.f_globals) in self.gl:

                # initialize one of the mprop modules
                g = f.f_globals
                m = init(g)
                self.gl.pop(id(f.f_globals))

                if not self.gl:
                    # no more mprop modules
                    sys.setprofile(self.op)
                    self.op = None

auto_init = auto_init()

class mproperty(object):
    '''
    Use this descriptor as a decorator in the same way that you would use
    'property', but only apply it to module-level functions, and watch as your
    module gains properties!
    '''
    __slots__ = 'fget', 'fset', 'fdel', 'doc'
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        # Make sure we've got a valid function so we can pull its globals.
        for func in [fget, fset, fdel]:
            if isinstance(func, types.FunctionType):
                break
        if not isinstance(func, types.FunctionType):
            raise TypeError("At least one of fget, fset, or fdel must be a function")

        # If we haven't installed the profiler for the module, install it. We
        # need it to set up the properties after the module is loaded. Replaces
        # the need for init() at the end.
        auto_init.add(func.__globals__ if PY3 else func.func_globals)

        # Update our references
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.doc = doc

    def getter(self, get):
        return mproperty(get, self.fset, self.fdel, self.doc)
 
    def setter(self, set):
        return mproperty(self.fget, set, self.fdel, self.doc)
 
    def deleter(self, delete):
        return mproperty(self.fget, self.fset, delete, self.doc)
