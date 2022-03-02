#!/bin/bash


update_dns() {
	sed -ri '/^DNS=/d;/#DNS=/a DNS=8.8.8.8 114.114.114.114' /etc/systemd/resolved.conf
	systemctl enable systemd-resolved
	systemctl restart systemd-resolved
	mv /etc/resolv.conf /etc/resolv.conf.bak
	ln -s /run/systemd/resolve/resolv.conf /etc/
}

update_apt_source(){
cp -f /etc/apt/sources.list /etc/apt/sources.list.bak
if cat /etc/issue | grep "18." &>/dev/null ; then
	cat >/etc/apt/sources.list <<EOF
deb http://mirrors.aliyun.com/ubuntu bionic main restricted
deb http://mirrors.aliyun.com/ubuntu bionic-updates main restricted
deb http://mirrors.aliyun.com/ubuntu bionic universe
deb http://mirrors.aliyun.com/ubuntu bionic-updates universe
deb http://mirrors.aliyun.com/ubuntu bionic multiverse
deb http://mirrors.aliyun.com/ubuntu bionic-updates multiverse
deb http://mirrors.aliyun.com/ubuntu bionic-backports main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu bionic-security main restricted
deb http://mirrors.aliyun.com/ubuntu bionic-security universe
deb http://mirrors.aliyun.com/ubuntu bionic-security multiverse
EOF
elif cat /etc/issue | grep "20." &>/dev/null ; then
        cat >/etc/apt/sources.list <<EOF
deb http://mirrors.aliyun.com/ubuntu focal main restricted
deb http://mirrors.aliyun.com/ubuntu focal-updates main restricted
deb http://mirrors.aliyun.com/ubuntu focal universe
deb http://mirrors.aliyun.com/ubuntu focal-updates universe
deb http://mirrors.aliyun.com/ubuntu focal multiverse
deb http://mirrors.aliyun.com/ubuntu focal-updates multiverse
deb http://mirrors.aliyun.com/ubuntu focal-backports main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu focal-security main restricted
deb http://mirrors.aliyun.com/ubuntu focal-security universe
deb http://mirrors.aliyun.com/ubuntu focal-security multiverse
EOF
fi
}

update_system(){
    apt update 

    dkms remove sgx/1.41 --all
    rm -rf /var/lib/dpkg/lock*
    rm -rf /var/cache/apt/archives/lock
    dpkg --configure -a
    # 更新系统，可以跳过这一步 
    # apt dist-upgrade --fix-missing -y

    apt install -y net-tools git vim unzip zip lrzsz glances docker docker.io docker-compose expect
    # 开启子菜单选项，配置默认内核选项
    if cat /etc/issue | grep "18." &>/dev/null ; then
        apt install -y linux-headers-5.4.0-84-generic linux-image-5.4.0-84-generic linux-hwe-5.4-tools-5.4.0-84 linux-modules-5.4.0-84-generic linux-modules-extra-5.4.0-84-generic
	      cur_kernel=$(uname -r | awk -F'-[a-z]' '{print $1}')
        packages=`dpkg --list | grep linux | grep -E "5.8|5.11|$cur_kernel" | awk '{print $2}' | sed ':a;N;s/\n/ /g;ta'`
        if [ "$cur_kernel" == "5.4.0-84" ] ; then
                packages=`dpkg --list | grep linux | grep -E "5.8|5.11" | awk '{print $2}' | sed ':a;N;s/\n/ /g;ta'`
        fi
    elif cat /etc/issue | grep "20." &>/dev/null ; then
        apt install -y linux-headers-5.8.0-63-generic linux-image-5.8.0-63-generic linux-hwe-5.8-tools-5.8.0-63 linux-modules-5.8.0-63-generic linux-modules-extra-5.8.0-63-generic
	      # apt purge -y `dpkg --list | grep linux | grep -E "5.4|5.11|$(uname -r | awk -F'-[a-z]' '{print $1}')" | awk '{print $2}' | sed ':a;N;s/\n/ /g;ta'`
	      cur_kernel=$(uname -r | awk -F'-[a-z]' '{print $1}')
	      packages=`dpkg --list | grep linux | grep -E "5.4|5.11|5.8.0-59|$cur_kernel" | awk '{print $2}' | sed ':a;N;s/\n/ /g;ta'`
	      if [ "$cur_kernel" == "5.8.0-63" ] ; then
		        packages=`dpkg --list | grep linux | grep -E "5.4|5.11|5.8.0-59" | awk '{print $2}' | sed ':a;N;s/\n/ /g;ta'`
	      fi
    fi
}

