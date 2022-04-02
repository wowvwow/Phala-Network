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
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Connection": "keep-alive",
            "Host": f"{ip_port}",
            "Origin": f"http://{ip_port}",
            "Referer": f"http://{ip_port}/discover",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
        }

        try:
            self.resp = requests.post(self.url, headers=self.headers, timeout=120)
            self.resp_data = self.resp.json()
            self.resp.close()
            print(self.resp_data)

            self.data_providers = self.resp_data['dataProviders']
            self.lifecycleManagers = self.resp_data['lifecycleManagers']
            # print(self.data_providers)
            # print(self.lifecycleManagers)

        except Exception as post_err:
            print('Failed: ', post_err)

    def get_status_data(self):
        for data_provider in self.data_providers:
            pass

    def get_resp_data(self, post_data):
        """

        :param post_data:
        :return:
        """
        try:
            resp = requests.post(self.url, data=json.dumps(post_data), headers=self.headers, timeout=120)
            resp_data = resp.json()
            resp.close()
            # print(resp_data)
            return resp_data
        except Exception as post_err:
            return ['failed', post_err]

    @staticmethod
    def get_uuid(uuid_data):
        """

        :param uuid_data:
        :return:
        """
        uuid_dict = {}
        uuid_list = []
        for data in uuid_data:
            uuid_dict['uuid'] = data['uuid']
            uuid_list.append(uuid_dict.copy())
        return uuid_list


class PrbCreatPool(PrbPostRequestForDiscover):
    def __init__(self, ip_port, n=0):
        super().__init__(ip_port)
        self.lifecyclemanager_peer_id = self.lifecycleManagers[n]["peerId"]
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecyclemanager_peer_id}/CreatePool'
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Connection": "keep-alive",
            "Host": f"{ip_port}",
            "Origin": f"http://{ip_port}",
            "Referer": f"http://{ip_port}/lifecycle/pools/{self.lifecyclemanager_peer_id}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
        }


class PrbCreatWorker(PrbCreatPool):
    def __init__(self, ip_port, n):
        super().__init__(ip_port, n)
        self.url = f'http://{ip_port}/ptp/proxy/{self.lifecyclemanager_peer_id}/CreateWorker'
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Connection": "keep-alive",
            "Host": f"{ip_port}",
            "Origin": f"http://{ip_port}",
            "Referer": f"http://{ip_port}/lifecycle/workers/{self.lifecyclemanager_peer_id}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
        }


# class PrbPostRequestForFetcher(PrbPostRequest):
#     """
#
#     """
#     def __init__(self, ip_port):
#         super().__init__(ip_port)
#         self.url = f'http://{ip_port}/api/query_fetcher'
#         self.headers = {
#             "Accept": "application/json, text/plain, */*",
#             "Accept-Encoding": "gzip, deflate",
#             "Accept-Language": "zh-CN,zh;q=0.9",
#             "Content-Type": "application/json;charset=UTF-8",
#             "Connection": "keep-alive",
#             "Host": f"{ip_port}",
#             "Origin": f"http://{ip_port}",
#             "Referer": f"http://{ip_port}/fetcher",
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
#         }


class PrbDataMethod:
    @staticmethod
    def get_fetcher_data():
        """
        请求prb所有fetcher信息
        :return:
        """
        return {"callOnlineFetcher": {}}

    @staticmethod
    def get_workers_pools_data():
        """
        请求prb所有workers和pools信息
        :return:
        """
        return {"callOnlineLifecycleManager": {}}

    # @staticmethod
    # def get_workers_pools_data_with_uuid(uuid):
    #     return {'callOnlineLifecycleManager': {'requests': [{'id': {'uuid': f'{uuid}'}}]}}

    @staticmethod
    def get_request_start_worker_lifecycle(uuid):
        """
        restart worker的lifecycle
        :param uuid:
        :return:
        """
        return {
            "requestStartWorkerLifecycle": {
                "requests": [{"id": {"uuid": f"{uuid}"}}]
            }
        }

    @staticmethod
    def get_request_kick_worker(uuid):
        """
        kill worker的pruntime，等于重启pruntime
        :return:
        """
        return {
            "requestKickWorker": {"requests": [{"id": {"uuid": f"{uuid}"}}]}}

    @staticmethod
    def get_request_update_worker(uuid):
        """
        update worker的相关信息
        :param uuid:
        :return:
        """
        return {
            "requestUpdateWorker": {
                "items": [
                    {"id": {"uuid": f"{uuid}"},
                        "worker": {
                            "uuid": f"{uuid}",
                            "pid": "1472",
                            "name": "192.168.50.101",
                            "endpoint": "http://192.168.50.100:8000",
                            "enabled": True,
                            "deleted": False,
                            "stake": "10000000000000"
                        }
                    }
                ]
            }
        }

    # @staticmethod
    # def get_request_update_worker_delete(uuid):
    #     """Delete worker信息"""
    #     return {
    #         "requestUpdateWorker": {
    #             "items": [
    #                 {"id": {"uuid": f"{uuid}"},
    #                  "worker": {
    #                      "uuid": "18571db4-abac-46ba-a647-cbccad424d08",
    #                      "pid": "88",
    #                      "name": "192.168.5.74",
    #                      "endpoint": "http://192.168.5.74:8000",
    #                      "enabled": true,
    #                      "deleted": true,
    #                      "stake": "10000000000000",
    #                      "status": "S_ERROR",
    #                      "worker": {
    #                          "uuid": "18571db4-abac-46ba-a647-cbccad424d08",
    #                          "pid": "88", "name": "192.168.5.74",
    #                          "endpoint": "http://192.168.5.74:8000",
    #                          "stake": "10000000000000"},
    #                      "lastMessage": "1636889212205 - xxxxxxxxxx}",
    #                      "minerInfoJson": "{}", "minerInfo": {}
    #                     }
    #                 }
    #             ]
    #         }
    #     }

    @staticmethod
    def get_request_create_pool(pools_list):
        """
        请求创建pool质押池信息
        :param pools_list:
        [
            {
                "pid": pid,
                "name": "pid_name",
                "realPhalaSs58": "",
                "enabled": true,
                "syncOnly": false,
                "owner": {"mnemonic": "mnemonic"}
            }
        ]
        :return:
        """
        return {"pools": pools_list}

    @staticmethod
    def get_request_create_worker(workers_list):
        """
        请求创建worker信息
        :param workers_list:
        [
            {
                "enabled": True,
                "pid": f"{pid}",
                "name": f"{name}",
                "endpoint": f"http://{name}:8000",
                "stake": f"{stake}"
            }
        ]
        [
            {
                "pid": f"{pid}",
                "name": f"{192.168.5.111}",
                "endpoint": f"http://{192.168.5.111}:8000",
                "stake": "10000000000000",
                "enabled": true,
                "syncOnly": false
            }
        ]
        :return:
        """
        return {"workers": workers_list}


