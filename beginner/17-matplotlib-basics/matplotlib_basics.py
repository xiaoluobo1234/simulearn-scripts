"""
SimuLearn Scripts — 初级 #17：Matplotlib 基础绘图
===================================================
知识点：basic-plotting

仿真数据的可视化是工程师的"眼睛"：
  - 变形云图的前身 → 折线/散点/等值线
  - 参数扫描 → 多曲线对比
  - 结果验证 → 理论与仿真 overlay

本节涵盖：
  1. pyplot 基础 — figure/axes 模型
  2. 折线图与散点图
  3. 多子图布局
  4. 仿真专用图表
  5. 样式与导出
  6. 常见坑与调试

运行方式：
  python matplotlib_basics.py

前置依赖：
  pip install matplotlib numpy
"""

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # 无 GUI 后端，适合服务器/脚本

import matplotlib.pyplot as plt
import numpy as np

# ── 全局样式设置 ──
plt.rcParams.update({
    "figure.dpi": 150,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
})

OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# 1. pyplot 基础 — figure/axes 模型
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. pyplot 基础 — figure/axes 模型")
print("=" * 60)

# 方式 A：plt 快捷接口（适合快速探索）
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 4))
plt.plot(x, y, "b-", linewidth=2, label="sin(x)")
plt.xlabel("x")
plt.ylabel("y")
plt.title("pyplot 快捷接口示例")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "01_pyplot_quick.png")
plt.close()
print("✅ 01_pyplot_quick.png")

# 方式 B：显式 axes 对象（推荐，完全控制）
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, np.sin(x), "b-", linewidth=2, label="sin(x)")
ax.plot(x, np.cos(x), "r--", linewidth=2, label="cos(x)")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("显式 Axes 对象 — 推荐方式")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 10)
ax.set_ylim(-1.2, 1.2)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "02_axes_explicit.png")
plt.close(fig)
print("✅ 02_axes_explicit.png")

print("\n💡 推荐使用 fig, ax = plt.subplots() 而非 plt.xxx()")
print("   原因: 多子图、双 y 轴等复杂场景下 axes 对象更清晰。")


# ═══════════════════════════════════════════════════════════════
# 2. 折线图与散点图
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 折线图与散点图 — 工程数据可视化")
print("=" * 60)

# ── 2a. 多曲线对比：不同厚度的应力-载荷曲线 ──
fig, ax = plt.subplots(figsize=(8, 5))

loads = np.linspace(0, 1.0, 50)  # MPa
thicknesses = [5, 8, 10, 12]  # mm
colors = ["#2166ac", "#67a9cf", "#ef8a62", "#b2182b"]

for t, color in zip(thicknesses, colors):
    # 简支板中心应力（近似）
    stress = 0.2874 * loads * 300**2 / t**2
    ax.plot(loads, stress, "-", color=color, linewidth=2, label=f"t={t} mm")

# 添加许用应力线
ax.axhline(y=235, color="red", linestyle="--", linewidth=1.5, alpha=0.7, label="Allowable 235 MPa")
ax.set_xlabel("Uniform Load (MPa)")
ax.set_ylabel("Max Stress (MPa)")
ax.set_title("Plate Center Stress vs. Load — Parameter Sweep")
ax.legend(title="Thickness")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "03_stress_vs_load.png")
plt.close(fig)
print("✅ 03_stress_vs_load.png — 参数扫描曲线")

# ── 2b. 散点图：节点应力分布 ──
np.random.seed(42)
n_nodes = 200
node_ids = np.arange(1, n_nodes + 1)
stress_x = np.random.normal(100, 30, n_nodes)
stress_y = np.random.normal(-20, 10, n_nodes)
von_mises = np.sqrt(stress_x**2 - stress_x*stress_y + stress_y**2)

fig, ax = plt.subplots(figsize=(8, 5))
scatter = ax.scatter(stress_x, stress_y, c=von_mises, cmap="RdYlBu_r",
                     s=von_mises/5, alpha=0.7, edgecolors="gray", linewidth=0.3)
