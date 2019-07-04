
#include <Python.h>
#include <algorithm>
#include <utility>
#include <new>
#include <cstddef>
#include <vector>
#include <unordered_map>
#include <string>

#include "_python_support.h"

namespace {

struct global_backends
{
  py_ref global;
  std::vector<py_ref> registered;
};


struct backend_options
{
  py_ref backend;
  bool coerce, only;
};

struct local_backends
{
  std::vector<py_ref> skipped;
  std::vector<backend_options> preferred;
};

static std::unordered_map<std::string, global_backends> global_domain_map;

#if !HAS_CONTEXT_VARS
#  define CONTEXT_LOCAL thread_local
#else
#  define CONTEXT_LOCAL
#endif

CONTEXT_LOCAL std::unordered_map<
  std::string, py_contextvar<local_backends>> local_domain_map;

std::string domain_to_string(PyObject * domain)
{
  if (!PyUnicode_Check(domain))
  {
    PyErr_SetString(PyExc_TypeError, "__ua_domain__ must be a string");
    return {};
  }

  Py_ssize_t size;
  const char * str = PyUnicode_AsUTF8AndSize(domain, &size);
  if (!str)
    return {};

  if (size == 0)
  {
    PyErr_SetString(PyExc_ValueError, "__ua_domain__ must be non-empty");
    return {};
  }

  return std::string(str, size);
}

std::string backend_to_domain_string(PyObject * backend)
{
  auto domain = py_ref::steal(PyObject_GetAttrString(backend, "__ua_domain__"));
  if (!domain)
    return {};

  return domain_to_string(domain);
}


PyObject * set_global_backend(PyObject * /*self*/, PyObject * args)
{
  PyObject * backend;
  if (!PyArg_ParseTuple(args, "O", &backend))
    return nullptr;

  auto domain = backend_to_domain_string(backend);
  if (domain.empty())
    return nullptr;

  global_domain_map[domain].global = py_ref::ref(backend);
  Py_RETURN_NONE;
}

PyObject * register_backend(PyObject * /*self*/, PyObject * args)
{
  PyObject * backend;
  if (!PyArg_ParseTuple(args, "O", &backend))
    return nullptr;

  auto domain = backend_to_domain_string(backend);
  if (domain.empty())
    return nullptr;

  global_domain_map[domain].registered.push_back(py_ref::ref(backend));
  Py_RETURN_NONE;
}


struct SetBackendContext
{
  PyObject_HEAD

  using backends_type = py_contextvar<local_backends>;

  backend_options new_backend;
  backends_type * backends;
  backends_type::token restore_token;

  static void dealloc(SetBackendContext * self)
    {
      self->~SetBackendContext();
      Py_TYPE(self)->tp_free(self);
    }

  static PyObject * new_(PyTypeObject * type, PyObject * args, PyObject * kwargs)
    {
      auto self = reinterpret_cast<SetBackendContext *>(type->tp_alloc(type, 0));
      if (self == nullptr)
        return nullptr;

      // Placement new
      self = new (self) SetBackendContext;
      return reinterpret_cast<PyObject *>(self);
    }

  static int init(
    SetBackendContext * self, PyObject * args, PyObject * kwargs)
    {
      static const char * kwlist[] = {"backend", "coerce", "only", nullptr};
      PyObject * backend = nullptr;
      PyObject * coerce = nullptr;
      PyObject * only = nullptr;

      if (!PyArg_ParseTupleAndKeywords(
            args, kwargs,
            "O|O!O!", (char**)kwlist,
            &backend,
            &PyBool_Type, &coerce,
            &PyBool_Type, &only))
        return -1;


      auto domain = backend_to_domain_string(backend);
      if (domain.empty())
        return -1;

      try { self->backends = &local_domain_map[domain]; }
      catch(std::bad_alloc&)
      {
        PyErr_NoMemory();
        return -1;
      }
      if (!self->backends)
        return -1;

      self->new_backend.backend = py_ref::ref(backend);
      self->new_backend.coerce = (coerce == Py_True);
      self->new_backend.only = (only == Py_True);

      return 0;
    }

