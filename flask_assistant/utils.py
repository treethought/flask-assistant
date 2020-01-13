from __future__ import absolute_import
from typing import Dict, Any
import os
import sys
import logging
from google.auth import jwt
from flask_assistant.core import Assistant
from . import logger
import requests

logger.setLevel(logging.INFO)

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
    r = requests.get('https://accounts.google.com/.well-known/openid-configuration')
    if(r.status_code != 200):
        print("status_code != 200; status_code =", r.status_code)
        print(r)
        try:
            return {'status':'BAD','error':r.status_code, "output": r.text}
        except requests.exceptions.RequestException as e:   
            return {'status':'BAD','error':r.status_code}

    if "jwks_uri" not in r.json():
        error_message = "Missing jwks_uri in 'https://accounts.google.com/.well-known/openid-configuration'"
        print(error_message)
        return {'status':'BAD','error':error_message}

    googleapis_certs = r.json()["jwks_uri"].replace("/v3/", "/v1/")
    r = requests.get(googleapis_certs)
    if(r.status_code != 200):
        print("status_code != 200; status_code =", r.status_code)
        print(r)
        try:
            return {'status':'BAD','error':r.status_code, "output": r.text}
        except requests.exceptions.RequestException as e:   
            return {'status':'BAD','error':r.status_code}
    else:
        public_keys = r.json()
        decoded = jwt.decode(token, certs=public_keys, verify=True, audience=client_id)
        return {'status':'OK','output': decoded}
        
