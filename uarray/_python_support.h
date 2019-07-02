#include <Python.h>
#include <utility>
#include <memory>
#include <string>

// PyContextVar is new in python 3.7
#define HAS_CONTEXT_VARS           (PY_VERSION_HEX >= 0x03070000)
// In python 3.7.1, the context vars API was changed to take PyObject *
#define HAS_CONTEXT_VAR_OBJECT_API (PY_VERSION_HEX >= 0x03070100)

/** Handle to a python object that automatically handles DECREFs */
class py_ref
{
	explicit py_ref(PyObject * object): obj(object) {}
public:

	py_ref() noexcept: obj(nullptr) {}
	py_ref(std::nullptr_t) noexcept: py_ref() {}

	py_ref(const py_ref & other) noexcept: obj(other.obj) { Py_XINCREF(obj); }
	py_ref(py_ref && other) noexcept: obj(other.obj) { other.obj = nullptr; }

	static py_ref steal(PyObject * object) { return py_ref(object); }

	static py_ref ref(PyObject * object)
		{
			Py_XINCREF(object);
			return py_ref(object);
		}

	~py_ref(){ Py_XDECREF(obj); }

	py_ref & operator = (const py_ref & other) noexcept
		{
			py_ref(other).swap(*this);
			return *this;
		}

  py_ref & operator = (py_ref && other) noexcept
		{
			py_ref(std::move(other)).swap(*this);
			return *this;
		}

  void swap(py_ref & other) noexcept
    {
      std::swap(other.obj, obj);
    }

  friend void swap(py_ref & a, py_ref & b) noexcept
    {
      a.swap(b);
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

/** Make tuple from variadic set of PyObjects */
template <typename ... Ts>
py_ref py_make_tuple(Ts... args)
{
	using py_obj = PyObject *;
	return py_ref::steal(PyTuple_Pack(sizeof...(args), py_obj{args}...));
}

#if HAS_CONTEXT_VARS


/** Simple wrapper around PyContextVar for 3.7.0 compatibility */
class py_contextref
{
	py_ref var_;


#if HAS_CONTEXT_VAR_OBJECT_API
	using var_type = PyObject *;
	using token_type = PyObject *;
#else
	using var_type = PyContextVar *;
	using token_type = PyContextToken *;
#endif


public:

	class token
	{
		py_ref token_obj_;

    friend py_contextref;
    token(py_ref ref): token_obj_(std::move(ref)) {}

	public:

		explicit operator bool() const
			{
				return !!token_obj_;
			}
	};

	py_contextref(const char * name)
		{
			var_ = py_ref::steal((PyObject*)PyContextVar_New(name, nullptr));
		}

	py_ref get()
		{
			PyObject * value = nullptr;
			if (!PyContextVar_Get((var_type)var_.get(), nullptr, &value))
        return {};
      return py_ref::ref(value);
		}


	token set(py_ref value)
		{
			return { py_ref::steal((PyObject*)PyContextVar_Set(
                               (var_type)var_.get(), value.get())) };
		}

	bool reset(const token & tok)
		{
			return !!PyContextVar_Reset(
				(var_type)var_.get(), (token_type)tok.token_obj_.get());
		}

	explicit operator bool() const
		{
			return !!var_;
		}

};


/** Store a context specific C++ variable */
template <typename T>
class py_contextvar:
  public py_contextref
{

/** Returns a constant string identifier, unique to the type. */
  const char * get_unique_id()
    {
      static const char * id =
        [] {
          static char id_[50];  // Memory address of id_ is the unique value
          snprintf(id_, sizeof(id_), "py_contextvar<%p>", id_);
          return id_;
        }();
      return id;
    }

public:
  using token = py_contextref::token;

	py_contextvar(const char * name): py_contextref(name) {}

	T * get()
		{
			PyObject * cap = py_contextref::get();
			if (!PyCapsule_CheckExact(cap))
				return nullptr;
			return PyCapsule_GetPointer(cap, get_unique_id());
		}


	token set(T value)
		{
			std::unique_ptr<T> obj(new T(std::move(value)));
			py_ref cap = py_ref::steal(
				PyCapsule_New(
					static_cast<void*>(obj.get()), get_unique_id(),
					+[](PyObject * capsule)  // deleter
						 {
							 if (PyCapsule_CheckExact(capsule))
               {
                 delete PyCapsule_GetPointer(
                   capsule, get_unique_id());
               }
						 }));

			if (!cap)
        return {};

      obj.release();  // capsule will handle deletion
      return py_contextref::set(cap);
		}

  using py_contextref::operator bool;
};


#else  // HAS_CONTEXT_VARS


class py_contextref
{
  thread_local py_ref var_;
public:

	class token
	{
		py_ref old_var_;
	public:

		explicit operator bool() const
			{
				return !!old_var_;
			}
	};

	py_contextvar(const char * /*name*/) {}

	py_ref get()
		{
      return var_;
		}

	token set(py_ref value)
		{
      std::swap(var_, value);
      return {value};
		}

	bool reset(const token & tok)
		{
      if (!tok)
        return false;
      var_ = tok.old_var_;
      return true;
		}

	explicit operator bool() const
		{
			return !!var_;
		}
};


/** Store a context specific C++ variable */
template <typename T>
class py_contextvar
{
	thread_local std::shared_ptr<T> var_;

public:

	class token
	{
    std::shared_ptr<T> old_var_;
	public:

		explicit operator bool() const
			{
				return !!old_var_;
			}
	};

	py_contextvar(const char * /*name*/) {}

	T * get()
		{
      return var_.get();
		}


	token set(T value)
		{
      auto new_var = std::make_shared<T>(std::move(value));
      std::swap(var_, new_var);
      return {new_var};
		}

	bool reset(const token & tok)
		{
      if (!tok)
        return false;

      var_ = tok.old_var_;
      return true;
		}

	explicit operator bool() const
		{
			return !!var_;
		}
};


#endif
