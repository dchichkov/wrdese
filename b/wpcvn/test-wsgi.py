from django.test import Client
#c = Client()
#print c.get('/w')
#quit()


from django.core.handlers.wsgi import WSGIRequest

class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.
    
    Usage:
    
    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})
    
    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client
    
    Once you have a request object you can pass it to any view function, 
    just as if that view had been hooked up using a URLconf.
    
    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': '127.0.0.1',
            'SERVER_PORT': 8080,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        print environ
        return WSGIRequest(environ)

        # request = WSGIRequest(environ)
        # handler = BaseHandler()
        # handler.load_middleware()
        # for middleware_method in handler._request_middleware:
        #    if middleware_method(request):
        #        raise Exception("Couldn't create request mock object - "
        #                        "request middleware returned a response")
        #return request



rf = RequestFactory()
post_request = rf.post('/w/123', {'foo': 'bar'})
print post_request

