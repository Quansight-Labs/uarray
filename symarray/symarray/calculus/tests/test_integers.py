from symarray.calculus.integers import Integer, Int

def test_integer():
    a = Integer('a')
    b = Integer('b')
    c = Integer('c')
    d = Integer('d')
    assert str(a) == 'a'
    assert str(+a) == 'a'
    assert str(a + b) == 'a + b'
    assert str(a + 1) == '1 + a'
    assert str(1 + a) == '1 + a'
    assert str(a + 0) == 'a'
    assert str(a + a) == '2 * a'
    assert str(a + a + a) == '3 * a'
    assert str(a + a + b) == '2 * a + b'
    assert str(a + b + a) == '2 * a + b'
    assert str ((a+b) + (c)) == 'a + b + c'
    assert str ((a) + (b+c)) == 'a + b + c'
    assert str ((a+b) + (c+d)) == 'a + b + c + d'
    assert str ((a+b) + (c+c)) == 'a + b + 2 * c'
    assert str ((a+a) + (c+d)) == '2 * a + c + d'
    assert str ((a+b) + 2) == '2 + a + b'

    assert str(-a) == '-a'    
    assert str(a-a) == '0'
    assert str(a-b) == 'a - b'
    assert str ((a+b) - 2) == '-2 + a + b',repr((a+b)-2)
    assert str (2 + (a+b)) == '2 + a + b'
    assert str (-2 + (a+b)) == '-2 + a + b'
    assert str ((a+b) - (c+d)) == 'a + b - c - d'
    assert str ((a+b) - (c+c)) == 'a + b - 2 * c'
    assert str (a - (c+d)) == 'a - c - d'
    assert str ((a+b) - (c+c-d)) == 'a + b - 2 * c + d'

    assert str (a * 2) == '2 * a'
    assert str (2 * a) == '2 * a'
    assert str (-2 * a) == '-2 * a'
    assert str (1 * a) == 'a'
    assert str (-1 * a) == '-a'
    assert str (a * 2 * 3) == '6 * a'
    assert str (2 * a * 3) == '6 * a'
    
    assert str (a * b) == 'a * b'
    assert str (a * a) == 'a ** 2'
    assert str (a / a) == '1'
    assert str (a ** 2) == 'a ** 2'
    assert str (a * b * 2) == '2 * a * b'
    assert str (2 * a * b) == '2 * a * b'
    assert str (a * b * c) == 'a * b * c'
    assert str (a * (b * c)) == 'a * b * c'

    assert str ((a+b)*c) == 'a * c + b * c'
    assert str (c*(a+b)) == 'a * c + b * c'
    assert str ((a+b)*(c+d)) == 'a * c + a * d + b * c + b * d'
    assert str ((a+b)*(a+b)) == '2 * a * b + a ** 2 + b ** 2'
    assert str ((a+b)**2) == '2 * a * b + a ** 2 + b ** 2'
    assert str ((a+b)**2*(a+b)) == '3 * a * b ** 2 + 3 * a ** 2 * b + a ** 3 + b ** 3'
    assert str ((a+b)*(a+b)**2) == '3 * a * b ** 2 + 3 * a ** 2 * b + a ** 3 + b ** 3'
    assert str ((a+b)**3) == '3 * a * b ** 2 + 3 * a ** 2 * b + a ** 3 + b ** 3'
    
    assert str ((a+b)*2) == '2 * a + 2 * b'
    assert str ((a+b)*c*2) == '2 * a * c + 2 * b * c'
    assert str ((a*b)*2) == '2 * a * b'

    assert str (Int(2)*(a*b)) == '2 * a * b'

    assert str ((a*b)**2) == 'a ** 2 * b ** 2'
    assert str ((a*b)**(Int(1)/2)) == '(a * b) ** 1/2'

def test_number():
    n = Int(2)
    m = Int(3)

    assert str(+n)=='2'
    assert str(-n)=='-2'
    
    assert str(n+m)=='5'
    assert str(n+3)=='5'
    assert str(2+m)=='5'

    assert str(n-m)=='-1'
    assert str(n-3)=='-1'
    assert str(2-m)=='-1'

    assert str(n*m)=='6'
    assert str(n*3)=='6'
    assert str(2*m)=='6'
    
    assert str(n/m)=='2/3'
    assert str(n/3)=='2/3'
    assert str(2/m)=='2/3'

    assert str(n**m)=='8'
    assert str(n**3)=='8'
    assert str(2**m)=='8'