ax.set_xlabel("σ_x (MPa)")
ax.set_ylabel("σ_y (MPa)")
ax.set_title("Nodal Stress Distribution — Colored by von Mises")
ax.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")
ax.axvline(x=0, color="gray", linewidth=0.5, linestyle="--")
cbar = fig.colorbar(scatter, ax=ax)
cbar.set_label("von Mises Stress (MPa)")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "04_stress_scatter.png")
plt.close(fig)
print("✅ 04_stress_scatter.png — 节点应力散点图")


# ═══════════════════════════════════════════════════════════════
# 3. 多子图布局
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 多子图布局 — 仿真结果面板")
print("=" * 60)

# ── 3a. 规则网格：subplots(nrows, ncols) ──
x = np.linspace(0, 2 * np.pi, 100)

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes = axes.flatten()  # 展平方便索引

titles = [
    "Displacement UY",
    "Stress SX",
    "Stress SY",
    "von Mises Stress"
]
y_data = [
    np.sin(x) * 2.5,            # 位移
    np.sin(x) * 120 + 100,       # SX
    np.cos(x) * 30 - 20,         # SY
    np.sqrt((np.sin(x)*120+100)**2 + (np.cos(x)*30-20)**2)  # von Mises
]
units = ["mm", "MPa", "MPa", "MPa"]

for i, ax in enumerate(axes):
    ax.plot(x, y_data[i], "-", color=f"C{i}", linewidth=2)
    ax.set_title(titles[i])
    ax.set_xlabel("Position")
    ax.set_ylabel(f"Value ({units[i]})")
    ax.grid(True, alpha=0.3)

fig.suptitle("Simulation Results Dashboard — Path Plot", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(OUTPUT_DIR / "05_subplots_grid.png")
plt.close(fig)
print("✅ 05_subplots_grid.png — 2×2 结果面板")

# ── 3b. 非对称布局：GridSpec ──
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(10, 7))
gs = GridSpec(3, 3, figure=fig)

ax_main = fig.add_subplot(gs[0:2, 0:2])    # 主图：左上 2x2
ax_top = fig.add_subplot(gs[0, 2])          # 右上
ax_mid = fig.add_subplot(gs[1, 2])          # 右中
ax_bottom = fig.add_subplot(gs[2, :])       # 底部横条

# 主图：应力云图伪彩色
X, Y = np.meshgrid(np.linspace(-5, 5, 50), np.linspace(-3, 3, 30))
Z = np.sqrt(X**2 + 0.5*Y**2) * 50
im = ax_main.contourf(X, Y, Z, levels=15, cmap="jet")
ax_main.set_title("Stress Contour (MPa)")
ax_main.set_xlabel("X (mm)")
ax_main.set_ylabel("Y (mm)")
fig.colorbar(im, ax=ax_main)

# 右上：X 轴应力曲线
ax_top.plot(X[15, :], Z[15, :], "r-", linewidth=2)
ax_top.set_title("Stress @ Y=0")
ax_top.grid(True, alpha=0.3)

# 右中：Y 轴应力曲线
ax_mid.plot(Y[:, 25], Z[:, 25], "b-", linewidth=2)
ax_mid.set_title("Stress @ X=0")
ax_mid.grid(True, alpha=0.3)

# 底部：统计条形图
categories = ["Max", "Min", "Mean", "Std"]
values = [np.max(Z), np.min(Z), np.mean(Z), np.std(Z)]
bars = ax_bottom.bar(categories, values, color=["#d7191c", "#2b83ba", "#abdda4", "#fdae61"])
ax_bottom.set_title("Stress Statistics (MPa)")
ax_bottom.bar_label(bars, fmt="%.1f", fontsize=9)

