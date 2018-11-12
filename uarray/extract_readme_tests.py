# inspired by https://github.com/boxed/pytest-readme/blob/752508892fa0c39a02ca5a2ef621a30282914f5b/pytest_readme/__init__.py
with open('test_readme.py', 'w') as out, open('README.md') as readme:
    in_code = False
    for i, line in enumerate(readme.readlines()):
        if not in_code and line.strip() == '```python':
            in_code = True
        elif in_code and line.strip() == '```':
            in_code = False
        elif in_code:
            out.write(line)
