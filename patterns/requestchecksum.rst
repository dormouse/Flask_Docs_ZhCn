请求内容校验
=========================

请求数据会由不同的代码来处理或者预处理。例如 JSON 数据和表单数据都来源于已经
读取并处理的请求对象，但是它们的处理代码是不同的。这样，当需要校验进来的请求
数据时就会遇到麻烦。因此，有时候就有必要使用一些 API 。

幸运的是可以通过包装输入流来方便地改变这种情况。

下面的例子演示在 WSGI 环境下读取和储存输入数据，得到数据的 SHA1 校验::

    import hashlib

    class ChecksumCalcStream(object):

        def __init__(self, stream):
            self._stream = stream
            self._hash = hashlib.sha1()

        def read(self, bytes):
            rv = self._stream.read(bytes)
            self._hash.update(rv)
            return rv

        def readline(self, size_hint):
            rv = self._stream.readline(size_hint)
            self._hash.update(rv)
            return rv

    def generate_checksum(request):
        env = request.environ
        stream = ChecksumCalcStream(env['wsgi.input'])
        env['wsgi.input'] = stream
        return stream._hash

要使用上面的类，你只要在请求开始消耗数据之前钩接要计算的流就可以了。（按：小心
操作 ``request.form`` 或类似东西。例如 ``before_request_handlers`` 就应当小心不
要操作。）

用法示例::

    @app.route('/special-api', methods=['POST'])
    def special_api():
        hash = generate_checksum(request)
        # Accessing this parses the input stream
        files = request.files
        # At this point the hash is fully constructed.
        checksum = hash.hexdigest()
        return 'Hash was: %s' % checksum
