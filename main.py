# Copyright (C) 2024 officialputuid

import asyncio
import datetime
import json
import random
import ssl
import time
import uuid
from loguru import logger
from websockets_proxy import Proxy, proxy_connect
import pyfiglet

logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=''),
    format=(
        "<green>{time:DD/MM/YY HH:mm:ss}</green> | "
        "<level>{level:8} | {message}</level>"
    ),
    colorize=True
)

# main.py
def print_header():
    cn = pyfiglet.figlet_format("xGrassBot")
    print(cn)
    print("🌱 第二季")

# 初始化标题
print_header()

# 使用的代理数量 /uid
ONETIME_PROXY = 100

# 读取 UID 和代理数量
def read_uid_and_proxy():
    with open('uid.txt', 'r') as file:
        uid_count = sum(1 for line in file)

    with open('proxy.txt', 'r') as file:
        proxy_count = sum(1 for line in file)

    return uid_count, proxy_count

uid_count, proxy_count = read_uid_and_proxy()

print()
print(f"🔑 UID: {uid_count}.")
print(f"🌐 加载了 {proxy_count} 个代理。")
print(f"🌐 每个任务加载的活跃代理: {ONETIME_PROXY} 个。")
print()

print("\033[1;31m🧩 桌面节点仍在开发中。请使用扩展/GrassLite！\033[0m")
print("\033[1;31m🧩 桌面节点仍在开发中。请使用扩展/GrassLite！\033[0m")
print("\033[1;31m🧩 桌面节点仍在开发中。请使用扩展/GrassLite！\033[0m \n")
print("\033[1;32m🧩 好吧，你已经读了三遍。你被警告了。\033[0m \n")

# 获取用户输入以处理代理失败
def get_user_input():
    user_input = ""
    while user_input not in ['yes', 'no']:
        user_input = input("🔵 如果出现特定故障，您想删除代理吗（yes/no）？ ").strip().lower()
        if user_input not in ['yes', 'no']:
            print("🔴 输入无效。请输入 'yes' 或 'no'。")
    return user_input == 'yes'

remove_on_all_errors = get_user_input()
print(f"🔵 您选择了: {'是' if remove_on_all_errors else '否'}, 祝您愉快！\n")

# 询问用户节点类型
def get_node_type():
    node_type = "extension"  # 默认值设置为 'extension'
    print(f"🧩 扩展 (1.25x 奖励), GrassLite (1.0x 奖励) 扩展/GrassLite")
    user_input = input("🔵 选择节点类型 (extension/grasslite) [回车默认选择 extension]: ").strip().lower()
    
    if user_input in ['grasslite']:
        node_type = user_input  # 如果用户输入 'grasslite'，则更新 node_type

    return node_type

node_type = get_node_type()
print(f"🔵 您选择了: {node_type.capitalize()} 节点。祝您愉快！\n")

def truncate_userid(user_id):
    return f"{user_id[:3]}--{user_id[-3:]}"

def truncate_proxy(proxy):
    return f"{proxy[:4]}--{proxy[-4:]}"

