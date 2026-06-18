import os
import csv
from flask import Flask, render_template

app = Flask(__name__)

# CSVファイルのパス
LOG_FILE = os.path.join(os.path.dirname(__file__), '../data/env_log.csv')

def get_latest_data():
    """CSVファイルから最新の1行を取得する関数"""
    if not os.path.exists(LOG_FILE):
        return {"timestamp": "データなし", "co2": "-", "temp": "-", "hum": "-"}
    
    try:
        with open(LOG_FILE, mode='r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) > 1:  # ヘッダー以外のデータがある場合
                latest = rows[-1]  # 最後の行を取得
                return {
                    "timestamp": latest[0],
                    "co2": latest[1],
                    "temp": latest[2],
                    "hum": latest[3]
                }
    except Exception as e:
        print(f"データ読み込みエラー: {e}")
        
    return {"timestamp": "エラー", "co2": "-", "temp": "-", "hum": "-"}

@app.route('/')
def index():
    # 最新のセンサーデータを取得
    data = get_latest_data()
    # HTMLテンプレートにデータを渡して表示
    return render_template('index.html', data=data)

if __name__ == '__main__':
    # 0.0.0.0 で起動することで、ローカルネットワーク内の他のPCからアクセス可能にする
    app.run(host='0.0.0.0', port=5000, debug=True)
