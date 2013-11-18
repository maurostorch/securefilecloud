import dropbox

class DropBoxClient(object):

    def __init__(self,app_key, app_secret,code):
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
        authorize_url = flow.start()
        if not code:
            print "If you don't have a auth code check: "+authorize_url
        code = raw_input("Enter the authorize code: ").strip()
        access_token, user_id = flow.finish(code)
        self.client = dropbox.client.DropboxClient(access_token)

    def upload(self,filename):
        self.upload_file(file)

    def upload_file(self,file):
        self.client.put_file("/"+file.name,file)

    def close(self):
	    return
