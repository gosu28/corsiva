import hashlib
import hmac


def get_sign(secret, api, parameters):
    sort_dict = sorted(parameters)
    parameters_str = "%s%s" % (api, str().join('%s%s' % (key, parameters[key]) for key in sort_dict))
    h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"), digestmod=hashlib.sha256)
    return h.hexdigest().upper()
