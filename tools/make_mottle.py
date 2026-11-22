# 넓은 범위의 수채 얼룩 (바닥 위에 아주 크게 한 번 더 깔아서 잔디 반복을 가림)
import numpy as np, sys
from PIL import Image, ImageFilter
N = 512
def pn(power, seed):
    r = np.random.default_rng(seed); f = np.sqrt(np.fft.fftfreq(N)[None]**2 + np.fft.fftfreq(N)[:, None]**2); f[0, 0] = 1
    n = np.real(np.fft.ifft2((r.normal(size=(N, N)) + 1j * r.normal(size=(N, N))) / f**power)); return (n - n.mean()) / n.std()
n = 0.7 * pn(2.4, 11) + 0.3 * pn(1.7, 12)
light, dark = np.array([226, 222, 140.]), np.array([120, 158, 70.])
t = np.clip(0.5 + 0.35 * n, 0, 1)[..., None]
rgb = light * (1 - t) + dark * t
edge = np.exp(-((n - 0.5) / 0.06) ** 2)[..., None]; rgb -= edge * 14
Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)).save(sys.argv[1], 'WEBP', quality=85)
print('ok')