remove_extra_kernel(){
    if cat /etc/issue | grep "18." &>/dev/null ; then
        # apt install -y linux-headers-5.4.0-84-generic linux-image-5.4.0-84-generic linux-hwe-5.4-tools-5.4.0-84 linux-modules-5.4.0-84-generic linux-modules-extra-5.4.0-84-generic
        cur_kernel=$(uname -r | awk -F'-[a-z]' '{print $1}')
        packages=`dpkg --list | grep linux | grep -E "5.8|5.11|$cur_kernel" | awk '{print $2}' | sed ':a;N;s/\n/ /g;ta'`
        if [ "$cur_kernel" == "5.4.0-84" ] ; then
                packages=`dpkg --list | grep linux | grep -E "5.8|5.11" | awk '{print $2}' | sed ':a;N;s/\n/ /g;ta'`
        fi

    elif cat /etc/issue | grep "20." &>/dev/null ; then
        # apt install -y linux-headers-5.8.0-63-generic linux-image-5.8.0-63-generic linux-hwe-5.8-tools-5.8.0-63 linux-modules-5.8.0-63-generic linux-modules-extra-5.8.0-63-generic
        # apt purge -y `dpkg --list | grep linux | grep -E "5.4|5.11|$(uname -r | awk -F'-[a-z]' '{print $1}')" | awk '{print $2}' | sed ':a;N;s/\n/ /g;ta'`
        cur_kernel=$(uname -r | awk -F'-[a-z]' '{print $1}')
        packages=`dpkg --list | grep linux | grep -E "5.4|5.11|5.8.0-59|$cur_kernel" | awk '{print $2}' | sed ':a;N;s/\n/ /g;ta'`
        if [ "$cur_kernel" == "5.8.0-63" ] ; then
                packages=`dpkg --list | grep linux | grep -E "5.4|5.11|5.8.0-59" | awk '{print $2}' | sed ':a;N;s/\n/ /g;ta'`
        fi
    fi
expect <<EOF
spawn sudo apt purge -y $packages
expect {
    "Package*" { send "\t\r" }
    "软件包设置*" { send "\t\r" }
    }
spawn sudo apt remove -y $packages
expect {
    "Package*" { send "\t\r" }
    "软件包设置*" { send "\t\r" }
    }
EOF
    apt autoremove -y 
    # update-grub
    # update-grub2

    # 建议更新内核后，手动reboot机器，即可生效最新内核
    # reboot
}

fixed_system_version(){
cur_kernel=$(uname -r | awk -F'-[a-z]' '{print $1}')
if [ "$cur_kernel" != "5.8.0-63" ] ; then
cp -f /etc/default/grub /etc/default/grub.bak
cat >/etc/default/grub <<EOF
# If you change this file, run 'update-grub' afterwards to update
# /boot/grub/grub.cfg.
# For full documentation of the options in this file, see:
#   info -f grub -n 'Simple configuration'

GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux 5.8.0-63-generic"
#GRUB_TIMEOUT_STYLE=hidden
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX=""

# Uncomment to enable BadRAM filtering, modify to suit your needs
# This works with Linux (no patch required) and with any kernel that obtains
# the memory map information from GRUB (GNU Mach, kernel of FreeBSD ...)
#GRUB_BADRAM="0x01234567,0xfefefefe,0x89abcdef,0xefefefef"

# Uncomment to disable graphical terminal (grub-pc only)
#GRUB_TERMINAL=console
EOF

apt autoremove -y 
update-grub
update-grub2

# reboot
fi
}

