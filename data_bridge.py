import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json

# --- 1. 这里填你刚刚保存的三个秘密 (必须要改！) ---
INFLUX_TOKEN = "EzWUZF_hQFLkg4DAJKWN2Y1XFtIO-7w-vzj2DWTGXtquihFJ_KFVPaHWLGQ-85yJ4yKeJNqtHdSt_Ml87dHTBA=="
INFLUX_ORG = "1672534253cf4331"  # 比如 "your_email@gmail.com" 或者一串ID
INFLUX_BUCKET = "simucity"

# --- InfluxDB 配置 (这是云端版的固定地址) ---
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
# 注意：如果你注册时选的不是 AWS US East，请去你的浏览器地址栏复制前半部分网址

# --- MQTT 配置 (跟之前一样) ---
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "simucity/my_project/sensor01" # 必须和你发送端完全一致！

# --- 连接 InfluxDB ---
print("正在连接数据库...")
db_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = db_client.write_api(write_options=SYNCHRONOUS)

# --- 收到 MQTT 消息后的处理函数 ---
def on_message(client, userdata, msg):
    try:
        # 1. 解码收到的数据
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        print(f"收到数据: {data}")

        # 2. 制作一个数据库的点 (Point)
        # 这里的 "temperature" 是表名，field是数值
        point = Point("environment_sensor") \
            .tag("device_id", data["device_id"]) \
            .field("temperature", float(data["temperature"]))

        # 3. 写入数据库
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print("✅ 数据已存入 InfluxDB")

    except Exception as e:
        print(f"❌ 写入失败: {e}")

# --- 启动 MQTT 监听 ---
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

print(f"正在连接 MQTT: {MQTT_BROKER}...")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.subscribe(MQTT_TOPIC)
print(f"监听主题: {MQTT_TOPIC}")

# 让程序一直运行
mqtt_client.loop_forever()