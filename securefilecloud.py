import dropbox
import rsa
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

if __name__ == "__main__":
	client = connect(app_key,app_secret,'')
	upload(client, sys.argv[1])
