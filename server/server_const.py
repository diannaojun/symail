import hashlib

__ROOT__ = "."
__DBNM__ = "/server.db"

__DBPT__ = __ROOT__ + __DBNM__

__HASHPW__ = lambda s : hashlib.sha256(s.encode()).hexdigest()
__TOKN__ = __HASHPW__("333uuu99")

__MX_LSTN__ = 4