default_grub_conf(){
cp -f /etc/default/grub /etc/default/grub.bak
cat >/etc/default/grub <<EOF
# If you change this file, run 'update-grub' afterwards to update
# /boot/grub/grub.cfg.
# For full documentation of the options in this file, see:
#   info -f grub -n 'Simple configuration'

GRUB_DEFAULT=0
GRUB_TIMEOUT_STYLE=hidden
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX=""

# Uncomment to enable BadRAM filtering, modify to suit your needs
# This works with Linux (no patch required) and with any kernel that obtains
# the memory map information from GRUB (GNU Mach, kernel of FreeBSD ...)
#GRUB_BADRAM="0x01234567,0xfefefefe,0x89abcdef,0xefefefef"

# Uncomment to disable graphical terminal (grub-pc only)
#GRUB_TERMINAL=console

# The resolution used on graphical terminal
# note that you can use only modes which your graphic card supports via VBE
# you can see them in real GRUB with the command 'vbeinfo'
#GRUB_GFXMODE=640x480

# Uncomment if you don't want GRUB to pass "root=UUID=xxx" parameter to Linux
#GRUB_DISABLE_LINUX_UUID=true

# Uncomment to disable generation of recovery mode menu entries
#GRUB_DISABLE_RECOVERY="true"

# Uncomment to get a beep at grub start
#GRUB_INIT_TUNE="480 440 1"
EOF

update-grub
update-grub2

# reboot
}


update_ssh_config(){
    # # 修改ssh端口，为2201端口
    # sed -ri 's/^Port /d' /etc/ssh/sshd_config
    # sed -ri 's/#Port 22/Port 2201/' /etc/ssh/sshd_config

    # # 禁止root用户远程登录，只允许普通用户登录
    # sed -ri '/PermitRootLogin yes/d' /etc/ssh/sshd_config

    # 禁止空密码登录
    sed -ri '/PermitEmptyPasswords yes/d' /etc/ssh/sshd_config

    # 禁用DNS
    sed -ri 's/#UseDNS no|UseDNS yes/UseDNS no/g' /etc/ssh/sshd_config

    # 禁用GSSAPI认证，解决连接慢问题
    sed -ri 's/#GSSAPIAuthentication no|GSSAPIAuthentication yes/GSSAPIAuthentication no/g' /etc/ssh/sshd_config

    # 关闭第一次ssh远程输入yes问题
    sed -ri '/StrictHostKeyChecking no/d' /etc/ssh/ssh_config
    sed -ri '$a \ \ \ \ StrictHostKeyChecking no' /etc/ssh/ssh_config

    # 锁定失败次数的账号
    echo "auth required pam_tally2.so onerr=fail deny=6 unlock_time=30 even_deny_root root_unlock_time=100" >>/etc/pam.d/sshd 
    
    systemctl enable ssh.service 
    systemctl restart sshd.service
}

update_open_log(){
    sed -ri 's@^#cron\.\*@cron\.\*@g' /etc/rsyslog.d/50-default.conf
    sed -ri 's@^#daemon\.\*@daemon\.\*@g' /etc/rsyslog.d/50-default.conf
    sed -ri 's@^#lpr\.\*@lpr\.\*@g' /etc/rsyslog.d/50-default.conf 
    sed -ri 's@^#user\.\*@user\.\*@g' /etc/rsyslog.d/50-default.conf

    systemctl enable rsyslog.service
    systemctl restart rsyslog.service
}


update_firewall(){
    iptables -F
    systemctl stop firewalld.service
    systemctl disable firewalld.service 
    systemctl stop ufw.service
    systemctl disable ufw.service
}

update_security_auditd(){
    apt install -y auditd
    systemctl start auditd
    systemctl enable auditd
    chmod 700 /var/log/audit
    chmod 600 /var/log/audit/audit.log 
}

