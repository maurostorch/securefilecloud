import aes
import Ecc
import dropbox
import random
import rsa
import shutil
import sys
import tempfile
import time
from os import urandom
from os import rename
from os import remove

app_key = 'digkwqezrgetnmk'
app_secret = 'lyfqfd82znxp99i'

def connect(app_key, app_secret,code):
	flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
	authorize_url = flow.start()
	if not code:
		print "If you don't have a auth code check: "+authorize_url
		code = raw_input("Enter the authorize code: ").strip()
	access_token, user_id = flow.finish(code)
	client = dropbox.client.DropboxClient(access_token)
	print 'account: ', client.account_info()
	return client

def zip(filepath,mode):
	if mode == 'zip':
		with zipfile.ZipFile(filepath+'.zip','w') as zipfile:
			zipfile.write(filepath)
		
	elif mode == 'unzip':
		with zipfile.ZipFile(filepath,'r') as zipfile:
			zipfile

def upload(client, filepath, e, n, mode):
	print 'upload file '+filepath
	t=time.time()
	(e,n,filetmp) = encrypt(filepath, e, n, mode)
	f = open(filetmp)
	client.put_file("/"+filepath,f)
	print str(time.time()-t)+'secs.'

def encrypt(filepath, e, n, mode):
	f = open(filepath,'r')
	data = f.read()
	f.close()
	if mode == 'RSA': secure = rsa.encrypt(data,e,n)
	elif mode == 'AES': secure = aes.encryptAES(e,data.encode('hex'),'CTR')
	elif mode == 'ECC':
		R,secure = e.encrypt(data)
		secure = str(R)+secure
	tmp = tempfile.NamedTemporaryFile(delete=False)
	tmpfile = tmp.name
	tmp.write(secure.decode('hex'))
	tmp.close()
	return (e,n,tmpfile)

def download(client, filepath, d, n, mode):
	print 'downloading file: '+filepath
	t=time.time()
	try:
		f = client.get_file(filepath).read()
	except dropbox.rest.ErrorResponse:
		print 'Error on request'
		return
	out = file('./'+filepath[filepath.rfind('/')+1:],'w')
	out.write(f)
	out.close()
	decrypt(out.name,d,n,mode)
	print str(time.time()-t)+'secs'

def decrypt(filepath, d, n, mode):
	tmp = tempfile.NamedTemporaryFile(delete=False)
	tmp.close()
	shutil.copy(filepath, tmp.name)
	tmp = open(tmp.name)
	c = tmp.read()
	f = open(filepath, 'w')
	if mode == 'RSA': f.write(rsa.decrypt(c,d,n))
	elif mode == 'AES': f.write(aes.decryptAES(d,c[:16],c[16:],'ctr').decode('hex'))
	elif mode == 'ECC':
		R = (c[1:c.index(',')],c[c.index(',')+1:c.index(')')])
		f.write(d.decrypt(R, c[c.index(')')+1:]))
	f.close()
	tmp.close()

def listfiles(client, directory):
	meta = 	client.metadata(directory)
	print meta
	#for item in meta.contents:
	#	print item.path

def loadconf(conffile):
	try:
		conf = open(conffile and conffile or '.securefilecloud.keys')
		mode = conf.readline()
		if mode == 'RSA':
			e = long(conf.readline())
			d = long(conf.readline())
			n = long(conf.readline())
			conf.close()
			return (mode,e,d,n)
		elif mode == 'ECC':
			a = int(conf.readline())
			b = int(conf.readline())
			n = long(conf.readline())
			base = conf.readline().strip()
			base = (int(base[1:base.index(',')]),int(base[base.index(',')+1:len(base)]))
			private = int(conf.readline())
			ecc = Ecc.ECC(a,b,n,base,private)
			return mode,ecc,0,0
		else:
			k = conf.readline()
			conf.close()
			return (mode,k,k,0)
	except IOError:
		print 'No configuration file found.'
		mode = ''
		while str(mode) != "AES" and str(mode) != "RSA" and str(mode) != 'ECC':
			mode = raw_input('Enter an encrypt mode (AES|RSA|ECC): ').strip().upper()
		print 'Generating keys... (It may take a while)'
		f = open('.securefilecloud.keys', 'w')
		f.write(mode+'\n')
		if mode == 'RSA':
			e,d,n = rsa.keys(1024)
			f.write(str(e)+'\n')
			f.write(str(d)+'\n')
			f.write(str(n)+'\n')
			f.close()
			return (mode,e,d,n)
		elif mode == 'ECC':
			mod = Ecc.prime(160)
			ecc = Ecc.ECC(2,2,mod,(5,1),random.randint(2,mod))
			f.write(str(2)+'\n')
			f.write(str(2)+'\n')
			f.write(str(mod)+'\n')
			f.write('(5,1)'+'\n')
			f.write(str(ecc.private)+'\n')
			return mode,ecc,0,0
		else:
			k=urandom(16)
			f.write(k)
			f.close()
			return (mode,k,k,0)

def prompt(client, mode,e,d,n):
	level = '/'
	while True:
		command = raw_input('command: ').strip()
		if command.split(' ')[0] == 'upload':
			upload(client, command.split(' ')[1],e,n,mode)
		elif command.split(' ')[0] == 'download':
			download(client,command.split(' ')[1],d,n,mode)
		elif command.split(' ')[0] == 'list':
			listfiles(client,level)
		elif command.split(' ')[0] == 'cd':
			if command.split(' ')[1] == '..':
				if level == '/': print '/'
				else:
					level = level[:level[:len(level)-1].rfind('/')+1]
			else:
				level = level+command.split(' ')[1]+'/'
		elif command.split(' ')[0] == 'exit':
			print 'Bye!\n\n'
			break
		elif command.split(' ')[0] == 'pwd':
			print level
		elif command.split(' ')[0] == 'help':
			print 'upload <file> - Encrypt and upload a file.'
			print 'download <file> - Download and Decrypt a file'
			print 'list - List DropBox files'
			print 'cd [..|<dirname>] - Change Directory'
			print 'pwd - Print the current dir'
			print 'exit - Quit program'
		else:
			print 'command not found.\n'
			print 'type help for command list'

if __name__ == "__main__":
	#client = connect(app_key,app_secret,'')
	client = ''  #for command line test, uncomment this and comment line before this.
	mode,e,d,n = loadconf('')
	prompt(client,mode,e,d,n)
