#include <Python.h>
#include <utility>
#include <memory>
#include <string>

// PyContextVar is new in python 3.7
#define HAS_CONTEXT_VARS           (0)  // Context var wrapper doesn't work?
//#define HAS_CONTEXT_VARS           (PY_VERSION_HEX >= 0x03070000)
// In python 3.7.1, the context vars API was changed to take PyObject *
#define HAS_CONTEXT_VAR_OBJECT_API (PY_VERSION_HEX >= 0x03070100)

/** Handle to a python object that automatically handles DECREFs */
class py_ref
{
  explicit py_ref(PyObject * object): obj_(object) {}
public:

  py_ref() noexcept: obj_(nullptr) {}
  py_ref(std::nullptr_t) noexcept: py_ref() {}

  py_ref(const py_ref & other) noexcept: obj_(other.obj_) { Py_XINCREF(obj_); }
  py_ref(py_ref && other) noexcept: obj_(other.obj_) { other.obj_ = nullptr; }

  static py_ref steal(PyObject * object) { return py_ref(object); }

  static py_ref ref(PyObject * object)
    {
      Py_XINCREF(object);
      return py_ref(object);
    }

  ~py_ref(){ Py_XDECREF(obj_); }

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
      std::swap(other.obj_, obj_);
    }

  friend void swap(py_ref & a, py_ref & b) noexcept
    {
      a.swap(b);
    }

  explicit operator bool () const { return obj_ != nullptr; }

  operator PyObject* () const { return get(); }

  PyObject * get() const { return obj_; }
  PyObject * release()
    {
      PyObject * t = obj_;
      obj_ = nullptr;
      return t;
    }
  void reset()
    {
      Py_CLEAR(obj_);
    }
private:
  PyObject * obj_;
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

    token() = default;

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
  static const char * get_unique_id()
    {
      static const char * id =
        [] {
          static char id_[50];  // Memory address of id_ is unique
          snprintf(id_, sizeof(id_), "py_contextvar<%p>", id_);
          return id_;
        }();
      return id;
    }

  py_ref make_capsule(std::unique_ptr<T> obj)
    {
      auto cap = py_ref::steal(
        PyCapsule_New(
          static_cast<void*>(obj.get()), get_unique_id(),
          +[](PyObject * capsule)  // deleter
             {
               if (PyCapsule_CheckExact(capsule))
               {
                 delete static_cast<T*>(PyCapsule_GetPointer(
                                          capsule, get_unique_id()));
               }
             }));

      if (cap)
        obj.release();  // capsule will handle deletion

      return cap;
    }

public:
  using token = py_contextref::token;

  py_contextvar(): py_contextref(get_unique_id())
    {
      py_ref cap = make_capsule(std::unique_ptr<T>(new T));
      if (!cap)
        return;
      py_contextref::set(std::move(cap));
    }

  T * get()
    {
      PyObject * cap = py_contextref::get();
      if (!cap)
        return nullptr;
      if (!PyCapsule_CheckExact(cap))
      {
        PyErr_SetString(PyExc_TypeError, "Context var contained incorrect type");
        return nullptr;
      }
      return static_cast<T*>(PyCapsule_GetPointer(cap, get_unique_id()));
    }


  token set(T value)
    {
      py_ref cap = make_capsule(std::unique_ptr<T>(new T(std::move(value))));

      if (!cap)
        return {};

      return py_contextref::set(std::move(cap));
    }

  using py_contextref::operator bool;
};


#else  // HAS_CONTEXT_VARS


/** Wrap a C++ variable while imitating the py_contextvar API

This version isn't actually context local at all.
*/
template <typename T>
class py_contextvar
{
  std::shared_ptr<T> var_;

public:

  class token
  {
    std::shared_ptr<T> old_var_;
    friend py_contextvar;
    token(std::shared_ptr<T> var): old_var_(std::move(var)) {}

  public:
    token() = default;

    explicit operator bool() const
      {
        return !!old_var_;
      }
  };

  py_contextvar():
    var_(std::make_shared<T>())
    {}

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
