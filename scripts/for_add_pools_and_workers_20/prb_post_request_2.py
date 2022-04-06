#!/usr/bin/env python
# -*- coding:utf-8 -*-


import requests
import json


class PrbPostRequestForDiscover(object):
    """

    """
    def __init__(self, ip_port):
        """

        :param ip_port:
        """
        self.url = f'http://{ip_port}/ptp/discover'
        self.referer = f'http://{ip_port}/discover'
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Connection": "keep-alive",
            "Host": f"{ip_port}",
            "Origin": f"http://{ip_port}",
            "Referer": f"{self.referer}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
        }
        self.data_provider_ips_peerid = dict()
        self.lifecycle_manager_ips_peerid = dict()

        try:
            self.resp = requests.post(self.url, headers=self.headers, timeout=120)
            self.resp_data = self.resp.json()
            self.resp.close()

            self.data_providers = self.resp_data['dataProviders']
            self.lifecycleManagers = self.resp_data['lifecycleManagers']

        except Exception as post_err:
            print('Failed: ', post_err)

    def get_data_provider_peer_id(self):
        for data_provider in self.data_providers:
            self.data_provider_ips_peerid[data_provider['remoteAddr'].split('/')[2]] \
                = data_provider['peerId']

        return self.data_provider_ips_peerid

    def get_lifecycle_managers_peer_id(self):
        for lifecycle_manager in self.lifecycleManagers:
            self.lifecycle_manager_ips_peerid[lifecycle_manager['remoteAddr'].split('/')[2]] = \
                lifecycle_manager['peerId']

        return self.lifecycle_manager_ips_peerid

    def get_resp_data(self, post_data):
        """

        :param post_data:
        :return:
        """
        try:
            if post_data != '':
                post_data = json.dumps(post_data)
            resp = requests.post(url=self.url, data=post_data, headers=self.headers, timeout=120)
            resp_data = resp.json()
            resp.close()

            return resp_data
        except Exception as post_err:
            return ['failed', post_err]


class PrbGetDpStatus(PrbPostRequestForDiscover):
    """
    Get Data Provider Info
    """
    def __init__(self, ip_port, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.data_provider_peer_id = self.get_data_provider_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.data_provider_peer_id}/GetDataProviderInfo'
        self.referer = f'http://{ip_port}/dp/status/{self.data_provider_peer_id}'
        self.result = super().get_resp_data('')


class PrbGetWorkersStatus(PrbPostRequestForDiscover):
    """
    Get Worker Status
    """
    def __init__(self, ip_port, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecycleManager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecycleManager_peer_id}/GetWorkerStatus'
        self.referer = f'http://{ip_port}/lifecycle/status/{self.lifecycleManager_peer_id}'
        self.result = super().get_resp_data({})


class PrbRestartWorkers(PrbPostRequestForDiscover):
    """
    Restart Worker
    """
    def __init__(self, ip_port, workers_list, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecycleManager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecycleManager_peer_id}/RestartWorker'
        self.referer = f'http://{ip_port}/lifecycle/status/{self.lifecycleManager_peer_id}'
        self.result = super().get_resp_data({"ids": workers_list})


class PrbKickWorkers(PrbPostRequestForDiscover):
    """
    Kick Worker
    """
    def __init__(self, ip_port, workers_list, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecycleManager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecycleManager_peer_id}/KickWorker'
        self.referer = f'http://{ip_port}/lifecycle/status/{self.lifecycleManager_peer_id}'
        self.result = super().get_resp_data({"ids": workers_list})


class PrbRefreshRaAndRestartWorkers(PrbPostRequestForDiscover):
    """
    Refresh Ra and Restart Workers
    """
    def __init__(self, ip_port, workers_list, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecycleManager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecycleManager_peer_id}/RefreshRaAndRestartWorker'
        self.referer = f'http://{ip_port}/lifecycle/status/{self.lifecycleManager_peer_id}'
        self.result = super().get_resp_data({"ids": workers_list})


class PrbGetListPool(PrbPostRequestForDiscover):
    """
    Get List of Pool
    """
    def __init__(self, ip_port, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecycleManager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecycleManager_peer_id}/ListPool'
        self.referer = f'http://{ip_port}/lifecycle/pools/{self.lifecycleManager_peer_id}'
        self.result = super().get_resp_data({})


class PrbGetListWorker(PrbPostRequestForDiscover):
    """
    Get List of Workers
    """
    def __init__(self, ip_port, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecycleManager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecycleManager_peer_id}/ListWorker'
        self.referer = f'http://{ip_port}/lifecycle/workers/{self.lifecycleManager_peer_id}'
        self.result = super().get_resp_data({})


class PrbCreatWorker(PrbPostRequestForDiscover):
    """
    Create Workers
    """
    def __init__(self, ip_port, workers_list, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecyclemanager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecyclemanager_peer_id}/CreateWorker'
        self.referer = f'http://{ip_port}/lifecycle/workers/{self.lifecyclemanager_peer_id}'
        # self.result = super().get_resp_data({"workers": workers_list})


class PrbUpdateWorker(PrbPostRequestForDiscover):
    """
    Update or Delete Workers
    """
    def __init__(self, ip_port, workers_list, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecyclemanager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecyclemanager_peer_id}/UpdateWorker'
        self.referer = f'http://{ip_port}/lifecycle/workers/{self.lifecyclemanager_peer_id}'
        # self.result = super().get_resp_data({"items": workers_list})


