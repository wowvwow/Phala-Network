#!/usr/bin/env python
# -*- coding:utf-8 -*-


from prb_post_request import GetPrbWorkersPoolsData
from prb_post_request import PostPrbRestartLifecycle
import re
# from time import sleep


def restart_workers_lifecycle(ip_port):
    """

    :param ip_port:
    :return:
    """

    cls_get = GetPrbWorkersPoolsData(ip_port)
    workers_data = cls_get.get_workers_data()
    # print(workers_data)

    # mis_and_timeout = []
    for data in workers_data:
        # print(data)
        last_message = data['lastMessage']
        if not (re.search('.+RequestError.+', last_message) or
                re.search('.+ S_IDLE to S_STARTING', last_message)):
            block_heigh = data['paraBlockDispatchedTo']
        else:
            block_heigh = 0

        uuid = data['worker']['uuid']
        # print(block_heigh)

        if re.search('.+BlockNumberMismatch.+', last_message):
            print(uuid)
            # mis_and_timeout.append(uuid)
            PostPrbRestartLifecycle.post_prb_restart_lifecycle(ip_port, uuid)
        elif re.search('.+TimeoutError.+', last_message):
            print(uuid)
            # mis_and_timeout.append(uuid)
            PostPrbRestartLifecycle.post_prb_restart_lifecycle(ip_port, uuid)
        elif re.search('.+Notice: worker unresponsive.+', last_message) and block_heigh == -1:
            print(uuid)
            PostPrbRestartLifecycle.post_prb_restart_lifecycle(ip_port, uuid)

    # print(mis_and_timeout)


if __name__ == '__main__':
    pass
    # '''示例代码'''
    # # prb_list对应多个prb-monitore的ip和端口号
    # prb_list = ['192.168.2.1:3000', '192.168.3.1:3000', '192.168.4.1:3000']
    # for prb in prb_list:
    #     restart_workers_lifecycle(prb)