update_history(){
if [ ! -d /usr/share/.history ] ; then
    mkdir -p /usr/share/.history 
    chmod 777 /usr/share/.history
fi
if ! grep "history 命令历史加固" /etc/profile ; then
cat >> /etc/profile <<"EOF"
# set umask
umask=027

# set ssh TMOUT 10mins 
# export TMOUT=600
# readonly TMOUT

# history 命令历史加固
# 获取当前登录用户的IP地址
USER_IP=`who -u am i 2>/dev/null | awk '{print $NF}' | sed -e 's/[()]//g'` 

# 定义存储命令历史的目录位置
HISTDIR=/usr/share/.history

if [ -z $USER_IP   ]; then
    USER_IP=`hostname` 
fi

if [ ! -d $HISTDIR   ]; then
    mkdir -p $HISTDIR
    chmod 777 $HISTDIR
fi

# ${LOGNAME} 为系统变量，存储了当前登录用户的名字
if [ ! -d $HISTDIR/${LOGNAME} ]; then
    mkdir -p $HISTDIR/${LOGNAME}
    chmod 300 $HISTDIR/${LOGNAME}
fi


# set history format and file 
DT=`date +%Y%m%d`
export HISTTIMEFORMAT="%Y%m%d-%H%M%S  "
export HISTSIZE=50
export HISTFILESIZE=50
export HISTFILE="$HISTDIR/${LOGNAME}/${USER_IP}.$DT.history"
HISTCONTROL=ignoredups:ignorespace
shopt -s histappend
PROMPT_COMMAND='history -a'
shopt -s checkwinsize 

alias ll='ls -lha --color=auto'
export EDITOR=/usr/bin/vim
export VISUAL=/usr/bin/vim 
EOF
fi

if ! grep "\$HOME/.bash_history" /etc/skel/.bash_logout ; then
	echo "echo> \$HOME/.bash_history" >>/etc/skel/.bash_logout 
fi
}

