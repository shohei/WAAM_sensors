# realtime_spectrogram_normalized.py
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ===== 設定 =====
fs = 44100
NFFT = 4096
OVERLAP = 3072
blocksize = NFFT
seconds = 10 
channels = 1

nblocks = int(seconds * fs / blocksize)
nfreq = NFFT // 2 + 1
spec_data = np.zeros((nblocks, nfreq))
freqs = np.fft.rfftfreq(NFFT, 1/fs)

# focus range (例: 1-10 kHz). 変更可
fmin, fmax = 1000, 10000
idx_min = np.searchsorted(freqs, fmin)
idx_max = np.searchsorted(freqs, fmax)

# グラフ準備（上：スペクトログラム、下：特徴量）
fig, (ax_spec, ax_feat) = plt.subplots(2, 1, figsize=(10, 6), 
                                       gridspec_kw={'height_ratios':[3,1]})
im = ax_spec.imshow(
    np.zeros((idx_max-idx_min, nblocks)),
    origin='lower', aspect='auto',
    extent=[-seconds, 0, freqs[idx_min], freqs[idx_max-1]],
    cmap='magma', vmin=-40, vmax=0  # 初期レンジ（dB相対）
)
ax_spec.set_ylabel('Freq [Hz]')
ax_spec.set_title('Normalized Spectrogram (1-10 kHz)')

# 特徴量プロット（spectral centroid, rms）
t_axis = np.linspace(-seconds, 0, nblocks)
centroid_line, = ax_feat.plot(t_axis, np.zeros(nblocks), label='Spectral Centroid [Hz]')
rms_line, = ax_feat.plot(t_axis, np.zeros(nblocks), label='RMS (linear)')
ax_feat.set_xlim(-seconds, 0)
ax_feat.set_ylim(0, freqs[idx_max-1])
ax_feat.set_xlabel('Time [s]')
ax_feat.legend(loc='upper right')

# コールバック
def audio_callback(indata, frames, time, status):
    global spec_data
    if status:
        print("Status:", status)
    x = indata[:,0] * np.hanning(len(indata))
    X = np.fft.rfft(x, n=NFFT)
    mag = np.abs(X)  # linear magnitude

    # roll and append
    spec_data = np.roll(spec_data, -1, axis=0)
    spec_data[-1,:] = mag

def update(frame):
    # convert to dB and crop
    mag = spec_data.copy()  # shape (nblocks, nfreq)
    # compute centroid and rms per frame
    centroid = np.zeros(nblocks)
    rms = np.zeros(nblocks)
    for i in range(nblocks):
        s = mag[i, idx_min:idx_max]
        # avoid all-zero
        if s.sum() <= 0:
            centroid[i] = 0
            rms[i] = 0
        else:
            # normalize per-frame to emphasize shape (remove overall level)
            s_norm = s / (np.max(s) + 1e-12)
            # dB for display (clipped)
            db = 20*np.log10(s_norm + 1e-12)
            # compute centroid on linear magnitude (not normalized)
            freqs_slice = freqs[idx_min:idx_max]
            centroid[i] = np.sum(freqs_slice * s) / (np.sum(s) + 1e-12)
            rms[i] = np.sqrt(np.mean((s)**2))

            # write back for display
            mag[i, idx_min:idx_max] = db  # overwrite with normalized dB

    # transpose for imshow: rows = freqs, cols = time
    im.set_data(mag[:, idx_min:idx_max].T)
    im.set_extent([-seconds, 0, freqs[idx_min], freqs[idx_max-1]])

    # update feature plot
    centroid_line.set_ydata(centroid)
    centroid_line.set_xdata(np.linspace(-seconds, 0, nblocks))
    rms_line.set_ydata(rms * 1e3)  # scale RMS to viewable range
    rms_line.set_xdata(np.linspace(-seconds, 0, nblocks))
    return [im, centroid_line, rms_line]

# start stream & animation
stream = sd.InputStream(samplerate=fs, device=1, channels=channels,
                        blocksize=blocksize, callback=audio_callback)
with stream:
    ani = animation.FuncAnimation(fig, update, interval=50, blit=True, cache_frame_data=False)
    plt.show()

