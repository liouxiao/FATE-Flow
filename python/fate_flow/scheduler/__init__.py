from arch.api.client import FlowSchedulerApi
from fate_flow.runtime.runtime_config import RuntimeConfig
from fate_flow.settings import HOST, HTTP_PORT, PROXY_PROTOCOL, API_VERSION, HTTP_REQUEST_TIMEOUT
from fate_flow.utils.api_utils import get_federated_proxy_address


def init_scheduler():
    remote_host, remote_port, remote_protocol, grpc_channel = get_federated_proxy_address()

    protocol = remote_protocol if remote_protocol else PROXY_PROTOCOL
    RuntimeConfig.set_schedule_client(FlowSchedulerApi(host=HOST, port=HTTP_PORT, protocol=protocol,
                                                       api_version=API_VERSION, timeout=HTTP_REQUEST_TIMEOUT,
                                                       remote_protocol=protocol, remote_host=remote_host,
                                                       remote_port=remote_port, grpc_channel=grpc_channel))