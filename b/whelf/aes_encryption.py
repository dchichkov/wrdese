#!/usr/bin/env python

from Crypto.Cipher import AES
import base64

"""
    EncodeAES, DecodeAES with MIN_PADDING and 
    naive verification on the MIN_PADDING presence.
"""

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 16

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = 'x'
MIN_PADDING = 8
LFIELD = 1
  
# add padding, encrypt with AES, encode with base64
def EncodeAES(c, s):
    l = (BLOCK_SIZE - (len(s) + LFIELD + MIN_PADDING) % BLOCK_SIZE)
    s += l * PADDING + chr(l) + MIN_PADDING * PADDING
    return base64.b64encode(c.encrypt(s))

# decode with base64, decrypt with AES, verify minimum padding, 
def DecodeAES(c, e):
    try: 
        s = c.decrypt(base64.b64decode(e));
        
        # verify minimum padding
        if(s[-MIN_PADDING:] != MIN_PADDING * PADDING):
            return None        
        s = s[:-MIN_PADDING-LFIELD-ord(s[-MIN_PADDING-LFIELD:-MIN_PADDING])]    
    except:
        return None    
    return s


if __name__ == "__main__":    
    import os
    
    # generate a random secret key
    secret = os.urandom(BLOCK_SIZE)
    print "Secret:", base64.b64encode(secret)
    
    # create a cipher object using the random secret
    cipher = AES.new(secret)
    
    # encode a string
    encoded = EncodeAES(cipher, 'password123')
    print 'Encrypted string:', encoded

    # decode the encoded string
    decoded = DecodeAES(cipher, encoded)
    print 'Decrypted string:', decoded

    # generate a random secret key
    secret = os.urandom(BLOCK_SIZE)
    
    # create a cipher object using the random secret
    badcipher = AES.new(secret)
        
    # decode the encoded string
    decoded = DecodeAES(badcipher, encoded)
    print 'Decrypted string with invalid key:', decoded


    for i in xrange(50):
        s = 'A' * i
        if( DecodeAES(cipher, EncodeAES(cipher, s)) != s):
            print "Test1 FAILED: ", i, s 
        elif( DecodeAES(badcipher, EncodeAES(cipher, s)) != None):
            print "Test2 FAILED: ", i, s
        else:  
            print "Test PASSED: ", i
        
        