async def connect_to_wss(protocol_proxy, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, protocol_proxy))

    while True:
        try:
            await asyncio.sleep(random.uniform(0.1, 1.0))  # 减少频率
            custom_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            }
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            urilist = [
                "wss://proxy2.wynd.network:4444",
                "wss://proxy2.wynd.network:4650"
            ]
            uri = random.choice(urilist)
            server_hostname = uri.split("://")[1].split(":")[0]
            proxy = Proxy.from_url(protocol_proxy)

            if node_type == 'extension':
                async with proxy_connect(
                    uri,
                    proxy=proxy,
                    ssl=ssl_context,
                    server_hostname=server_hostname,
                    extra_headers={"Origin": "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi", "User-Agent": custom_headers["User-Agent"]}
                ) as websocket:
                    logger.success(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功连接到 WS，使用代理: {truncate_proxy(protocol_proxy)}")

                    async def send_ping():
                        while True:
                            send_message = json.dumps({
                                "id": str(uuid.uuid4()),
                                "version": "1.0.0",
                                "action": "PING",
                                "data": {}
                            })
                            logger.debug(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 发送 PING | ID: {json.loads(send_message)['id']}")
                            await websocket.send(send_message)
                            rand_sleep = random.uniform(10, 30)  # 随机延迟 + 减少带宽使用
                            logger.info(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功发送 PING | 下次在 {rand_sleep:.2f} 秒后")
                            await asyncio.sleep(rand_sleep)

                    await asyncio.sleep(1)
                    send_ping_task = asyncio.create_task(send_ping())

                    try:
                        while True:
                            response = await websocket.recv()
                            message = json.loads(response)
                            simply_message = {
                                'id': message.get('id'),
                                'action': message.get('action')
                            }
                            logger.info(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 收到消息: {simply_message}")

                            custom_date = datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

                            if message.get("action") == "AUTH":
                                auth_response = {
                                    "id": message["id"],
                                    "origin_action": "AUTH",
                                    "result": {
                                        "browser_id": device_id,
                                        "user_id": user_id,
                                        "user_agent": custom_headers['User-Agent'],
                                        "timestamp": int(time.time()),
                                        "device_type": "extension",
                                        "version": "4.26.2",
                                        "extension_id": "lkbnfiajjmbhnfledhphioinpickokdi"
                                    }
                                }
                                logger.debug(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 发送 AUTH | ID: {auth_response['id']} | 版本: {auth_response['result']['version']}")
                                await websocket.send(json.dumps(auth_response))
                                logger.success(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功 AUTH，设备 ID: {device_id}")
                            elif message.get("action") == "PONG":
                                pong_response = {"id": message["id"], "origin_action": "PONG"}
                                logger.debug(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 发送 PONG: {pong_response}")
                                await websocket.send(json.dumps(pong_response))
                                logger.success(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功发送 PONG | ID: {pong_response['id']} | 动作: {pong_response['origin_action']}")
                            elif message.get("action") == "HTTP_REQUEST":
                                http_request_response = {"id": message["id"], "origin_action": "HTTP_REQUEST"}
                                logger.debug(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 发送 HTTP_REQUEST: {http_request_response}")
                                await websocket.send(json.dumps(http_request_response))
                                logger.success(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功发送 HTTP_REQUEST | ID: {http_request_response['id']} | 动作: {http_request_response['origin_action']}")
                            elif message.get("action") == "OPEN_TUNNEL":
                                opentunnel_request_response = {
                                    "id": message["id"],
                                    "origin_action": "OPEN_TUNNEL",
                                    "result": {
                                        "url": message["url"],
                                        "status": 200,
                                        "status_text": "OK",
                                        "headers": {
                                            "content-type": "application/json; charset=utf-8",
                                            "date": custom_date,
                                            "keep-alive": "timeout=5",
                                            "proxy-connection": "keep-alive",
                                            "x-powered-by": "Express",
                                        }
                                    }
                                }
                                logger.debug(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 发送 OPEN_TUNNEL: {opentunnel_request_response}")
                                await websocket.send(json.dumps(opentunnel_request_response))
                                logger.success(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功发送 OPEN_TUNNEL | ID: {opentunnel_request_response['id']} | 动作: {opentunnel_request_response['origin_action']}")
                    except websockets.exceptions.ConnectionClosedError as e:
                        logger.error(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 连接关闭错误 | 代理: {truncate_proxy(protocol_proxy)} | 错误: {str(e)[:30]}**")
                    finally:
                        await websocket.close()
                        logger.warning(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | WebSocket 连接关闭 | 代理: {truncate_proxy(protocol_proxy)}")
                        send_ping_task.cancel()
                        break

            elif node_type == 'grasslite':
                async with proxy_connect(
                    uri,
                    proxy=proxy,
                    ssl=ssl_context,
                    server_hostname=server_hostname,
                    extra_headers={"Origin": "chrome-extension://ilehaonighjijnmpnagapkhpcdbhclfg", "User-Agent": custom_headers["User-Agent"]}
                ) as websocket:
                    logger.success(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功连接到 WS，使用代理: {truncate_proxy(protocol_proxy)}")

                    async def send_ping():
                        while True:
                            send_message = json.dumps({
                                "id": str(uuid.uuid4()),
                                "version": "1.0.0",
                                "action": "PING",
                                "data": {}
                            })
                            logger.debug(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 发送 PING | ID: {json.loads(send_message)['id']}")
                            await websocket.send(send_message)
                            rand_sleep = random.uniform(10, 30)  # 随机延迟 + 减少带宽使用
                            logger.info(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功发送 PING | 下次在 {rand_sleep:.2f} 秒后")
                            await asyncio.sleep(rand_sleep)

                    await asyncio.sleep(1)
                    send_ping_task = asyncio.create_task(send_ping())

                    try:
                        while True:
                            response = await websocket.recv()
                            message = json.loads(response)
                            simply_message = {
                                'id': message.get('id'),
                                'action': message.get('action')
                            }
                            logger.info(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 收到消息: {simply_message}")

                            custom_date = datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

                            if message.get("action") == "AUTH":
                                auth_response = {
                                    "id": message["id"],
                                    "origin_action": "AUTH",
                                    "result": {
                                        "browser_id": device_id,
                                        "user_id": user_id,
                                        "user_agent": custom_headers['User-Agent'],
                                        "timestamp": int(time.time()),
                                        "device_type": "extension",
                                        "version": "4.26.2",
                                        "extension_id": "ilehaonighjijnmpnagapkhpcdbhclfg"
                                    }
                                }
                                logger.debug(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 发送 AUTH | ID: {auth_response['id']} | 版本: {auth_response['result']['version']}")
                                await websocket.send(json.dumps(auth_response))
                                logger.success(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功 AUTH，设备 ID: {device_id}")
                            elif message.get("action") == "PONG":
                                pong_response = {"id": message["id"], "origin_action": "PONG"}
                                logger.debug(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 发送 PONG: {pong_response}")
                                await websocket.send(json.dumps(pong_response))
                                logger.success(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功发送 PONG | ID: {pong_response['id']} | 动作: {pong_response['origin_action']}")
                            elif message.get("action") == "HTTP_REQUEST":
                                http_request_response = {"id": message["id"], "origin_action": "HTTP_REQUEST"}
                                logger.debug(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 发送 HTTP_REQUEST: {http_request_response}")
                                await websocket.send(json.dumps(http_request_response))
                                logger.success(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功发送 HTTP_REQUEST | ID: {http_request_response['id']} | 动作: {http_request_response['origin_action']}")
                            elif message.get("action") == "OPEN_TUNNEL":
                                opentunnel_request_response = {
                                    "id": message["id"],
                                    "origin_action": "OPEN_TUNNEL",
                                    "result": {
                                        "url": message["url"],
                                        "status": 200,
                                        "status_text": "OK",
                                        "headers": {
                                            "content-type": "application/json; charset=utf-8",
                                            "date": custom_date,
                                            "keep-alive": "timeout=5",
                                            "proxy-connection": "keep-alive",
                                            "x-powered-by": "Express",
                                        }
                                    }
                                }
                                logger.debug(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 发送 OPEN_TUNNEL: {opentunnel_request_response}")
                                await websocket.send(json.dumps(opentunnel_request_response))
                                logger.success(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 成功发送 OPEN_TUNNEL | ID: {opentunnel_request_response['id']} | 动作: {opentunnel_request_response['origin_action']}")
                    except websockets.exceptions.ConnectionClosedError as e:
                        logger.error(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | 连接关闭错误 | 代理: {truncate_proxy(protocol_proxy)} | 错误: {str(e)[:30]}**")
                    finally:
                        await websocket.close()
                        logger.warning(f"UID: {truncate_userid(user_id)} | 节点: {node_type} | WebSocket 连接关闭 | 代理: {truncate_proxy(protocol_proxy)}")
                        send_ping_task.cancel()
                        break

        except Exception as e:
            logger.error(f"UID: {truncate_userid(user_id)} | 代理 {truncate_proxy(protocol_proxy)} 出现错误 ➜ {str(e)[:30]}**")
            error_conditions = [
                "主机无法访问",
                "[SSL: WRONG_VERSION_NUMBER]",
                "无效的打包 IP 地址字符串长度",
                "空连接回复",
                "设备创建限制超出",
                "[Errno 111] 无法连接到代理",
                "发送 1011 (内部错误) keepalive ping 超时; 未收到关闭帧"
            ]

            if remove_on_all_errors:
                if any(error_msg in str(e) for error_msg in error_conditions):
                    logger.warning(f"UID: {truncate_userid(user_id)} | 从列表中移除错误代理 ➜ {truncate_proxy(protocol_proxy)}")
                    remove_proxy_from_list(protocol_proxy)
                    return None
            else:
                if "设备创建限制超出" in str(e):
                    logger.warning(f"UID: {truncate_userid(user_id)} | 从列表中移除错误代理 ➜ {truncate_proxy(protocol_proxy)}")
                    remove_proxy_from_list(protocol_proxy)
                    return None
            continue

async def main():
    with open('uid.txt', 'r') as file:
        user_ids = file.read().splitlines()

    with open('proxy.txt', 'r') as file:
        all_proxies = file.read().splitlines()

    # 动态分配代理
    total_proxies = len(all_proxies)
    total_users = len(user_ids)

    if total_users == 0:
        raise ValueError("没有用户 ID 可供分配代理。")

    # 根据可用代理数量和用户 ID 数量计算每个用户 ID 可以分配的代理数量
    proxies_per_user = total_proxies // total_users

    if proxies_per_user == 0:
        raise ValueError("代理数量不足，无法为每个 user_id 分配代理。")

    # 为每个用户 ID 分配代理
    proxy_allocation = {
        user_id: all_proxies[i * proxies_per_user: (i + 1) * proxies_per_user]
        for i, user_id in enumerate(user_ids)
    }

    for user_id, proxies in proxy_allocation.items():
        logger.warning(f"用户 ID: {user_id} | 总代理: {len(proxies)}")
        await asyncio.sleep(1)

    tasks = {}

    for user_id, proxies in proxy_allocation.items():
        for proxy in proxies:
            await asyncio.sleep(random.uniform(5.0, 1))
            task = asyncio.create_task(connect_to_wss(proxy, user_id))
            tasks[task] = (proxy, user_id)

    while True:
        done, pending = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if task.result() is None:
                failed_proxy, user_id = tasks[task]
                logger.warning(f"UID: {truncate_userid(user_id)} | 移除并替换失败的代理: {truncate_proxy(failed_proxy)}")

                proxy_allocation[user_id].remove(failed_proxy)
                new_proxy = random.choice(list(set(all_proxies) - set(proxy_allocation[user_id])))
                proxy_allocation[user_id].append(new_proxy)

                await asyncio.sleep(random.uniform(5.0, 1))
                new_task = asyncio.create_task(connect_to_wss(new_proxy, user_id))
                tasks[new_task] = (new_proxy, user_id)
                logger.success(f"UID: {truncate_userid(user_id)} | 成功替换失败的代理: {truncate_proxy(failed_proxy)} 为: {truncate_proxy(new_proxy)}")

            tasks.pop(task)

def remove_proxy_from_list(proxy):
    with open("proxy.txt", "r+") as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if line.strip() != proxy:
                file.write(line)
        file.truncate()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info(f"程序被用户终止。祝您愉快！\n")
