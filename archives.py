import io
import tarfile
import zipfile

class ZipReader:
    def __init__(self, buf):
        self.zip = zipfile.ZipFile(io.BytesIO(buf))

    def namelist(self):
        return self.zip.namelist()

    def open(self, name):
        return self.zip.open(name)

class TarReader:
    def __init__(self, buf):
        self.tar = tarfile.open(fileobj=io.BytesIO(buf))

    def namelist(self):
        return self.tar.getnames()

    def open(self, name):
        return self.tar.extractfile(name)

def open_archive(buf):
    if buf[:4]==b'PK\x03\x04':
        return ZipReader(buf)
    # assume .tar.gz or similar
    return TarReader(buf)
