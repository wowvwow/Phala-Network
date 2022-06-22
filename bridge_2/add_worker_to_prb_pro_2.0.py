#!/usr/bin/env python
# -*- coding:utf-8 -*-


# sys.path.append('..')
from prb_post_request_2 import AddWorkerAndPoolsToPrb


class AddWorker(object):
    def __init__(self, ip_port, mnemonic):
        self.ip_port = ip_port
        self.__mnemonic = mnemonic
        self.worker_cls = AddWorkerAndPoolsToPrb(self.ip_port)

    def add_pools(self, pid, mnemonic):
        pools = [
            {
                "name": f"{pid}",
                "pid": f"{pid}",
                "enabled": True,
                "syncOnly": False,
                "owner": {
                    "mnemonic": f"{mnemonic}"
                }
             },
        ]
        self.worker_cls.add_pools_to_prb(pools)

    def add_workers(self, prbs_txt, pid):
        '''
        创建workers
        :param prbs_txt:
        :param pid:
        :return:
        '''
        workers_list = []
        for line in open(prbs_txt, 'r'):
            name = line.replace('\n', '')
            workers_list.append(
                {
                    "pid": f"{pid}",
                    "name": f"{name}",
                    "endpoint": f"http://{name}:8000",
                    "stake": '10000000000000',
                    "enabled": True,
                    "syncOnly": False,
                }
            )
        print(workers_list)
        self.worker_cls.add_workers_to_prb(workers_list)

    def add_workers_for_each(self, single_prbs_txt, mnemonic):
        workers_list = []
        for line in open(single_prbs_txt, 'r'):
            line = line.replace('\n', '')
            pid = line.split(':')[0]
            name = line.split(':')[1]
            workers_list.append({"enabled": True,
                                 "syncOnly": False,
                                 "pid": f"{pid}",
                                 "name": f"{name}",
                                 "endpoint": f"http://{name}:8000",
                                 "stake": '10000000000000'})

            self.add_pools(pid=pid, mnemonic=mnemonic)

        print(workers_list)
        self.worker_cls.add_workers_to_prb(workers_list)


def add_worker_for_ip(txt, pid, mnemonic, ip_port='192.168.2.100:3000'):
    """
    执行要添加到同一个prb的worker，并且该文件下的worker属于同一个pid
    :param txt: 添加workers的文件
    :param pid: 你要添加的worker对应的pid号
    :param mnemonic: 助记词
    :param ip_port: prb-monitor的ip和端口
    :return:
    """
    a = AddWorker(ip_port=ip_port, mnemonic=mnemonic)
    a.add_pools(pid, mnemonic)
    a.add_workers(txt, pid)


def add_worker_for_pid_ip(txt, mnemonic, ip_port='192.168.3.100:3000'):
    """
    执行要添加到同一个prb的worker，并且该文件下的worker对应不同的pid，而这些pid使用同一个Gas账户，即同一个助记词
    :param mnemonic: 助记词
    :param ip_port: prb-monitor的ip和端口
    :param txt: 添加workers的文件，格式：pid:worker_ip, 如 88:192.168.2.1 , 一行一个
    :return:
    """
    a = AddWorker(ip_port, mnemonic)
    a.add_workers_for_each(txt, mnemonic)


if __name__ == '__main__':
    pass

    # '''示例代码'''
    # worker_ips.txt文件，放置要添加到同一个prb的worker对应的ip地址，一行一个
    # worker_pids_ips.txt文件，放置要添加到同一个prb的worker对应的pid和ip，以 : 分隔，一行一个

    your_pid = 83
    mnemonic1 = 'xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx'
    ip_port1 = '192.168.2.100:3000'
    add_worker_for_ip(pid=your_pid,
                      ip_port=ip_port1,
                      mnemonic=mnemonic1,
                      txt='./worker_ips.txt')

    mnemonic2 = 'xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx'
    ip_port2 = '192.168.3.100:3000'
    add_worker_for_pid_ip(ip_port=ip_port2,
                          mnemonic=mnemonic2,
                          txt='./worker_pids_ips.txt')

    # 其他情况，用户可自行添加