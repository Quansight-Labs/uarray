#include "vectorcall.h"

#ifdef PYPY_VERSION

/* PyPy doesn't have any support for Vectorcall/FastCall.
 * These helpers are for translating to PyObject_Call. */

static PyObject * build_arg_tuple(PyObject * const * args, Py_ssize_t nargs) {
  PyObject * tuple = PyTuple_New(nargs);
  if (!tuple) {
    return NULL;
  }

  for (Py_ssize_t i = 0; i < nargs; ++i) {
    Py_INCREF(args[i]); /* SET_ITEM steals a reference */
    PyTuple_SET_ITEM(tuple, i, args[i]);
  }
  return tuple;
}

static PyObject * build_kwarg_dict(
    PyObject * const * args, PyObject * names, Py_ssize_t nargs) {
  PyObject * dict = PyDict_New();
  if (!dict) {
    return NULL;
  }

  for (Py_ssize_t i = 0; i < nargs; ++i) {
    PyObject * key = PyTuple_GET_ITEM(names, i);
    int success = PyDict_SetItem(dict, key, args[i]);
    if (success == -1) {
      Py_DECREF(dict);
      return NULL;
    }
  }
  return dict;
}
#elif ((PY_VERSION_HEX >= 0x03070000) && (PY_VERSION_HEX < 0x03090000))
#  ifdef __cplusplus
extern "C" {
#  endif
extern int _PyObject_GetMethod(PyObject *, PyObject *, PyObject **);
#  ifdef __cplusplus
}
#  endif
#endif /* PYPY_VERSION */


Py_ssize_t Q_PyVectorcall_NARGS(size_t n) {
  return n & (~Q_PY_VECTORCALL_ARGUMENTS_OFFSET);
}

PyObject * Q_PyObject_Vectorcall(
    PyObject * callable, PyObject * const * args, size_t nargsf,
    PyObject * kwnames) {
#ifdef PYPY_VERSION
  PyObject * dict = NULL;
  Py_ssize_t nargs = Q_PyVectorcall_NARGS(nargsf);
  if (kwnames) {
    Py_ssize_t nkwargs = PyTuple_GET_SIZE(kwnames);
    dict = build_kwarg_dict(&args[nargs - nkwargs], kwnames, nkwargs);
    if (!dict) {
      return NULL;
    }
    nargs -= nkwargs;
  }
  PyObject * ret = Q_PyObject_VectorcallDict(callable, args, nargs, dict);
  Py_XDECREF(dict);
  return ret;
#elif (PY_VERSION_HEX >= 0x03090000)
  return PyObject_Vectorcall(callable, args, nargsf, kwnames);
#elif (PY_VERSION_HEX >= 0x03080000)
  return _PyObject_Vectorcall(callable, args, nargsf, kwnames);
#else
  Py_ssize_t nargs = Q_PyVectorcall_NARGS(nargsf);
  return _PyObject_FastCallKeywords(
      callable, (PyObject **)args, nargs, kwnames);
#endif
}

PyObject * Q_PyObject_VectorcallDict(
    PyObject * callable, PyObject * const * args, size_t nargsf,
    PyObject * kwdict) {
#ifdef PYPY_VERSION
  Py_ssize_t nargs = Q_PyVectorcall_NARGS(nargsf);
  PyObject * tuple = build_arg_tuple(args, nargs);
  if (!tuple) {
    return NULL;
  }
  PyObject * ret = PyObject_Call(callable, tuple, kwdict);
  Py_DECREF(tuple);
  return ret;
#elif (PY_VERSION_HEX >= 0x03090000)
  return PyObject_VectorcallDict(callable, args, nargsf, kwdict);
#else
  Py_ssize_t nargs = Q_PyVectorcall_NARGS(nargsf);
  return _PyObject_FastCallDict(callable, (PyObject **)args, nargs, kwdict);
#endif
}

PyObject * Q_PyObject_VectorcallMethod(
    PyObject * name, PyObject * const * args, size_t nargsf,
    PyObject * kwnames) {
#if (defined(PYPY_VERSION) || (PY_VERSION_HEX < 0x03070000))
  PyObject * callable = PyObject_GetAttr(args[0], name);
  if (!callable) {
    return NULL;
  }
  PyObject * result =
      Q_PyObject_Vectorcall(callable, &args[1], nargsf - 1, kwnames);
  Py_DECREF(callable);
  return result;
#elif (PY_VERSION_HEX >= 0x03090000)
  return PyObject_VectorcallMethod(name, args, nargsf, kwnames);
#else /* (PY_VERSION_HEX >= 0x03070000) */
  /* Private CPython code for CALL_METHOD opcode */
  PyObject * callable = NULL;
  int unbound = _PyObject_GetMethod(args[0], name, &callable);
  if (callable == NULL) {
    return NULL;
  }

  if (unbound) {
    /* We must remove PY_VECTORCALL_ARGUMENTS_OFFSET since
     * that would be interpreted as allowing to change args[-1] */
    nargsf &= ~Q_PY_VECTORCALL_ARGUMENTS_OFFSET;
  } else {
    /* Skip "self". We can keep PY_VECTORCALL_ARGUMENTS_OFFSET since
     * args[-1] in the onward call is args[0] here. */
    args++;
    nargsf--;
  }
  PyObject * result = Q_PyObject_Vectorcall(callable, args, nargsf, kwnames);
  Py_DECREF(callable);
  return result;
#endif
}