class PrbCreatPool(PrbPostRequestForDiscover):
    """
    Create Pools
    """
    def __init__(self, ip_port, pools_list, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecyclemanager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecyclemanager_peer_id}/CreatePool'
        self.referer = f'http://{ip_port}/lifecycle/pools/{self.lifecyclemanager_peer_id}'
        # self.result = super().get_resp_data({"pools": pools_list})


class PrbUpdatePool(PrbPostRequestForDiscover):
    """
    Update or Delete Pools
    """
    def __init__(self, ip_port, pools_list, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecyclemanager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecyclemanager_peer_id}/UpdatePool'
        self.referer = f'http://{ip_port}/lifecycle/pools/{self.lifecyclemanager_peer_id}'
        # self.result = super().get_resp_data({"items": pools_list})


class PrbDeletePool(PrbPostRequestForDiscover):
    """
    Delete Pools
    """
    def __init__(self, ip_port, pools_list, prb_ip_port='127.0.0.1'):
        super().__init__(ip_port)
        self.lifecyclemanager_peer_id = self.get_lifecycle_managers_peer_id()[prb_ip_port]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecyclemanager_peer_id}/UpdatePool'
        self.referer = f'http://{ip_port}/lifecycle/pools/{self.lifecyclemanager_peer_id}'
        # self.result = super().get_resp_data({"items": pools_list})


class AddWorkerAndPoolsToPrb(object):
    def __init__(self, ip_port, n=0):
        self.n = n
        self.ip_port = ip_port

    def add_pools_to_prb(self, pools_list):
        req = PrbCreatPool(self.ip_port, self.n)
        result = req.get_resp_data({"pools": pools_list})
        print(result)
        return result

    def add_workers_to_prb(self, workers_list):
        req = PrbCreatWorker(self.ip_port, self.n)
        result = req.get_resp_data({"workers": workers_list})
        print(result)
        return result


if __name__ == '__main__':
    pass

    """示例代码"""
    # # 获取dp_status
    # dp_status = PrbGetDpStatus('192.168.2.239:3000').result
    # print(dp_status)

    # # 获取pools_list
    # pools_list = PrbGetListPool('192.168.2.239:3000').result
    # print(pools_list)

    # # 获取workers_list
    # workers_list = PrbGetListWorker('192.168.2.239:3000').result
    # print(workers_list)

    # # 获取worker_status
    # worker_status = PrbGetWorkersStatus('192.168.2.239:3000').result
    # print(worker_status)

    # # 创建pools
    # ip_port = '192.168.5.239:3000'
    # mnemonic_staker = ''
    # pools = [{"name": "1903",
    #           "pid": "1903",
    #           "enabled": True,
    #           "syncOnly": False,
    #           "realPhalaSs58":"",
    #           "owner": {"mnemonic": f"{mnemonic_staker}"}}
    #          ]
    # a = PrbCreatPool(ip_port, pools).result
    # print(a)

    # # # 更新pools
    # ip_port = '192.168.2.239:3000'
    # pools = [
    #     {
    #         "id": {"uuid": "xxxx-xxxxxx-xxxxxxxxx-xxxxxxxxx"},
    #         "pool": {
    #             "pid": 123123,
    #             "name": "12312312311111111111111111",
    #             "realPhalaSs58": "",
    #             "enabled": True,
    #             "syncOnly": False
    #         }
    #     },
    # ]
    # a = PrbUpdatePool(ip_port, pools).result
    # print(a)

    # # # 删除pools
    # ip_port = '192.168.2.239:3000'
    # pools = [
    #     {
    #         "id": {"uuid": "xxxx-xxxx-xxxx-xxxxxxxxxx"},
    #         "pool": {"deleted": True}
    #      },
    # ]
    # a = PrbUpdatePool(ip_port, pools).result
    # print(a)

    # # 创建workers
    # ip_port = '192.168.2.239:3000'
    # workers = [{"enabled": True,
    #             "syncOnly": False,
    #             "pid": "1931",
    #             "name": "192.168.1.1",
    #             "endpoint": "http://192.168.1.1:8000",
    #             "stake": "10000000000000"}]
    # a = PrbCreatWorker(ip_port, workers_list=workers).result
    # print(a)

    # # 更新workers
    # ip_port = '192.168.2.239:3000'
    # workers = [
    #     {
    #         "id": {"uuid": "xxxx-xxxx-xxxx-xxxxxxxxxx"},
    #         "worker": {
    #             "pid": 1931,
    #             "name": "192.168.1.1111",
    #             "endpoint": "http://192.168.1.111:8000",
    #             "stake": "10000000000000",
    #             "enabled": True,
    #             "syncOnly": False
    #         }
    #     }
    # ]
    # a = PrbUpdateWorker(ip_port, workers_list=workers).result
    # print(a)

    # # 删除workers
    # ip_port = '192.168.2.239:3000'
    # workers = [
    #     {
    #         "id": {"uuid": "6fd18158-7957-442f-8385-0618a08e3404"}, "worker": {"deleted": True}
    #     }
    # ]
    # a = PrbUpdateWorker(ip_port, workers).result
    # print(a)