class GetPrbWorkersPoolsData:
    def __init__(self, ip_port):
        self.req = PrbPostRequestForDiscover(ip_port)
        # self.post_data = PrbDataMethod.get_fetcher_data()
        self.post_data = PrbDataMethod.get_workers_pools_data()
        self.post_result = self.req.get_resp_data(self.post_data)

    def get_pools_data(self):
        """

        :return:
        """
        pools_data = self.post_result
        if type(pools_data) is list:
            pass
        try:
            uuid_data = pools_data['content']['lifecycleManagerStateUpdate']['pools']
            # print(uuid_data)
            # uuid_result = PrbPostRequest.get_uuid(uuid_data)
            # print(uuid_result)
        except KeyError as e:
            pass
        except TypeError as e:
            pass
        else:
            return uuid_data

    def get_workers_data(self):
        """

        :return:
        """
        workers_data = self.post_result
        # print(workers_data)
        # fetcher_cls = GetPrbFetcherData(ip__port)

        # manager_data = manager_cls.post_result
        # fetcher_data = fetcher_cls.post_data
        # print(manager_data)
        # print(fetcher_data)
        # exit()

        if type(workers_data) is list:
            pass
        try:
            uuid_data = workers_data['content']['lifecycleManagerStateUpdate']['workers']
        except KeyError as e:
            pass
        except TypeError as e:
            pass
        else:
            uuid_result = PrbPostRequestForDiscover.get_uuid(uuid_data)
            post_data_query = {"queryWorkerState": {"ids": uuid_result}}
            prb_data = self.req.get_resp_data(post_data_query)['content']['workerStateUpdate']['workerStates']

            # print(prb_data)
            return prb_data


# class GetPrbFetcherData(object):
#     def __init__(self, ip_port):
#         self.req = PrbPostRequestForFetcher(ip_port)
#         self.post_data = PrbDataMethod.get_fetcher_data()
#         self.post_result = self.req.get_resp_data(self.post_data)


class PostPrbRestartLifecycle(object):
    def __init__(self):
        pass

    @staticmethod
    def post_prb_restart_lifecycle(ip_port, uuid):
        req = PrbPostRequestForDiscover(ip_port)
        post_data = PrbDataMethod.get_request_start_worker_lifecycle(uuid)
        req.get_resp_data(post_data)


class AddWorkerAndPoolsToPrb(object):
    def __init__(self, ip_port, n=0):
        self.n = n
        self.ip_port = ip_port


    def add_pools_to_prb(self, pools_list):
        req = PrbCreatPool(self.ip_port, self.n)
        post_data = PrbDataMethod.get_request_create_pool(pools_list)
        post_result = req.get_resp_data(post_data)

        print(post_result)
        return post_result

    def add_workers_to_prb(self, workers_list):
        req = PrbCreatWorker(self.ip_port, self.n)
        post_data = PrbDataMethod.get_request_create_worker(workers_list)
        post_result = req.get_resp_data(post_data)

        print(post_result)
        return post_result


if __name__ == '__main__':
    '''示例代码'''
    # 获取pools和workers信息
    pass

    # 创建pools
    ip_port = '192.168.5.100:3000'
    mnemonic_pid = 'xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx'
    pools = [
        {
            "name": "88",
            "pid": "88",
            "enabled": True,
            "syncOnly": False,
            "owner": {
                "mnemonic": f"{mnemonic_pid}"}
        },
    ]

    a = AddWorkerAndPoolsToPrb(ip_port)
    a.add_pools_to_prb(pools)

    # 创建workers
    workers = [{"enabled": True,
                "syncOnly": False,
                "pid": "1500",
                "name": "192.168.5.100",
                "endpoint": "http://192.168.5.100:8000",
                "stake": "10000000000000"}]

    a.add_workers_to_prb(workers)
