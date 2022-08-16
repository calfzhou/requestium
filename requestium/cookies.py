import http.cookiejar

import requests.cookies


class ExpireOkCookiePolicy(http.cookiejar.DefaultCookiePolicy):
    """Custom cookie policy which can return expired cookies back to the server."""
    def return_ok_expires(self, cookie, request):
        return True


class RequestsMozillaCookieJar(http.cookiejar.MozillaCookieJar, requests.cookies.RequestsCookieJar):
    """Custom mozilla cookie jar which also compatible with requests cookie jar interface.

    Since we use MozillaCookieJar to load and save Netscape HTTP cookie file,
    while requestium's Session object relies on RequestsCookieJar to update cookies.
    """
    pass
