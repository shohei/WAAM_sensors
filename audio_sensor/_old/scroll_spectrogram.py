import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# === 設定 ===
samplerate = 44100      # サンプリング周波数 [Hz]
blocksize = 1024        # FFTに使うサンプル数
seconds = 5             # 表示する時間幅 [秒]
channels = 1            # Scarlett Solo のマイク入力はモノラルでOK

# === スペクトログラム用バッファ ===
nblocks = int(seconds * samplerate / blocksize)   # 横方向に確保するフレーム数
spec_data = np.zeros((nblocks, blocksize // 2 + 1))

# === Figure 準備 ===
fig, ax = plt.subplots()
im = ax.imshow(
    20 * np.log10(spec_data + 1e-6).T,  # dBスケール
    origin="lower",
    aspect="auto",
    extent=[0, seconds, 0, samplerate / 2],
    cmap="magma",
    #vmin=-80, vmax=0   # dBスケールを固定
    vmin=-120, vmax=20   # dBスケールを固定
)
ax.set_xlabel("Time [s]")
ax.set_ylabel("Frequency [Hz]")
ax.set_title("Real-time Spectrogram (Scrolling)")

# === 音声コールバック ===
def audio_callback(indata, frames, time, status):
    global spec_data
    if status:
        print(status)
    # FFTを計算
    windowed = indata[:, 0] * np.hanning(blocksize)
    fft = np.fft.rfft(windowed)
    magnitude = np.abs(fft)
    magnitude /= np.max(magnitude) + 1e-6  # 正規化
    print(magnitude[:5])  # デバッグ用
    # バッファをシフトして最新データを追加
    spec_data = np.roll(spec_data, -1, axis=0)
    spec_data[-1, :] = magnitude

# === アニメーション更新 ===
def update(frame):
    im.set_data(20 * np.log10(spec_data + 1e-6).T)
    return [im]

# === ストリーミング開始 ===
DEVICE_ID =  1 # Scarlett Solo の入力デバイス番号（Noneならデフォルト）
print(sd.query_devices())
print('Selected DEVICE_ID=')
print(DEVICE_ID)
stream = sd.InputStream(
    device=DEVICE_ID, channels=channels, samplerate=samplerate,
    blocksize=blocksize, callback=audio_callback
)
with stream:
    ani = animation.FuncAnimation(
        fig, update, interval=50, blit=True, cache_frame_data=False
    )
    plt.show()
