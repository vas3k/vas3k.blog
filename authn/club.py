import logging

import requests

log = logging.getLogger(__name__)


def parse_membership(user_slug, jwt_token):
    try:
        return requests.get(
            url=f"https://vas3k.club/user/{user_slug}.json",
            params={
                "jwt": jwt_token
            }
        ).json()
    except Exception as ex:
        log.exception(ex)
        return None
