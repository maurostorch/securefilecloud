from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto import Random
from os import urandom

BLOCK_SIZE = 16

def encryptAES(key,pt,mode):
	mode = mode=='CBC' and AES.MODE_CBC or AES.MODE_CTR
	iv = Random.get_random_bytes(BLOCK_SIZE)
	engine = mode == AES.MODE_CBC and AES.new(key,mode,iv) or AES.new(key,mode,counter = Counter.new(BLOCK_SIZE*8,initial_value=long(iv.encode('hex'),16)))
	fill= mode==AES.MODE_CBC and (BLOCK_SIZE-(len(pt)%BLOCK_SIZE)) * chr(BLOCK_SIZE-(len(pt)%BLOCK_SIZE)) or ''
	r = engine.encrypt(pt+fill)
	return iv.encode('hex')+(r).encode('hex')
def decryptAES(key,iv,ct,mode):
	mode = mode=='CBC' and AES.MODE_CBC or AES.MODE_CTR
	ctr = Counter.new(BLOCK_SIZE * 8,initial_value=long(iv.encode('hex'),16))
	engine = mode == AES.MODE_CBC and AES.new(key,mode,iv) or AES.new(key,mode,counter = ctr)
	fill= mode==AES.MODE_CBC and (BLOCK_SIZE-len(ct)%BLOCK_SIZE) * chr(BLOCK_SIZE-len(ct)%BLOCK_SIZE) or ''
	return engine.decrypt(ct+fill)[:ct.__len__()]

