
#include <Python.h>
#include <utility>
#include <new>
#include <cstddef>

namespace {
class py_ref
{
	explicit py_ref(PyObject * object): obj(object) {}
public:

	py_ref(): obj(nullptr) {}
	py_ref(std::nullptr_t): py_ref() {}

	py_ref(const py_ref & other): obj(other.obj) { Py_XINCREF(obj); }
	py_ref(py_ref && other): obj(other.obj) { other.obj = nullptr; }

	static py_ref steal(PyObject * object) { return py_ref(object); }

	static py_ref ref(PyObject * object)
		{
			Py_XINCREF(object);
			return py_ref(object);
		}

	~py_ref(){ Py_XDECREF(obj); }

	py_ref & operator = (const py_ref & other)
		{
			auto temp = py_ref(other);
			swap(temp);
			return *this;
		}

	py_ref & operator = (py_ref && other)
		{
			auto temp = py_ref(std::move(other));
			swap(temp);
			return *this;
		}

	void swap(py_ref & other)
		{
			std::swap(other.obj, obj);
		}

	explicit operator bool () const { return obj != nullptr; }

	operator PyObject* () const { return get(); }

	PyObject * get() const { return obj; }
	PyObject * release()
		{
			PyObject * t = obj;
			obj = nullptr;
			return t;
		}
private:
	PyObject * obj;
};

template <typename ... Ts>
py_ref py_make_tuple(Ts... args)
{
	using py_obj = PyObject *;
	return py_ref::steal(PyTuple_Pack(sizeof...(args), py_obj{args}...));
}


py_ref py_make_tuple()
{
	return py_ref::steal(PyTuple_New(0));
}

struct Function
{
	PyObject_HEAD
	py_ref extractor, replacer;   // functions to handle dispatchables
	py_ref backends;              // function returning backends as iterable
	py_ref def_args, def_kwargs;  // default arguments
	py_ref def_impl;              // default implementation
	py_ref dict;                  // __dict__

	static void dealloc(Function * self)
		{
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
			PyObject * extractor_, * replacer_;
			PyObject * backends_;
			PyObject * def_args_, * def_kwargs_;
			PyObject * def_impl_;

			if (!PyArg_ParseTuple(
				    args, "OOOO!O!O",
				    &extractor_,
				    &replacer_,
				    &backends_,
				    &PyTuple_Type, &def_args_,
				    &PyDict_Type, &def_kwargs_,
				    &def_impl_))
			{
				return -1;
			}

			if (!PyCallable_Check(extractor_) || !PyCallable_Check(replacer_))
			{
				PyErr_SetString(PyExc_TypeError,
				                "Argument extractor and replacer must be callable");
				return -1;
			}

			if (!PyCallable_Check(backends_))
			{
				PyErr_SetString(PyExc_TypeError,
				                "The backends argument must be callable");
				return -1;
			}

			if (def_impl_ != Py_None && !PyCallable_Check(def_impl_))
			{
				PyErr_SetString(PyExc_TypeError,
				                "Default implementation must be Callable or None");
				return -1;
			}

			self->extractor = py_ref::ref(extractor_);
			self->replacer = py_ref::ref(replacer_);
			self->backends = py_ref::ref(backends_);
			self->def_args = py_ref::ref(def_args_);
			self->def_kwargs = py_ref::ref(def_kwargs_);
			self->def_impl = py_ref::ref(def_impl_);

			return 0;
		}
};


bool is_default(PyObject * value, PyObject * def)
{
	// TODO: richer comparison for builtin types? (if cheap)
	return (value == def);
}


py_ref canonicalize_args(PyObject * args, const PyObject * defaults)
{
	const auto arg_size = PyTuple_GET_SIZE(args);
	const auto def_size = PyTuple_GET_SIZE(defaults);

	if (arg_size > def_size)
		return py_ref::ref(args);

	Py_ssize_t mismatch = 0;
	for (Py_ssize_t i = arg_size - 1; i >= 0; --i)
	{
		auto val = PyTuple_GET_ITEM(args, i);
		auto def = PyTuple_GET_ITEM(defaults, i);
		if (!is_default(val, def))
		{
			mismatch = i + 1;
			break;
		}
	}

	return py_ref::steal(PyTuple_GetSlice(args, 0, mismatch));
}


py_ref canonicalize_kwargs(PyObject * kwargs, PyObject * defaults)
{
	if (kwargs == nullptr)
		return py_ref::steal(PyDict_New());

	PyObject * key, * def_value;
	Py_ssize_t pos = 0;
	while (PyDict_Next(defaults, &pos, &key, &def_value))
	{
		auto val = PyDict_GetItem(kwargs, key);
		if (is_default(val, def_value))
		{
			PyDict_DelItem(kwargs, key);
		}
	}
	return py_ref::ref(kwargs);
}


struct py_func_args { py_ref args, kwargs; };


py_func_args replace_dispatchables(
	PyObject * backend, PyObject * args, PyObject * kwargs,
	PyObject * extractor, PyObject * replacer, PyObject * coerce)
{
	auto ua_convert =
		py_ref::steal(PyObject_GetAttrString(backend, "__ua_convert__"));

	if (!ua_convert)
	{
		return {py_ref::ref(args), py_ref::ref(kwargs)};
	}

	auto dispatchables = py_ref::steal(PyObject_Call(extractor, args, kwargs));
	if (!dispatchables)
		return {};

	auto convert_args = py_make_tuple(dispatchables, coerce);
	auto res = py_ref::steal(PyObject_Call(ua_convert, convert_args, nullptr));
	if (!res || res == Py_NotImplemented)
		return {};

	auto itr = py_ref::steal(PyObject_GetIter(res));
	if (itr == nullptr)
		return {};

	const auto num_disp = PyTuple_Size(dispatchables);
	auto replaced_args = py_ref::steal(PyTuple_New(num_disp));
	Py_ssize_t pos = 0;
	while (auto item = py_ref::steal(PyIter_Next(itr)))
	{
		if (pos > num_disp)
		{
			PyErr_SetString(PyExc_ValueError,
			                "Too many values returned from __ua_convert__");
			return {};
		}
		PyTuple_SET_ITEM(replaced_args.get(), pos, item.release());
		++pos;
	}

	auto replacer_args = py_make_tuple(args, kwargs, replaced_args);
	if (!replacer_args)
		return {};

	res = py_ref::steal(PyObject_Call(replacer, replacer_args, nullptr));
	if (PyTuple_Size(res) != 2)
		return {};

	auto new_args = py_ref::ref(PyTuple_GET_ITEM(res.get(), 0));
	auto new_kwargs = py_ref::ref(PyTuple_GET_ITEM(res.get(), 1));

	if (!PyTuple_Check(new_args) || !PyDict_Check(new_kwargs))
	{
		PyErr_SetString(PyExc_ValueError, "Invalid return from argument_replacer");
		return {};
	}

	return {std::move(new_args), std::move(new_kwargs)};
}


PyObject * uarray_function_call(
	PyObject * self_, PyObject * args_, PyObject * kwargs_)
{
	auto * self = reinterpret_cast<Function *>(self_);

	auto args = canonicalize_args(args_, self->def_args);
	auto kwargs = canonicalize_kwargs(kwargs_, self->def_kwargs);

	auto backends = py_ref::steal(
		PyObject_Call(self->backends, py_make_tuple(), nullptr));
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

		auto new_args = replace_dispatchables(
			backend, args, kwargs, self->extractor, self->replacer, coerce);
		if (new_args.args == nullptr)
			continue;

		auto ua_function =
			py_ref::steal(PyObject_GetAttrString(backend, "__ua_function__"));
		if (!ua_function)
		{
			PyErr_SetString(PyExc_TypeError, "Backend must have __ua_function__");
			return nullptr;
		}

		auto ua_func_args = py_make_tuple(
			reinterpret_cast<PyObject *>(self), new_args.args, new_args.kwargs);
		auto result = py_ref::steal(
			PyObject_Call(ua_function, ua_func_args, nullptr));
		if (result != Py_NotImplemented)
			return result.release();
	}

