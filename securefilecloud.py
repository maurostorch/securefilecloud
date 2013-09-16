import dropbox
import rsa
import shutil
import sys
import tempfile

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

def upload(client, filepath, e, n):
	print 'upload file '+filepath
	(e,n,filetmp) = encrypt(filepath, e, n)
	f = open(filetmp)
	client.put_file("/"+filepath,f)

def encrypt(filepath, e, n):
	f = open(filepath,'r')
	data = f.read()
	f.close()
	secure = rsa.encrypt(data,e,n)
	tmp = tempfile.NamedTemporaryFile(delete=False)
	tmpfile = tmp.name
	tmp.write(secure)
	tmp.close()
	return (e,n,tmpfile)

def download(client, filepath, d, n):
	print 'downloading file: '+filepath
	out = file('./'+filepath[filepath.rfind('/')+1:],'w')
	f = client.get_file(filepath).read()
	out.write(f)
	out.close()
	decrypt(out.name,d,n)

def decrypt(filepath, d, n):
	tmp = tempfile.NamedTemporaryFile(delete=False)
	tmp.close()
	shutil.copy(filepath, tmp.name)
	tmp = open(tmp.name)
	c = tmp.read()
	f = open(filepath, 'w')
	f.write(rsa.decrypt(c,d,n))
	f.close()
	tmp.close()

def listfiles(client, directory):
	meta = 	client.metadata(directory)
	print meta
	#for item in meta.contents:
	#	print item.path

def loadconf(conffile):
	try:
		conf = open(conffile and conffile or 'rsa.keys')
		e = long(conf.readline())
		d = long(conf.readline())
		n = long(conf.readline())
		conf.close()
		return (e,d,n)
	except IOError:
		print 'No config file found. Generating keys... (It may take a while)'
		e,d,n = rsa.keys(1024)
		f = open('rsa.keys', 'w')
		f.write(str(e)+'\n')
		f.write(str(d)+'\n')
		f.write(str(n)+'\n')
		f.close()
		return (e,d,n)

if __name__ == "__main__":
	#client = connect(app_key,app_secret,'')
	e,d,n = loadconf('')
	level = '/'
	while True:
		command = raw_input('command: ').strip()
		if command.split(' ')[0] == 'upload':
			upload(client, command.split(' ')[1],e,n)
		elif command.split(' ')[0] == 'download':
			download(client,command.split(' ')[1],d,n)
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
