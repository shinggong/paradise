# 이음새 없는 수채화풍 잔디 텍스처 생성 (1536x1024)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import sys
W, H = 1536, 1024
rng = np.random.default_rng(7)

def pnoise(power, seed):
    r = np.random.default_rng(seed)
    fx = np.fft.fftfreq(W)[None, :]; fy = np.fft.fftfreq(H)[:, None]
    f = np.sqrt(fx**2 + fy**2); f[0, 0] = 1
    spec = (r.normal(size=(H, W)) + 1j * r.normal(size=(H, W))) / f**power
    spec[0, 0] = 0
    n = np.real(np.fft.ifft2(spec))
    return (n - n.mean()) / n.std()

big = pnoise(2.2, 1)      # 큰 얼룩
mid = pnoise(1.6, 2)      # 중간 번짐
grain = pnoise(0.6, 3)    # 종이 결
fine = pnoise(0.2, 4)

base = np.array([196, 205, 118], float)      # 연두
deep = np.array([150, 178, 86], float)       # 짙은 초록
warm = np.array([222, 214, 140], float)      # 노르스름

t = np.clip(0.5 + 0.10 * big + 0.12 * mid, 0, 1)[..., None]  # 큰 얼룩은 약하게 (반복 덜 보이게, 큰 얼룩은 mottle.webp가 담당)
col = base * (1 - t) + deep * t
w = np.clip(0.22 - 0.12 * pnoise(2.0, 5), 0, 1)[..., None]
col = col * (1 - w) + warm * w
# 수채 번짐 가장자리: 등고선 근처를 살짝 진하게
for lvl in (-1.2, 1.3):
    edge = np.exp(-((big + 0.4 * mid - lvl) / 0.05) ** 2)[..., None]
    col -= edge * 10
# 종이 결·안료 알갱이
col += grain[..., None] * 5 + fine[..., None] * 3
img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))

# 풀잎 붓질 (가장자리 넘어가면 반대편에도 그려서 이음새 없게)
layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
greens = [(96, 146, 62), (112, 160, 70), (80, 128, 52), (130, 170, 80)]
def blade(x, y, h, lean, c, a, wdt):
    pts = []
    for i in range(7):
        s = i / 6
        pts.append((x + lean * s * s * h, y - h * s))
    for ox in (-W, 0, W):
        for oy in (-H, 0, H):
            d.line([(px + ox, py + oy) for px, py in pts], fill=c + (a,), width=wdt, joint='curve')
for _ in range(900):  # 풀 덤불
    cx, cy = rng.uniform(0, W), rng.uniform(0, H)
    n = rng.integers(4, 11); c = greens[rng.integers(len(greens))]
    for _ in range(n):
        blade(cx + rng.normal(0, 7), cy + rng.normal(0, 3), rng.uniform(14, 34), rng.normal(0, 0.45), c, int(rng.uniform(55, 120)), int(rng.choice([1, 2, 2, 3])))
for _ in range(2500):  # 흩어진 잔풀
    blade(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(6, 14), rng.normal(0, 0.5), greens[rng.integers(len(greens))], int(rng.uniform(35, 80)), 1)
layer = layer.filter(ImageFilter.GaussianBlur(0.6))
img = img.convert('RGBA'); img.alpha_composite(layer)

# 아주 드문 작은 꽃 점
fl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fl)
for _ in range(30):
    x, y = rng.uniform(0, W), rng.uniform(0, H)
    c = [(250, 248, 236), (240, 196, 206), (200, 190, 232), (250, 232, 150)][rng.integers(4)]
    for k in range(rng.integers(1, 4)):
        px, py = x + rng.normal(0, 10), y + rng.normal(0, 5)
        r = rng.uniform(2.5, 4.5)
        for ox in (-W, 0, W):
            for oy in (-H, 0, H):
                fd.ellipse([px - r + ox, py - r * .8 + oy, px + r + ox, py + r * .8 + oy], fill=c + (215,))
fl = fl.filter(ImageFilter.GaussianBlur(0.7))
img.alpha_composite(fl)
img.convert('RGB').save(sys.argv[1], 'WEBP', quality=88)
print('ok')
