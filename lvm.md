# LVM磁盘处理

# ***数据无价，谨慎操作***


## 内容列表
- [LVM介绍](#LVM介绍)
- [LVM创建与扩容](#LVM创建与扩容)
  - [LVM创建](#LVM创建)
    - [单独分区创建lVM](#单独分区创建LVM)
    - [单独磁盘创建LVM](#单独磁盘创建LVM)
  - [LVM扩容](#LVM扩容)
- [结合PHALA用户情况处理磁盘容量](#结合PHALA用户情况处理磁盘容量)
  - [完美布局：独立系统盘+独立数据盘](#完美布局：独立系统盘+独立数据盘)
  - [系统+数据共用一块盘](#系统+数据共用一块盘)
    - [无单独的数据分区](#无单独的数据分区)
    - [有单独的数据分区](#有单独的数据分区)
      - [单独的数据分区为lvm](#单独的数据分区为lvm)
      - [单独的数据分区非lvm](#单独的数据分区非lvm)


## LVM介绍
每个Linux使用者在安装Linux时都会遇到这样的困境：在为系统分区时，如何精确评估和分配各个硬盘分区的容量，因为系统管理员不但要考虑到当前某个分区需要的容量，还要预见该分区以后可能需要的容量的最大值。因为如果估 计不准确，当遇到某个分区不够用时管理员可能甚至要备份整个系统、清除硬盘、重新对硬盘分区，然后恢复数据到新分区。 

虽然有很多动态调整磁盘的工具可以使用，例如PartitionMagic等等，但是它并不能完全解决问题，因为某个分区可能会再次被耗尽；另外一个方面这需要 重新引导系统才能实现，对于很多关键的服务器，停机是不可接受的，而且对于添加新硬盘，希望一个能跨越多个硬盘驱动器的文件系统时，分区调整程序就不能解决问题。

因此完美的解决方法应该是在零停机前提下可以自如对文件系统的大小进行调整，可以方便实现文件系统跨越不同磁盘和分区。幸运的是Linux提供的逻辑盘卷管理（LVM，LogicalVolumeManager）机制就是一个完美的解决方案。

引用：[LVM](https://baike.baidu.com/item/LVM/6571177)


## LVM创建与扩容
### LVM创建
整体步骤：
> a. 创建物理卷PV   
> 
> b. 创建卷组，将物理卷加入卷组  
> 
> c. 扩展卷组
> - 以 GB 为单位创建逻辑卷
> - 以 PE 大小创建逻辑卷
> 
> d. 创建文件系统
> 
> e. 挂载逻辑卷

需要安装：
```shell
sudo apt update
sudo apt install -y lvm2
```

- #### 单独分区创建LVM 
以下演示分区为``/dev/sda2``分区，该分区挂载``/opt``目录，我们现在将其转换为``lvm``，请注意，``/dev/sda2``，核对好你要转换的分区名  

该分区为空数据分区，无数据存放，方可操作，否则后果自负  

该分区如果存有需要数据，请迁移到其他分区目录保存后，方可操作

1. 查看块设备信息
```shell
# umount /dev/sda2                      # 如果待转换的分区已经挂载到了某个目录如/opt，需要先取消挂载

# lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda      8:0    0  100G  0 disk 
├─sda1   8:1    0   50G  0 part /
└─sda2   8:5    0   50G  0 part /opt

# 进入lvm操作终端，输入help，可以查看更多帮助
# lvm
lvm> help


# 创建物理卷PV(Physical Volume)
# 先查看一些是否存在PV，分区中没有lvm时，输出为空，往下执行
lvm> pvdisplay
                                      
# 创建LVM PV
# 创建PV命令，将删除给定磁盘分区上的所有数据，请谨慎执行
lvm> pvcreate /dev/sda2                 
WARNING: ext4 signature detected on /dev/sda2 at offset 1080. Wipe it? [y/n]: y
  Wiping ext4 signature on /dev/sda2.
  Physical volume "/dev/sda2" successfully created.
  
# 再次查看，返回如下信息，说明该分区已经添加到LVM PV中
lvm> pvdisplay                          
  "/dev/sda2" is a new physical volume of "50.00 GiB"
  --- NEW Physical volume ---
  PV Name               /dev/sda2
  VG Name               
  PV Size               50.00 GiB
  Allocatable           NO
  PE Size               0   
  Total PE              0
  Free PE               0
  Allocated PE          0
  PV UUID               qLwrce-jsUg-1nCe-URfb-W7IU-K7El-UJ3l0f


# 创建VG卷组(Volume Group)
# 卷组由你创建的 LVM 物理卷PV组成
# 你可以将物理卷添加到现有的卷组中，或者根据需要为物理卷创建新的卷组
# vgcreate  [卷组名(自定义)]  [物理卷名1(上面的/dev/sda2)]  [物理卷名2] ...
lvm> vgcreate LVM /dev/sda2             
  Volume group "LVM" successfully created
  
# 查看创建的卷组信息，可以看到VG名，VG Size，PE Size，Free PE / Size这几个重要参数
lvm> vgdisplay                          
  --- Volume group ---
  VG Name               LVM
  System ID             
  Format                lvm2
  Metadata Areas        1
  Metadata Sequence No  1
  VG Access             read/write
  VG Status             resizable
  MAX LV                0
  Cur LV                0
  Open LV               0
  Max PV                0
  Cur PV                1
  Act PV                1
  VG Size               50.00 GiB
  PE Size               4.00 MiB
  Total PE              2559
  Alloc PE / Size       0 / 0   
  Free  PE / Size       2559 / 50.00 GiB
  VG UUID               brnxX3-XYO5-Ajsr-CkbG-rzeS-7uBq-4yrO9o


# 扩展卷组
# 扩展卷组，是用来帮助扩展VG空间，VG空间不够用了，后期还可以动态添加更多的空间
# vgextend [已有卷组名(对应上面创建VG name: LVM)] [物理卷名(上面对应的/dev/sda2)]
lvm> vgextend LVM /dev/sda2             # 
  Physical volume '/dev/sda2' is already in volume group 'LVM'
  Unable to add physical volume '/dev/sda2' to volume group 'LVM'
  /dev/sdb2: physical volume not initialized.


# 创建逻辑卷
# 以GB为单位创建逻辑卷，如果上面的VG Size 显示为50.00 GiB，可以直接采用，如果显示为 < 50.00 GiB，请采用PE创建逻辑卷
# 以PE大小创建逻辑卷
# 二者采用其一即可，建议根据情况采用，多采用PE大小创建逻辑卷

# 法一：
# 使用GB为单位创建逻辑卷
# lvcreate –n [逻辑卷名(自定义)] –L [逻辑卷大小(VG Size对应的指标)] [要创建的 LV 所在的卷组名称(VG name对应名)]
lvm> lvcreate -n DB_DATA -L 50G LVM
Logical volume "LVM_DB_DATA" created

# 法二：
# 使用PE大小创建逻辑卷
# lvcreate –n [逻辑卷名] –l [物理扩展（PE）大小(上面对应的Free PE / Size对应的指标)] [要创建的 LV 所在的卷组名称]
lvm> lvcreate -n DB_DATA -l 2559 LVM 
  Logical volume "LVM_DB_DATA" created.

# 查看创建的逻辑卷信息，注意核对 LV Path(后期要开机挂载的路径)，LV Name，VG Name，LV Size, Current LE等参数
lvm> lvdisplay
  --- Logical volume ---
  LV Path                /dev/LVM/DB_DATA
  LV Name                DB_DATA
  VG Name                LVM
  LV UUID                BgVumx-YigN-b9qr-wXxN-cTRV-Nn80-8oBQzv
  LV Write Access        read/write
  LV Creation host, time kali, 2022-03-03 14:46:04 +0800
  LV Status              available
  # open                 0
  LV Size                <50.00 GiB
  Current LE             2559
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           254:0


# lvm整个创建过程完成，退出lvm命令行exit/quit
lvm> 
lvm> exit


# 再次查看系统块设备信息，对应的lvm出现，说明/dev/sda2分区已经转换为lvm了，继续往下走
# lsblk
sda                   8:16   0   100G  0 disk 
├─sda1                8:17   0   50G  0 part  /
└─sda2                8:18   0   50G  0 part 
  └─LVM-DB_DATA 254:0    0   50G  0 lvm 
  
  
# 创建文件系统
# 在创建有效的文件系统之前，是不能使用逻辑卷的，会无法挂载到其他目录
# 创建文件系统时，必须指定逻辑卷名位置，否则对应块设备名，不能对应 /dev/sda2 ，否则无法格式化
# 这里使用 ext4 文件系统，其他文件系统，如 xfs 等，请使用 mkfs -t xfs /dev/mapper/LVM-DB_DATA 命令
# mkfs.ext4 /dev/mapper/LVM-DB_DATA
mke2fs 1.46.4 (18-Aug-2021)
Creating filesystem with 2620416 4k blocks and 655360 inodes
Filesystem UUID: 4b897a22-215e-4e43-a0b9-276b21df077c
Superblock backups stored on blocks: 
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632

Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (16384 blocks): done
Writing superblocks and filesystem accounting information: done 


# 手动挂载
# mount /dev/mapper/LVM-DB_DATA /opt

# 配置开机启动自动挂载
# cat /etc/fstab 
/dev/LVM/DB_DATA  /opt  ext4  defaults  0   1

# 查看挂载的lvm卷
# df -hT 
/dev/mapper/LVM-DB_DATA ext4      9.8G   24K  9.3G   1% /opt


# 至此，完成整个lvm的创建过程
```
参照：  
[国内相关文档](https://linux.cn/article-12670-1.html)  
[国外相关文档](https://www.2daygeek.com/create-lvm-storage-logical-volume-manager-in-linux/)


- #### 单独磁盘创建LVM 
