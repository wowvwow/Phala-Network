#!/bin/bash


crt_time=`date +"%Y%m%d-%H%M%S"`
crt_ip=`ip a | grep -EA3 ".*: e.*:" | grep inet | awk '{print $2}' | awk -F'/' '{print $1}' | head -n1`


get_last_node_high(){
	# - $1:

	last_highest_khala_node_block=`cat .node_block_high.txt | sed -n 1p | awk -F':' '{print $1}'`
	last_khala_node_block=`cat .node_block_high.txt | sed -n 1p | awk -F':' '{print $2}'`

	last_highest_kusama_node_block=`cat .node_block_high.txt | sed -n 2p | awk -F':' '{print $1}'`
	last_kusama_node_block=`cat .node_block_high.txt | sed -n 2p | awk -F':' '{print $2}'`
}


get_crt_node_high() {
	# - $1: 传入服务器ip地址

	current_khala_node_block=$(curl -sH "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_syncState", "params":[]}' http://${1:-$crt_ip}:9933 | jq '.result.currentBlock')
	highest_khala_node_block=$(curl -sH "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_syncState", "params":[]}' http://${1:-$crt_ip}:9933 | jq '.result.highestBlock')
	
	current_kusama_node_block=$(curl -sH "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_syncState", "params":[]}' http://${1:-$crt_ip}:9934 | jq '.result.currentBlock')
	highest_kusama_node_block=$(curl -sH "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_syncState", "params":[]}' http://${1:-$crt_ip}:9934 | jq '.result.highestBlock')
	
	khala_diff_num=$[highest_khala_node_block-current_khala_node_block]
	kusama_diff_num=$[highest_kusama_node_block-current_kusama_node_block]
	
	echo "$highest_khala_node_block:$current_khala_node_block" >.node_block_high.txt
	echo "$highest_kusama_node_block:$current_kusama_node_block" >>.node_block_high.txt
}


restart_node_server(){
	# - $1:

	# solo用户
  docker restart phala-node

  # # 集群用户
	# docker ps -a | grep bridge | awk '{print $1}' | xargs docker stop
	# docker restart phala-node
	# docker ps -a | grep bridge | awk '{print $1}' | xargs docker start
	# docker restart bridge_fetch_1
}


monitor_node_high() {
  # - $1:
  #

	if [ ! -f .node_block_high.txt ] ; then
		get_crt_node_high
	else
		get_last_node_high
		get_crt_node_high

		info_same_high="当前服务器时间: $crt_time
当前服务器ip地址: $crt_ip

khala 当前node同步高度: $current_khala_node_block
khala 当前node最新高度: $highest_khala_node_block
khala 当前node高度相差: $khala_diff_num
；；
kusama当前node同步高度: $current_kusama_node_block
kusama当前node最新高度: $highest_kusama_node_block
kusama当前node高度相差: $kusama_diff_num
；；
由于5分钟内khala/kusama高度未发生变化，完成一次node服务重启
"

		# 高度相同，卡高度的情况
		if [ $current_khala_node_block -eq $last_khala_node_block -o $current_kusama_node_block -eq $last_kusama_node_block ] ; then
			restart_node_server
			python3 dingding.py "$info_same_high"
		fi
	fi
}


monitor_node_high
