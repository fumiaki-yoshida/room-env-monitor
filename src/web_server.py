import os
import csv
from datetime import datetime, timedelta
from flask import Flask, render_template

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

def read_csv_rows(file_path):
    """指定されたCSVファイルからヘッダーを除いたデータ行を返す"""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, mode='r') as f:
            reader = csv.reader(f)
            next(reader) # ヘッダーをスキップ
            return list(reader)
    except Exception as e:
        print(f"ファイル読み込みエラー ({file_path}): {e}")
        return []

def get_env_data():
    """今日と昨日のCSVから直近のデータを取得する"""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    
    today_file = os.path.join(DATA_DIR, f"env_log_{today_str}.csv")
    yesterday_file = os.path.join(DATA_DIR, f"env_log_{yesterday_str}.csv")
    
    # 今日と昨日のデータをそれぞれ読み込む
    today_rows = read_csv_rows(today_file)
    yesterday_rows = read_csv_rows(yesterday_file)
    
    # 2日分のデータを結合
    all_rows = yesterday_rows + today_rows
    
    # 1件もデータがない場合のフォールバック
    if not all_rows:
        return {"latest": {"timestamp": "データなし", "co2": "-", "temp": "-", "hum": "-"}, "history": []}
    
    # 最新の1件を取得
    latest = all_rows[-1]
    latest_data = {
        "timestamp": latest[0],
        "co2": latest[1],
        "temp": latest[2],
        "hum": latest[3]
    }
    
    # グラフ用に直近120件（過去2時間分）を抽出
    history_data = all_rows[-120:]
    
    return {
        "latest": latest_data,
        "history": history_data
    }

@app.route('/')
def index():
    data = get_env_data()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)