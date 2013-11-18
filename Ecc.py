import random
from os import urandom
from fractions import gcd
from gmpy2 import invert
import sys
import hashlib 
from Crypto.Cipher import AES
from Crypto import Random

BLOCK_SIZE = 16

#Generate a radom prime number 
def prime(size):
	r = random.Random()
	while True:
		r.seed(urandom(16))
		p = r.randint(pow(2, size), pow(2, size + 1) - 1)
		if p % 2 != 0 and pow(2, p - 1, p) == 1:
			return p

class ECC(object):

	def __init__(self,a=-1,b=-1,mod=-1,basepoint=(-1,-1),private=-1,pk=(-1,-1)):
		if a == -1 and b == -1 and mod == -1:
			self.curvegeneration()
		else:
			self.a = a
			self.b = b
			self.mod = mod
			self.basepoint = basepoint
			self.private = private
		if private == -1 or pk == (-1,-1):
			self.keypair()
		else:
			self.pk = pk
	
	def pointlist(self):
		pts = []
		pts.append((self.basepoint[0],self.basepoint[1]))
		i = 2 #starts from 2P until infinite point raised from PointGenerator
		while True:
			try:
				pts.append(self.PointMultiplication(x,y,i))
				i = i + 1
			except:
				break
		return pts

	def pointmultiplication(self,x,y,i):
		p=(x,y)
		pnew = None
		try:
			for bpos in range(len(bin(i))-3):
				pnew = self.pointdoubling(p[0],p[1])
				if bin(i)[bpos+3] == '1' :
					pnew = self.pointaddition(pnew[0],pnew[1],x,y)
				p = pnew
		except:
			raise
		return pnew	

	def pointaddition(self,x1,y1,x2,y2):
		try:
			s1 = ((y2-y1)%self.mod)
			s2 = int(invert(x2-x1,self.mod))
			s = (s1 * s2) % self.mod
			x3 = (pow(s,2) - x1 - x2) % self.mod
			y3 = (s * (x1-x3) - y1) % self.mod
			return (x3,y3)
		except:
			raise

	def pointdoubling(self,x1,y1):
		try:
			s1 = (3 * pow(x1,2) + self.a) % self.mod
			s2 = int(invert(2*y1,self.mod))
			s = (s1 * s2) % self.mod
			x3 = (pow(s,2) - x1 - x1) % self.mod
			y3 = (s * (x1-x3) - y1) % self.mod
			return (x3,y3)
		except:
			raise	

	#Verify if a point is on curve
	def ispointoncurve(self,x,y):
		pc = ((pow(x,3) + (self.a * x) + self.b)) % self.mod
		p  = pow(y,2) 
		return p == pc

	#Generate a Eliptic Curve
	def curvegenerate(self,bitsize):
		while True:
			self.mod=prime(bitsize)
			self.a=random.randint(100,1000)
			self.b=random.randint(100,1000)
			pts=[]
			for x in range(1000):
				for y in range(1000):
					if ispointoncurve(x,y,self.a,self.b,self.mod):
						pts.append((x,y))
			if pts.__len__() > 0:
				break
		self.basepoint = pts[0]
		return pts

	#Generate a KeyPair
	def keypair(self):
		while True:
			try:
				self.private = self.private == None and random.randint(1,self.mod) or self.private
				self.pk = self.pointmultiplication(self.basepoint[0],self.basepoint[1],self.private)
				break
			except:
				pass
	
	#Encrypt using AES
	def encrypt(self,plaintext):
		#generate a radom integer number
		r = random.randint(1,self.mod)
		#generate R returns aside the ciphertext
		R = self.pointmultiplication(self.basepoint[0],self.basepoint[1],r)
		#generate S - Point which x is the syncronous key for AES
		S = self.pointmultiplication(self.pk[0],self.pk[1],r)
		#generate K - K is a hash SHA256 of S.x
		K = hashlib.sha256(str(S[0])).digest()
		iv = Random.get_random_bytes(16)
		engine = AES.new(K, AES.MODE_CBC,iv)
		#MODE_C = obs.Encrypt(plaintext)
		fill =  (BLOCK_SIZE - (len(plaintext) % BLOCK_SIZE)) * chr(BLOCK_SIZE - (len(plaintext) % BLOCK_SIZE))
		C = iv + engine.encrypt(plaintext + fill) 
		return(R,C)

	#Decrypt Using AES
	def decrypt(self,R,ciphertext):
		#generate a S
		S = self.pointmultiplication(R[0],R[1],self.private)
		K = hashlib.sha256(str(S[0])).digest()
		iv = ciphertext[:16]
		ciphertext = ciphertext[16:]
		engine = AES.new(K, AES.MODE_CBC,iv)
		pt = engine.decrypt(ciphertext)
		return pt[0:-ord(pt[-1])]

if __name__ == "__main__":
	print "Elliptical Curve Cryptography Diffie-Hellmann"
	p = prime(160) #for now, 160 bit long modulus still secure
	ecc = ECC(2,2,p,(5,1)) #setting just the public key for encrypting process
	print "PK = " + str(ecc.pk)
	print " ------- ENCRYPT -------"
	R,C = ecc.encrypt("Cryptography test!")
	print "done."
	print " ------- DECRYPT -------"	
	print "R = " + str(R)
	ecc2 = ECC(2,2,p,(5,1),ecc.private) # setting just the private key for decryption process
	print ecc2.decrypt(R,C)
