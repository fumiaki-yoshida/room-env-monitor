import time
import csv
import os
from datetime import datetime
import board
import adafruit_scd4x

# データ保存ディレクトリのベースパス
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

# 記録間隔（秒）
WRITE_INTERVAL = 60

def get_log_file_path():
    """現在の日付に基づいたCSVファイルのパスを返す (例: data/env_log_2026-06-19.csv)"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(DATA_DIR, f"env_log_{today_str}.csv")

def main():
    i2c = board.I2C()
    scd4x = adafruit_scd4x.SCD4X(i2c)
    print("SCD40センサーを初期化しています...")

    scd4x.start_periodic_measurement()
    print(f"計測を開始しました。{WRITE_INTERVAL}秒ごとに日別のCSVへ保存します。")

    # 保存先ディレクトリが無い場合は作成
    os.makedirs(DATA_DIR, exist_ok=True)

    last_write_time = 0

    try:
        while True:
            if scd4x.data_ready:
                current_time = time.time()
                
                if current_time - last_write_time >= WRITE_INTERVAL:
                    co2 = scd4x.CO2
                    temp = scd4x.temperature
                    hum = scd4x.relative_humidity
                    
                    now = datetime.now()
                    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
                    
                    print(f"[{now_str}] CO2: {co2:4d} ppm | Temp: {temp:.1f} °C | Hum: {hum:.1f} %")

                    # 書き込む直前に、その日のファイルパスを取得
                    log_file = get_log_file_path()
                    file_exists = os.path.exists(log_file)

                    # CSVファイルへの書き込み（新規ファイルならヘッダーも追加）
                    with open(log_file, mode='a', newline='') as f:
                        writer = csv.writer(f)
                        if not file_exists:
                            writer.writerow(["timestamp", "co2_ppm", "temperature_c", "humidity_percent"])
                        writer.writerow([now_str, co2, round(temp, 1), round(hum, 1)])
                    
                    last_write_time = current_time

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n計測を終了します。")
        scd4x.stop_periodic_measurement()

if __name__ == "__main__":
    main()