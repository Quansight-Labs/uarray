project(
  'uarray',
  'cpp',
  version: run_command(['tools/gitversion.py'], check: true).stdout().strip(),
  license: 'BSD-3-Clause',
  license_files: ['LICENSE'],
  default_options: 'cpp_std=c++17',
)

fs = import('fs')
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
    'src/uarray/_version.pyi',
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

uarray_dir = py.get_install_dir() / 'uarray'
# Generate _version.py for sdist
meson.add_dist_script(
   ['tools/gitversion.py']
)
if not fs.exists('_version.py')
  custom_target(
    'generate-version',
    install: true,
    build_always_stale: true,
    build_by_default: true,
    output: '_version.py',
    input: 'tools/gitversion.py',
    command: ['tools/gitversion.py'],
    install_dir: uarray_dir,
    install_tag: 'python-runtime',
  )
else
  # When building from sdist, _version.py exists and should be included
  py.install_sources(['_version.py'], subdir : 'uarray')
endif
