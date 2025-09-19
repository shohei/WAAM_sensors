#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib
# 重要：GUIバックエンドを無効化してスレッドセーフにする
matplotlib.use('Agg')

from flask import Flask, render_template, Response
import pyaudio
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import io
import base64
import threading

app = Flask(__name__)

# グローバル変数
audio = None
stream = None
device_index = None 
lock = threading.Lock()

def audiostart(dev_index):
    global audio, stream, device_index
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        rate=44100,
                        channels=1,
                        input_device_index=dev_index,
                        input=True,
                        frames_per_buffer=10240)
    device_index = dev_index

def audiostop():
    global audio, stream
    if stream:
        stream.stop_stream()
        stream.close()
    if audio:
        audio.terminate()
    stream = None
    audio = None

def generate_spectrogram():
    global stream
    while True:
        if stream is None:
            continue
        try:
            # スレッドセーフなロックを使用
            with lock:
                data = stream.read(10240, exception_on_overflow=False)
                audiodata = np.frombuffer(data, dtype=np.int16)
            
            # オーディオデータの処理
            stft_result = librosa.stft(audiodata.astype(np.float32), n_fft=2048, hop_length=512)
            spectrogram = np.abs(stft_result)**2
            log_spectrogram = librosa.power_to_db(spectrogram)
            
            # matplotlibの図を作成（Aggバックエンドでスレッドセーフ）
            fig, ax = plt.subplots(figsize=(10, 6))
            librosa.display.specshow(log_spectrogram, sr=44100, hop_length=512, 
                                   x_axis='time', y_axis='log', ax=ax)
            ax.set_title('Real-time Audio Spectrogram')
            plt.tight_layout()
            
            # メモリ上にPNG画像を保存
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=80, bbox_inches='tight')
            plt.close(fig)  # メモリリークを防ぐため必ず閉じる
            buf.seek(0)
            
            # HTTPストリーミング用のレスポンス
            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + buf.read() + b'\r\n')
                   
        except Exception as e:
            print(f"Error in generate_spectrogram: {e}")
            audiostop()
            break

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spectrogram')
def spectrogram():
    return Response(generate_spectrogram(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# アプリケーション終了時のクリーンアップ
import atexit

def cleanup():
    audiostop()

atexit.register(cleanup)

if __name__ == '__main__':
    # デバイス情報を表示（デバッグ用）
    #print("=== Audio Device List ===")
    #p = pyaudio.PyAudio()
    #for i in range(p.get_device_count()):
    #    info = p.get_device_info_by_index(i)
    #    if info["maxInputChannels"] > 0:
    #        print(f"Input Device ID {i}: {info['name']}")
    
    dev_index = 1  # 適切なデバイスIDに変更してください
    
    # 利用可能な入力デバイスを自動検出
    input_devices = [1]
    #for i in range(p.get_device_count()):
    #    info = p.get_device_info_by_index(i)
    #    if info["maxInputChannels"] > 0:
    #        input_devices.append(i)
    #
    #p.terminate()
    
    if input_devices:
        # 最初に見つかった入力デバイスを使用
        #dev_index = input_devices[0]
        dev_index = 1
        print(f"Using audio device ID: {dev_index}")
        audiostart(dev_index)
    else:
        print("No input device found")
        exit(1)
    
    # Flaskアプリを起動（debug=Falseに変更してマルチスレッド問題を回避）
    app.run(host='0.0.0.0', port=5050, debug=False, threaded=True)
