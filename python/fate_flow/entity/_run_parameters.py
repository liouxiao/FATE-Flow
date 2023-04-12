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
from copy import deepcopy

from ._base import BaseEntity
from ..utils.runtime_conf_parse_util import RuntimeConfParserUtil


class RunParameters(BaseEntity):
    def __init__(self, **kwargs):
        self.job_type = "train"
        self.inheritance_info = {}  # job_id, component_list
        self.computing_engine = None
        self.federation_engine = None
        self.storage_engine = None
        self.engines_address = {}
        self.federated_mode = None
        self.federation_info = None
        self.task_cores = None
        self.task_parallelism = None
        self.computing_partitions = None
        self.federated_status_collect_type = None
        self.federated_data_exchange_type = None  # not use in v1.5.0
        self.model_id = None
        self.model_version = None
        self.dsl_version = None
        self.auto_retries = None
        self.auto_retry_delay = None
        self.timeout = None
        self.eggroll_run = {}
        self.spark_run = {}
        self.rabbitmq_run = {}
        self.pulsar_run = {}
        self.adaptation_parameters = {}
        self.assistant_role = None
        self.map_table_name = None
        self.map_namespace = None
        self.task_conf = {}
        self.roles = {}
        self.role_parameters = {}
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def role_parameter(self, parameter_name, role, party_id):
        if not self.roles:
            # compatible with previous versions
            return getattr(self, parameter_name)
        index = [str(_p) for _p in self.roles.get(role)].index(str(party_id))
        _conf = deepcopy(getattr(self, parameter_name))
        _role = self.role_parameters.get(role, {}).get(str(index), {}).get(parameter_name, {})
        if isinstance(_conf, dict):
            # dict
            _conf = RuntimeConfParserUtil.merge_dict(_conf, _role)
        else:
            # int, str, etc.
            _conf = _role if _role else _conf
        return _conf

    def to_dict(self):
        d = {}
        for k, v in self.__dict__.items():
            if v is None:
                continue
            d[k] = v
        return d

    def __str__(self):
        return str(self.to_dict())
