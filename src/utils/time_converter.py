from datetime import datetime
import pytz

def stamp_to_utc(timestamp):

    # 将时间戳转换为 UTC 时间
    utc_time = datetime.utcfromtimestamp(int(timestamp))

    # 定义北京时间（UTC+8）
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # 转换为北京时间
    beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)

    return beijing_time.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    print(stamp_to_utc(1741911064))
