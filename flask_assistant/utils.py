from __future__ import absolute_import
from typing import Dict, Any
import os
import sys
import logging
from google.auth import jwt
from flask_assistant.core import Assistant
from . import logger


logger.setLevel(logging.INFO)

GOOGLE_PUBLIC_KEY = {
    "ee4dbd06c06683cb48dddca6b88c3e473b6915b9": "-----BEGIN CERTIFICATE-----\nMIIDJjCCAg6gAwIBAgIIXlp0tU/OdR8wDQYJKoZIhvcNAQEFBQAwNjE0MDIGA1UE\nAxMrZmVkZXJhdGVkLXNpZ25vbi5zeXN0ZW0uZ3NlcnZpY2VhY2NvdW50LmNvbTAe\nFw0xOTEwMDMxNDQ5MzRaFw0xOTEwMjAwMzA0MzRaMDYxNDAyBgNVBAMTK2ZlZGVy\nYXRlZC1zaWdub24uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20wggEiMA0GCSqG\nSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC41NLGPK9PRi0KjFTIQ9qEirje2IrmWSwZ\n7lmgTzwA4mpc4tqDn7AfUTHmuyhDrbweGq2wQeYJDbBPT5uX86XcQgAcu4IzSuZG\nJZ68ASYOWWlKV0vYjf6W/9v73sGJFxbkoAB8X7QH/fN80QYoXvSX+IwNnePnoikM\nnAsNiZrkLoqHuv5+ahOgpBN5qyvKglasNiXGpv8EL96CKb+nmMudzpypjbQHJUp2\nmfDvOiTX6IuSXyeYRkyzOeX7wqpV1l+TU3A8orMylNe8e+oL/2mAYVzCC9Wk1nq2\nGT4vRRmzrr2GW4eKr9525JQe7BKBKkC2WWhKE+EmqPm2ZFnQ/frlAgMBAAGjODA2\nMAwGA1UdEwEB/wQCMAAwDgYDVR0PAQH/BAQDAgeAMBYGA1UdJQEB/wQMMAoGCCsG\nAQUFBwMCMA0GCSqGSIb3DQEBBQUAA4IBAQA+mwyWb+SZMLOiQS1lUgN6iXO2JZm+\nq6rmSYnpLP5nCtwKjHbGSw0DoUchem2g0AYsB/HqNl5zLvJb5CXlP79sTO6Ot7sX\nHI3Mtqw4Fe1QFCC5QVhudpMNKNQYq8P45SrfwMW1qSYYsMXbpmNkIPbFvxib1L0l\niUfnjCXFB4XiDa80Cb73cxmU7a24/j03o42kjcRX2BtXs6jhP7z8BxnDCjybjlLT\no5gBombtlPKgOTdcF+eKdaO1LLQ+9LmueiZH/HCsvAmmxLT9g1XZCEFg5zttdetT\nVV+03sFBGhoJPbChiOJMdH8IQVEdtpvnAiYyVBYEUSj7CWSZEI50syL2\n-----END CERTIFICATE-----\n",
    "8c58e138614bd58742172bd5080d197d2b2dd2f3": "-----BEGIN CERTIFICATE-----\nMIIDJjCCAg6gAwIBAgIIFqFLh91FQ0kwDQYJKoZIhvcNAQEFBQAwNjE0MDIGA1UE\nAxMrZmVkZXJhdGVkLXNpZ25vbi5zeXN0ZW0uZ3NlcnZpY2VhY2NvdW50LmNvbTAe\nFw0xOTA5MjUxNDQ5MzRaFw0xOTEwMTIwMzA0MzRaMDYxNDAyBgNVBAMTK2ZlZGVy\nYXRlZC1zaWdub24uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20wggEiMA0GCSqG\nSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDJ/fKZfxfVD68YAuMfl5bnoNBjZ4kyhXMi\nffkizGpJGkMR2gL6ansSYLrd94Gn/W5FH0hMLCWK41gBXXI6alI6y0YNGSeGnmbO\nZz8Si+oMfiPAj9NaawMwNnusdMqrkMUrMBUmWSTzk4ttu3U9TVkIXZ5i0LNvntJO\nuG+Ga4A+CaipE6Y1QoXkFwFDDum8qpXYKMlF0pSbGz/Nb2o1RjINlo9gx+KWgaPK\n2wWw+n6XJDLFtcmhRtQPuMDpxRveY63OlE4CCRhnJLvjSD4ZlxUtqmoDALpRnGUI\n36VdsZpvtz5CsIy8PB+7ZTcBBK8jfy73kxpuuMdlaxZEJuolV8cjAgMBAAGjODA2\nMAwGA1UdEwEB/wQCMAAwDgYDVR0PAQH/BAQDAgeAMBYGA1UdJQEB/wQMMAoGCCsG\nAQUFBwMCMA0GCSqGSIb3DQEBBQUAA4IBAQCY7YX8EDcPQGFpklGVtqN7tlfm+Gi8\n0v3E9WoQUiMQJ9Mt34ixd3zPjMeKOtVxj6BZzHrpyR6rM9lB4nzoyCWf9K86HaWS\nuxtAACj7yovKAh2x5pFwEB014qNdG03YYQFy8MvDxegaL4soWqCa2UfEK4vdWyJi\nZKM0iT6s78VY6vOWxK+z1IC/6AYbyskzv57T+dBUwGcwQEf0yBeu89tR7LFSaVV/\n6A+dTGyFlHysR6dddwJvzl7jG83RQs2L58qIISD+6RdRxcD02h388YhhMy9Nrpmo\nZeXouJ7YLsHGFkn3yfWi3KWYVdTGbd/9BQPBjhKzS93SxdolTKKVOI/7\n-----END CERTIFICATE-----\n",
    "3db3ed6b9574ee3fcd9f149e59ff0eef4f932153": "-----BEGIN CERTIFICATE-----\nMIIDJjCCAg6gAwIBAgIIeBPD3wqfL6EwDQYJKoZIhvcNAQEFBQAwNjE0MDIGA1UE\nAxMrZmVkZXJhdGVkLXNpZ25vbi5zeXN0ZW0uZ3NlcnZpY2VhY2NvdW50LmNvbTAe\nFw0xOTEwMTExNDQ5MzRaFw0xOTEwMjgwMzA0MzRaMDYxNDAyBgNVBAMTK2ZlZGVy\nYXRlZC1zaWdub24uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20wggEiMA0GCSqG\nSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDYpym/gLFOh4IoQhfOeGo+DbUyEIA/0Odf\nmzb9R1nVvM5WFHyqKiT8/yPvLxgXYzYlzyvZu18KAkYWWNuS21Vzhe+d4949P6EZ\n/096QjVFSHvKTo94bSQImeZxZiBhfFcvw/RMM0eTeZZPgOXI3YIJyWjAZ9FUslt7\nWoLU0HZFc/JyPRF8M2kinkdYxnzA+MjzCetXlqmhAr+wLPg/QLKwACyRIF2FJHgf\nPsvqaeF7JXo0zHPcGuHUOqXCHon6KiHZF7OC4bzTuTEzVipJTLYy9QUyL4M2L8bQ\nu1ISUSaXhj+i1WT0RDJwqpioOFprVFqqkVvbUW0nXD/x1UA4nvf7AgMBAAGjODA2\nMAwGA1UdEwEB/wQCMAAwDgYDVR0PAQH/BAQDAgeAMBYGA1UdJQEB/wQMMAoGCCsG\nAQUFBwMCMA0GCSqGSIb3DQEBBQUAA4IBAQBr5+4ZvfhP436NdJgN0Jn7iwwVArus\nXUn0hfuBbCoj1DhuRkP9wyLCpOo6cQS0T5bURVZzirsKc5sXP4fNYXqbfLaBpc7n\njTUtTOIqoA4LKPU7/FH6Qt/UfZ4DQIsKaD3087KdY3ePatSn/HTxvT8Ghqy/JGjf\nLXZehQnlyyCRaCMqv1gEOMiY/8LG3d1hLL7CMphnb4ASk0YMKrWkKhIoa6NWU2Rd\nqp01F4iG44ABpea+ymXAGmWBVPnep51kr/wIPIzr9WvNFAAZW2Enk3+kUWNupuz+\npdXq9KnegVsCs4G7QcTPqwc/vMu7uGq/pruDEOYVOd9Rm+rr0wlMgkcf\n-----END CERTIFICATE-----\n",
}


def import_with_3(module_name, path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_with_2(module_name, path):
    import imp

    return imp.load_source(module_name, path)


def get_assistant(filename):
    """Imports a module from filename as a string, returns the contained Assistant object"""

    agent_name = os.path.splitext(filename)[0]

    try:
        agent_module = import_with_3(agent_name, os.path.join(os.getcwd(), filename))

    except ImportError:
        agent_module = import_with_2(agent_name, os.path.join(os.getcwd(), filename))

    for name, obj in agent_module.__dict__.items():
        if isinstance(obj, Assistant):
            return obj


def decode_token(token, client_id):
    decoded = jwt.decode(token, certs=GOOGLE_PUBLIC_KEY, verify=True, audience=client_id)
    return decoded
    
