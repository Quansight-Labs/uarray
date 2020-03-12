# Contributing

Contribution to `uarray` are welcome and appreciated. Contributions can take the form of bug reports, documentation, code, and more.

## Getting the code

Make a fork of the main [uarray repository](https://github.com/Quansight-Labs/uarray) and clone the fork:

```
git clone https://github.com/<your-github-username>/uarray
```

## Install

`uarray` and all development dependencies can be installed via:

```
pip install -e ".[all]"
```

Note that uarray supports Python versions >= 3.5. If you're running `conda` and would prefer to have dependencies
pulled from there, use

```
conda env create -f .conda/environment.yml
```

This will create an environment named `uarray` which you can use for development.

## Testing

Tests can be run from the main uarray directory as follows:

```
pytest --pyargs uarray
```

To run a subset of tests:

```
pytest uarray.tests.test_backend
```
