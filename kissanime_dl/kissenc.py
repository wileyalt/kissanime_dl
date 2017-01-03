# -*- coding: utf-8 -*-
# Wiley Yu

try:
    from pkcs7 import PKCS7Encoder
except ImportError:
    from .pkcs7 import PKCS7Encoder

from Crypto.Protocol import KDF
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import requests
import binascii
import base64

# lets cache those values!

pkc = PKCS7Encoder()
post_headers = {
    'X-Requested-With': 'XMLHttpRequest'
}

asian_c = "32b812e9a1321ae0e84af660c4722b3a".encode('utf8')
cartoon_hex = "a5e8d2e9c1721ae0e84ad660c472c1f3".encode('utf8')

comb = {}
# BEGIN ASIAN
comb['Asian'] = {}
comb['Asian']['sha'] = ""
comb['Asian']['topost'] = 'http://kissasian.com/External/RSK'
comb['Asian']['payload'] = {"krsk": "krsk"}
comb['Asian']['f'] = binascii.unhexlify(asian_c)
# END ASIAN

# BEGIN CARTOON
comb['Cartoon'] = {}
comb['Cartoon']['sha'] = ""
comb['Cartoon']['topost'] = 'http://kisscartoon.se/External/RSK'
comb['Cartoon']['payload'] = {}
comb['Cartoon']['f'] = binascii.unhexlify(cartoon_hex)
# END CARTOON


def ver5(raw_str, sess, type):
    # for version 5
    # requires a session because the js makes an ajax request
    # in 256
    sha = comb[type]['sha']
    topost = comb[type]['topost']
    payload = comb[type]['payload']
    f = comb[type]['f']

    if(sha == ''):
        post_data = sess.post(topost, headers=post_headers, data=payload)
        comb[type]['sha'] = post_data.text.encode('utf8')
        sha = comb[type]['sha']

    obj_sha = SHA256.new(sha)
    a = binascii.unhexlify(obj_sha.hexdigest())
    g = AES.new(a, AES.MODE_CBC, f)
    jj = base64.b64decode(raw_str)
    #
    filled = g.decrypt(jj)
    return pkc.decode(filled).decode('utf8')


def ver3(raw_str, sess, type):
    # lazy fix
    # since cartoon_payload is empty, the functionality should still be the
    # same
    return ver5(raw_str, sess, type)


def kissencCartoon(raw_str, sess):
    # Using Version 3
    return ver3(raw_str, sess, "Cartoon")


def kissencAsian(raw_str, sess):
    # Using Version 5
    return ver5(raw_str, sess, "Asian")


def kissencAnime(raw_str):
    return base64.b64decode(raw_str).decode('utf8')