def test_number_calculus():
    n = Int(2)
    a = Integer('a')
    b = Integer('b')
    
    assert str(+a)=='a'
    assert str(-a)=='-a'
    assert str(a + n)=='2 + a'
    assert str(a + 2)=='2 + a'
    assert str(n + a)=='2 + a'
    assert str(2 + a)=='2 + a'
    
    assert str(a - n)=='-2 + a'
    assert str(a - 2)=='-2 + a'
    assert str(n - a)=='2 - a'
    assert str(2 - a)=='2 - a'

    
    assert str(a * n)=='2 * a',repr(a * n)
    assert str(a * 2)=='2 * a'
    assert str(n * a)=='2 * a'
    assert str(2 * a)=='2 * a'

    assert str(a / n)=='1/2 * a'
    assert str(a / 2)=='1/2 * a'

    assert str(a ** n)=='a ** 2'
    assert str(a ** 2)=='a ** 2'
    assert str(n ** a)=='2 ** a'
    assert str(2 ** a)=='2 ** a'

    c = a + a
    assert str(+c) == '2 * a'
    assert str(-c) == '-2 * a'
    assert str(c + n) == '2 + 2 * a'
    assert str(n + c) == str (c+n)
    assert str(c + 2) == str (c+n)
    assert str(2 + c) == str (c+n)
    assert str(c - n) == '-2 + 2 * a'
    assert str(c - 2) == str (c-n)
    assert str(n - c) == '2 - 2 * a'
    assert str(2 - c) == str (n-c)

    assert str(c * n) == '4 * a'
    assert str(c * 2) == str(c * n)
    assert str(n * c) == str(c * n)
    assert str(2 * c) == str(c * n)

    assert str(c / n) == 'a'
    assert str(c / 2) == str(c / n)

    assert str(n / c) in ['a ** -1', 'a ** (-1)'], repr(n/c)
    assert str(2 / c) == str(n / c)
    
    assert str(c ** n) == '4 * a ** 2'
    assert str(c ** 2) == str(c ** n)

    assert str(n ** c) == '2 ** (2 * a)'
    assert str(n ** c) == str(2 ** c)

    c = a + b
    assert str(+c) == 'a + b'
    assert str(-c) == '-a - b'
    assert str(c + n) == '2 + a + b'
    assert str(n + c) == str(c + n)
    assert str(c + 2) == str(c + n)
    assert str(2 + c) == str(c + n)
    assert str(c - n) == '-2 + a + b'
    assert str(c - 2) == str(c - n)
    assert str(n - c) == '2 - a - b'
    assert str(2 - c) == str(n - c)

    assert str(c * n) == '2 * a + 2 * b'
    assert str(c * 2) == str(c * n)
    assert str(n * c) == str(c * n)
    assert str(2 * c) == str(c * n)

    assert str(c / n) == '1/2 * a + 1/2 * b'
    assert str(c / 2) == str(c / n)
    assert str(n / c) in ['2 * (a + b) ** -1', '2 * (a + b) ** (-1)'],repr((n/c))
    assert str(2 / c) == str(n / c)

    assert str(c ** n) == '2 * a * b + a ** 2 + b ** 2'
    assert str(c ** 2) == str(c ** n)

    assert str(n ** c) == '2 ** (a + b)'
    assert str(n ** c) == str(2 ** c)

    c = a * b
    assert str(+c) == 'a * b'
    assert str(-c) == '-a * b'
    assert str(c + n) == '2 + a * b'
    assert str(c + 2) == str(c + n)
    assert str(n + c) == str(c + n)
    assert str(2 + c) == str(c + n)

    assert str(c - n) == '-2 + a * b'
    assert str(c - 2) == str(c - n)
    assert str(n - c) == '2 - a * b'
    assert str(2 - c) == str(n - c)

    assert str(c * n) == '2 * a * b'
    assert str(c * 2) == str(c * n)
    assert str(n * c) == str(c * n)
    assert str(2 * c) == str(c * n)

    assert str(c / n) == '1/2 * a * b'
    assert str(c / 2) == str(c / n)
    assert str(n / c) in ['2 * a ** -1 * b ** -1', '2 * a ** (-1) * b ** (-1)']
    assert str(2 / c) == str(n / c)

    assert str (c ** n) == 'a ** 2 * b ** 2'
    assert str (c ** 2) == str (c**n)
    assert str (n ** c) == '2 ** (a * b)'
    assert str (2 ** c) == str (n ** c)

    c = a * a
    assert str(+c) == 'a ** 2'
    assert str(-c) == '-a ** 2'
    assert str(c + n) == '2 + a ** 2'
    assert str(c + 2) == str(c + n)
    assert str(n + c) == str(c + n)
    assert str(2 + c) == str(c + n)

    assert str(c - n) == '-2 + a ** 2'
    assert str(c - 2) == str(c - n)
    assert str(n - c) == '2 - a ** 2'
    assert str(2 - c) == str(n - c)

    assert str(c * n) == '2 * a ** 2'
    assert str(c * 2) == str(c * n)
    assert str(n * c) == str(c * n)
    assert str(2 * c) == str(c * n)

    assert str(c / n) == '1/2 * a ** 2'
    assert str(c / 2) == str(c / n)
    assert str(n / c) in ['2 * a ** -2', '2 * a ** (-2)']
    assert str(2 / c) == str(n / c)

    assert str (c ** n) == 'a ** 4'
    assert str (c ** 2) == str (c**n)
    assert str (n ** c) == '2 ** (a ** 2)'
    assert str (2 ** c) == str (n ** c)