set_trash_for_rm(){
    # set trash for rm -rf command

if ! grep "替换rm指令" /etc/profile ; then
cat >> /etc/profile <<"EOF"

# update rm (-r|-rf) command to mv file to $HOME/trash 
alias rm='trash'  
alias rl='trashlist' 
alias ur='undelfile' 
alias ct='cleartrash'

if [ ! -d $HOME/.trash  ] ; then
    mkdir -p $HOME/.trash
    chmod 777 $HOME/.trash
fi 

# 替换rm指令移动文件到$HOME/.trash/中
trash() 
{ 
        if echo $@ | grep -E "\-[a-zA-Z]{0,}r[a-zA-Z]{0,}" &>/dev/null; then
                all=$(for i in $@; do echo $i | grep -Ev '^-.*'; done)
                arg=$(for i in $@; do echo $i | grep -E '^-.*'; done | sed 's/r/f/g')
                mv $arg -u $all $HOME/.trash/ 
        else
                mv $@ $HOME/.trash/ 
        fi
} 
# 显示回收站中垃圾清单
trashlist() 
{
        echo -e "33[32m==== Garbage Lists in $HOME/.trash/ ====33[0m" 
        echo -e "\a33[33m----Usage------33[0m" 
        echo -e "\a33[33m-1- Use 'cleartrash' to clear all garbages in $HOME/.trash!!!33[0m" 
        echo -e "\a33[33m-2- Use 'ur' to mv the file in garbages to current dir!!!33[0m" 
        ls -al $HOME/.trash
}
# 找回回收站相应文件
undelfile() 
{
        mv -i $HOME/.trash/$@ ./
}
# 清空回收站
cleartrash() 
{ 
        echo -ne "\a33[33m!!!Clear all garbages in $HOME/.trash, Sure?[y/n]33[0m" 
        read confirm
        if [ $confirm == 'y' -o $confirm == 'Y' ] ;then
                /bin/rm -rf $HOME/.trash/*
                /bin/rm -rf $HOME/.trash/.* 2>/dev/null
        fi
}
EOF
fi
}

update_datetime_conf(){
    echo -e "NTP=ntp1.aliyun.com\nFallbackNTP=ntp.ubuntu.com" >> /etc/systemd/timesyncd.conf
    systemctl restart systemd-timesyncd
}

update_file_limits(){
if ! grep "\ 1048576\ " /etc/security/limits.conf ; then
cat >> /etc/security/limits.conf <<EOF
*		soft		nofile	1048576
*		hard		nofile	1048576
*		soft		nproc	1048576
*		hard		nproc	1048576
root		soft		nofile	1048576
root		hard		nofile	1048576
root		soft		nproc	1048576
root		hard		nproc	1048576
EOF
fi
}


update_sysctl(){
cp -f /etc/sysctl.conf /etc/sysctl.conf.bak
cat > /etc/sysctl.conf <<EOF

# 表示进程(比如一个worker进程)可以同时打开的最大句柄数，
# 这个参数直线限制最大并发连接数，需根据实际情况配置。
# fs.file-max = 999999

# 禁用整个系统所有接口的IPv6
net.ipv6.conf.all.disable_ipv6 = 1
# 默认关闭系统的ipv6
net.ipv6.conf.default.disable_ipv6 = 1

# 避免放大攻击
net.ipv4.icmp_echo_ignore_broadcasts = 1
# 开启恶意icmp错误消息保护
net.ipv4.icmp_ignore_bogus_error_responses = 1

# 禁止系统被ping
# net.ipv4.icmp_echo_ignore_all=1

# 不充当路由器
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# 开启反向路径过滤
net.ipv4.conf.all.rp_filter = 1
# 开启数据包的反向地址校验,可以防止IP欺骗，并减少伪造IP带来的DDoS问题
net.ipv4.conf.default.rp_filter = 1

# 开启并记录欺骗，源路由和重定向包
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# 处理无源路由的包
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0

# 确保无人能修改路由表
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0

# 如果该文件指定的值为非0，则激活sysctem request key。默认值：0。
kernel.sysrq = 0

# 默认coredump filename是“核心”。
# 通过设置core_uses_pid为1(默认值为0)，文件名的coredump成为核心PID。
# 如果core_pattern不包括“%p”（默认是不）和core_uses_pid设置。
# 那时pid将附加到文件名上。
kernel.core_uses_pid = 1

# 该文件指定在一个消息队列中最大的字节数 缺省设置：16384。
kernel.msgmnb = 65536

# 该文件指定了从一个进程发送到另一个进程的消息最大长度。
# 进程间的消息传递是在内核的内存中进行的。不会交换到硬盘上。
# 所以如果增加该值，则将增加操作系统所使用的内存数量。
kernel.msgmax = 65536

# 该参数定义了共享内存段的最大尺寸（以字节为单位）。默认是32M。
kernel.shmmax = 68719476736

# 该参数表示统一一次可以使用的共享内存总量（以页为单位）。默认是2097152，通常不需要修改。
kernel.shmall = 4294967296

# 这个参数表示操作系统允许TIME_WAIT套接字数量的最大值，
# 如果超过这个数字，TIME_WAIT套接字将立刻被清除并打印警告信息。
# 该参数默认为180000，过多的TIME_WAIT套接字会使Web服务器变慢。
net.ipv4.tcp_max_tw_buckets = 6000

# 使用 Selective ACK﹐它可以用来查找特定的遗失的数据报
# 因此有助于快速恢复状态。
# 该文件表示是否启用有选择的应答（Selective Acknowledgment），
# 这可以通过有选择地应答乱序接收到的报文来提高性能（这样可以让发送者只发送丢失的报文段）。
# (对于广域网通信来说这个选项应该启用，但是这会增加对 CPU 的占用。)
net.ipv4.tcp_sack = 1

# 打开FACK(Forward ACK) 拥塞避免和快速重传功能。
# (注意，当tcp_sack设置为0的时候，这个值即使设置为1也无效)
net.ipv4.tcp_fack = 1

# 滑动窗口因子，决定tcp传输数据的包大小
net.ipv4.tcp_window_scaling = 1

# TCP内存参数，3G，8G，16G
net.ipv4.tcp_mem = 786432 2097152 3145728
# 这个参数定义了TCP接受缓存(用于TCP接受滑动窗口)的最小值、默认值、最大值。
net.ipv4.tcp_rmem = 4096 4096 16777216
# 这个参数定义了TCP发送缓存(用于TCP发送滑动窗口)的最小值、默认值、最大值。
net.ipv4.tcp_wmem = 4096 4096 16777216

# 定义了系统中每一个端口最大的监听队列的长度,这是个全局的参数,默认值为128，
# 对于一个经常处理新连接的高负载 web服务环境来说，默认的 128 太小了。
# 大多数环境这个值建议增加到 1024 或者更多。大的侦听队列对防止拒绝服务 DoS 攻击也会有所帮助。
# net.core.somaxconn = 40960
net.core.somaxconn = 65535

# 这个参数表示内核套接字发送缓存区默认的大小。
net.core.wmem_default = 8388608
# 这个参数表示内核套接字接受缓存区默认的大小。
net.core.rmem_default = 8388608
# 这个参数表示内核套接字接受缓存区的最大大小。
net.core.rmem_max = 16777216
# 这个参数表示内核套接字发送缓存区的最大大小。
net.core.wmem_max = 16777216

# 每个网络接口接收数据包的速率比内核处理这些包的速率快时，允许送到队列的数据包的最大数目。
# net.core.netdev_max_backlog = 65535
net.core.netdev_max_backlog = 262144

# 表示系统中最多有多少TCP套接字不被关联到任何一个用户文件句柄上。
# 如果超过这里设置的数字，连接就会复位并输出警告信息。
# 这个限制仅仅是为了防止简单的DoS攻击。此值不能太小。
net.ipv4.tcp_max_orphans = 3276800

# 标示TCP三次握手建立阶段接受SYN请求队列的最大长度，默认为1024，
# 将其设置得大一些可以使出现Nginx繁忙来不及accept新连接的情况时，
# Linux不至于丢失客户端发起的连接请求。
# net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_max_syn_backlog = 262144

# 该参数用于设置时间戳，这可以避免序列号的卷绕，
# 在一个1Gb/s的链路上，遇到以前用过的序列号的概率很大。
# 当此赋值为0时，禁用对于TCP时间戳的支持，
# 在默认情况下，TCP 协议会让内核接受这种“异常”的数据包。
# 针对Nginx服务器来说，建议将其关闭
# net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_timestamps = 1

# 该参数用于设置内核放弃TCP链接之前向客户端发送SYN+ACK包的数量。
# 为了建立对端的连接服务，服务器和客户端需要进行三次握手，
# 第二次握手期间，内核需要发送SYN并附带一个回应前一个SYN的ACK ，
# 这个参数主要影响这个过程，一般赋值为1，即内核放弃链接之前发送一次SYN+ACK包
net.ipv4.tcp_synack_retries = 1

# 表示开启TCP连接中TIME-WAIT sockets的快速回收，默认为0，表示关闭。 
# 表示应用程序进行 connect() 系统调用时，在对方不返回 SYN + ACK 的情况下 (也就是超时的情况下)，
# 第一次发送之后，内核最多重试几次发送 SYN 包;并且决定了等待时间.
# 设置3次，等待超时时间为15s(2的4次方-1,单位是秒)
net.ipv4.tcp_syn_retries = 3

# 开启SYN Cookies，当出现SYN等待队列溢出时，启用cookies来处理
# 该参数与性能无关，用于解决TCP的SYN攻击。
net.ipv4.tcp_syncookies = 1

# prb内核优化
# 
net.ipv4.tcp_rfc1337 = 1
# 
vm.overcommit_memory = 1
# 
vm.nr_hugepages = 1
# 
vm.nr_hugepages = 0
# 
vm.nr_hugepages_mempolicy = 0
# 
vm.hugepages_treat_as_movable = 0
# 
vm.nr_overcommit_hugepages = 0

# 启用timewait快速回收
net.ipv4.tcp_tw_recycle = 1

# 开启重用。允许将TIME-WAIT, sockets重新用于新的TCP连接。这对于服务器来说很有意义，因为服务器上总会有大量TIME-WAIT状态的连接。
net.ipv4.tcp_tw_reuse = 1

# 表示如果套接字由本端要求关闭，这个参数决定了它保持在FIN-WAIT-2状态的时间。设置10s
# net.ipv4.tcp_fin_timeout = 20
net.ipv4.tcp_fin_timeout = 10

# TCP发送keepalive探测以确定该连接已经断开的次数。根据情形也可以适当地缩短此值。设置5次
net.ipv4.tcp_keepalive_probes = 5

# 探测消息发送的频率，乘以tcp_keepalive_probes就得到对于从开始探测以来没有响应的连接杀除的时间。
# 默认值为75秒，也就是没有活动的连接将在大约11分钟以后将被丢弃。
# 对于普通应用来说,这个值有一些偏大,可以根据需要改小.特别是web类服务器需要改小该值。
net.ipv4.tcp_keepalive_intvl = 30

# 这个参数表示当keepalive启用时，TCP发送keepalive消息的频度。默认是2小时，若将其设置的小一些，可以更快地清理无效的连接，设置30s
net.ipv4.tcp_keepalive_time = 30

# 允许系统打开的端口范围
net.ipv4.ip_local_port_range = 1024    65000
# net.ipv4.ip_local_port_range = 8000 65535
EOF

/sbin/sysctl -p
}

close_linux_update(){
# 法一
# 禁用系统更新
cp -f /etc/apt/apt.conf.d/20auto-upgrades /etc/apt/apt.conf.d/20auto-upgrades.bak
cat >/etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::AutocleanInterval "0";
APT::Periodic::Unattended-Upgrade "0";
EOF
# 开启系统更新
# cp /etc/apt/apt.conf.d/20auto-upgrades /etc/apt/apt.conf.d/20auto-upgrades.bak
# cat >/etc/apt/apt.conf.d/20auto-upgrades <<EOF
# APT::Periodic::Update-Package-Lists "2";
# APT::Periodic::Download-Upgradeable-Packages "1";
# APT::Periodic::AutocleanInterval "0";
# APT::Periodic::Unattended-Upgrade "1";
# EOF

# 法二
# 关闭内核更新
# sudo apt-mark hold linux-image-xx.x.x-xx-generic
# sudo apt-mark hold linux-headers-xx.x.x-xx-generic
# sudo apt-mark hold linux-modules-extra-xx.x.x-xx-generic
# 启动内核更新
# sudo apt-mark unhold linux-image-xx.x.x-xx-generic
# sudo apt-mark unhold linux-headers-xx.x.x-xx-generic
# sudo apt-mark unhold linux-modules-extra-xx.x.x-xx-generic
}


install_nvm_and_node(){
    tar -xf /tmp/nvm.tar.gz -C /opt/
if ! grep "配置nvm" /etc/profile ; then
    cat >>/etc/profile <<"EOF"

# 配置nvm切换多个node版本管理包
if [ ! -d $HOME/.nvm ] ; then
    cp -r /opt/.nvm $HOME/ 
fi 
export NVM_DIR="$HOME/.nvm"
# This loads nvm
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
# This loads nvm bash_completion
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
EOF
fi
    # source /etc/profile  
    # # nvm install node v14.17.5 
    # nvm install node
    # node -v
    # # nvm alias default v14.17.5
    # nvm alias default v14.17.5

    ln -s /opt/.nvm/versions/node/v16.7.0/bin/node /usr/bin/node
    rm -rf /tmp/nvm.tar.gz
}

update_docker_conf(){
    # if [ ! -f /etc/docker/daemon.json ] ; then
    #     touch /etc/docker/daemon.json
    #     chmod 755 /etc/docker/daemon.json 
    # fi 
    cp -rf /etc/docker/daemon.json /etc/docker/daemon.json.bak
    cat >/etc/docker/daemon.json <<EOF
{
    // "registry-mirrors": [
    //     "https://kfwkfulq.mirror.aliyuncs.com",
    //     "https://2lqq34jg.mirror.aliyuncs.com",
    //     "https://pee6w651.mirror.aliyuncs.com",
    //     "https://registry.docker-cn.com",
    //     "http://hub-mirror.c.163.com",
    //     "https://eiqg0bg0.mirror.aliyuncs.com"
    // ],
    "registry-mirrors": []

    "dns": ["114.114.114.114","8.8.8.8","8.8.4.4"],

    "log-driver":"json-file",
    "log-opts": { "max-size": "100m", "max-file": "5" },
    "log-level": "debug"  
}
EOF
systemctl daemon-reload
systemctl enable docker
systemctl restart docker
}

update_memory_clear(){
    cp -f /tmp/ReleaseMemory.sh /opt/ReleaseMemory.sh
    chmod 755 /opt/ReleaseMemory.sh
    echo "0 */3 * * * bash /opt/ReleaseMemory.sh" >/var/spool/cron/crontabs/root
    [ -f /tmp/ReleaseMemory.sh ] && rm -rf /tmp/ReleaseMemory.sh
}

config_network(){
    ethernet_name=`ip a  | grep ": e" | awk -F'[ :|: ]' '{print $3}' | head -n1`
    # ip=`ip a  | grep -A5 ": e" | awk '/ inet /{print $2}' | awk -F'[./]' '{print $1"."$2"."$3"."$4}' | head -n1`
    ip=`ip a  | grep -A5 ": e" | awk '/ inet /{print $2}' | head -n1`
    ip_route=`ip route | grep -E "default.*$ethernet_name" | awk '{print $3}'`

    cp -f /etc/netplan/01-network-manager-all.yaml /etc/netplan/01-network-manager-all.yaml.bak
    cat >/etc/netplan/01-network-manager-all.yaml <<EOF
# Let NetworkManager manage all devices on this system
network:
  version: 2
  # renderer: NetworkManager
  ethernets:
    $(ethernet_name):
      critical: true
      dhcp-identifier: mac
      dhcp4: false
      addresses:
        - $(ip)
      gateway4: $(ip_route)
      nameservers:
        addresses:
        - 114.114.114.114
        - 8.8.8.8
EOF
    netplan apply
}

config_hostname(){
	company="your_company_name"
	project="phala"
	group_num="groupX"

	ip_num=`ip a  | grep -A5 ": e" | awk '/ inet /{print $2}' | awk -F '[./]' '{print $3"-"$4}' | head -n1`
	
	hostnamectl set-hostname "${company}-${project}-${group_num}-${ip_num}"
	sed -ri '/Default/c '"127.0.1.1\t${company}-${project}-${group_num}-${ip_num}"'' /etc/hosts
}

clear_docker_and_uninstall_pha(){
	docker ps -aq | xargs docker stop | xargs docker rm
	docker images | grep -v "REPOSITORY" | awk '{print $3}' | xargs docker rmi -f 
	phala uninstall clean
	[ -d /opt/phala ] && \rm -rf /opt/phala
}


# 更新dns
update_dns					      # &>/dev/null

# 更新apt系统更新源
update_apt_source 				# &>/dev/null

# 更新内核到最新稳定版
# update_system					  # &>/dev/null

# 更新和优化ssh配置
update_ssh_config 				# &>/dev/null

# 更新系统日志审计
update_open_log 				  # &>/dev/null

# 关闭防火墙
update_firewall 				  # &>/dev/null

# 更新系统时间
update_datetime_conf 			# &>/dev/null

# 更新系统打开文件数
update_file_limits 				# &>/dev/null

# 更新和优化内核等参数
update_sysctl 					  # &>/dev/null

# 更新安全审计
update_security_auditd 		# &>/dev/null

# 更新历史命令记录
update_history 					  # &>/dev/null

# 替换rm -rf 命令，防止误删除
set_trash_for_rm 				  # &>/dev/null

# 关系系统更新
close_linux_update 				# &>/dev/null

# 安装nvm和管理node不同版本
install_nvm_and_node 			# &>/dev/null

# 更新docker配置，优化日志存储
update_docker_conf 				# &>/dev/null

# 更新内存定时清理
update_memory_clear 			# &>/dev/null

# 配置静态ip，未测试完毕# 
# config_network 				  # &>/dev/null

# 配置hostname
config_hostname					  # &>/dev/null

# 清理docker程序和镜像，卸载phala和目录
# clear_docker_and_uninstall_pha			# &>/dev/null



# 修复内核,1和2步
# 1、还原到5.8.63，并且重启系统
update_system
fixed_system_version
# # 2、上面第1步执行重启后，移除多余内核，还原默认grub配置
# remove_extra_kernel 
# default_grub_conf
rm -rf /tmp/init.sh
reboot