  static PyObject * enter__(SetBackendContext * self, PyObject * /*args*/)
    {
      auto * curr_backends = self->backends->get();
      if (!curr_backends)
      {
        if (!PyErr_Occurred())
          PyErr_SetString(PyExc_RuntimeError,
                          "Failed to get preferred backends");
        return nullptr;
      }

      auto new_backends = *curr_backends;
      new_backends.preferred.push_back(self->new_backend);
      self->restore_token = self->backends->set(std::move(new_backends));
      if (PyErr_Occurred())
        return nullptr;

      Py_RETURN_NONE;
    }

  static PyObject * exit__(SetBackendContext * self, PyObject * /*args*/)
    {
      self->backends->reset(std::move(self->restore_token));
      Py_RETURN_NONE;
    }
};


struct SkipBackendContext
{
  PyObject_HEAD

  using backends_type = py_contextvar<local_backends>;

  py_ref skip_backend_;
  backends_type * backends_;
  backends_type::token restore_token_;

  static void dealloc(SkipBackendContext * self)
    {
      self->~SkipBackendContext();
      Py_TYPE(self)->tp_free(self);
    }

  static PyObject * new_(PyTypeObject * type, PyObject * args, PyObject * kwargs)
    {
      auto self = reinterpret_cast<SkipBackendContext *>(type->tp_alloc(type, 0));
      if (self == nullptr)
        return nullptr;

      // Placement new
      self = new (self) SkipBackendContext;
      return reinterpret_cast<PyObject *>(self);
    }

  static int init(
    SkipBackendContext * self, PyObject * args, PyObject * kwargs)
    {
      static const char *kwlist[] = {"backend", nullptr};
      PyObject * backend;

      if (!PyArg_ParseTupleAndKeywords(args, kwargs,
                                       "O", (char**)kwlist,
                                       &backend))
        return -1;

      auto domain = backend_to_domain_string(backend);
      if (domain.empty())
        return -1;

      try { self->backends_ = &local_domain_map[domain]; }
      catch(std::bad_alloc&)
      {
        PyErr_NoMemory();
        return -1;
      }

      self->skip_backend_ = py_ref::ref(backend);

      return 0;
    }

  static PyObject * enter__(SkipBackendContext * self, PyObject * /*args*/)
    {
      auto * curr_backends = self->backends_->get();
      if (!curr_backends)
      {
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to get skipped backends");
        return nullptr;
      }

      auto new_backends = *curr_backends;
      new_backends.skipped.push_back(self->skip_backend_);
      self->restore_token_ = self->backends_->set(std::move(new_backends));
      if (!self->restore_token_)
        return nullptr;

      Py_RETURN_NONE;
    }

  static PyObject * exit__(SkipBackendContext * self, PyObject * /*args*/)
    {
      self->backends_->reset(std::move(self->restore_token_));
      Py_RETURN_NONE;
    }
};

enum class LoopReturn { Continue, Break, Error };

template <typename Callback>
LoopReturn for_each_backend(const std::string & domain_key, Callback call)
{
  auto * locals = local_domain_map[domain_key].get();
  if (!locals)
    return LoopReturn::Error;


  auto & skip = locals->skipped;
  auto & pref = locals->preferred;

  auto should_skip =
    [&](PyObject * backend)
      {
        auto it = std::find_if(
          skip.begin(), skip.end(),
          [&](const py_ref & be) { return be.get() == backend; });

        return (it != skip.end());
      };

  LoopReturn ret = LoopReturn::Continue;
  for (auto & options : pref)
  {
    if (should_skip(options.backend))
      continue;

    ret = call(options.backend.get(), options.coerce);
    if (ret != LoopReturn::Continue)
      return ret;

    if (options.only || options.coerce)
      return ret;
  }

  auto & globals = global_domain_map[domain_key];

  if (globals.global && !should_skip(globals.global))
  {
    ret = call(globals.global.get(), false);
    if (ret != LoopReturn::Continue)
      return ret;
  }

  for (auto & backend : globals.registered)
  {
    if (should_skip(backend))
      continue;

    ret = call(backend.get(), false);
    if (ret != LoopReturn::Continue)
      return ret;
  }
  return ret;
}

struct py_func_args { py_ref args, kwargs; };

struct Function
{
  PyObject_HEAD
  py_ref extractor_, replacer_;   // functions to handle dispatchables
  std::string domain_key_;        // associated __ua_domain__ in UTF8
  py_ref def_args_, def_kwargs_;  // default arguments
  py_ref def_impl_;               // default implementation
  py_ref dict_;                   // __dict__