	if (self->def_impl == Py_None)
	{
		PyErr_SetString(
			PyExc_NotImplementedError,
			"No selected backends had an implementation for this function.");
		return nullptr;
	}

	return PyObject_Call(self->def_impl, args, kwargs);
}


PyObject * dummy(PyObject * /*self*/, PyObject * args)
{
	Py_RETURN_NONE;
}


PyMethodDef method_defs[] =
{
	{"dummy", dummy, METH_VARARGS, nullptr},
	{nullptr, nullptr, 0, nullptr}
};

PyModuleDef uarray_module =
{
	PyModuleDef_HEAD_INIT,
	"_uarray",
	nullptr,
	-1,
	method_defs
};

static PyGetSetDef Function_getset[] = {
	{"__dict__", PyObject_GenericGetDict, PyObject_GenericSetDict},
	{NULL} /* Sentinel */
};

static PyTypeObject FunctionType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"_uarray.Function",            /* tp_name */
	sizeof(Function),              /* tp_basicsize */
	0,                             /* tp_itemsize */
	(destructor)Function::dealloc, /* tp_dealloc */
	0,                             /* tp_print */
	0,                             /* tp_getattr */
	0,                             /* tp_setattr */
	0,                             /* tp_reserved */
	0,                             /* tp_repr */
	0,                             /* tp_as_number */
	0,                             /* tp_as_sequence */
	0,                             /* tp_as_mapping */
	0,                             /* tp_hash  */
	uarray_function_call,          /* tp_call */
	0,                             /* tp_str */
	PyObject_GenericGetAttr,       /* tp_getattro */
	PyObject_GenericSetAttr,       /* tp_setattro */
	0,                             /* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,            /* tp_flags */
	0,                             /* tp_doc */
	0,                             /* tp_traverse */
	0,                             /* tp_clear */
	0,                             /* tp_richcompare */
	0,                             /* tp_weaklistoffset */
	0,                             /* tp_iter */
	0,                             /* tp_iternext */
	0,                             /* tp_methods */
	0,                             /* tp_members */
	Function_getset,               /* tp_getset */
	0,                             /* tp_base */
	0,                             /* tp_dict */
	0,                             /* tp_descr_get */
	0,                             /* tp_descr_set */
	offsetof(Function, dict),      /* tp_dictoffset */
	(initproc)Function::init,      /* tp_init */
	0,                             /* tp_alloc */
	Function::new_,                /* tp_new */
};

}  // namespace (anonymous)


PyMODINIT_FUNC
PyInit__uarray(void)
{
	PyObject* m;

	if (PyType_Ready(&FunctionType) < 0)
		return NULL;

	m = PyModule_Create(&uarray_module);
	if (m == NULL)
		return NULL;

	Py_INCREF(&FunctionType);
	PyModule_AddObject(m, "Function", (PyObject *)&FunctionType);
	return m;
}
