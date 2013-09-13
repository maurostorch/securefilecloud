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

def upload(client, filepath):
	print 'upload file '+filepath
	(e,d,n,filetmp) = encrypt(filepath)
	f = open(filetmp)
	client.put_file("/"+filepath,f)
	print (e,d,n)

def encrypt(filepath):
	(e,d,n) = rsa.keys(1024)
	f = open(filepath,'r')
	data = f.read()
	f.close()
	secure = rsa.encrypt(data,e,n)
	tmp = tempfile.NamedTemporaryFile(delete=False)
	tmpfile = tmp.name
	tmp.write(secure)
	tmp.close()
	return (e,d,n,tmpfile)

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

if __name__ == "__main__":
	client = connect(app_key,app_secret,'')
	level = '/'
	while True:
		command = raw_input('upload <file> | download <file> key mod | list | cd | exit:').strip()
		if command.split(' ')[0] == 'upload':
			upload(client, command.split(' ')[1])
		elif command.split(' ')[0] == 'download':
			download(client,command.split(' ')[1],long(command.split(' ')[2]),long(command.split(' ')[3]))
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
			break
		elif command.split(' ')[0] == 'pwd':
			print level
