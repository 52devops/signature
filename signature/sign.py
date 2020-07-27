# encoding: utf-8

import time
import json
import logging
import base64
import hmac
import hashlib
import urllib.parse
from django.http import HttpResponse
from appkey.models import AppKey
from signature.sing_code import *


class Signer(object):
    @staticmethod
    def make_sign(request, secret_key):
        """
        Signature = Base64(HMAC-SHA1(YourSecretKey, UTF-8-Encoding-Of(Content\nHost\nMethod\nPath\nTimestamp\nVersion)))

        Content: id=1&name=chuck
        Host: www.52devops.com
        Method: post
        Path: /api/v1/user/
        Timestamp: 1595836721
        Version: v2
        """
        try:
            params = json.loads(request.body)
        except Exception as e:
            logging.error('签名获取request.body异常：{0}'.format(str(e)))
            return None

        payload = dict(Host='',
                       Timestamp=0,
                       Version='',
                       )

        for key, value in payload.items():
            payload[key] = request.META.get('HTTP_{0}'.format(key.upper()), payload[key])

        content = urllib.parse.urlencode(params)
        payload['Content'] = content
        payload['Path'] = request.path
        payload['Method'] = request.method

        payload = [str(payload[key]) for key in sorted(payload.keys(), reverse=False)]

        payload = "\n".join(payload).encode('utf-8')
        secret_key = secret_key.encode('utf-8')

        digest = hmac.new(secret_key, payload, digestmod=hashlib.sha1).digest()
        return base64.b64encode(digest)

    @staticmethod
    def check_signature(request, secret_key):
        signature = request.META.get('HTTP_SIGNATURE', '')
        return signature == Signer.make_sign(request, secret_key)

    def __call__(self, func):
        def wrapper(request, *args, **kwargs):
            msg = dict(code=UNKNOW_EXCEPTION_CODE, message=UNKNOW_EXCEPTION_MESSAGE)

            access_key = request.META.get('HTTP_ACCESSKEY', '')
            timestamp = request.META.get('HTTP_TIMESTAMP', '')
            signature = request.META.get('HTTP_SIGNATURE', '')
            host = request.META.get('HTTP_HOST', '')
            version = request.META.get('HTTP_VERSION', '')
            headers = [
                dict(key='access_key', value=access_key,
                     msg=dict(code=ACCESSKEY_HEADER_NOT_FOUND_CODE, message=ACCESSKEY_HEADER_NOT_FOUND_MESSAGE)),
                dict(key='timestamp', value=timestamp,
                     msg=dict(code=TIMESTAMP_HEADER_NOT_FOUND_CODE, message=TIMESTAMP_HEADER_NOT_FOUND_MESSAGE)),
                dict(key='signature', value=signature,
                     msg=dict(code=SIGNATURE_HEADER_NOT_FOUND_CODE, message=SIGNATURE_HEADER_NOT_FOUND_MESSAGE)),
                dict(key='host', value=host,
                     msg=dict(code=HOST_HEADER_NOT_FOUND_CODE, message=HOST_HEADER_NOT_FOUND_MESSAGE)),
                dict(key='version', value=version,
                     msg=dict(code=VERSION_HEADER_NOT_FOUND_CODE, message=VERSION_HEADER_NOT_FOUND_MESSAGE)),
            ]
            try:
                for header in headers:
                    if not header['value']:
                        msg = header['msg']
                        raise Exception()

                now_timestamp = int(time.time())

                try:
                    timestamp = int(timestamp)
                except:
                    msg = dict(code=TIMESTAMP_INVALID_CODE, message=TIMESTAMP_EXPIRED_MESSAGE)
                    raise Exception()

                if now_timestamp - int(timestamp) > 30:
                    msg = dict(code=TIMESTAMP_EXPIRED_CODE, message=TIMESTAMP_EXPIRED_MESSAGE)
                    raise Exception()

                app_keys = AppKey.objects.filter(access_key=access_key)
                if app_keys.count() > 0:
                    app_key = app_keys.first()
                    if Signer.check_signature(request, app_key.secret_key):
                        return func(request, *args, **kwargs)
                    else:
                        msg = dict(code=SIGNATURE_INVALID_CODE, message=SIGNATURE_INVALID_MESSAGE)
                else:
                    msg = dict(code=ACCESSKEY_NOT_FOUND_CODE, message=ACCESSKEY_NOT_FOUND_MESSAGE)
            except Exception as e:
                logging.error(u'签名检查流程出错：{0}'.format(str(e)))

            return HttpResponse(json.dumps(msg))

        return wrapper
