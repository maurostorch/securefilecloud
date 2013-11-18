import random
from os import urandom
from gmpy2 import invert
from gmpy2 import mul
from gmpy2 import powmod
import sys

'''
Authors: Endrigo, Mauro

Recieve a number size in bits, i.e. size=1024 bits,
and returns a random prime.
'''

def prime(size):
	r = random.Random()
	while True:
		r.seed(urandom(16))
		p = r.randint(pow(2, size), pow(2, size + 1) - 1)
		if p % 2 != 0 and pow(2, p - 1, p) == 1:
			return p

'''
Euclidian Algorithm by Zorzo
'''

def aeea(x, n):
	if n == 0: return (x, 1, 0)
	(d1, a1, b1) = aeea(n, x % n)
	d = d1
	a = b1
	b = a1 - (x / n) * b1
	return (d, a, b)

'''
Authors: Endrigo, Mauro

The inverse x in Zn
Inverse exists if d in aeea is equals to 1
If a in aeea is negative, the inverse is a + n
else the inverse is a itself.
'''

def inverse(x, n):
	(d, a, b) = aeea(x, n)
	if d != 1: return -1
	if a < 0:
		return a + n
	else:
		return a

'''
Authors: Endrigo, Mauro

Key generator
For a give key size it calculate the e(ncrypt) and d(ecrypt) RSA values
The thirdy value is the n (value that could be factored in two "big" prime numbers)
'''

def keys(bitsize):
	p = prime(bitsize)
	q = prime(bitsize)
	n = p * q
	phin = (p - 1) * (q - 1)
	r = random.Random(urandom(bitsize))
	e = phin
	while e > 1:
		d = inverse(e, phin)
		if d != 1 and d >= 0 and d != e:
			if r.sample([0, 1], 1)[0] == 1:
				break
		e = e - 1
	return (e, d, n)

'''
Authors: Endrigo, Mauro
RSA Encrypt algorithm
'''

def encrypt(m, e, n):
	c = []
	for l in m:
		c.append(hex(powmod(ord(l), e, n)))
	return ''.join(c)

'''
Authors: Endrigo, Mauro
RSA Decrypt algorithm
'''

def decrypt(c, d, n):
	m = []
	for l in c.split('0x'):
		if len(l) > 0: m.append(chr(int(powmod(int("0x" + l, 0), d, n))))
	return ''.join(m)

'''
Authors: Endrigo, Mauro

Calculate the Discret Log for
p=modulus, g=some value to the power of x is equals to h, h= some value.
The result is the x value
-- Result:
By using gmpy2 lib the execution took 1m25.768s. 
By using the inverse function above in this file and standard math, it took 14m58.007s.
'''

def dlog(p, g, h):
	hashleft = {}
	''' A loop to populate the hashtable that have de left side values '''
	for i in range(0, 2 ** 20):
		d = powmod(g, i, p)
		inv = invert(d, p)
		v = mul(h, inv)
		hashleft[v % p] = i
	''' A loop to find the value which match with a value in the hashtable'''
	for i in range(0, 2 ** 20):
		rs = pow(g, (2 ** 20) * i, p)
		if rs in hashleft:
			break
	''' x is given by: x=x0.B+x1 '''
	x = ((i * 2 ** 20) + hashleft[rs]) % p
	return x

'''
Program call: rsa.py bitsize - Return the keys, ie: python rsa.py 1024 
ras.py p g h - Return the Discret log, ie: python rsa.py 35 3 8
'''
if __name__ == "__main__":
	if sys.argv[2]:
		print str(dlog(long(sys.argv[1]), long(sys.argv[2]), long(sys.argv[3])))
	else:
		print str(keys(int(sys.argv[1])))
