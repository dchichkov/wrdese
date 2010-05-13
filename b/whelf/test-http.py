method = 'PUT'
url = '/i'
body = "123"
headers = {}
headers['CONTENT-TYPE'] = 'octet/stream'
import httplib
c = httplib.HTTPConnection('localhost:8080')

for i in xrange(10):
    c.request(method, url, body, headers)
    print c.getresponse()
c.close()
# c.request(method, url, body, headers)
