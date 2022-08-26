import paypalrestsdk
from httpx import RequestError
from OpenSSL import crypto
from OpenSSL.crypto import X509

import services


class WebhookEvent(paypalrestsdk.WebhookEvent):
    # wrap around this bad boy to make it's cert lookup asynchronous
    # https://github.com/paypal/PayPal-Python-SDK/blob/master/paypalrestsdk/notifications.py#L28

    @staticmethod
    async def _get_cert(cert_url: str) -> X509 | None:
        """Fetches the paypal certificate used to sign the webhook event payload
        """
        try:
            r = await services.http_client.get(cert_url)
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, r.content)
            return cert
        except RequestError as exc:
            print("Error retrieving PayPal certificate with url " + cert_url)
            print(exc)

    @classmethod
    async def verify(cls, transmission_id: str, timestamp: str, webhook_id: str,
                     event_body: str, cert_url: str, actual_sig: str,
                     auth_algo: str = 'sha256') -> bool:
        """Verify certificate and payload
        """
        __auth_algo_map = {
            'SHA256withRSA': 'sha256WithRSAEncryption',
            'SHA1withRSA': 'sha1WithRSAEncryption'
        }
        try:
            if auth_algo != 'sha256' and auth_algo not in __auth_algo_map.values():
                auth_algo = __auth_algo_map[auth_algo]
        except KeyError as e:
            print('Authorization algorithm mapping not found in verify method.')
            return False
        cert = await cls._get_cert(cert_url)
        return cls._verify_certificate(cert) and cls._verify_signature(
            transmission_id, timestamp, webhook_id,
            event_body, cert, actual_sig, auth_algo,
        )


async def verify_signature(transmission_id: str, timestamp: str, webhook_id: str,
                           event_body: str, cert_url: str, actual_sig: str,
                           auth_algo: str = 'sha256'
                           ) -> bool:
    """Wrapper around classmethod as i'm not a fan of it's API design."""
    return await WebhookEvent.verify(transmission_id, timestamp, webhook_id,
                                     event_body, cert_url, actual_sig,
                                     auth_algo)
