import base64
import os
import struct
from uuid import uuid4

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


MECHANICAL_TURK_PLATFORM_CHOOSE = (
    ('sandbox', _(u'sandbox')),
    ('real', _(u'real')),
)


def get_xml_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid4()), ext)
    file_path = 'xml/%s/' % instance.expt_id
    return os.path.join(file_path, filename)


def get_swf_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid4()), ext)
    file_path = 'swf/'
    return os.path.join(file_path, filename)


def get_expt_uuid():
    return uuid4().hex


def get_image_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid4()), ext)
    file_path = '%s/' % instance.expt_info.expt_id
    return os.path.join(file_path, filename)


def encrypt(val):
    try:
        index = 0
        result = ''
        key_bytes = bytearray(settings.ENCRYPT_KEY)
        for byte in bytearray(val):
            encode = (byte + key_bytes[index]) % 256
            result += struct.pack('b', encode)
            index = (index + 1) % len(key_bytes)
        return result
    except Exception as e:
        print(e.message)
        return val


def decrypt(val):
    try:
        index = 0
        result = ''
        key_bytes = bytearray(settings.ENCRYPT_KEY)
        for byte in bytearray(val):
            decode = (byte + 256 - key_bytes[index]) % 256
            result += struct.pack('b', decode)
            index = (index + 1) % len(key_bytes)
        return result
    except Exception as e:
        print(e.message)
        return val



def _pad(s):
    bs = 16
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)


def _unpad(s):
    return s[:-ord(s[len(s) - 1:])]