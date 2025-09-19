import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

# ===== パラメータ設定 =====
DEVICE_ID = None   # Scarlett Solo のデバイス番号を指定 (None ならデフォルト入力)
FS = 44100         # サンプリングレート (Scarlett Soloは44.1kHz対応)
DURATION = 5       # 収録時間 [秒]

# ===== 録音 =====
print("Recording...")
audio = sd.rec(int(DURATION * FS), samplerate=FS, channels=1, dtype='float32', device=DEVICE_ID)
sd.wait()
print("Done.")

# ===== スペクトログラム計算 =====
f, t, Sxx = spectrogram(audio[:, 0], FS, nperseg=1024, noverlap=512)

# ===== プロット =====
plt.figure(figsize=(10, 6))
plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.title("Spectrogram (Scarlett Solo Input)")
plt.colorbar(label="Power [dB]")
plt.show()

