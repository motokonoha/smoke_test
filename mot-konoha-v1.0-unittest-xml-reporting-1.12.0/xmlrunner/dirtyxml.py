# 
# Matches invalid XML1.0 unicode characters, like control characters:
# http://www.w3.org/TR/2006/REC-xml-20060816/#charsets
# For Jython users, see http://bugs.jython.org/issue1836
#

#     INVALID_XML_1_0_UNICODE_RE = re.compile(
#         u'[\u0000-\u0008\u000B\u000C\u000E-\u001F\uD800-\uDFFF\uFFFE\uFFFF]',
#         re.UNICODE
#     )

import sys
import re
from six import unichr

_illegal_unichrs = [
    (0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F), 
    (0x7F, 0x84), (0x86, 0x9F), 
    (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
] 
if sys.maxunicode >= 0x10000:  # not narrow build 
    _illegal_unichrs.extend([
        (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), 
        (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF), 
        (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF), 
        (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), 
        (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF), 
        (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF), 
        (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), 
        (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF),
    ]) 

_illegal_ranges = [
    "%s-%s" % (unichr(low), unichr(high))
    for (low, high) in _illegal_unichrs
]

INVALID_XML_1_0_UNICODE_RE = re.compile(u'[%s]' % u''.join(_illegal_ranges)) 
