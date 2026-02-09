project(
  'uarray',
  'cpp',
  version: run_command(['python', 'tools/write_and_get_version.py'], check: true).stdout().strip(),
  license: 'BSD-3-Clause',
  license_files: ['LICENSE'],
  default_options: 'cpp_std=c++17',
)

py = import('python').find_installation(pure: false)

# Sources variable definitions #

# NOTE: downstream projects may rely on these variable names when vendoring,
# do not change them without consulting with downstream projects
python_sources = {
  'uarray': files(
    'src/uarray/__init__.py',
    'src/uarray/_backend.py',
    'src/uarray/_typing.pyi',
    'src/uarray/_typing.pyi',
    'src/uarray/_version.py',
  )
}

cpp_sources = files(
  'src/_uarray_dispatch.cxx',
)

include_dirs = include_directories('src')

subdir('src/uarray')

# Installation #
foreach prefix, files : python_sources
  py.install_sources(files, subdir: prefix)
endforeach

py.extension_module('_uarray',
  cpp_sources,
  include_directories: include_dirs,
  install: true,
  subdir: 'uarray',
)
