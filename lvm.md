# LVM磁盘处理

# ***数据无价，谨慎操作，一切后果自行承担***


## 内容列表
- [LVM介绍](#LVM介绍)
- [LVM创建与扩容](#LVM创建与扩容)
  - [LVM创建](#LVM创建)
    - [单独分区创建lVM](#单独分区创建LVM)
    - [单独磁盘创建LVM](#单独磁盘创建LVM)
  - [LVM扩容](#LVM扩容)
- [结合PHALA用户情况处理磁盘容量](#结合PHALA用户情况处理磁盘容量)
  - [完美布局：独立系统盘与独立数据盘](#完美布局：独立系统盘与独立数据盘)
  - [系统与数据共用一块盘](#系统与数据共用一块盘)
    - [无单独的数据分区](#无单独的数据分区)
    - [有单独的数据分区](#有单独的数据分区)
      - [单独的数据分区为lvm](#单独的数据分区为lvm)
      - [单独的数据分区非lvm](#单独的数据分区非lvm)
  - [其他磁盘布局情况](#其他磁盘布局情况)

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

>> 该分区为空数据分区，无数据存放，方可操作，否则后果自负  
> 
>>该分区如果存有需要数据，请迁移到其他分区目录保存后，方可操作

1. 查看块设备信息
```shell
# lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda      8:0    0  150G  0 disk 
├─sda1   8:1    0   50G  0 part /
└─sda2   8:5    0  100G  0 part /opt

# 如果待转换的分区已经挂载到了某个目录如/opt，需要先取消挂载
# umount /dev/sda2                      
```

2. 进入lvm
```shell
# 进入lvm操作终端，输入help，可以查看更多帮助
# lvm
lvm> help
```

3. 创建物理卷PV(Physical Volume)
```shell
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
  PV Size               100.00 GiB
  Allocatable           NO
  PE Size               0   
  Total PE              0
  Free PE               0
  Allocated PE          0
  PV UUID               qLwrce-jsUg-1nCe-URfb-W7IU-K7El-UJ3l0f
```

4. 创建VG卷组(Volume Group)
```shell
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
  VG Size               100.00 GiB
  PE Size               4.00 MiB
  Total PE              25590
  Alloc PE / Size       0 / 0   
  Free  PE / Size       25590 / 100.00 GiB
  VG UUID               brnxX3-XYO5-Ajsr-CkbG-rzeS-7uBq-4yrO9o
```

5. 扩展卷组
```shell
# 扩展卷组，是用来帮助扩展VG空间，VG空间不够用了，后期还可以动态添加更多的空间
# vgextend [已有卷组名(对应上面创建VG name: LVM)] [物理卷名(上面对应的/dev/sda2)]
lvm> vgextend LVM /dev/sda2             
  Physical volume '/dev/sda2' is already in volume group 'LVM'
  Unable to add physical volume '/dev/sda2' to volume group 'LVM'
  /dev/sdb2: physical volume not initialized.
```

6. 创建逻辑卷  
   - 以``GB``为单位创建逻辑卷，如果上面的VG Size 显示为100.00 GiB，可以直接采用，如果显示为 < 100.00 GiB，请采用PE创建逻辑卷
   - 以``PE``大小创建逻辑卷  
   - 二者采用其一即可，建议根据情况采用，多采用``PE``大小创建逻辑卷
   
> 使用GB为单位创建逻辑卷
```shell
# lvcreate –n [逻辑卷名(自定义)] –L [逻辑卷大小(VG Size对应的指标)] [要创建的 LV 所在的卷组名称(VG name对应名)]
lvm> lvcreate -n DB_DATA -L 100G LVM
Logical volume "LVM_DB_DATA" created
```
> 使用PE大小创建逻辑卷
```shell
# lvcreate –n [逻辑卷名] –l [物理扩展（PE）大小(上面对应的Free PE / Size对应的指标)] [要创建的 LV 所在的卷组名称]
lvm> lvcreate -n DB_DATA -l 25590 LVM 
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
  LV Size                <100.00 GiB
  Current LE             25590
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           254:0
```
至此，``lvm``整个创建过程完成，退出``lvm``命令行``exit``/``quit``，别着急，请**继续**往下看
```shell
lvm> 
lvm> exit
```
再次查看系统块设备信息，对应的``lvm``出现，说明``/dev/sda2``分区已经转换为``lvm``了，继续往下走
```shell
# lsblk
sda                   8:16   0   150G  0 disk 
├─sda1                8:17   0    50G  0 part  /
└─sda2                8:18   0   100G  0 part 
  └─LVM-DB_DATA 254:0    0   100G  0 lvm 
  
# 如果lsblk查看不到lvm的逻辑卷，可以尝试使用resize2fs命令刷新文件系统，或者重启系统
# resize2fs /dev/mapper/LVM-DB_DATA
```
  
7. 创建文件系统  
在创建有效的文件系统之前，是不能使用逻辑卷的，会无法挂载到其他目录  
创建文件系统时，必须指定逻辑卷名位置，否则对应块设备名，不能对应 ``/dev/sda2`` ，否则无法格式化  
这里使用 ``ext4`` 文件系统，其他文件系统，如 ``xfs`` 等，请使用 ``mkfs -t xfs /dev/mapper/LVM-DB_DATA`` 命令  
```shell
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
```

8. 挂载
```shell
# 手动挂载
# mount /dev/mapper/LVM-DB_DATA /opt

# 配置开机启动自动挂载
# cat /etc/fstab 
/dev/LVM/DB_DATA  /opt  ext4  defaults  0   1

# 查看挂载的lvm卷
# df -hT 
/dev/mapper/LVM-DB_DATA ext4      99.8G   24K  99.3G   1% /opt
```
至此，整个lvm的创建过程，才最终完成

参照：  
[国内相关文档](https://linux.cn/article-12670-1.html)  
[国外相关文档](https://www.2daygeek.com/create-lvm-storage-logical-volume-manager-in-linux/)

- #### 单独磁盘创建LVM 
单独磁盘创建lvm，其实和单独分区创建lvm，没有什么区别，按照上面的步骤，将``/dev/sda2`` 换成你的块设备名，通过 ``lsblk`` 查看系统新加入的磁盘  
> 如：新增了一块SATA盘：``/dev/sdb`` , 将``/dev/sda2`` 换成 ``/dev/sdb``，进行操作  
> 如：新增了一块固态盘：``/dev/nvme0n1`` , 将``/dev/sda2`` 换成 ``/dev/nvme0n1``，进行操作


- ### LVM扩容
如果系统中，没有进行过任何块设备的lvm转换，同时新增了一块磁盘作为专用数据存储，有将其转换为lvm的需求，请参考上面 [单独磁盘创建LVM](#单独磁盘创建LVM) 步骤来进行  

如果系统中，已经存在了块设备的lvm转换，新增一块磁盘，但是又作为不同的数据存储，想区分已经存在的``lvm``，可以设置不同的卷组，请参考上面 [单独分区创建LVM](#单独分区创建LVM) 步骤，请设置不同的``VG卷组名`` 和 ``逻辑卷名``，来区分已经存在的``VG卷组`` 和 ``逻辑卷名``，来达到不同的专用数据存储目录，方便后期数据动态扩容磁盘

如果系统中，已经存在了块设备的``lvm``转换，但是该``lvm``对应的``VG卷组名``下的``逻辑卷``不够用了，新增一块磁盘，来进行动态扩容，请参考以下步骤：  
如：我们将给上面的``/dev/sda2``对应的``VG卷组``中的``逻辑卷``进行扩容，新增一块100G大小的磁盘``/dev/sdb``，来进行演示
```shell
# 查看系统新增的块设备信息
# lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda      8:0    0  150G  0 disk 
├─sda1   8:1    0   50G  0 part /
└─sda2   8:5    0  100G  0 part /opt
sdb      8:16   0  100G  0 disk
```
这一步``/dev/sda2`` 以及挂载好了，无需取消挂载，只需要确定新增磁盘``/dev/sdb`` 未挂载即可

进入lvm
```shell
# lvm
```

创建PV
```shell
# 该命令，会格式化/dev/sdb磁盘，请核对好块设备对应磁盘名
# 但不会影响/dev/sda2对应的逻辑卷里面的数据，从而来实现不停机，不停服务，给逻辑卷的动态扩容
lvm> pvcreate /dev/sdb
  Physical volume "/dev/sdb" successfully created.
# 查看PV信息  
lvm> pvdisplay /dev/sdb
  "/dev/sdb" is a new physical volume of "100.00 GiB"
  --- NEW Physical volume ---
  PV Name               /dev/sdb
  VG Name               
  PV Size               100.00 GiB
  Allocatable           NO
  PE Size               0   
  Total PE              0
  Free PE               0
  Allocated PE          0
  PV UUID               MwEbyg-Pj3o-xHfo-6Ri6-fQv7-eDIf-meYP2H
```

扩展卷组，逻辑卷``LVM`` 对应之前定义的卷组名``VG Name``
```shell
lvm> vgextend LVM /dev/sdb
  Volume group "LVM" successfully extended
# 查看扩展卷组信息
lvm> vgdisplay
  --- Volume group ---
  VG Name               LVM
  System ID             
  Format                lvm2
  Metadata Areas        2
  Metadata Sequence No  3
  VG Access             read/write
  VG Status             resizable
  MAX LV                0
  Cur LV                1
  Open LV               0
  Max PV                0
  Cur PV                2
  Act PV                2
  VG Size               199.99 GiB
  PE Size               4.00 MiB
  Total PE              51180
  Alloc PE / Size       25590 / <100.00 GiB
  Free  PE / Size       25590 / <100.00 GiB
  VG UUID               HwURLY-JDrg-il1S-YRD3-WrVo-suly-zoHHVO
```
扩展逻辑卷
```shell
# 先查看当前存在的逻辑卷信息
lvm> lvdisplay
  --- Logical volume ---
  LV Path                /dev/LVM/DB_DATA
  LV Name                DB_DATA
  VG Name                LVM
  LV UUID                oVBdGa-UtWj-jxwT-tIIA-eIDH-2hBD-SNLevv
  LV Write Access        read/write
  LV Creation host, time kali, 2022-03-03 15:07:34 +0800
  LV Status              available
  # open                 0
  LV Size                <100.00 GiB
  Current LE             25590
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           254:0
``` 
再扩展逻辑卷，这里采用PE大小，下面的25590，从``vgdisplay``中的 ``Free  PE / Size`` 获取
```shell
lvm> lvextend -l +25590 /dev/LVM/DB_DATA
  Size of logical volume LVM/DB_DATA changed from <100.00 GiB (25590 extents) to 199.99 GiB (51180 extents).
  Logical volume LVM/DB_DATA successfully resized.
```
再次查看 ``PV`` 信息，``/dev/sda2``和``/dev/sdb`` 已经同属于一个 ``VG Name``下面
```shell
lvm> pvdisplay 
  --- Physical volume ---
  PV Name               /dev/sda2
  VG Name               LVM
  PV Size               <100.00 GiB / not usable 2.98 MiB
  Allocatable           yes (but full)
  PE Size               4.00 MiB
  Total PE              25590
  Free PE               0
  Allocated PE          25590
  PV UUID               9wsi1p-oZB6-cdm8-xQWA-NZEf-RabT-dimpiz
   
  --- Physical volume ---
  PV Name               /dev/sdb
  VG Name               LVM
  PV Size               100.00 GiB / not usable 4.00 MiB
  Allocatable           yes (but full)
  PE Size               4.00 MiB
  Total PE              25590
  Free PE               0
  Allocated PE          25590
  PV UUID               MwEbyg-Pj3o-xHfo-6Ri6-fQv7-eDIf-meYP2H
```
再次查看 ``LV`` 信息，``/dev/LVM/DB_DATA`` 逻辑卷已经扩容到199.99GB，就是我们要从100G扩容到了200G
```shell
lvm> lvdisplay 
  --- Logical volume ---
  LV Path                /dev/LVM/DB_DATA
  LV Name                DB_DATA
  VG Name                LVM
  LV UUID                oVBdGa-UtWj-jxwT-tIIA-eIDH-2hBD-SNLevv
  LV Write Access        read/write
  LV Creation host, time kali, 2022-03-03 15:07:34 +0800
  LV Status              available
  # open                 0
  LV Size                199.99 GiB
  Current LE             51180
  Segments               2
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           254:0
```
完成逻辑卷扩容，退出``exit``
```shell
lvm> exit
```

再次查看块设备信息
```shell
# lsblk
sda               8:0    0    150G  0 disk 
├─sda1            8:1    0     50G  0 part /
└──sda2            8:2   0    100G  0 part 
   └─LVM-DB_DATA 254:0   0    100G  0 lvm  /opt
sdb               8:16   0    100G  0 disk 
└─LVM-DB_DATA 253:0      0    100G  0 lvm  /opt

# 如果查看不到新创建的lvm信息，可以使用resize2fs来刷新文件系统
# resize2fs /dev/mapper/LVM-DB_DATA
```
这里便已经结束，**无需再次格式化**(否则会格式化之前创建好的 ``逻辑卷`` 中已有的数据)，也无需再次执行挂载和配置开机挂载


## 结合PHALA用户情况处理磁盘容量

### 完美布局：独立系统盘与独立数据盘
个人认为比较完美的磁盘布局：``独立的系统盘`` + ``独立的数据盘``，钱多事少，自由多  
对于Phala用户，我个人建议``独立的系统盘``控制到``120G``，``独立的数据盘`` 至少 ``2T+``，同时``独立的数据盘``转换为``lvm``，或者多块1T的数据盘并为一组逻辑卷组

### 系统与数据共用一块盘
#### 无单独的数据分区
  - 该情况：即``/``分区作为数据存放的目录，如果``/``分区空间不足，先清理系统无用文件，释放一定空间，但仅仅无法满足需求，对于此，在保留系统文件的情况下，只能添加新磁盘来达到更多的使用空间，最好将新磁盘转换为lvm，方便后期动态扩容


  - 你需要准备一个刻录Ubuntu18.04桌面版或者Ubuntu20.04桌面版的U盘系统，尽量使用桌面版系统刻录U盘，当然也可以使用命令行，相对来说比较麻烦
  

  - 对于phala用户，假设``phala-node``默认数据目录：``/var/khala-dev-node``，``phala-runtime-bridge``数据目录：``/opt/bridge_data``(该目录应该用户自己指定的位置，请核对)
  

  - 具体步骤：  
    - 保持当前系统和数据目录不变，将新磁盘插入系统，将新磁盘(假设为``/dev/nvme0n1``固态盘)转换为``lvm``，假设配置好后的逻辑卷路径为```/dev/mapper/LVM-DB_DATA```，参考 [单独磁盘创建LVM](#单独磁盘创建LVM)
    
    - 以下步骤，在用户**完成** [单独磁盘创建LVM](#单独磁盘创建LVM) 后，方可参考执行

    ```shell
    # 将 /dev/mapper/LVM-DB_DATA 挂载到一个临时目录，如 /mnt/ 目录
    umount /dev/mapper/LVM-DB_DATA
    mount /dev/mapper/LVM-DB_DATA /mnt/
    # 查看挂载情况
    lsblk
    ```
    ```shell
    # 停止 phala-node 服务，如果存在定时任务重启，请暂时注销
    sudo docker stop phala-node
    
    # 集群用户，还需要停止 phala-runtime-bridge（prb）所有组件，如果存在定时任务重启，请暂时注销
    sudo docker ps -a | grep bridge | awk '{print $1}' | xargs docker stop
    ```
    ```shell
    # 拷贝 phala-node数据 和 phala-runtime-bridge数据 到 新增磁盘 对应的逻辑卷上，并放置后台运行，这一步将花费数个小时时间
    nohup sudo rsync -avzP --progress --delete /var/khala-dev-node /opt/bridge_data /mnt/ &>./phala-data.txt &
    # 查看拷贝文件进度
    tail -f ./phala-data.txt
    
    # 这一步比较重要，为了数据完整性，当上面命令，执行数据拷贝完成后，请再次核对 phala-node 和 phala-runtime-bridge 程序是否停止运行，
    # 并再次运行一次上面的同步命令，这一步将为数据的完整性，起着很重要的步骤
    ```
    ```shell
    # 查看拷贝的文件目录
    ls -lha /mnt/
    
    # 查看文件大小
    du -sh /mnt/*
    ```
    ```shell
    # 数据彻底拷贝完整后，移除对应的 /var/khala-dev-node 和 /opt/bridge_data
    \rm -rf  /var/khala-dev-node  /opt/bridge_data
    ```
    ```shell
    # 将 /opt 目录下的所有文件，迁移到 /mnt/ ，这一步如果你的/opt目录下，没有存放其他大数据，这一步同步，可能只需要花费数分钟时间
    rsync -avzP --progress /opt/ /mnt/
    ```
    
    完成上面步骤后，接下来，就是将 / 分区多余的空间，新建分区，并加入新磁盘的逻辑卷组  
    这一步需要你自己负责，也可以联系我；将需要用到先前准备好的ubuntu对应的U盘系统, 如果你成功的调整好了``/`` 分区的大小，并将多余的空间新建了一个分区，切勿调整上面假设新增磁盘/dev/nvme0n1的分区大小，这里面目前都是phala的数据 [参考网络文献](https://blog.csdn.net/weixin_45464501/article/details/118727120)  
  
    完成上面步骤后，如果你能正常进入系统，表示上面步骤没问题  
    如果无法进入系统，没有关系，前面的几个步骤已经将你的phala数据备份到了新增磁盘/dev/nvme0n1的磁盘了，你只需要原来的重装系统
    
    当你正常进入系统后，我们接着往下走，我们将刚``/`` 多余的空间，新建了分区，接着将新建的分区，加入到新磁盘对应的``/dev/mapper/LVM-DB_DATA``逻辑卷组中，具体步骤参考 [单独分区创建lVM](#单独分区创建LVM) 

    至此，完成 [无单独的数据分区](#无单独的数据分区) 这种情况，新增磁盘、扩容磁盘等操作
  
#### 有单独的数据分区
###### 单独的数据分区为lvm
这种情况，有单独的数据分区，并且为lvm，意思就是，你将phala的所有数据都存放在了一个单独的数据分区里面，并且很幸运的是该分区还是lvm，那就通过新增更大的磁盘，来进行lvm的动态扩容处理，参考 [LVM扩容](#LVM扩容)

###### 单独的数据分区非lvm 
这种情况，与上面相反，phala的所有数据存在一个不是lvm的单独数据分区里面，其实也是新增磁盘、磁盘转lvm、数据迁移新盘、再将之前的单独数据分区转加入新盘的lvm卷组，只比 [无单独的数据分区](#无单独的数据分区)  少走一步``利用U盘进入系统调整/分区大小``


## 其他磁盘布局情况
欢迎补充


