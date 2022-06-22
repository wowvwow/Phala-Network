#!/usr/bin/env python
# -*- coding:utf-8 -*-


import sys
sys.path.append('..')
from for_add_pools_and_workers_20.prb_post_request_2 import PrbGetWorkersStatus
from for_add_pools_and_workers_20.prb_post_request_2 import MethodForWorkers
from prb_post_request import GetPrbWorkersPoolsData
from prb_post_request import PostPrbRestartLifecycle

import re
# from time import sleep


def restart_workers_lifecycle(ip_port):
    """

    :param ip_port:
    :return:
    """

    workers_data = None
    if isinstance(ip_port, dict):
        (monitor_ip_port, prb_ip), = ip_port.items()
        try:
            workers_data = PrbGetWorkersStatus(ip_port=monitor_ip_port,
                                               prb_ip_port=prb_ip
                                               ).result['data']['workerStates']
            # print(workers_data)
        except KeyError:
            pass
    else:
        cls_get = GetPrbWorkersPoolsData(ip_port)
        workers_data = cls_get.get_workers_data()
        # print(workers_data)

    if workers_data is not None:
        # mis_and_timeout = []
        for data in workers_data:
            # print(data)
            try:
                worker_status = data['status']
                last_message = data['lastMessage']
                # print(last_message)
                if not (re.search('.+RequestError.+', last_message)
                        or re.search('.+ S_IDLE to S_STARTING', last_message)
                        or re.search('.+Error.+', last_message)):
                    block_heigh = data['paraBlockDispatchedTo']
                else:
                    block_heigh = 0

                uuid = data['worker']['uuid']
                uuid_list = list()

                # print(block_heigh, worker_status)

                # prb10
                if re.search('.+BlockNumberMismatch.+', last_message) or \
                        re.search('.+TimeoutError.+', last_message):
                    print(uuid)
                    # mis_and_timeout.append(uuid)
                    PostPrbRestartLifecycle.post_prb_restart_lifecycle(ip_port, uuid)

                # prb10和20, 卡-1的情况
                elif re.search('.+Notice: worker unresponsive.+', last_message) and block_heigh == -1:
                    print(uuid)
                    # prb10
                    PostPrbRestartLifecycle.post_prb_restart_lifecycle(ip_port, uuid)

                    # prb20
                    uuid_list.append(uuid)
                    (monitor_ip_port, prb_ip), = ip_port.items()
                    cls = MethodForWorkers(ip_port=monitor_ip_port,
                                           prb_ip_port=prb_ip)
                    cls.restart_worker(workers_list=[uuid])

                # prb20
                elif re.search('.+Error: timeout.+', last_message) or \
                        re.search('.+"Error: connect ECONNREFUSED.+', last_message) or \
                        re.search('.+"Error: connect EHOSTUNREACH.+', last_message) or \
                        re.search('.+"Error: connect ETIMEDOUT.+', last_message) or \
                        re.search('.+"BlockNumberMismatch".+', last_message) or \
                        re.search('.+Error while synching mq egress: Error: .+', last_message) or \
                        (block_heigh == -1 and worker_status == "S_SYNCHING"):
                    # re.search('.+Error while synching mq egress: Error: connect ETIMEDOUT.+', last_message) or \
                    # (re.search('.+Error while synching mq egress: TypeError: errorIndex.+', last_message) and
                    #  worker_status == 'S_MINING') or \
                    print(uuid)
                    uuid_list.append(uuid)
                    (monitor_ip_port, prb_ip), = ip_port.items()
                    cls = MethodForWorkers(ip_port=monitor_ip_port,
                                           prb_ip_port=prb_ip)
                    cls.restart_worker(workers_list=[uuid])

            except KeyError:
                pass

    # print(mis_and_timeout)

    # for uuid in mis_and_timeout:
    #     print(uuid)
    #     PostPrbRestartLifecycle.post_prb_restart_lifecycle(ip_port='192.168.3.239:3000', uuid=uuid)
    #     # sleep(3)


if __name__ == '__main__':
    pass
    prb_list = [
        # prb10
        '192.168.1.1:3000',
        '192.168.2.1:3000',
        # prb20, monitor_ip_port: lifecycle_ip
        {'192.168.3.1:3000': '127.0.0.1'},
        {'192.168.4.1:3000': '192.168.4.1'}
    ]
    for prb in prb_list:
        print(prb)
        restart_workers_lifecycle(prb)




