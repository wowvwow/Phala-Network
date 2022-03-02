#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import requests
import json


def dingtalk(txt):
    print(txt)
    headers = {"Content-Type": "application/json"}
    data = {"msgtype": "text", "text": {"content": txt}}
    json_data = json.dumps(data)

    access_token = '1111111111111111111111111111111111111111111111111'
    requests.post(url=f'https://oapi.dingtalk.com/robot/send?access_token={access_token}',
                  data=json_data, headers=headers)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('python main.py 信息')
        exit(0)
    dingtalk(sys.argv[1])
