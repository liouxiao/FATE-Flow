#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import json

from flask import (
    Response, jsonify
)
from webargs import fields
from webargs.flaskparser import use_kwargs
from werkzeug.http import HTTP_STATUS_CODES

from fate_flow.entity.engine_types import CoordinationProxyService, GRPCChannel
from fate_flow.entity.types import RetCode, CoordinationCommunicationProtocol, FederatedMode
from fate_flow.settings import stat_logger, PROXY_NAME, ENGINES, PROXY


def get_json_result(code=RetCode.SUCCESS, message='success', data=None, job_id=None, meta=None):
    result_dict = {
        "code": code,
        "message": message,
        "data": data,
        "job_id": job_id,
        "meta": meta,
    }

    response = {}
    for key, value in result_dict.items():
        if value is not None:
            response[key] = value
    return jsonify(response)


def server_error_response(e):
    stat_logger.exception(e)
    if len(e.args) > 1:
        return get_json_result(code=RetCode.EXCEPTION_ERROR, message=repr(e.args[0]), data=e.args[1])
    return get_json_result(code=RetCode.EXCEPTION_ERROR, message=repr(e))


def args_error_response(e):
    stat_logger.exception(e)
    messages = e.data.get("messages", {})
    return get_json_result(code=RetCode.EXCEPTION_ERROR, message="Invalid request.",
                           data=messages)


def error_response(response_code, retmsg=None):
    if retmsg is None:
        retmsg = HTTP_STATUS_CODES.get(response_code, 'Unknown Error')

    return Response(json.dumps({
        'retmsg': retmsg,
        'retcode': response_code,
    }), status=response_code, mimetype='application/json')


def validate_request_json(**kwargs):
    return use_kwargs(kwargs, location='json')


def job_request_json(**kwargs):
    return validate_request_json(
        job_id=fields.String(required=True),
        role=fields.String(required=True),
        party_id=fields.String(required=True),
        **kwargs
    )


def task_request_json(**kwargs):
    return validate_request_json(
        job_id=fields.String(required=True),
        task_id=fields.String(required=True),
        task_version=fields.Integer(required=True),
        role=fields.String(required=True),
        party_id=fields.String(required=True),
        **kwargs
    )


def validate_request_headers(**kwargs):
    return use_kwargs(kwargs, location='headers')


def get_federated_proxy_address():
    grpc_channel = GRPCChannel.DEFAULT
    # protocol = CoordinationCommunicationProtocol.HTTP
    if ENGINES.get("federated_mode") == FederatedMode.SINGLE:
        return "127.0.0.1", 9360, CoordinationCommunicationProtocol.GRPC, GRPCChannel.OSX
    if PROXY_NAME == CoordinationProxyService.OSX:
        grpc_channel = GRPCChannel.OSX
        host = PROXY.get(PROXY_NAME).get("host")
        port = PROXY.get(PROXY_NAME).get("port")
        protocol = CoordinationCommunicationProtocol.GRPC

    elif PROXY_NAME == CoordinationProxyService.ROLLSITE:
        host = PROXY.get(PROXY_NAME).get("host")
        port = PROXY.get(PROXY_NAME).get("port")
        protocol = CoordinationCommunicationProtocol.GRPC

    elif PROXY_NAME == CoordinationProxyService.NGINX:
        host = PROXY.get(PROXY_NAME).get("grpc_host")
        port = PROXY.get(PROXY_NAME).get("port")
        protocol = CoordinationCommunicationProtocol.GRPC
    else:
        raise RuntimeError(f"can not support coordinate proxy {PROXY}")
    return host, port, protocol, grpc_channel