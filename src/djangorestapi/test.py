def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    text = b'''
    <html>
        <head>
            <title>uWSGI test</title>
        </head>
        <body bgcolor="black" style="color:white;">
            <h1>Test Successful !</h1>
        </body>
    </html>
    '''
    # text = b""
    return [text]