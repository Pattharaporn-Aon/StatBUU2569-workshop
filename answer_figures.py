"""
เฉลยกราฟ STAT × AI Workshop
รันใน Google Colab ได้ทันที: กราฟทุกภาพจะบันทึกเป็นไฟล์ .png ในโฟลเดอร์ figures/
ข้อมูลทุกชุดเป็นข้อมูลจำลองเพื่อการสอน (ยกเว้น Anscombe)
"""
import os
import json
import urllib.request

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

BASE = os.environ.get(
    "DATA_BASE",
    "https://raw.githubusercontent.com/Pattharaporn-Aon/StatBUU2569-workshop/main/data/",
)
GEOJSON = os.environ.get(
    "TH_GEOJSON",
    "https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json",
)
OUT = "figures"
os.makedirs(OUT, exist_ok=True)

# ---------- ฟอนต์ภาษาไทย ----------
def use_thai_font():
    for name in ["Loma", "Sarabun", "TH Sarabun New", "Noto Sans Thai", "Tahoma"]:
        if any(name.lower() in f.name.lower() for f in font_manager.fontManager.ttflist):
            plt.rcParams["font.family"] = [name, "DejaVu Sans"]
            return
    # Colab: ติดตั้งฟอนต์ไทยอัตโนมัติ
    try:
        os.system("apt-get -qq install -y fonts-tlwg-loma > /dev/null 2>&1")
        font_manager._load_fontmanager(try_read_cache=False)
        plt.rcParams["font.family"] = ["Loma", "DejaVu Sans"]
    except Exception:
        pass

use_thai_font()
plt.rcParams.update({"figure.dpi": 120, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 14})
YELLOW, ORANGE, BLUE, RED, GREY = "#f2b705", "#f28705", "#2b8cd0", "#d62828", "#888888"