  PyObject * call(PyObject * args, PyObject * kwargs);

  py_func_args replace_dispatchables(
    PyObject * backend, PyObject * args, PyObject * kwargs, PyObject * coerce);

  py_ref canonicalize_args(PyObject * args);
  py_ref canonicalize_kwargs(PyObject * kwargs);

  static void dealloc(Function * self)
    {
      PyObject_GC_UnTrack(self);
      self->~Function();
      Py_TYPE(self)->tp_free(self);
    }

  static PyObject * new_(PyTypeObject * type, PyObject * args, PyObject * kwargs)
    {
      auto self = reinterpret_cast<Function *>(type->tp_alloc(type, 0));
      if (self == nullptr)
        return nullptr;

      // Placement new
      self = new (self) Function;
      return reinterpret_cast<PyObject *>(self);
    }

  static int init(Function * self, PyObject * args, PyObject * /*kwargs*/)
    {
      PyObject * extractor, * replacer;
      PyObject * domain;
      PyObject * def_args, * def_kwargs;
      PyObject * def_impl;

      if (!PyArg_ParseTuple(
            args, "OOO!O!O!O",
            &extractor,
            &replacer,
            &PyUnicode_Type, &domain,
            &PyTuple_Type, &def_args,
            &PyDict_Type, &def_kwargs,
            &def_impl))
      {
        return -1;
      }

      if (!PyCallable_Check(extractor)
          || (replacer != Py_None && !PyCallable_Check(replacer)))
      {
        PyErr_SetString(PyExc_TypeError,
                        "Argument extractor and replacer must be callable");
        return -1;
      }

      if (def_impl != Py_None && !PyCallable_Check(def_impl))
      {
        PyErr_SetString(PyExc_TypeError,
                        "Default implementation must be Callable or None");
        return -1;
      }

      self->domain_key_ = domain_to_string(domain);
      if (PyErr_Occurred())
        return -1;

      self->extractor_ = py_ref::ref(extractor);
      self->replacer_ = py_ref::ref(replacer);
      self->def_args_ = py_ref::ref(def_args);
      self->def_kwargs_ = py_ref::ref(def_kwargs);
      self->def_impl_ = py_ref::ref(def_impl);

      return 0;
    }
};


bool is_default(PyObject * value, PyObject * def)
{
  // TODO: richer comparison for builtin types? (if cheap)
  return (value == def);
}


py_ref Function::canonicalize_args(PyObject * args)
{
  const auto arg_size = PyTuple_GET_SIZE(args);
  const auto def_size = PyTuple_GET_SIZE(def_args_.get());

  if (arg_size > def_size)
    return py_ref::ref(args);

  Py_ssize_t mismatch = 0;
  for (Py_ssize_t i = arg_size - 1; i >= 0; --i)
  {
    auto val = PyTuple_GET_ITEM(args, i);
    auto def = PyTuple_GET_ITEM(def_args_.get(), i);
    if (!is_default(val, def))
    {
      mismatch = i + 1;
      break;
    }
  }

  return py_ref::steal(PyTuple_GetSlice(args, 0, mismatch));
}


py_ref Function::canonicalize_kwargs(PyObject * kwargs)
{
  if (kwargs == nullptr)
    return py_ref::steal(PyDict_New());

  PyObject * key, * def_value;
  Py_ssize_t pos = 0;
  while (PyDict_Next(def_kwargs_, &pos, &key, &def_value))
  {
    auto val = PyDict_GetItem(kwargs, key);
    if (val && is_default(val, def_value))
    {
      PyDict_DelItem(kwargs, key);
    }
  }
  return py_ref::ref(kwargs);
}


py_func_args Function::replace_dispatchables(
  PyObject * backend, PyObject * args, PyObject * kwargs, PyObject * coerce)
{
  auto ua_convert =
    py_ref::steal(PyObject_GetAttrString(backend, "__ua_convert__"));

  if (!ua_convert)
  {
    PyErr_Clear();
    return {py_ref::ref(args), py_ref::ref(kwargs)};
  }

  auto dispatchables = py_ref::steal(PyObject_Call(extractor_, args, kwargs));
  if (!dispatchables)
    return {};

  auto convert_args = py_make_tuple(dispatchables, coerce);
  auto res = py_ref::steal(PyObject_Call(ua_convert, convert_args, nullptr));
  if (!res)
  {
    return {};
  }

  if (res == Py_NotImplemented)
  {
    return {std::move(res), nullptr};
  }

  auto replaced_args = py_ref::steal(PySequence_Tuple(res));
  if (!replaced_args)
    return {};

  auto replacer_args = py_make_tuple(args, kwargs, replaced_args);
  if (!replacer_args)
    return {};

  res = py_ref::steal(PyObject_Call(replacer_, replacer_args, nullptr));
  if (!res)
    return {};

  if (!PyTuple_Check(res) || PyTuple_Size(res) != 2)
  {
    PyErr_SetString(PyExc_TypeError,
                    "Argument replacer must return a 2-tuple (args, kwargs)");
    return {};
  }

  auto new_args = py_ref::ref(PyTuple_GET_ITEM(res.get(), 0));
  auto new_kwargs = py_ref::ref(PyTuple_GET_ITEM(res.get(), 1));

  new_kwargs = canonicalize_kwargs(new_kwargs);

  if (!PyTuple_Check(new_args) || !PyDict_Check(new_kwargs))
  {
    PyErr_SetString(PyExc_ValueError, "Invalid return from argument_replacer");
    return {};
  }

  return {std::move(new_args), std::move(new_kwargs)};
}


PyObject * Function_call(
  Function * self, PyObject * args, PyObject * kwargs)
{
  return self->call(args, kwargs);
}


static py_ref BackendNotImplementedError;


PyObject * Function::call(PyObject * args_, PyObject * kwargs_)
{
  auto args = canonicalize_args(args_);
  auto kwargs = canonicalize_kwargs(kwargs_);

  py_ref result;

  auto ret = for_each_backend(
    domain_key_,
    [&, this](PyObject * backend, bool coerce)
      {
        auto new_args = replace_dispatchables(backend, args, kwargs,
                                              coerce ? Py_True : Py_False);
        if (new_args.args == Py_NotImplemented)
          return LoopReturn::Continue;
        if (new_args.args == nullptr)
          return LoopReturn::Error;

        auto ua_function =
          py_ref::steal(PyObject_GetAttrString(backend, "__ua_function__"));
        if (!ua_function)
          return LoopReturn::Error;

        auto ua_func_args = py_make_tuple(
          reinterpret_cast<PyObject *>(this), new_args.args, new_args.kwargs);
        if (!ua_func_args)
          return LoopReturn::Error;

        result = py_ref::steal(
          PyObject_Call(ua_function, ua_func_args, nullptr));
        if (result == Py_NotImplemented)
          return LoopReturn::Continue;
        if (!result)
          return LoopReturn::Error;

        return LoopReturn::Break;  // Backend called successfully
      }
    );

  if (ret != LoopReturn::Continue)
    return result.release();

  if (def_impl_ == Py_None)
  {
    PyErr_SetString(
      BackendNotImplementedError,
      "No selected backends had an implementation for this function.");
    return nullptr;
  }

  return PyObject_Call(def_impl_, args, kwargs);
}


PyObject * Function_repr(Function * self)
{
  if (self->dict_)
    if (auto name = PyDict_GetItemString(self->dict_, "__name__"))
      return PyUnicode_FromFormat("<uarray multimethod '%S'>", name);

  return PyUnicode_FromString("<uarray multimethod>");
}


/** Implements the descriptor protocol to allow binding to class instances */
PyObject * Function_descr_get(PyObject * self, PyObject * obj, PyObject * type)
{
  if (!obj)
  {
    Py_INCREF(self);
    return self;
  }

  return PyMethod_New(self, obj);
}


/** Make members visible to the garbage collector */
int Function_traverse(Function * self, visitproc visit, void * arg)
{
  Py_VISIT(self->extractor_);
  Py_VISIT(self->replacer_);
  Py_VISIT(self->def_args_);
  Py_VISIT(self->def_kwargs_);
  Py_VISIT(self->def_impl_);
  Py_VISIT(self->dict_);
  return 0;
}


PyObject * dummy(PyObject * /*self*/, PyObject * args)
{
  Py_RETURN_NONE;
}


PyMethodDef method_defs[] =
{
  {"set_global_backend", set_global_backend, METH_VARARGS, nullptr},
  {"register_backend", register_backend, METH_VARARGS, nullptr},
  {"dummy", dummy, METH_VARARGS, nullptr},
  {NULL} /* Sentinel */
};

PyModuleDef uarray_module =
{
  PyModuleDef_HEAD_INIT,
  "_uarray",
  nullptr,
  -1,
  method_defs
};

PyGetSetDef Function_getset[] =
{
  {"__dict__", PyObject_GenericGetDict, PyObject_GenericSetDict},
  {NULL} /* Sentinel */
};

PyTypeObject FunctionType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  "_uarray.Function",             /* tp_name */
  sizeof(Function),               /* tp_basicsize */
  0,                              /* tp_itemsize */
  (destructor)Function::dealloc,  /* tp_dealloc */
  0,                              /* tp_print */
  0,                              /* tp_getattr */
  0,                              /* tp_setattr */
  0,                              /* tp_reserved */
  (reprfunc)Function_repr,        /* tp_repr */
  0,                              /* tp_as_number */
  0,                              /* tp_as_sequence */
  0,                              /* tp_as_mapping */
  0,                              /* tp_hash  */
  (ternaryfunc)Function_call,     /* tp_call */
  0,                              /* tp_str */
  PyObject_GenericGetAttr,        /* tp_getattro */
  PyObject_GenericSetAttr,        /* tp_setattro */
  0,                              /* tp_as_buffer */
  (Py_TPFLAGS_DEFAULT
   | Py_TPFLAGS_HAVE_GC),         /* tp_flags */
  0,                              /* tp_doc */
  (traverseproc)Function_traverse,/* tp_traverse */
  0,                              /* tp_clear */
  0,                              /* tp_richcompare */
  0,                              /* tp_weaklistoffset */
  0,                              /* tp_iter */
  0,                              /* tp_iternext */
  0,                              /* tp_methods */
  0,                              /* tp_members */
  Function_getset,                /* tp_getset */
  0,                              /* tp_base */
  0,                              /* tp_dict */
  Function_descr_get,             /* tp_descr_get */
  0,                              /* tp_descr_set */
  offsetof(Function, dict_),      /* tp_dictoffset */
  (initproc)Function::init,       /* tp_init */
  0,                              /* tp_alloc */
  Function::new_,                 /* tp_new */
};


