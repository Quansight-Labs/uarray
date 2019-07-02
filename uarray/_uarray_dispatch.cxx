
#include <Python.h>
#include <utility>
#include <new>
#include <cstddef>

#include "_python_support.h"

namespace {

struct py_func_args { py_ref args, kwargs; };

struct Function
{
	PyObject_HEAD
	py_ref extractor_, replacer_;   // functions to handle dispatchables
	py_ref backends_;               // function returning backends as iterable
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
			PyObject * backends;
			PyObject * def_args, * def_kwargs;
			PyObject * def_impl;

			if (!PyArg_ParseTuple(
				    args, "OOOO!O!O",
				    &extractor,
				    &replacer,
				    &backends,
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

			if (!PyCallable_Check(backends))
			{
				PyErr_SetString(PyExc_TypeError,
				                "The backends argument must be callable");
				return -1;
			}

			if (def_impl != Py_None && !PyCallable_Check(def_impl))
			{
				PyErr_SetString(PyExc_TypeError,
				                "Default implementation must be Callable or None");
				return -1;
			}

			self->extractor_ = py_ref::ref(extractor);
			self->replacer_ = py_ref::ref(replacer);
			self->backends_ = py_ref::ref(backends);
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

	auto backends = py_ref::steal(
		PyObject_Call(backends_, py_make_tuple(), nullptr));
	if (!backends)
		return nullptr;

	auto i_backends = py_ref::steal(PyObject_GetIter(backends));
	if (!i_backends)
	{
		PyErr_SetString(PyExc_TypeError, "backends must return an iterable");
		return nullptr;
	}

	while (auto be = py_ref::steal(PyIter_Next(i_backends)))
	{
		auto backend = py_ref::steal(PyObject_GetAttrString(be, "backend"));
		auto coerce = py_ref::steal(PyObject_GetAttrString(be, "coerce"));

		if (!backend || !coerce)
		{
			PyErr_SetString(PyExc_TypeError, "Invalid backend spec");
			return nullptr;
		}

		if (!PyBool_Check(coerce))
		{
			PyErr_SetString(PyExc_TypeError, "coerce must be a Bool");
			return nullptr;
		}

		auto new_args = replace_dispatchables(backend, args, kwargs, coerce);
		if (new_args.args == Py_NotImplemented)
		{
			continue;
		}
		if (new_args.args == nullptr)
		{
			return nullptr;
		}

		auto ua_function =
			py_ref::steal(PyObject_GetAttrString(backend, "__ua_function__"));
		if (!ua_function)
		{
			PyErr_SetString(PyExc_TypeError, "Backend must have __ua_function__");
			return nullptr;
		}

		auto ua_func_args = py_make_tuple(
			reinterpret_cast<PyObject *>(this), new_args.args, new_args.kwargs);
		auto result = py_ref::steal(
			PyObject_Call(ua_function, ua_func_args, nullptr));
		if (result != Py_NotImplemented)
			return result.release();
	}

	if (PyErr_Occurred())
		return nullptr;

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
	Py_VISIT(self->backends_);
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

static PyGetSetDef Function_getset[] =
{
	{"__dict__", PyObject_GenericGetDict, PyObject_GenericSetDict},
	{NULL} /* Sentinel */
};

static PyTypeObject FunctionType = {
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

}  // namespace (anonymous)


PyMODINIT_FUNC
PyInit__uarray(void)
{
	if (PyType_Ready(&FunctionType) < 0)
		return nullptr;

	auto m = py_ref::steal(PyModule_Create(&uarray_module));
	if (!m)
		return nullptr;

	Py_INCREF(&FunctionType);
	PyModule_AddObject(m, "Function", (PyObject *)&FunctionType);

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
