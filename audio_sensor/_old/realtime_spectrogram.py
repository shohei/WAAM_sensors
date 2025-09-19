import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import spectrogram

# ===== パラメータ設定 =====
DEVICE_ID =  1 # Scarlett Solo の入力デバイス番号（Noneならデフォルト）
print(sd.query_devices())
print('Selected DEVICE_ID=')
print(DEVICE_ID)

FS = 44100            # サンプリングレート
CHUNK = 2048          # 一度に処理するサンプル数
NFFT = 1024           # FFTサイズ
OVERLAP = 512         # FFTのオーバーラップ

# ===== グラフ初期化 =====
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(NFFT // 2 + 1)
y = np.linspace(0, 5, 100)   # 縦軸: 直近5秒分を表示
spec_img = ax.imshow(np.zeros((len(x), 100)), 
                     aspect='auto', origin='lower', 
                     extent=[0, 5, 0, FS // 2], cmap='magma')

ax.set_xlabel("Time [s]")
ax.set_ylabel("Frequency [Hz]")
ax.set_title("Real-time Spectrogram (Scarlett Solo)")
fig.colorbar(spec_img, ax=ax, label="Power [dB]")

# ===== バッファ =====
buffer = np.zeros(int(FS * 5))  # 直近5秒分を保存

# ===== 音声コールバック =====
def audio_callback(indata, frames, time, status):
    global buffer
    if status:
        print(status)
    buffer = np.roll(buffer, -frames)
    buffer[-frames:] = indata[:, 0]

# ===== アニメーション更新関数 =====
def update(frame):
    global buffer
    f, t, Sxx = spectrogram(buffer, FS, nperseg=NFFT, noverlap=OVERLAP)
    spec_img.set_data(10 * np.log10(Sxx + 1e-10))  # dBに変換
    spec_img.set_extent([0, 5, 0, FS // 2])
    return [spec_img]

# ===== 音声ストリーム開始 =====
stream = sd.InputStream(device=DEVICE_ID, channels=1, samplerate=FS,
                        blocksize=CHUNK, callback=audio_callback)
stream.start()

ani = animation.FuncAnimation(fig, update, interval=100, blit=True)
plt.show()

stream.stop()
stream.close()