PyMethodDef SetBackendContext_Methods[] = {
  {"__enter__", (binaryfunc)SetBackendContext::enter__, METH_NOARGS, nullptr},
  {"__exit__", (binaryfunc)SetBackendContext::exit__, METH_VARARGS, nullptr},
  {NULL}  /* Sentinel */
};

PyTypeObject SetBackendContextType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  "_uarray.SetBackendContext",             /* tp_name */
  sizeof(SetBackendContext),               /* tp_basicsize */
  0,                                       /* tp_itemsize */
  (destructor)SetBackendContext::dealloc,  /* tp_dealloc */
  0,                                       /* tp_print */
  0,                                       /* tp_getattr */
  0,                                       /* tp_setattr */
  0,                                       /* tp_reserved */
  0,                                       /* tp_repr */
  0,                                       /* tp_as_number */
  0,                                       /* tp_as_sequence */
  0,                                       /* tp_as_mapping */
  0,                                       /* tp_hash  */
  0,                                       /* tp_call */
  0,                                       /* tp_str */
  0,                                       /* tp_getattro */
  0,                                       /* tp_setattro */
  0,                                       /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,                      /* tp_flags */
  0,                                       /* tp_doc */
  0,                                       /* tp_traverse */
  0,                                       /* tp_clear */
  0,                                       /* tp_richcompare */
  0,                                       /* tp_weaklistoffset */
  0,                                       /* tp_iter */
  0,                                       /* tp_iternext */
  SetBackendContext_Methods,               /* tp_methods */
  0,                                       /* tp_members */
  0,                                       /* tp_getset */
  0,                                       /* tp_base */
  0,                                       /* tp_dict */
  0,                                       /* tp_descr_get */
  0,                                       /* tp_descr_set */
  0,                                       /* tp_dictoffset */
  (initproc)SetBackendContext::init,       /* tp_init */
  0,                                       /* tp_alloc */
  SetBackendContext::new_,                 /* tp_new */
};