def test_integer_calculus():
    a = Integer('a')
    b = Integer('b')
    c = Integer('c')

    assert str(a + b) == 'a + b'
    assert str(a + a) == '2 * a'
    assert str(a - b) == 'a - b'
    assert str(a - a) == '0'

    assert str(a * b) == 'a * b'
    assert str(a * a) == 'a ** 2'
    assert str(a / b) in ['a * b ** -1', 'a * b ** (-1)']
    assert str(b / a) in ['a ** -1 * b', 'a ** (-1) * b']

    assert str(a ** b) == 'a ** b',repr(a ** b)

    x = b + c
    assert str(a + x) == 'a + b + c'
    assert str(x + a) == str(a + x)
    assert str(a - x) == 'a - b - c'
    assert str(x - a) == '-a + b + c'
    assert str(a * x) == 'a * b + a * c'
    assert str(x * a) == str(a * x)
    assert str(a / x) in ['a * (b + c) ** -1', 'a * (b + c) ** (-1)']
    assert str (x / a) in ['a ** -1 * b + a ** -1 * c', 'a ** (-1) * b + a ** (-1) * c']
    assert str(a ** x) == 'a ** (b + c)'
    assert str(x ** a) == '(b + c) ** a'

    x = b + b
    assert str(a + x) == 'a + 2 * b'
    assert str(x + a) == str(a + x)
    assert str(a - x) == 'a - 2 * b'
    assert str(x - a) == '-a + 2 * b'
    assert str(a * x) == '2 * a * b'
    assert str(x * a) == str(a * x)
    assert str(a / x) in ['1/2 * a * b ** -1', '1/2 * a * b ** (-1)']
    assert str (x / a) in ['2 * a ** -1 * b', '2 * a ** (-1) * b']
    assert str(a ** x) == 'a ** (2 * b)'
    assert str(x ** a) == '(2 * b) ** a'

    x = b * c
    assert str(a + x) == 'a + b * c'
    assert str(x + a) == str(a + x)
    assert str(a - x) == 'a - b * c'
    assert str(x - a) == '-a + b * c'
    assert str(a * x) == 'a * b * c'
    assert str(x * a) == str(a * x)
    assert str(a / x) in ['a * b ** -1 * c ** -1', 'a * b ** (-1) * c ** (-1)']
    assert str (x / a) in ['a ** -1 * b * c', 'a ** (-1) * b * c']
    assert str(a ** x) == 'a ** (b * c)'
    assert str(x ** a) == '(b * c) ** a'

    x = b * b
    assert str(a + x) == 'a + b ** 2'
    assert str(x + a) == str(a + x)
    assert str(a - x) == 'a - b ** 2'
    assert str(x - a) == '-a + b ** 2'
    assert str(a * x) == 'a * b ** 2'
    assert str(x * a) == str(a * x)
    assert str(a / x) in ['a * b ** -2', 'a * b ** (-2)']
    assert str (x / a) in ['a ** -1 * b ** 2', 'a ** (-1) * b ** 2']
    assert str(a ** x) == 'a ** (b ** 2)'
    assert str(x ** a) in ['b ** (2 * a)', '(b ** 2) ** a']

