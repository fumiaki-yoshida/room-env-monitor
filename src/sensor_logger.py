import time
import csv
import os
from datetime import datetime
import board
import adafruit_scd4x

# 保存先ファイルのパス（srcディレクトリの1つ上の階層にある data フォルダ内）
LOG_FILE = os.path.join(os.path.dirname(__file__), '../data/env_log.csv')

# 記録間隔（秒）
WRITE_INTERVAL = 60

def main():
    # I2Cバスとセンサーの初期化
    i2c = board.I2C()
    scd4x = adafruit_scd4x.SCD4X(i2c)
    print("SCD40センサーを初期化しています...")

    # 計測開始
    scd4x.start_periodic_measurement()
    print(f"計測を開始しました。{WRITE_INTERVAL}秒ごとにCSVへ保存します。")

    # 保存先ディレクトリ（dataフォルダ）が無い場合は自動で作成
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # CSVファイルのヘッダー作成（ファイルが新規作成の場合のみ）
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "co2_ppm", "temperature_c", "humidity_percent"])

    last_write_time = 0

    try:
        while True:
            # センサーのデータが準備できているか確認
            if scd4x.data_ready:
                current_time = time.time()
                
                # 指定した間隔（60秒）が経過していたら記録する
                if current_time - last_write_time >= WRITE_INTERVAL:
                    co2 = scd4x.CO2
                    temp = scd4x.temperature
                    hum = scd4x.relative_humidity
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # ターミナルへ現在の状況を出力
                    print(f"[{now_str}] CO2: {co2:4d} ppm | Temp: {temp:.1f} °C | Hum: {hum:.1f} %")

                    # CSVファイルへの追記（モード 'a' は追記モード）
                    with open(LOG_FILE, mode='a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([now_str, co2, round(temp, 1), round(hum, 1)])
                    
                    last_write_time = current_time

            # SCD40の更新間隔（約5秒）に合わせて待機
            time.sleep(5)

    except KeyboardInterrupt:
        # Ctrl+C で安全に終了するための処理
        print("\n計測を終了します。")
        scd4x.stop_periodic_measurement()

if __name__ == "__main__":
    main()