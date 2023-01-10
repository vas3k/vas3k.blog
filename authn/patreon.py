import logging
from json import JSONDecodeError

import requests
from django.conf import settings

from authn.exceptions import PatreonException

logger = logging.getLogger(__name__)


def fetch_auth_data(code, original_redirect_uri):
    try:
        response = requests.post(
            url=settings.PATREON_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "code": code,
                "grant_type": "authorization_code",
                "client_id": settings.PATREON_CLIENT_ID,
                "client_secret": settings.PATREON_CLIENT_SECRET,
                "redirect_uri": original_redirect_uri,
            },
        )
    except requests.exceptions.RequestException as ex:
        if "invalid_grant" not in str(ex):
            logger.exception(f"Patreon error on login: {ex}")
        raise PatreonException(ex)

    if response.status_code >= 400:
        logger.error(f"Patreon error on login {response.status_code}: {response.text}")
        raise PatreonException(response.text)

    try:
        return response.json()
    except JSONDecodeError:
        raise PatreonException("Patreon is down")


def refresh_auth_data(refresh_token):
    try:
        response = requests.post(
            url=settings.PATREON_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
                "client_id": settings.PATREON_CLIENT_ID,
                "client_secret": settings.PATREON_CLIENT_SECRET,
            },
        )
    except requests.exceptions.RequestException as ex:
        logger.exception(f"Patreon error on refreshing token: {ex}")
        raise PatreonException(ex)

    if response.status_code >= 400:
        logger.error(
            f"Patreon error on refreshing token {response.status_code}: {response.text}"
        )
        raise PatreonException(response.text)

    try:
        return response.json()
    except JSONDecodeError:
        raise PatreonException("Patreon is down")


def fetch_user_data(access_token):
    logger.info(f"Fetching user data with access token: {access_token}")
    try:
        response = requests.get(
            url=settings.PATREON_USER_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {access_token}",
            },
            params={
                "include": "memberships",
                "fields[user]": "full_name,email,image_url,about",
                "fields[member]": "patron_status,last_charge_status,pledge_relationship_start,lifetime_support_cents",
            },
        )
    except requests.exceptions.RequestException as ex:
        logger.exception(f"Patreon error on fetching user data: {ex}")
        raise PatreonException(ex)

    if response.status_code >= 400:  # unauthorized etc
        logger.warning(
            f"Patreon error on fetching user data {response.status_code}: {response.text}"
        )
        raise PatreonException(response.text)

    try:
        return response.json()
    except JSONDecodeError:
        raise PatreonException("Patreon is down")


def parse_my_membership(user_data):
    if not user_data or not user_data.get("data") or not user_data.get("included"):
        return None

    for membership in user_data["included"]:
        if (
            membership["attributes"]["patron_status"] == "active_patron"
            and membership["attributes"]["last_charge_status"] == "Paid"
        ):
            return membership["attributes"]

    return None