fig.suptitle("Advanced GridSpec Layout — Stress Analysis", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(OUTPUT_DIR / "06_gridspec_layout.png")
plt.close(fig)
print("✅ 06_gridspec_layout.png — 非对称 GridSpec 布局")


# ═══════════════════════════════════════════════════════════════
# 4. 仿真专用图表
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 仿真专用图表")
print("=" * 60)

# ── 4a. 双 y 轴：应力 + 位移 ──
x = np.linspace(0, 500, 100)  # 梁长度 [mm]
stress = 200 * np.exp(-((x - 250)**2) / (2 * 80**2))  # 模拟应力分布
displacement = 5 * (1 - np.cos(np.pi * x / 500))       # 模拟挠度

fig, ax1 = plt.subplots(figsize=(8, 4))

color1 = "#d62728"
ax1.plot(x, stress, "-", color=color1, linewidth=2, label="Stress")
ax1.set_xlabel("Position along beam (mm)")
ax1.set_ylabel("Stress (MPa)", color=color1)
ax1.tick_params(axis="y", labelcolor=color1)
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()  # 共享 x 轴的双 y 轴
color2 = "#1f77b4"
ax2.plot(x, displacement, "--", color=color2, linewidth=2, label="Deflection")
ax2.set_ylabel("Deflection (mm)", color=color2)
ax2.tick_params(axis="y", labelcolor=color2)

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

fig.suptitle("Beam Analysis — Stress & Deflection (Dual Y-Axis)", fontweight="bold")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "07_dual_axis.png")
plt.close(fig)
print("✅ 07_dual_axis.png — 双 y 轴（应力+位移）")

# ── 4b. S-N 曲线（疲劳） ──
N = np.logspace(3, 7, 50)  # 寿命 1e3 ~ 1e7
S_ut = 600  # 抗拉强度 [MPa]
S_e_prime = 0.5 * S_ut  # 旋转弯曲疲劳极限
S_1000 = 0.9 * S_ut     # 1000 次寿命强度

# Basquin 方程：S = S_1000 * (N/1000)^b
b = math.log10(S_e_prime / S_1000) / math.log10(1e6 / 1000)
S = S_1000 * (N / 1000) ** b

fig, ax = plt.subplots(figsize=(8, 5))
ax.loglog(N, S, "b-", linewidth=2.5, label="S-N Curve (Basquin)")
ax.axhline(y=S_e_prime, color="red", linestyle="--", linewidth=1.5, alpha=0.7,
           label=f"Endurance Limit {S_e_prime:.0f} MPa")
ax.axvline(x=1e6, color="gray", linestyle=":", linewidth=1, alpha=0.5,
           label="1E6 cycles (knee point)")

# 标注工作点
N_work = 5e5
S_work = S_1000 * (N_work / 1000) ** b
ax.plot(N_work, S_work, "ro", markersize=8)
ax.annotate(f"Working Point\nN={N_work:.0e}\nS={S_work:.0f} MPa",
            xy=(N_work, S_work), xytext=(N_work*3, S_work*1.15),
            arrowprops=dict(arrowstyle="->", color="red"),
            fontsize=9, color="red")

ax.set_xlabel("Cycles to Failure N")
ax.set_ylabel("Stress Amplitude S_a (MPa)")
ax.set_title("S-N Curve — Fatigue Analysis")
ax.legend()
ax.grid(True, alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "08_sn_curve.png")
plt.close(fig)
print("✅ 08_sn_curve.png — S-N 疲劳曲线")

# ── 4c. 载荷工况对比条形图 ──
cases = ["LC1\nDead", "LC2\nLive", "LC3\nWind", "LC4\nSeismic", "LC5\nCombo"]
stresses = [145, 198, 312, 445, 398]
allowable = 235

fig, ax = plt.subplots(figsize=(8, 5))
colors_bar = ["#2ca02c" if s < allowable else "#d62728" for s in stresses]
bars = ax.bar(cases, stresses, color=colors_bar, edgecolor="white", linewidth=0.5)

# 许用应力线
ax.axhline(y=allowable, color="orange", linestyle="--", linewidth=2, label=f"Allowable: {allowable} MPa")

# 数值标签
for bar, val in zip(bars, stresses):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f"{val}", ha="center", va="bottom", fontsize=10, fontweight="bold")

