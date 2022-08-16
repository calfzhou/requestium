from http import cookiejar as cookielib

import requests
from requests.cookies import cookiejar_from_dict, RequestsCookieJar, merge_cookies
from requests.sessions import merge_hooks, merge_setting
from requests.structures import CaseInsensitiveDict
from requests.utils import get_netrc_auth


class RequestsSessionEx(requests.Session):
    """Extend `requests.Session` class to fix some known issues.

    - fix: Persist session-level CookiePolicy. https://github.com/psf/requests/pull/4042
    """
    # Rewrite super's `prepare_request` to persist session-level CookiePolicy.
    def prepare_request(self, request):
        """Constructs a :class:`PreparedRequest <PreparedRequest>` for
        transmission and returns it. The :class:`PreparedRequest` has settings
        merged from the :class:`Request <Request>` instance and those of the
        :class:`Session`.

        :param request: :class:`Request` instance to prepare with this
            session's settings.
        :rtype: requests.PreparedRequest
        """
        cookies = request.cookies or {}

        # Bootstrap CookieJar.
        if not isinstance(cookies, cookielib.CookieJar):
            cookies = cookiejar_from_dict(cookies)

        # Merge with session cookies
        # Hack: Persist session-level CookiePolicy.
        merged_cookies = merge_cookies(
            merge_cookies(RequestsCookieJar(self.cookies._policy), self.cookies), cookies)

        # Set environment's basic authentication if not explicitly set.
        auth = request.auth
        if self.trust_env and not auth and not self.auth:
            auth = get_netrc_auth(request.url)

        p = requests.PreparedRequest()
        p.prepare(
            method=request.method.upper(),
            url=request.url,
            files=request.files,
            data=request.data,
            json=request.json,
            headers=merge_setting(request.headers, self.headers, dict_class=CaseInsensitiveDict),
            params=merge_setting(request.params, self.params),
            auth=merge_setting(auth, self.auth),
            cookies=merged_cookies,
            hooks=merge_hooks(request.hooks, self.hooks),
        )
        return p
