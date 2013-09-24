import aes
import dropbox
import rsa
import shutil
import sys
import tempfile
import time
from os import urandom

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
	tmp = tempfile.NamedTemporaryFile(delete=False)
	tmpfile = tmp.name
	tmp.write(secure.decode('hex'))
	tmp.close()
	return (e,n,tmpfile)

def download(client, filepath, d, n, mode):
	print 'downloading file: '+filepath
	t=time.time()
	out = file('./'+filepath[filepath.rfind('/')+1:],'w')
	f = client.get_file(filepath).read()
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
		else:
			k = conf.readline()
			conf.close()
			return (mode,k,k,0)
	except IOError:
		print 'No configuration file found.'
		mode = ''
		while str(mode) != "AES" and str(mode) != "RSA":
			mode = raw_input('Enter an encrypt mode (AES|RSA): ').strip().upper()
		print 'Generating keys... (It may take a while)'
		f = open('.securefilecloud.keys', 'w')
		f.write(mode)
		if mode == 'RSA':
			e,d,n = rsa.keys(1024)
			f.write(str(e)+'\n')
			f.write(str(d)+'\n')
			f.write(str(n)+'\n')
			f.close()
			return (mode,e,d,n)
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
	client = connect(app_key,app_secret,'')
	#client = ''  #for command line test, uncomment this and comment line before this.
	mode,e,d,n = loadconf('')
	prompt(client,mode,e,d,n)