PyMethodDef SkipBackendContext_Methods[] = {
  {"__enter__", (binaryfunc)SkipBackendContext::enter__, METH_NOARGS, nullptr},
  {"__exit__", (binaryfunc)SkipBackendContext::exit__, METH_VARARGS, nullptr},
  {NULL}  /* Sentinel */
};

PyTypeObject SkipBackendContextType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  "_uarray.SkipBackendContext",             /* tp_name */
  sizeof(SkipBackendContext),               /* tp_basicsize */
  0,                                        /* tp_itemsize */
  (destructor)SkipBackendContext::dealloc,  /* tp_dealloc */
  0,                                        /* tp_print */
  0,                                        /* tp_getattr */
  0,                                        /* tp_setattr */
  0,                                        /* tp_reserved */
  0,                                        /* tp_repr */
  0,                                        /* tp_as_number */
  0,                                        /* tp_as_sequence */
  0,                                        /* tp_as_mapping */
  0,                                        /* tp_hash  */
  0,                                        /* tp_call */
  0,                                        /* tp_str */
  0,                                        /* tp_getattro */
  0,                                        /* tp_setattro */
  0,                                        /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT,                       /* tp_flags */
  0,                                        /* tp_doc */
  0,                                        /* tp_traverse */
  0,                                        /* tp_clear */
  0,                                        /* tp_richcompare */
  0,                                        /* tp_weaklistoffset */
  0,                                        /* tp_iter */
  0,                                        /* tp_iternext */
  SkipBackendContext_Methods,               /* tp_methods */
  0,                                        /* tp_members */
  0,                                        /* tp_getset */
  0,                                        /* tp_base */
  0,                                        /* tp_dict */
  0,                                        /* tp_descr_get */
  0,                                        /* tp_descr_set */
  0,                                        /* tp_dictoffset */
  (initproc)SkipBackendContext::init,       /* tp_init */
  0,                                        /* tp_alloc */
  SkipBackendContext::new_,                 /* tp_new */
};

}  // namespace (anonymous)


