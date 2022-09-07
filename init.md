# init System

此脚本用于刚安装的ubuntu18.04/20.04系统初始化配置，涉及系统基础优化、性能优化、安全优化等

## 内容列表

- [init System](#init-system)
  - [内容列表](#内容列表)
  - [重点提示](#重点提示)
  - [更新DNS](#更新dns)
  - [更新APT国内源](#更新apt国内源)
  - [更新稳定版内核](#更新稳定版内核)
  - [优化ssh配置](#优化ssh配置)
  - [关闭防火墙（不可后期运行）](#关闭防火墙不可后期运行)
  - [更新系统同步时间](#更新系统同步时间)
  - [优化系统文件数](#优化系统文件数)
  - [配置安全审计日志](#配置安全审计日志)
  - [配置历史命令记录](#配置历史命令记录)
  - [替换rm命令](#替换rm命令)
  - [禁用系统自动更新](#禁用系统自动更新)
  - [配置nvm管理多版本node](#配置nvm管理多版本node)
  - [优化docker配置](#优化docker配置)
  - [配置内存定期自动清理](#配置内存定期自动清理)
  - [配置静态IP](#配置静态ip)
  - [配置hostname](#配置hostname)
  - [清理docker程序和镜像以及phala程序](#清理docker程序和镜像以及phala程序)
  - [更新内核参数](#更新内核参数)

## 重点提示

>**该初始化脚本，在系统安装完毕后，未部署任何服务情况下，即刻执行为好**

## 更新DNS

更新系统DNS，为`8.8.8.8`和``114.114.114.114``，用户可自动替换为国内其他DNS，如阿里云公共DNS``223.5.5.5``和``223.6.6.6``等  

修改DNS的好处:

1. 适当提高上网速度；
2. 更换DNS可以访问某些因为域名解析存在问题而不能访问的网站；
3. 可以屏蔽运营商的广告，还可以帮助您避免被钓鱼的危险；

## 更新APT国内源

更新国内源，脚本默认涵盖了阿里云``ubuntu18``和``ubuntu20``更新源，会根据系统版本，自动更新源地址

## 更新稳定版内核

当刚完成系统后，发现内核不是最新版稳定内核(**ubuntu18.04**当前对应最新稳定版内核为``5.4.0-84``, **ubuntu20.04**当前对应最新稳定版内核为``5.8.0-63``)，可以执行该脚本对应的方法，脚本会自动识别系统版本，来更新对应的最新稳定版内核，更新内核涉及**机器重启**步骤，详细请看脚本，更新内核步骤会存在**一定风险**，如无法进入系统(引导菜单缺失导致)，但经过多次测试，暂未发现无法进入系统情况

## 优化ssh配置

1. 修改默认ssh端口号，脚本改行已注销
2. 禁止root用户登陆，防止权限过大
3. 禁止空密码登陆
4. 禁用DNS，优化ssh连接慢
5. 禁用``GSSAPI``认证，优化ssh连接慢
6. 关闭首次ssh远程需输入yes的提示
7. 锁定登陆失败次数的帐号，脚本默认：``普通用户``失败``6``次锁定``30s``时间，``root``用户失败``6``次后锁定``100s``时间

## 关闭防火墙（不可后期运行）

只能在系统安装完，即刻执行该函数，否则后期部署了程序再次执行，会清理``docker``程序对应的``iptables``，**后期执行，用户可注销脚本后面对应的该使用方法**

1. 清理``iptables``链表
2. 关闭``firewall``服务
3. 关闭``ufw``服务

## 更新系统同步时间

默认使用国内阿里云同步时间地址``ntp1.aliyun.com``，以保证时间一致性

## 优化系统文件数

系统默认最大文件数为``1024``，脚本默认为``1048576``

## 配置安全审计日志

开启auditd服务，即时控制审计守护进程的行为的工具，可自行添加规则，来记录系统安全行为

## 配置历史命令记录

优化历史命令记录，保存用户的历史命令，根据当前用户名和ip地址进行分类存放，目录```/usr/share/.history```

## 替换rm命令

替换``rm -r|rf`` 为 ``mv`` 对应的命令，使用rm删除文件，会保存到当前用户家目录下的```$HOME/.trash/```，防止因为意外情况误删除文件，可以再次找回文件； 当要真正删除某个文件时，请**谨慎**使用```\rm``` 来实现文件的真正销毁与删除

## 禁用系统自动更新

禁用系统自动更新，内核更新等，避免sgx驱动出现异常，导致pruntime程序无法启动

## 配置nvm管理多版本node

[nvm](https://github.com/nvm-sh/nvm) 是一个开源的管理多版本node程序的版本管理工具，phala程序使用``js``编写，需要依赖``node``(此``node``不是``phala-node``,请区别对待)，根据phala官方的更新情况，适当使用``nvm``调整和安装不同的``node``版本，来适应``phala``的程序，方便来回切换多个``node``版本，脚本默认使用的``node``版本为``v16.7.0``

## 优化docker配置

脚本内，默认注销了使用国内阿里云``docker``更新源，否则会导致``phala``的程序，无法拉取``dockerhub``中最新的``phala``程序镜像，同时配置了``docker``使用的``DNS``地址，以及``docker``容器的日志文件限制(默认脚本使用``json``格式，仅保留最新的``5``份日志文件，每个日志文件限制``100m``大小，以节省系统盘空间)

## 配置内存定期自动清理

[ReleaseMemory](scripts/init/ReleaseMemory.sh) 脚本  

配合定时任务执行

```shell
# 定时清理内存
0 */3 * * * bash /opt/ReleaseMemory.sh
```

## 配置静态IP

默认配置系统当前获取的ip地址，到系统网络配置文件

## 配置hostname

1. 示例``hostname``名： ``companyname—khala-group1-ip后缀``，如机器``ip``为 192.168.2.100： ``wantpool-phala-group1-2-100``
2. 当你``ssh``多个机器时，配置一个好``hostname``，可以明眼的区别``ssh``远程的机器，避免执行命令出现意外  
3. 该函数，需要用户修改``config_hostname``函数中``company``、``group_num``变量

## 清理docker程序和镜像以及phala程序

可不执行，注释即可

## 更新内核参数

可不执行，注释即可，仅供参考