def save(name):
    plt.tight_layout()
    plt.savefig(f"{OUT}/{name}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("saved", name)

def load(f):
    return pd.read_csv(BASE + f)

# ---------- 1) กราฟแท่ง: ผลผลิตทุเรียน ----------
d = load("1_durian_yield_east.csv").sort_values("durian_yield_kg_per_rai")
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(d["province_th"], d["durian_yield_kg_per_rai"], color=YELLOW, edgecolor="black")
ax.bar_label(bars, labels=[f"{v:,}" for v in d["durian_yield_kg_per_rai"]], padding=4)
ax.set_xlabel("ผลผลิตทุเรียนเฉลี่ย (กก./ไร่)")
ax.set_title("กิจกรรม 1: ผลผลิตทุเรียนต่อไร่ 8 จังหวัดภาคตะวันออก")
ax.set_xlim(0, 1650)
save("01_bar_durian_yield")

# ---------- 2) รูปร่างการกระจาย ----------
s = load("6_distribution_shapes.csv")
titles = {"symmetric": "สมมาตร", "right_skewed": "เบ้ขวา", "left_skewed": "เบ้ซ้าย", "bimodal": "สองยอด"}
fig, axes = plt.subplots(2, 2, figsize=(10, 7))
for ax, col in zip(axes.flat, s.columns):
    ax.hist(s[col], bins=25, color=YELLOW, edgecolor="black")
    m, md = s[col].mean(), s[col].median()
    ax.axvline(m, color=RED, lw=2.5, label=f"ค่าเฉลี่ย = {m:.1f}")
    ax.axvline(md, color=BLUE, lw=2.5, ls="--", label=f"มัธยฐาน = {md:.1f}")
    ax.set_title(f"{titles[col]} ({col})")
    ax.set_xlabel("คะแนน")
    ax.set_ylabel("จำนวนนักเรียน")
    ax.legend(fontsize=9)
fig.suptitle("กิจกรรม 2: รูปร่างการกระจาย 4 แบบ", fontsize=15, fontweight="bold")
save("02_hist_distribution_shapes")

# ---------- 3) ข้อมูลสกปรก ----------
dirty = load("3_water_level_daily_dirty.csv")
dirty["date"] = pd.to_datetime(dirty["date"])
bad = dirty[(dirty["water_level_m"] < 0) | (dirty["water_level_m"] > 10)]
miss = dirty[dirty["water_level_m"].isna()]
fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
ax = axes[0]
ax.plot(dirty["date"], dirty["water_level_m"], color=BLUE, lw=1)
ax.scatter(bad["date"], bad["water_level_m"], color=RED, s=60, zorder=3, label="ค่าผิดปกติ")
for _, r in bad.iterrows():
    ax.annotate(f"{r['water_level_m']}", (r["date"], r["water_level_m"]), xytext=(6, 4),
                textcoords="offset points", color=RED, fontweight="bold")
for x in miss["date"]:
    ax.axvline(x, color=GREY, ls=":", lw=1)
ax.set_ylabel("ระดับน้ำ (ม.)")
ax.set_title("กิจกรรม 3: ระดับน้ำรายวันก่อนทำความสะอาด (เส้นจุดสีเทา = วันที่ค่าสูญหาย)")
ax.legend()
ax = axes[1]
ax.bar(dirty["date"], dirty["rain_mm"], color=ORANGE, width=1)
big = dirty[dirty["rain_mm"] > 300]
ax.scatter(big["date"], big["rain_mm"], color=RED, s=60, zorder=3)
for _, r in big.iterrows():
    ax.annotate(f"{r['rain_mm']:.0f} มม.", (r["date"], r["rain_mm"]), xytext=(6, -4),
                textcoords="offset points", color=RED, fontweight="bold")
ax.set_ylabel("ฝน (มม.)")
ax.set_title("ปริมาณฝนรายวัน: มีวันที่ฝน 850 มม. ซึ่งผิดธรรมชาติ")
save("03_dirty_data_problems")

summary = pd.DataFrame({
    "ประเภทปัญหา": ["ค่าสูญหาย water_level_m", "ค่าสูญหาย rain_mm", "แถวซ้ำ", "ระดับน้ำ < 0 หรือ > 10 ม.", "ฝน > 300 มม."],
    "จำนวน": [dirty["water_level_m"].isna().sum(), dirty["rain_mm"].isna().sum(),
              dirty.duplicated().sum(), len(bad), len(big)],
})
fig, ax = plt.subplots(figsize=(6, 3))
bars = ax.barh(summary["ประเภทปัญหา"][::-1], summary["จำนวน"][::-1], color=RED)
ax.bar_label(bars, padding=3)
ax.set_xlabel("จำนวน")
ax.set_title(f"สรุปปัญหาที่พบ: รวม {summary['จำนวน'].sum()} จุด")
save("03b_dirty_data_summary")

# ---------- 4) ไอศกรีม vs จมน้ำ ----------
ice = load("4_icecream_drowning.csv")
fig, axes = plt.subplots(1, 3, figsize=(14, 4.3))
pairs = [("icecream_sales", "drowning_cases", "ยอดขายไอศกรีม (ถ้วย/วัน)", "จำนวนผู้จมน้ำ (ราย)"),
         ("avg_temp_c", "icecream_sales", "อุณหภูมิเฉลี่ย (°C)", "ยอดขายไอศกรีม (ถ้วย/วัน)"),
         ("avg_temp_c", "drowning_cases", "อุณหภูมิเฉลี่ย (°C)", "จำนวนผู้จมน้ำ (ราย)")]
for ax, (x, y, xl, yl) in zip(axes, pairs):
    ax.scatter(ice[x], ice[y], s=70, color=ORANGE, edgecolor="black")
    b, a = np.polyfit(ice[x], ice[y], 1)
    xs = np.linspace(ice[x].min(), ice[x].max(), 50)
    ax.plot(xs, a + b * xs, color=GREY, ls="--")
    ax.set_xlabel(xl); ax.set_ylabel(yl)
    ax.set_title(f"r = {ice[x].corr(ice[y]):.2f}")
fig.suptitle("กิจกรรม 4: สหสัมพันธ์สูง ≠ เหตุและผล (อุณหภูมิคือตัวแปรแทรกซ้อน)", fontsize=14, fontweight="bold")
save("04_scatter_icecream_drowning")

# ---------- 5) Anscombe ----------
ans = load("5_anscombe.csv")
fig, axes = plt.subplots(2, 2, figsize=(9, 7), sharex=True, sharey=True)
colors = [YELLOW, BLUE, ORANGE, "#7ed957"]
xs = np.linspace(2, 20, 50)
for ax, (name, g), c in zip(axes.flat, ans.groupby("dataset"), colors):
    ax.scatter(g["x"], g["y"], s=60, color=c, edgecolor="black")
    b, a = np.polyfit(g["x"], g["y"], 1)
    ax.plot(xs, a + b * xs, color=GREY, ls="--")
    ax.set_title(f"ชุด {name}: x เฉลี่ย={g['x'].mean():.1f}, y เฉลี่ย={g['y'].mean():.2f}, r={g['x'].corr(g['y']):.2f}", fontsize=11)
fig.suptitle("กิจกรรม 5: Anscombe's Quartet ค่าสถิติเท่ากัน แต่กราฟต่างกัน", fontsize=14, fontweight="bold")
save("05_anscombe_quartet")

# ---------- 6) ฮิสโทแกรมระดับน้ำ ----------
w = load("2_water_level_daily.csv")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(w["water_level_m"], bins=np.arange(0.5, 5.01, 0.25), color=BLUE, edgecolor="black")
ax.axvline(w["water_level_m"].mean(), color=RED, lw=2.5, label=f"ค่าเฉลี่ย = {w['water_level_m'].mean():.2f} ม.")
ax.axvline(w["water_level_m"].median(), color=YELLOW, lw=2.5, ls="--", label=f"มัธยฐาน = {w['water_level_m'].median():.2f} ม.")
ax.set_xlabel("ระดับน้ำแม่น้ำรายวัน (เมตร)")
ax.set_ylabel("จำนวนวัน")
ax.set_title("Notebook: ฮิสโทแกรมระดับน้ำ (เบ้ขวา)")
ax.legend()
save("06_hist_water_level")

# ---------- 7) Boxplot รายเดือน ----------
months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
fig, ax = plt.subplots(figsize=(10, 4.8))
bp = ax.boxplot([w.loc[w["month"] == m, "water_level_m"] for m in range(1, 13)],
                patch_artist=True, medianprops=dict(color="black", lw=2))
for p in bp["boxes"]:
    p.set_facecolor(BLUE); p.set_alpha(0.75)
ax.set_xticks(range(1, 13), months)
ax.set_ylabel("ระดับน้ำ (เมตร)")
ax.set_title("Notebook: Boxplot ระดับน้ำรายเดือน (ส.ค.–ต.ค. เสี่ยงน้ำท่วม, ม.ค.–ก.พ. น้ำน้อย)")
save("07_boxplot_water_level_by_month")

# ---------- 8) ระดับน้ำกับฝน ----------
w["date"] = pd.to_datetime(w["date"])
fig, ax1 = plt.subplots(figsize=(11, 4.5))
ax1.bar(w["date"], w["rain_mm"], color=ORANGE, width=1, label="ฝน (มม.)")
ax1.set_ylabel("ฝนรายวัน (มม.)", color=ORANGE)
ax2 = ax1.twinx()
ax2.plot(w["date"], w["water_level_m"], color=BLUE, lw=1.8, label="ระดับน้ำ (ม.)")
ax2.set_ylabel("ระดับน้ำ (ม.)", color=BLUE)
ax2.spines["right"].set_visible(True)
ax1.set_title(f"Prompt 2: ระดับน้ำขึ้นหลังฝนตกหนัก (r = {w['water_level_m'].corr(w['rain_mm']):.2f})")
save("08_water_level_vs_rain")

# ---------- 9) ฝนรายภาค ----------
r = load("7_rainfall_provinces.csv")
reg = r.groupby("region")["rain_mm_year"].mean().sort_values()
fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
b = axes[0].barh(reg.index, reg.values, color=BLUE)
axes[0].bar_label(b, labels=[f"{v:,.0f}" for v in reg.values], padding=3)
axes[0].set_xlabel("ปริมาณฝนเฉลี่ยรายปี (มม.)")
axes[0].set_title("ฝนเฉลี่ยแยกตามภาค")
axes[0].set_xlim(0, 2800)
top = r.nlargest(5, "rain_mm_year").iloc[::-1]
b = axes[1].barh(top["province_th"], top["rain_mm_year"], color="#1456a8")
axes[1].bar_label(b, labels=[f"{v:,}" for v in top["rain_mm_year"]], padding=3)
axes[1].set_xlabel("ปริมาณฝนรายปี (มม.)")
axes[1].set_title("5 จังหวัดที่ฝนตกมากที่สุด")
axes[1].set_xlim(0, 4700)
save("09_rainfall_by_region")

# ---------- 10) แผนที่ choropleth ----------
try:
    if GEOJSON.startswith("http"):
        geo = json.load(urllib.request.urlopen(GEOJSON))
    else:
        geo = json.load(open(GEOJSON))
    val = dict(zip(r["province_en"], r["rain_mm_year"]))
    val["Bangkok Metropolis"] = val.get("Bangkok")
    bins = [0, 1200, 1500, 2000, 3000, 10000]
    cols = ["#e6f4ff", "#a8d8f5", "#5cb8e6", "#2b8cd0", "#1456a8"]
    labels = ["< 1,200", "1,200–1,500", "1,500–2,000", "2,000–3,000", "> 3,000"]
    patches, fc = [], []
    for f in geo["features"]:
        v = val[f["properties"]["name"]]
        c = cols[np.digitize(v, bins) - 1]
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            patches.append(Polygon(np.array(poly[0]), closed=True)); fc.append(c)
    fig, ax = plt.subplots(figsize=(6, 9))
    ax.add_collection(PatchCollection(patches, facecolor=fc, edgecolor="#555555", linewidths=0.4))
    ax.set_xlim(97.2, 105.8); ax.set_ylim(5.4, 20.6); ax.set_aspect(1 / np.cos(np.radians(13)))
    ax.axis("off")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=c, edgecolor="#555555", label=l) for c, l in zip(cols, labels)][::-1],
              title="ฝนรายปี (มม.)", loc="lower right", frameon=False)
    ax.set_title("แผนที่ปริมาณฝนรายปี 77 จังหวัด")
    save("10_map_rainfall")
except Exception as e:
    print("ข้ามแผนที่ (โหลดไฟล์ขอบเขตจังหวัดไม่ได้):", e)

print("เสร็จแล้ว ดูไฟล์ในโฟลเดอร์", OUT)