PyMODINIT_FUNC
PyInit__uarray(void)
{

  auto m = py_ref::steal(PyModule_Create(&uarray_module));
  if (!m)
    return nullptr;

  if (PyType_Ready(&FunctionType) < 0)
    return nullptr;
  Py_INCREF(&FunctionType);
  PyModule_AddObject(m, "Function", (PyObject *)&FunctionType);

  if (PyType_Ready(&SetBackendContextType) < 0)
    return nullptr;
  Py_INCREF(&SetBackendContextType);
  PyModule_AddObject(m, "SetBackendContext", (PyObject*)&SetBackendContextType);

  if (PyType_Ready(&SkipBackendContextType) < 0)
    return nullptr;
  Py_INCREF(&SkipBackendContextType);
  PyModule_AddObject(
    m, "SkipBackendContext", (PyObject*)&SkipBackendContextType);

  BackendNotImplementedError = py_ref::steal(
    PyErr_NewExceptionWithDoc(
      "uarray.BackendNotImplementedError",
      "An exception that is thrown when no compatible"
      " backend is found for a method.",
      PyExc_NotImplementedError,
      nullptr));
  if (!BackendNotImplementedError)
    return nullptr;
  Py_INCREF(BackendNotImplementedError.get());
  PyModule_AddObject(
    m, "BackendNotImplementedError", BackendNotImplementedError);

  return m.release();
}