ax.set_ylabel("Max von Mises Stress (MPa)")
ax.set_title("Load Case Comparison — Max Stress")
ax.legend()
ax.set_ylim(0, max(stresses) * 1.2)
ax.grid(True, alpha=0.2, axis="y")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "09_load_case_bars.png")
plt.close(fig)
print("✅ 09_load_case_bars.png — 载荷工况对比条形图")


# ═══════════════════════════════════════════════════════════════
# 5. 样式与导出
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 样式与导出")
print("=" * 60)

# ── 5a. 预定义样式 ──
print("\n  可用样式:")
for s in ["default", "seaborn-v0_8", "ggplot", "bmh", "fivethirtyeight"]:
    try:
        plt.style.use(s)
        print(f"    ✅ {s}")
    except Exception:
        print(f"    ❌ {s} (not available)")

plt.style.use("default")  # 恢复默认

# ── 5b. 导出设置 ──
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot([0, 1, 2], [0, 1, 4], "b-o", linewidth=2)
ax.set_title("Export Format Demo")

# PNG — 位图，通用
fig.savefig(OUTPUT_DIR / "10_export.png", dpi=200, bbox_inches="tight")

# SVG — 矢量图，论文/报告推荐
fig.savefig(OUTPUT_DIR / "10_export.svg", bbox_inches="tight")

# PDF — 矢量，LaTeX 兼容
fig.savefig(OUTPUT_DIR / "10_export.pdf", bbox_inches="tight")

plt.close(fig)
print("\n✅ 导出格式: PNG (位图), SVG (矢量), PDF (矢量)")
print("  建议: 论文用 PDF/SVG, 快速预览用 PNG")

# ── 5c. 中文字体处理 ──
print("\n💡 中文字体提示:")
print("  import matplotlib.font_manager as fm")
print("  # 查找系统可用中文字体")
print("  fonts = [f.name for f in fm.fontManager.ttflist if 'Hei' in f.name or 'Song' in f.name]")
print("  plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', ...]")


# ═══════════════════════════════════════════════════════════════
# 6. 常见坑与调试
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 常见坑与调试")
print("=" * 60)

pitfalls = [
    ("坑1: GUI 后端崩溃",
     "服务器/无显示器环境调用 plt.show() → TclError",
     "脚本开头加 matplotlib.use('Agg')"),

    ("坑2: 内存泄漏",
     "循环中 plt.figure() 不 close() → 内存增长",
     "每次循环末尾 plt.close(fig) 或 plt.close('all')"),

    ("坑3: 中文字符方框",
     "标题/标签中的中文显示为 □",
     "设置 matplotlib 中文字体或改用英文"),

    ("坑4: 子图重叠",
     "不使用 tight_layout() → 标签/标题被截断",
     "fig.tight_layout() 或 constrained_layout=True"),

    ("坑5: 颜色映射选择",
     "jet 色图被过度使用，对色盲不友好",
     "考虑 viridis、plasma、coolwarm 等感知均匀色图"),

    ("坑6: 对数坐标误用",
     "loglog/semilog 中零值或负值 → 静默消失",
     "对数轴前先检查 min(data) > 0"),
]

for title, problem, solution in pitfalls:
    print(f"\n  ⚠  {title}")
    print(f"     问题: {problem}")
    print(f"     解决: {solution}")


# ═══════════════════════════════════════════════════════════════
# 7. 练习
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  7. 练习")
print("=" * 60)

print("""
  [练习 1] 修改 S-N 曲线脚本，添加第二个数据集：
           - 使用 Goodman 修正考虑平均应力
           - 在同一张图上叠加原始和修正曲线

  [练习 2] 创建"仿真报告封面图"：
           - 左上：变形云图 (contourf)
           - 右上：关键点应力时程
           - 下排：3 个统计表 (ax.table)

  [练习 3] 将参数扫描导出为多页 PDF：
           - 每页一个厚度，含应力+位移子图
           - 使用 matplotlib.backends.backend_pdf.PdfPages

  [练习 4] 从 CSV 读取仿真结果并可视化：
           - 读取 16-csv-export 生成的 param_sweep.csv
           - 绘制 thickness × load 的 utilization 热力图
""")

print("✅ 知识点 17 完成: Matplotlib 基础绘图")