def test_terms_calculus():
    a = Integer('a')
    b = Integer('b')
    c = Integer('c')
    d = Integer('d')

    x = a + b
    assert str (x + x) == '2 * a + 2 * b'
    assert str (x - x) == '0'
    assert str (x * x) == '2 * a * b + a ** 2 + b ** 2'
    assert str (x / x) == '1'
    assert str (x ** x) == '(a + b) ** (a + b)'

    y = c + d
    assert str (x + y) == 'a + b + c + d'
    assert str (y + x) == str (x + y)
    assert str (x - y) == 'a + b - c - d'
    assert str (y - x) == '-a - b + c + d'
    assert str (x * y) == 'a * c + a * d + b * c + b * d'
    assert str (x / y) in ['(a + b) * (c + d) ** -1', '(a + b) * (c + d) ** (-1)', 'a * (c + d) ** (-1) + b * (c + d) ** (-1)']
    assert str (x ** y) == '(a + b) ** (c + d)'

    y = c * d
    assert str (x + y) == 'a + b + c * d'
    assert str (y + x) == str (x + y)
    assert str (x - y) == 'a + b - c * d'
    assert str (y - x) == '-a - b + c * d'
    assert str (x * y) == 'a * c * d + b * c * d'
    assert str (x / y) in ['a * c ** -1 * d ** -1 + b * c ** -1 * d ** -1', 'a * c ** (-1) * d ** (-1) + b * c ** (-1) * d ** (-1)']
    assert str (x ** y) == '(a + b) ** (c * d)'
    assert str (y ** x) == '(c * d) ** (a + b)'

    y = c * c
    assert str (x + y) == 'a + b + c ** 2'
    assert str (y + x) == str (x + y)
    assert str (x - y) == 'a + b - c ** 2'
    assert str (y - x) == '-a - b + c ** 2'
    assert str (x * y) == 'a * c ** 2 + b * c ** 2'
    assert str (x / y) in ['a * c ** -2 + b * c ** -2', 'a * c ** (-2) + b * c ** (-2)']
    assert str (x ** y) == '(a + b) ** (c ** 2)'
    assert str (y ** x) in ['c ** (2 * a + 2 * b)', '(c ** 2) ** (a + b)']

    x = a + a
    y = c + d
    assert str (x + x) == '4 * a'
    assert str (x - x) == '0'
    assert str (x * x) == '4 * a ** 2'
    assert str (x / x) == '1',repr((x / x, x, (1/x)))
    assert str (x ** x) == '(2 * a) ** (2 * a)'

    assert str (x + y) == '2 * a + c + d'
    assert str (y + x) == str (x + y)
    assert str (x - y) == '2 * a - c - d'
    assert str (y - x) == '-2 * a + c + d'
    assert str (x * y) == '2 * a * c + 2 * a * d'
    assert str (x / y) in ['2 * a * (c + d) ** -1', '2 * a * (c + d) ** (-1)']
    assert str (x ** y) == '(2 * a) ** (c + d)'
    assert str (y ** x) == '(c + d) ** (2 * a)'
    
    y = c + c
    assert str (x + y) == '2 * a + 2 * c'
    assert str (y + x) == str (x + y)
    assert str (x - y) == '2 * a - 2 * c'
    assert str (y - x) == '-2 * a + 2 * c'
    assert str (x * y) == '4 * a * c'
    assert str (x / y) in ['a * c ** -1', 'a * c ** (-1)']
    assert str (x ** y) == '(2 * a) ** (2 * c)'
    assert str (y ** x) == '(2 * c) ** (2 * a)'

    y = c * d
    assert str (x + y) == '2 * a + c * d'
    assert str (y + x) == str (x + y)
    assert str (x - y) == '2 * a - c * d'
    assert str (y - x) == '-2 * a + c * d'
    assert str (x * y) == '2 * a * c * d'
    assert str (x / y) in ['2 * a * c ** -1 * d ** -1', '2 * a * c ** (-1) * d ** (-1)']
    assert str (x ** y) == '(2 * a) ** (c * d)'
    assert str (y ** x) == '(c * d) ** (2 * a)'

    y = c * c
    assert str (x + y) == '2 * a + c ** 2'
    assert str (y + x) == str (x + y)
    assert str (x - y) == '2 * a - c ** 2'
    assert str (y - x) == '-2 * a + c ** 2'
    assert str (x * y) == '2 * a * c ** 2'
    assert str (x / y) in ['2 * a * c ** -2', '2 * a * c ** (-2)']
    assert str (x ** y) == '(2 * a) ** (c ** 2)'
    assert str (y ** x) in ['c ** (4 * a)','(c ** 2) ** (2 * a)']

