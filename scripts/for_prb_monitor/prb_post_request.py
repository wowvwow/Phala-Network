#!/usr/bin/env python
# -*- coding:utf-8 -*-


import requests
import json


class PrbPostRequest:
    """

    """
    def __init__(self, ip_port):
        """

        :param ip_port:
        """
        self.url = f'http://{ip_port}/api/query_manager'
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Connection": "keep-alive",
            "Host": f"{ip_port}",
            "Origin": f"http://{ip_port}",
            "Referer": f"http://{ip_port}/workers",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
        }

    def get_resp_data(self, post_data):
        """

        :param post_data:
        :return:
        """
        try:
            resp = requests.post(self.url, data=json.dumps(post_data), headers=self.headers, timeout=120)
            resp_data = resp.json()
            resp.close()
            return resp_data
        except Exception as post_err:
            return ['filed', post_err]

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


class PrbPostRequestForFetcher(PrbPostRequest):
    """

    """
    def __init__(self, ip_port):
        super().__init__(ip_port)
        self.url = f'http://{ip_port}/api/query_fetcher'
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Connection": "keep-alive",
            "Host": f"{ip_port}",
            "Origin": f"http://{ip_port}",
            "Referer": f"http://{ip_port}/fetcher",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
        }


class PrbDataMethod:
    @staticmethod
    def get_fetcher_data():
        """
        ??????prb??????fetcher??????
        :return:
        """
        return {"callOnlineFetcher": {}}

    @staticmethod
    def get_workers_pools_data():
        """
        ??????prb??????workers???pools??????
        :return:
        """
        return {"callOnlineLifecycleManager": {}}

    # @staticmethod
    # def get_workers_pools_data_with_uuid(uuid):
    #     return {'callOnlineLifecycleManager': {'requests': [{'id': {'uuid': f'{uuid}'}}]}}

    @staticmethod
    def get_request_start_worker_lifecycle(uuid):
        """
        restart worker???lifecycle
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
        kill worker???pruntime???????????????pruntime
        :return:
        """
        return {
            "requestKickWorker": {"requests": [{"id": {"uuid": f"{uuid}"}}]}}

    @staticmethod
    def get_request_update_worker(uuid):
        """
        update worker???????????????
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
    #     """Delete worker??????"""
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
        ????????????pool???????????????
        :param pools_list:
        [
            {
                "name": f"{pool_name}",
                "pid": f"{pid}",
                "enabled": True,
                "owner": {"mnemonic": f"{mnemonic}"}
            }
        ]
        :return:
        """
        return {"requestCreatePool": {"pools": pools_list}}

    @staticmethod
    def get_request_create_worker(workers_list):
        """
        ????????????worker??????
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
        :return:
        """
        return {"requestCreateWorker": {"workers": workers_list}}


class GetPrbWorkersPoolsData:
    def __init__(self, ip_port):
        self.req = PrbPostRequest(ip_port)
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
            uuid_result = PrbPostRequest.get_uuid(uuid_data)
            post_data_query = {"queryWorkerState": {"ids": uuid_result}}
            prb_data = self.req.get_resp_data(post_data_query)['content']['workerStateUpdate']['workerStates']

            # print(prb_data)
            return prb_data


class GetPrbFetcherData(object):
    def __init__(self, ip_port):
        self.req = PrbPostRequestForFetcher(ip_port)
        self.post_data = PrbDataMethod.get_fetcher_data()
        self.post_result = self.req.get_resp_data(self.post_data)


class PostPrbRestartLifecycle(object):
    def __init__(self):
        pass

    @staticmethod
    def post_prb_restart_lifecycle(ip_port, uuid):
        req = PrbPostRequest(ip_port)
        post_data = PrbDataMethod.get_request_start_worker_lifecycle(uuid)
        req.get_resp_data(post_data)


class AddWorkerAndPoolsToPrb(object):
    def __init__(self, ip_port):
        self.req = PrbPostRequest(ip_port)

    def add_pools_to_prb(self, test):
        post_data = PrbDataMethod.get_request_create_pool(test)
        post_result = self.req.get_resp_data(post_data)

        # print(post_result)
        return post_result

    def add_workers_to_prb(self, workers_list):
        post_data = PrbDataMethod.get_request_create_worker(workers_list)
        post_result = self.req.get_resp_data(post_data)

        # print(post_result)
        return post_result


if __name__ == '__main__':
    pass
    # '''????????????'''
    # # prb-monitor??????????????????
    # ip_port = '192.168.2.100:3000'

    # # ??????prb??????pool??????
    # a = GetPrbWorkersPoolsData(ip_port).get_pools_data()
    # # ??????prb??????worker??????
    # b = GetPrbWorkersPoolsData(ip_port).get_workers_data()
    # print(a)
    # print(b)

    # # ??????pools?????????app????????????pid??????????????????????????????pid
    # mnemonic_for_83 = '83???pid????????????app???Gas??????????????????'
    # mnemonic_for_xx = 'xx???pid????????????app???Gas??????????????????'
    # pools = [{"name": "83", "pid": "83", "enabled": True, "owner": {"mnemonic": f"{mnemonic_for_83}"}},
    #          {"name": "xx", "pid": "xx", "enabled": True, "owner": {"mnemonic": f"{mnemonic_for_xx}"}},
    #          ]
    # a = AddWorkerAndPoolsToPrb(ip_port)
    # a.add_pools_to_prb(pools)

    # # ??????workers
    # workers = [{"enabled": True,
    #             "pid": "83",
    #             "name": "192.168.2.1",
    #             "endpoint": "http://192.168.2.1:8000",
    #             "stake": "10000000000000"}]
    # a.add_workers_to_prb(workers)
