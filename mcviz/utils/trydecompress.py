
try:
    from zlib import error as zliberror
except ImportError:
    # Just in case. If zlib isn't available for some crazy reason.
    class zliberror(Exception): pass

try:
    from gzip import GzipFile
except ImportError:
    GzipFile = None

from cStringIO import StringIO

def try_decompress(data):
    """
    Try various decompression algorithms on `data`, return the decompressed
    output
    """
    for encoding in "zlib zip bz2 gzip".split():
        try:
            if encoding == "gzip" and GzipFile is not None:
                data = GzipFile(fileobj=StringIO(data)).read()
                continue
            data = data.decode(encoding)
        except (zliberror, IOError, LookupError):
            pass
    return data
