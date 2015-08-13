# Author: Jaroslaw Niec (ajn017)
import argparse, os
from binascii import unhexlify

class SRecReader:
    def __init__(self, file):
        self.records = []
        self.file = file
        self.entry_addr = None

    def load(self):
        offset = 0
        line = 0

        last_address = None
        last_len = None
        image = b""
        line = 0
        pos = 0

        for buf in self.file.readlines():
            line += 1
            if not buf:
                break
            pos += len(buf)

            buf = buf.rstrip()
            try:
                if buf[:2] == "S3":
                    address = int(buf[4:12], 16) + offset
                    record = unhexlify(buf[12:-2])

                    if last_address == None or last_address+last_len != address:
                        self.records.append([address, [record]])
                    else:
                        self.records[-1][1].append(record)

                    last_address = address
                    last_len = len(record)
                elif buf[:2] == "S7" and 14 == len(buf):
                    self.entry_addr = int(buf[4:12], 16)

            except ValueError:
                raise SRecException("Line %d: syntax error" % (line))

        for r in self.records:
            r[1] = b''.join(r[1])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--file", help="path to s19 file", type=str)
    parser.add_argument("-v","--version", help="build version to verify", type=str)
    arguments = parser.parse_args()

    if not arguments.file or not os.path.exists(arguments.file):
        raise Exception("File doesn't exists")

    sign = b"\xDE\xC0\xAD\x70"

    if len(arguments.version) == 12:
        version = arguments.version.encode("ascii") + b"\x00"
    else:
        version = arguments.version.encode("ascii")

    if b"B13." in version or b"I13." in version or b"R13." in version or b"D13." in version:
        with open(arguments.file, 'r') as f:
            srec = SRecReader(f)
            srec.load()

            version_found = False
            for r in srec.records:
                if version in r[1][:1000]:
                    version_found = True
            if not version_found:
                raise Exception("Wrong build version")

            sign_found = False
            for r in srec.records:
                if r[0] == 0x10780000 or r[0] == 0x10810000:
                    sign_found = True
            if not sign_found:
                raise Exception("Build is not signed")
    else:
        with open(arguments.file, 'r') as f:
            srec = SRecReader(f)
            srec.load()
            for r in srec.records:
                if not version.lower() in r[1][:1000].lower():
                    raise Exception("Wrong build version")
                if not sign in r[1][-1000:]:
                    raise Exception("Build is not signed")
