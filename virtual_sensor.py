import paho.mqtt.client as mqtt
import time
import random
import json

# --- 配置部分 ---
# 我们使用 EMQX 的免费公共服务器，不需要注册就能用
BROKER_ADDRESS = "broker.emqx.io"
PORT = 1883
# 这是你的设备向云端发送数据的“频道”，建议把 my_project 改成你的名字拼音，防止和别人冲突
TOPIC = "simucity/my_project/sensor01"
# 给这个虚拟设备起个名字
CLIENT_ID = f"python-sensor-{random.randint(0, 1000)}"


# --- 连接成功后的回调函数 ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ 连接服务器成功!")
    else:
        print(f"❌ 连接失败，错误码: {rc}")


# --- 主程序 ---
client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect

print("正在连接到公共 MQTT 服务器...")
client.connect(BROKER_ADDRESS, PORT, 60)

# 开启一个后台线程处理网络通信
client.loop_start()

try:
    while True:
        # 1. 模拟生成数据：生成一个 20到30度之间的随机温度，保留2位小数
        temperature = round(random.uniform(20.0, 30.0), 2)

        # 2. 包装成 JSON 格式 (工业界标准格式)
        # 就像是用快递盒把数据打包好
        payload = {
            "device_id": "sensor01",
            "timestamp": time.time(),
            "temperature": temperature
        }
        payload_json = json.dumps(payload)

        # 3. 发送数据 (Publish)
        client.publish(TOPIC, payload_json)

        print(f"📡 已发送数据: {payload_json} 到主题: {TOPIC}")

        # 4. 休息 2 秒再发下一次
        time.sleep(2)

except KeyboardInterrupt:
    print("停止运行")
    client.loop_stop()
    client.disconnect()