"""Synthesized score for the WFD showreel. 120 BPM, every hit lands on a cut.
Run: python3 showreel/audio.py  ->  showreel/wfd-showreel-audio.wav (48k stereo, 15s)
"""
import wave
from pathlib import Path
import numpy as np

SR, DUR = 48000, 15.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
send = np.zeros(N)  # mono reverb send


def put(sig, t, gain=1.0, pan=0.0, verb=0.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt((1 - pan) / 2) * 1.414
    R[i:i + len(sig)] += sig * np.sqrt((1 + pan) / 2) * 1.414
    send[i:i + len(sig)] += sig * verb


def env(n, a, d):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    return e


def onepole(x, cut):
    """Time-varying one-pole lowpass. cut may be scalar or array (Hz)."""
    cut = np.broadcast_to(np.asarray(cut, float), x.shape)
    a = 1 - np.exp(-2 * np.pi * cut / SR)
    y = np.empty_like(x); z = 0.0
    for i in range(len(x)):
        z += a[i] * (x[i] - z); y[i] = z
    return y


def kick(len_s=0.45, f0=150, f1=42, drive=2.2):
    n = int(len_s * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env(n, .001, len_s / 3.2)
    click = rng.standard_normal(n) * np.exp(-t * 400) * .4
    return np.tanh((s + click) * drive) / np.tanh(drive)


def hat(len_s=0.06, bright=1.0):
    n = int(len_s * SR); x = rng.standard_normal(n)
    x = x - onepole(x, 7000)  # highpass
    return x * env(n, .0005, len_s / 4) * bright


def snare(len_s=0.25):
    n = int(len_s * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    nz = rng.standard_normal(n); nz = nz - onepole(nz, 1200)
    return np.tanh((body * .7 + nz * np.exp(-t * 16) * .8) * 1.6)


def impact(len_s=2.4, big=1.0):
    n = int(len_s * SR); t = np.arange(n) / SR
    k = np.zeros(n); kk = kick(1.4, 180, 34, 3.0)[:n]; k[:len(kk)] = kk
    boom = np.sin(2 * np.pi * np.cumsum(30 + 60 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.6)
    nz = rng.standard_normal(n); nz = onepole(nz, 2500 * np.exp(-t * 3) + 200) * np.exp(-t * 3.5) * 1.8
    crack = rng.standard_normal(n) * np.exp(-t * 60) * .6
    return np.tanh((k * .9 + boom * .8 * big + nz + crack) * 1.4)


def whoosh(len_s=0.5, up=True, peak=0.7):
    n = int(len_s * SR); t = np.linspace(0, 1, n)
    shape = np.sin(np.pi * np.clip(t / peak, 0, 1) * .5) ** 2 if up else np.exp(-t * 5)
    shape = np.where(t > peak, np.exp(-(t - peak) * 18), shape)
    cut = 300 + 7000 * shape
    x = onepole(rng.standard_normal(n), cut)
    return x * shape * 1.6


def riser(len_s, f0=180, f1=1400):
    n = int(len_s * SR); t = np.linspace(0, 1, n)
    f = f0 * (f1 / f0) ** (t ** 1.6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (np.sin(ph) + .5 * np.sin(ph * 1.5)) * t ** 2 * .25
    nz = onepole(rng.standard_normal(n), 400 + 9000 * t ** 2) * t ** 2.2 * .9
    return tone + nz


def tick(freq=2600, len_s=0.03):
    n = int(len_s * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 180)


def bell(freqs, len_s=1.2):
    n = int(len_s * SR); t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * (3 + i)) for i, f in enumerate(freqs)) * np.minimum(1, t / .003)


def bass(len_s, f=55):
    n = int(len_s * SR); t = np.arange(n) / SR
    saw = 2 * ((f * t) % 1) - 1
    return onepole(saw, 380) * env(n, .004, len_s / 2.5)


def pad(len_s, freqs):
    n = int(len_s * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * .3 * t) * .4) + .3 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs)
    return onepole(x, 1600) * np.minimum(1, t / .6)


# ---------------------------------------------------------------- arrangement
beat = 0.5

# 0 to 2: cold open. drone, typing ticks, riser, strike swipe
drone_t = np.arange(N) / SR
drone = np.sin(2 * np.pi * 41.2 * drone_t) * .18 + np.sin(2 * np.pi * 82.4 * drone_t) * .05
drone *= np.clip(drone_t / 1.5, 0, 1) * np.where(drone_t < 13.5, 1, np.exp(-(drone_t - 13.5) * 1.5))
L += drone; R += drone
for i in range(12): put(tick(3200 + (i % 3) * 400), .08 + i * .031, .22, pan=-.2 + .04 * i)
put(riser(1.55, 120, 900), .45, .5, verb=.3)
for i, t0 in enumerate([.45, .95]): put(whoosh(.35, True, .5), t0, .35, pan=-.3 + i * .6)
put(whoosh(.28, True, .35), 1.36, .7, pan=.5)
put(kick(.3, 120, 50, 1.5), 1.5, .5)
put(whoosh(.25, True, .9), 1.78, .6)

# 2.0: POWER impact
put(impact(2.6, 1.2), 2.0, 1.0, verb=.5)
put(bell([659.25, 987.77, 1318.5], 1.4), 2.0, .12, verb=.6)
put(whoosh(.35, True, .75), 2.72, .9, pan=-.4)

# 3.0 to 13.5: groove
for b in range(int((13.5 - 3.0) / beat)):
    t0 = 3.0 + b * beat
    in_id = 8.5 <= t0 < 10.5
    if t0 in (6.0, 8.5, 10.5, 12.5): continue  # impacts handle these downbeats
    if not in_id or b % 2 == 0: put(kick(), t0, .85)
    put(hat(.05, 1.0), t0 + .25, .35, pan=.3)
    if 6.0 <= t0 < 8.0 or 10.5 <= t0 < 12.5:
        put(hat(.03, .8), t0 + .125, .18, pan=-.35); put(hat(.03, .8), t0 + .375, .18, pan=-.35)
        put(bass(.22, 55 if (b // 4) % 2 == 0 else 49), t0 + .25, .45)
    if (b % 2 == 1) and not in_id and t0 < 12.5: put(snare(), t0, .45, verb=.25)
# service switches: pitched ticks
for i in range(6): put(tick(1800 + i * 180, .05), 3.0 + i * .5, .35, pan=.4, verb=.2)

# 5.8 zoom-through + 6.0 impact
put(riser(.28, 400, 2400), 5.72, .6)
put(impact(1.8, .8), 6.0, .8, verb=.4)

# 8.05 bars
for i in range(8): put(whoosh(.14, True, .6), 8.08 + i * .025, .18, pan=-.8 + i * .23)
put(impact(1.6, .5), 8.5, .55, verb=.5)
put(pad(2.0, [220, 329.63, 493.88]), 8.5, .05, verb=.4)
for i in range(7): put(tick(1400 + i * 90, .04), 8.8 + i * .03, .2, pan=-.5 + i * .15)
for i in range(6): put(whoosh(.2, True, .5), 9.42 + i * .055, .22, pan=-.6 + i * .24)

# 10.4 web reveal
put(whoosh(.35, True, .9), 10.36, .7)
put(impact(1.4, .5), 10.5, .5, verb=.3)
for i in range(10): put(tick(2400, .02), 10.75 + i * .03, .1)
put(tick(900, .04), 11.95, .6); put(tick(1500, .02), 12.05, .4)
put(bell([1318.5, 1760.0], .9), 12.07, .22, pan=.4, verb=.5)

# 12.5 partner + build into final hit
put(impact(1.2, .7), 12.5, .75, verb=.4)
put(riser(.95, 200, 2000), 12.52, .7, verb=.3)
roll = [12.9 + sum(.1 * (0.82 ** k) for k in range(i)) for i in range(14)]
for i, t0 in enumerate(r for r in roll if r < 13.47): put(snare(.12), t0, .15 + .025 * i)

# 13.5 final
put(impact(3.0, 1.4), 13.5, 1.0, verb=.7)
put(pad(1.5, [110, 164.81, 220, 261.63, 329.63]), 13.52, .09, verb=.5)
put(bell([880, 1318.5, 1760], 1.4), 13.55, .1, verb=.8)
for i in range(3): put(tick(3000, .03), 14.1 + i * .2, .12, pan=-.3 + i * .3, verb=.5)

# ---------------------------------------------------------------- fire foley
def roar(len_s, rise, fall):
    """Flame whoosh: filtered noise that swells with the wall of fire, plus crackle."""
    n = int(len_s * SR); t = np.arange(n) / SR
    shape = np.clip(t / rise, 0, 1) ** 2 * np.where(t > len_s - fall, np.clip((len_s - t) / fall, 0, 1), 1)
    body = onepole(rng.standard_normal(n), 250 + 3200 * shape) * 1.4
    rumble = onepole(rng.standard_normal(n), 90) * 3.0
    return (body + rumble) * shape + crackle(len_s, 60) * shape


def crackle(len_s, rate):
    n = int(len_s * SR); out = np.zeros(n)
    for _ in range(int(len_s * rate)):
        i = int(rng.random() * (n - 800)); m = int(80 + rng.random() * 600)
        out[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 5)) * (0.3 + rng.random())
    return out - onepole(out, 1500)


put(crackle(1.9, 25) * np.linspace(0, 1, int(1.9 * SR)) ** 2, .15, .35, pan=.1)
put(roar(.62, .06, .4), 1.95, .75, verb=.3)
put(roar(.85, .36, .38), 5.6, .7, pan=-.1, verb=.3)
put(roar(.85, .28, .42), 13.18, .75, pan=.1, verb=.4)
put(crackle(1.25, 18), 13.75, .25, pan=-.15, verb=.3)

# ---------------------------------------------------------------- reverb + master
ir_n = int(1.9 * SR); ir_t = np.arange(ir_n) / SR
ir = rng.standard_normal(ir_n) * np.exp(-ir_t * 3.2)
ir = onepole(ir, 3500)
size = 1 << int(np.ceil(np.log2(N + ir_n)))
wet = np.fft.irfft(np.fft.rfft(send, size) * np.fft.rfft(ir, size), size)[:N]
wet /= np.max(np.abs(wet)) + 1e-9
L += wet * .35; R += np.roll(wet, int(.011 * SR)) * .35

mix = np.stack([L, R])
mix = np.tanh(mix * 0.9)
fade = np.ones(N); fn = int(.35 * SR); fade[-fn:] = np.linspace(1, 0, fn) ** 2
mix *= fade
mix /= np.max(np.abs(mix)) / 0.79

out = Path(__file__).with_name('wfd-showreel-audio.wav')
pcm = (mix.T * 32767).astype('<i2')
with wave.open(str(out), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', out)
