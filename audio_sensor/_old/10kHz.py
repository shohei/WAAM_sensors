import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ===== 設定 =====
fs = 44100
NFFT = 4096
OVERLAP = 3072
blocksize = NFFT        # 音声コールバックごとに1フレームを処理
seconds = 5             # 横軸に表示する時間幅
channels = 1

# ===== バッファ =====
nblocks = int(seconds * fs / blocksize)
# rfft の出力長 = NFFT//2 + 1
nfreq = NFFT // 2 + 1
spec_data = np.zeros((nblocks, nfreq))

# 周波数配列
freqs = np.fft.rfftfreq(NFFT, d=1/fs)

# インデックス切り出し（1kHz〜10kHz）
fmin, fmax = 1000, 10000
idx_min = np.searchsorted(freqs, fmin)
idx_max = np.searchsorted(freqs, fmax)

# ===== Figure =====
fig, ax = plt.subplots(figsize=(8, 6))
# 初期表示は切り出した周波数のみ
im = ax.imshow(
    20 * np.log10(spec_data[:, idx_min:idx_max] + 1e-12).T,
    origin='lower', aspect='auto',
    extent=[0, seconds, freqs[idx_min], freqs[idx_max-1]],
    cmap='magma',
    vmin=-100, vmax=20
)
ax.set_xlabel('Time [s]')
ax.set_ylabel('Frequency [Hz]')
ax.set_title('Real-time Spectrogram (1-10 kHz)')
plt.colorbar(im, ax=ax, label='Power [dB]')

# ===== コールバック =====
def audio_callback(indata, frames, time, status):
    global spec_data
    if status:
        print('Status:', status)
    # 窓関数をかけてFFT
    x = indata[:, 0] * np.hanning(len(indata))
    X = np.fft.rfft(x, n=NFFT)
    mag = np.abs(X)

    # 正規化（必要なら）
    # mag /= (np.max(mag) + 1e-12)

    spec_data = np.roll(spec_data, -1, axis=0)
    spec_data[-1, :] = mag

# ===== 更新 =====
def update(frame):
    db = 20 * np.log10(spec_data + 1e-12)
    cropped_db = db[:, idx_min:idx_max]
    im.set_data(cropped_db.T)
    return [im]

# ===== ストリーミング開始 =====
stream = sd.InputStream(
    samplerate=fs, device=1, channels=channels,
    blocksize=blocksize, callback=audio_callback
)
with stream:
    ani = animation.FuncAnimation(fig, update, interval=100,
                                  blit=True, cache_frame_data=False)
    plt.show()

