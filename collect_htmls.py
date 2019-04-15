import os
import logging
import html as ihtml
from typing import Dict
from urllib.parse import urlparse

from tenacity import retry, stop_after_attempt, wait_fixed
import requests
from bs4 import BeautifulSoup


PROXY_URL = os.environ.get("SOCKS_PROXY", None)
PROXIES: Dict = dict()
if PROXY_URL is not None:
    PROXIES = dict(http=f'socks5h://{PROXY_URL}',
                   https=f'socks5h://{PROXY_URL}')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'}
LOGGER = logging.getLogger(__name__)


def meta_redirect(content, original_link):
    soup = BeautifulSoup(content, "html.parser")
    result = soup.find("meta", attrs={"http-equiv": "refresh"})
    if result:
        try:
            _, text = ihtml.unescape(result["content"]).split(";")
        except ValueError:
            LOGGER.warning(
                "WARNING: malformed redirect dectcted: %s", result['content'])
            return None
        text = text.strip().lower()
        if text.startswith("url="):
            url = text[4:].strip("\"\'")
            if not url.startswith("http"):
                base_url = '{uri.scheme}://{uri.netloc}'.format(
                    uri=urlparse(original_link))
                url = base_url + url
            return url
    return None


@retry(reraise=True, stop=stop_after_attempt(5), wait=wait_fixed(1))
def get_url(url, use_headers=True, timeout=10):
    LOGGER.debug("Retrieving of %s", url)
    headers = HEADERS if use_headers else {}
    response = requests.get(url, proxies=PROXIES,
                            headers=headers, timeout=timeout)
    new_url = meta_redirect(response.text, url)
    if new_url:
        LOGGER.debug("Meta refresh detected. Retrieving %s...", new_url)
        return requests.get(new_url, proxies=PROXIES, headers=HEADERS, timeout=timeout)
    return response