def test_factors_calculus ():
    a = Integer('a')
    b = Integer('b')
    c = Integer('c')
    d = Integer('d')

    x = a * b
    assert str (x + x) == '2 * a * b'
    assert str (x - x) == '0'
    assert str (x * x) == 'a ** 2 * b ** 2'
    assert str (x / x) == '1'
    assert str (x ** x) == '(a * b) ** (a * b)'
    
    y = c * d
    assert str (x + y) == 'a * b + c * d'
    assert str (y + x) == str (x + y)
    assert str (x - y) == 'a * b - c * d'
    assert str (y - x) == '-a * b + c * d'
    assert str (x * y) == 'a * b * c * d'
    assert str (x / y) in ['a * b * c ** -1 * d ** -1', 'a * b * c ** (-1) * d ** (-1)']
    assert str (x ** y) == '(a * b) ** (c * d)'

    y = c * c
    assert str (x + y) == 'a * b + c ** 2'
    assert str (y + x) == str (x + y)
    assert str (x - y) == 'a * b - c ** 2'
    assert str (y - x) == '-a * b + c ** 2'
    assert str (x * y) == 'a * b * c ** 2'
    assert str (y * x) == str(x * y)
    assert str (x / y) in ['a * b * c ** -2', 'a * b * c ** (-2)']
    assert str (y / x) in ['a ** -1 * b ** -1 * c ** 2', 'a ** (-1) * b ** (-1) * c ** 2']
    assert str (x ** y) in ['(a * b) ** (c ** 2)', '(a * b) ** c ** 2']
    assert str (y ** x) in ['c ** (2 * a * b)', '(c ** 2) ** (a * b)', 'c ** 2 ** (a * b)',
    ]

    x = a * a
    assert str (x + x) == '2 * a ** 2'
    assert str (x - x) == '0'
    assert str (x * x) == 'a ** 4'
    assert str (x / x) == '1'
    assert str (x ** x) in ['a ** (2 * a ** 2)', '(a ** 2) ** (a ** 2)', 'a ** 2 ** a ** 2',
    ]
    
    y = c * d
    assert str (x + y) == 'a ** 2 + c * d'
    assert str (y + x) == str (x + y)
    assert str (x - y) == 'a ** 2 - c * d'
    assert str (y - x) == '-a ** 2 + c * d'
    assert str (x * y) == 'a ** 2 * c * d'
    assert str (x / y) in ['a ** 2 * c ** -1 * d ** -1', 'a ** 2 * c ** (-1) * d ** (-1)']
    assert str (x ** y) in ['a ** (2 * c * d)', '(a ** 2) ** (c * d)', 'a ** 2 ** (c * d)',
    ]
    y = c * c
    assert str (x + y) == 'a ** 2 + c ** 2'
    assert str (y + x) == str (x + y)
    assert str (x - y) == 'a ** 2 - c ** 2'
    assert str (y - x) == '-a ** 2 + c ** 2'
    assert str (x * y) == 'a ** 2 * c ** 2'
    assert str (y * x) == str(x * y)
    assert str (x / y) in ['a ** 2 * c ** -2', 'a ** 2 * c ** (-2)']
    assert str (y / x) in ['a ** -2 * c ** 2', 'a ** (-2) * c ** 2']
    assert str (x ** y) in ['a ** (2 * c ** 2)', '(a ** 2) ** (c ** 2)', 'a ** 2 ** c ** 2',
    ]
    assert str (y ** x) in ['c ** (2 * a ** 2)','(c ** 2) ** (a ** 2)','c ** 2 ** a ** 2',
    ]


