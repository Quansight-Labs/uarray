cmake_minimum_required(VERSION 3.15...3.30)

project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module ${SKBUILD_SABI_COMPONENT})

if(NOT "${SKBUILD_SABI_VERSION}" STREQUAL "" AND Python_INTERPRETER_ID STREQUAL Python)
    python_add_library(_uarray MODULE WITH_SOABI USE_SABI ${SKBUILD_SABI_VERSION}
        small_dynamic_array.h
        vectorcall.h
        vectorcall.cxx
        _uarray_dispatch.cxx
    )
else()
    python_add_library(_uarray MODULE WITH_SOABI
        small_dynamic_array.h
        vectorcall.h
        vectorcall.cxx
        _uarray_dispatch.cxx
    )
endif()

set_property(TARGET _uarray PROPERTY CXX_STANDARD 17)
install(TARGETS _uarray LIBRARY DESTINATION uarray)
