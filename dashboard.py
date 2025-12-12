import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import time

# --- 1. 配置信息 (必须要改！跟上一步一样) ---
INFLUX_TOKEN = "EzWUZF_hQFLkg4DAJKWN2Y1XFtIO-7w-vzj2DWTGXtquihFJ_KFVPaHWLGQ-85yJ4yKeJNqtHdSt_Ml87dHTBA=="
INFLUX_ORG = "1672534253cf4331/load-data/tokens"
INFLUX_BUCKET = "simucity"
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"

# --- 2. 页面设置 ---
st.set_page_config(page_title="SimuCity 监控中心", layout="wide")
with st.sidebar:
    st.header("📱 手机扫码查看")
    st.image("my_project_qr.png")
    # 或者直接在线生成（更高级）：
    st.image(f"https://simucity-5snyzngayktkntdgrzvlpd.streamlit.app/", caption="扫码在手机上监控")
st.title("🏙️ SimuCity 城市环境实时监控")


# --- 3. 连接数据库函数 ---
# 使用 @st.cache_resource 防止每次刷新都重新连接数据库
@st.cache_resource
def get_client():
    return InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)


# --- 4. 读取数据函数 ---
def get_data():
    client = get_client()
    # 查询最近 10 分钟的数据
    query = f"""
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -10m)
      |> filter(fn: (r) => r["_measurement"] == "environment_sensor")
      |> filter(fn: (r) => r["_field"] == "temperature")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    """
    # 直接把查询结果转换成 Pandas 表格
    df = client.query_api().query_data_frame(org=INFLUX_ORG, query=query)
    return df


# --- 5. 页面布局与自动刷新 ---
# 创建两个占位符，用来动态更新内容
metric_placeholder = st.empty()
chart_placeholder = st.empty()

# 自动循环刷新 (模拟实时效果)
while True:
    try:
        # 获取最新数据
        df = get_data()

        if not df.empty:
            # 数据清洗：把时间设为索引，为了画图方便
            df["_time"] = pd.to_datetime(df["_time"])
            df.set_index("_time", inplace=True)

            # 获取最新的一个温度值
            latest_temp = df["temperature"].iloc[-1]

            # --- 渲染界面 ---

            # 1. 显示大数字指标
            with metric_placeholder.container():
                st.metric(label="🌡️ 实时温度 (Sensor-01)", value=f"{latest_temp} °C")

            # 2. 画折线图
            with chart_placeholder.container():
                st.line_chart(df["temperature"], height=400)
        else:
            st.warning("暂无数据，请检查数据源是否在运行...")

        # 休息 2 秒后刷新
        time.sleep(2)

    except Exception as e:
        st.error(f"发生错误: {e}")
        time.sleep(5)