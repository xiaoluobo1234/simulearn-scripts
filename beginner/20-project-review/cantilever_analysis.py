"""
SimuLearn Scripts — 初级 #20：综合项目实战
===========================================
知识点：project-review / 综合回顾

将前 19 个知识点融合为一个完整的仿真分析项目：
悬臂梁强度与挠度校核工具。

本项目串起全部初级知识点：

  01-python-intro       → 代码运行、注释、输出
  02-variables-types    → 类型注解、浮点精度
  03-operators          → 公式计算、比较判定
  04-strings            → f-string 格式化报告
  05-conditionals       → 分支校核逻辑
  06-loops              → 参数扫描循环
  07-lists-tuples       → 批量结果收集
  08-dicts-sets         → 材料库字典
  09-functions          → 模块化计算函数
  10-file-io            → JSON 配置读取、结果写入
  11-error-handling     → try/except 鲁棒处理
  12-modules            → import 组织
  13-virtual-env        → (环境已在 venv 中)
  14-ansys-data-types   → 应力张量数据表示
  15-apdl-parse         → (本脚本输出可供解析)
  16-csv-export         → CSV 结果导出
  17-basic-plotting     → Matplotlib 图表
  18-script-structure   → dataclass + CLI + logging + main()
  19-unit-conversion    → 单位安全换算

运行方式：
  # 默认参数
  python cantilever_analysis.py

  # 指定参数
  python cantilever_analysis.py --length 2.0 --force 5000 --material aluminum

  # 参数扫描模式
  python cantilever_analysis.py --sweep

  # 输出详细日志
  python cantilever_analysis.py --verbose

前置依赖：
  pip install numpy matplotlib
"""

import argparse
import csv
import json
import logging
import math
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

# 支持无 GUI 环境
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── 添加仓库根目录，以便导入 utils ──
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from utils.unit_converter import convert as safe_convert
except ImportError:
    # 如果导入失败，提供降级方案
    def safe_convert(value, from_unit, to_unit):
        """降级单位换算（当 utils 不可用时）。"""
        # 常用换算因子
        factors = {
            ("MPa", "Pa"): 1e6, ("GPa", "Pa"): 1e9,
            ("GPa", "MPa"): 1e3, ("mm", "m"): 1e-3,
            ("kN", "N"): 1e3, ("inch", "mm"): 25.4,
        }
        if (from_unit, to_unit) in factors:
            return value * factors[(from_unit, to_unit)]
        if (to_unit, from_unit) in factors:
            return value / factors[(to_unit, from_unit)]
        if from_unit == to_unit:
            return value
        raise ValueError(f"无法换算 {from_unit} → {to_unit}")
    print("⚠ utils.unit_converter 未找到，使用内置降级换算。")


# ═══════════════════════════════════════════════════════════════
# 1. 配置模型
# ═══════════════════════════════════════════════════════════════

# ── 材料库 (08-dicts-sets) ──
MATERIAL_DB: Dict[str, dict] = {
    "steel": {
        "name": "Structural Steel Q235",
        "E_GPa": 210.0,
        "nu": 0.30,
        "rho_kgm3": 7850.0,
        "sigma_y_MPa": 235.0,
        "sigma_u_MPa": 400.0,
        "thermal_expansion": 1.2e-5,
    },
    "aluminum": {
        "name": "Aluminum 6061-T6",
        "E_GPa": 69.0,
        "nu": 0.33,
        "rho_kgm3": 2700.0,
        "sigma_y_MPa": 275.0,
        "sigma_u_MPa": 310.0,
        "thermal_expansion": 2.3e-5,
    },
    "titanium": {
        "name": "Titanium Ti-6Al-4V",
        "E_GPa": 113.8,
        "nu": 0.34,
        "rho_kgm3": 4430.0,
        "sigma_y_MPa": 880.0,
        "sigma_u_MPa": 950.0,
        "thermal_expansion": 8.6e-6,
    },
    "stainless": {
        "name": "Stainless Steel 304",
        "E_GPa": 193.0,
        "nu": 0.29,
        "rho_kgm3": 8000.0,
        "sigma_y_MPa": 215.0,
        "sigma_u_MPa": 505.0,
        "thermal_expansion": 1.7e-5,
    },
}


@dataclass
class BeamConfig:
    """悬臂梁分析配置 (18-script-structure)。

    所有参数使用 SI 单位制内部存储。
    """

    # 几何
    length_m: float = 1.5
    width_mm: float = 100.0
    height_mm: float = 200.0

    # 材料
    material_key: str = "steel"

    # 载荷
    force_N: float = 10000.0
    force_location_m: Optional[float] = None  # None = 自由端

    # 安全系数
    safety_factor: float = 1.5

    # 网格
    n_evaluation_points: int = 50

    @property
    def width_m(self) -> float:
        return self.width_mm / 1000.0

    @property
    def height_m(self) -> float:
        return self.height_mm / 1000.0

    @property
    def area_m2(self) -> float:
        return self.width_m * self.height_m

    @property
    def inertia_m4(self) -> float:
        """矩形截面惯性矩 I = b·h³/12 [m⁴] (03-operators)"""
        return self.width_m * self.height_m**3 / 12.0

    @property
    def section_modulus_m3(self) -> float:
        """截面模量 W = I / (h/2) [m³]"""
        return self.inertia_m4 / (self.height_m / 2.0)

    @property
    def force_arm_m(self) -> float:
        """力臂长度（自由端 = 全长）。"""
        return self.length_m if self.force_location_m is None else self.force_location_m

    def get_material(self) -> dict:
        return MATERIAL_DB[self.material_key]

    @property
    def E_Pa(self) -> float:
        return self.get_material()["E_GPa"] * 1e9

    @property
    def sigma_y_Pa(self) -> float:
        return self.get_material()["sigma_y_MPa"] * 1e6

    @property
    def allowable_stress_Pa(self) -> float:
        return self.sigma_y_Pa / self.safety_factor

    def validate(self) -> List[str]:
        """验证配置 (11-error-handling)。"""
        errors = []
        if self.length_m <= 0:
            errors.append("length_m 必须 > 0")
        if self.width_mm <= 0:
            errors.append("width_mm 必须 > 0")
        if self.height_mm <= 0:
            errors.append("height_mm 必须 > 0")
        if self.force_N < 0:
            errors.append("force_N 必须 ≥ 0")
        if self.material_key not in MATERIAL_DB:
            errors.append(f"未知材料 '{self.material_key}'。可选: {list(MATERIAL_DB.keys())}")
        if self.safety_factor <= 0:
            errors.append("safety_factor 必须 > 0")
        if self.force_arm_m > self.length_m:
            errors.append(f"力臂 ({self.force_arm_m}m) 超过梁长 ({self.length_m}m)")
        return errors


# ═══════════════════════════════════════════════════════════════
# 2. 求解函数
# ═══════════════════════════════════════════════════════════════

@dataclass
class BeamResult:
    """悬臂梁分析完整结果 (14-ansys-data-types 概念)。"""

    config: BeamConfig

    # 全局极值
    max_stress_Pa: float = 0.0
    max_deflection_m: float = 0.0
    max_moment_Nm: float = 0.0
    max_shear_N: float = 0.0

    # 沿梁分布
    x_positions_m: List[float] = field(default_factory=list)
    moment_distribution_Nm: List[float] = field(default_factory=list)
    stress_distribution_Pa: List[float] = field(default_factory=list)
    deflection_distribution_m: List[float] = field(default_factory=list)

    # 判定
    utilization: float = 0.0
    passed: bool = False
    compute_time_s: float = 0.0


def compute_beam(config: BeamConfig) -> BeamResult:
    """悬臂梁理论求解 (09-functions, 03-operators)。

    悬臂梁，自由端受集中力 P：
      - 弯矩分布: M(x) = -P·(L - x)   (x 从固定端量起)
      - 最大弯矩: M_max = P·L (在固定端)
      - 挠度曲线: y(x) = P·x²·(3L - x) / (6·E·I)
      - 最大挠度: y_max = P·L³ / (3·E·I) (在自由端)
      - 弯曲应力: σ(x) = M(x) / W

    Args:
        config: 梁配置

    Returns:
        BeamResult 包含所有计算结果
    """
    t0 = time.perf_counter()

    L = config.length_m
    P = config.force_N
    E = config.E_Pa
    I = config.inertia_m4
    W = config.section_modulus_m3
    a = config.force_arm_m  # 力作用点距固定端

    # ── 离散化 ──
    n = config.n_evaluation_points
    x = np.linspace(0, L, n)

    # ── 弯矩分布 (06-loops 向量化) ──
    # 自由端集中力: M(x) = -P·(a - x)  for x ≤ a,  = 0 for x > a
    moment = np.where(x <= a, -P * (a - x), 0.0)
    # 取绝对值用于应力计算
    moment_abs = np.abs(moment)

    # ── 弯曲应力 (03-operators) ──
    stress = moment_abs / W

    # ── 挠度曲线 ──
    # 叠加法（自由端集中力）
    # 对 x ≤ a: y(x) = P·x²·(3a - x) / (6EI)
    # 对 x > a: y(x) = P·a²·(3x - a) / (6EI)
    deflection = np.where(
        x <= a,
        P * x**2 * (3*a - x) / (6 * E * I),
        P * a**2 * (3*x - a) / (6 * E * I)
    )
    # 挠度向下为正
    deflection_abs = np.abs(deflection)

    # ── 极值 ──
    max_moment = float(np.max(moment_abs))
    max_stress = float(np.max(stress))
    max_deflection = float(np.max(deflection_abs))

    # ── 校核 (05-conditionals) ──
    allowable = config.allowable_stress_Pa
    utilization = max_stress / allowable
    passed = utilization <= 1.0

    elapsed = time.perf_counter() - t0

    return BeamResult(
        config=config,
        max_stress_Pa=max_stress,
        max_deflection_m=max_deflection,
        max_moment_Nm=max_moment,
        max_shear_N=P,  # 悬臂梁全长剪力 = P
        x_positions_m=x.tolist(),
        moment_distribution_Nm=moment_abs.tolist(),
        stress_distribution_Pa=stress.tolist(),
        deflection_distribution_m=deflection_abs.tolist(),
        utilization=utilization,
        passed=passed,
        compute_time_s=elapsed,
    )


# ═══════════════════════════════════════════════════════════════
# 3. 报告生成
# ═══════════════════════════════════════════════════════════════

def format_report(result: BeamResult) -> str:
    """生成分析报告 (04-strings, 01-python-intro)。"""
    cfg = result.config
    mat = cfg.get_material()

    # 单位换算 (19-unit-conversion)
    stress_MPa = result.max_stress_Pa / 1e6
    deflection_mm = result.max_deflection_m * 1000
    moment_kNm = result.max_moment_Nm / 1000

    lines = [
        "╔══════════════════════════════════════════════════════════╗",
        "║          悬臂梁强度与挠度分析报告                       ║",
        "╚══════════════════════════════════════════════════════════╝",
        "",
        "━━━ 输入参数 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  梁长:        {cfg.length_m:.3f} m",
        f"  截面:        {cfg.width_mm:.0f} × {cfg.height_mm:.0f} mm",
        f"  面积:        {cfg.area_m2*1e6:.0f} mm²",
        f"  惯性矩:      {cfg.inertia_m4:.4e} m⁴",
        f"  截面模量:    {cfg.section_modulus_m3*1e6:.2f} cm³",
        "",
        f"  材料:        {mat['name']}",
        f"  弹性模量:    {mat['E_GPa']:.1f} GPa",
        f"  屈服强度:    {mat['sigma_y_MPa']:.0f} MPa",
        f"  安全系数:    {cfg.safety_factor:.1f}",
        f"  许用应力:    {cfg.allowable_stress_Pa/1e6:.1f} MPa",
        "",
        f"  载荷:        {cfg.force_N:.0f} N ({cfg.force_N/1000:.2f} kN)",
        f"  力臂:        {cfg.force_arm_m:.3f} m",
        "",
        "━━━ 计算结果 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  最大弯矩:    {moment_kNm:.2f} kN·m",
        f"  最大应力:    {stress_MPa:.2f} MPa",
        f"  最大挠度:    {deflection_mm:.3f} mm",
        f"  挠跨比:      {deflection_mm/(cfg.length_m*1000):.5f}",
        "",
        f"  应力利用率:  {result.utilization:.3f} ({result.utilization*100:.1f}%)",
        f"  安全裕度:    {(1-result.utilization)*100:.1f}%",
        "",
        f"  {'✅ 校核通过 — 设计安全' if result.passed else '❌ 校核失败 — 需修改设计'}",
        "",
        f"  计算耗时:    {result.compute_time_s:.4f} s",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# 4. 可视化 (17-matplotlib-basics)
# ═══════════════════════════════════════════════════════════════

def create_report_figures(result: BeamResult, output_dir: Path) -> List[Path]:
    """生成报告图表。"""
    cfg = result.config
    x = np.array(result.x_positions_m) * 1000  # 转为 mm
    files = []

    # ── 图 1: 综合面板 (弯矩 + 应力 + 挠度) ──
    fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

    # 弯矩图
    ax = axes[0]
    ax.fill_between(x, 0, np.array(result.moment_distribution_Nm)/1000,
                    color="#d62728", alpha=0.3)
    ax.plot(x, np.array(result.moment_distribution_Nm)/1000, "r-", linewidth=2)
    ax.set_ylabel("Moment (kN·m)", color="#d62728")
    ax.tick_params(axis="y", labelcolor="#d62728")
    ax.grid(True, alpha=0.3)
    ax.set_title("Cantilever Beam Analysis Results", fontsize=13, fontweight="bold")

    # 标注最大弯矩
    idx_max = np.argmax(np.abs(result.moment_distribution_Nm))
    ax.annotate(f'M_max={max(result.moment_distribution_Nm)/1000:.2f} kN·m',
                xy=(x[idx_max], max(result.moment_distribution_Nm)/1000),
                xytext=(x[idx_max]+50, max(result.moment_distribution_Nm)/1000*0.85),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=9, color='red')

    # 应力图
    ax = axes[1]
    ax.fill_between(x, 0, np.array(result.stress_distribution_Pa)/1e6,
                    color="#1f77b4", alpha=0.3)
    ax.plot(x, np.array(result.stress_distribution_Pa)/1e6, "b-", linewidth=2)
    # 许用应力线
    ax.axhline(y=cfg.allowable_stress_Pa/1e6, color="red", linestyle="--",
               linewidth=1.5, alpha=0.7, label=f'Allowable: {cfg.allowable_stress_Pa/1e6:.0f} MPa')
    ax.set_ylabel("Stress (MPa)", color="#1f77b4")
    ax.tick_params(axis="y", labelcolor="#1f77b4")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")

    # 挠度图
    ax = axes[2]
    ax.fill_between(x, 0, np.array(result.deflection_distribution_m)*1000,
                    color="#2ca02c", alpha=0.3)
    ax.plot(x, np.array(result.deflection_distribution_m)*1000, "g-", linewidth=2)
    ax.set_xlabel("Position along beam (mm)")
    ax.set_ylabel("Deflection (mm)", color="#2ca02c")
    ax.tick_params(axis="y", labelcolor="#2ca02c")
    ax.grid(True, alpha=0.3)

    # 标注最大挠度
    idx_max_d = np.argmax(result.deflection_distribution_m)
    ax.annotate(f'δ_max={max(result.deflection_distribution_m)*1000:.3f} mm',
                xy=(x[idx_max_d], max(result.deflection_distribution_m)*1000),
                xytext=(x[idx_max_d]-200, max(result.deflection_distribution_m)*1000*0.7),
                arrowprops=dict(arrowstyle='->', color='green'),
                fontsize=9, color='green')

    fig.tight_layout()
    path1 = output_dir / "beam_analysis_panel.png"
    fig.savefig(path1, dpi=150, bbox_inches="tight")
    plt.close(fig)
    files.append(path1)

    # ── 图 2: 应力利用率条形图 ──
    fig, ax = plt.subplots(figsize=(8, 2.5))

    ur = min(result.utilization, 1.5)

    # 背景条 (100% 线)
    ax.barh(["Utilization"], [1.0], color="#e0e0e0", height=0.4, label="Allowable (100%)")

    # 实际利用率
    bar_color = "#2ca02c" if result.utilization <= 1.0 else "#d62728"
    ax.barh(["Utilization"], [ur], color=bar_color, height=0.4, label=f"Actual ({ur*100:.1f}%)")

    # 100% 标记线
    ax.axvline(x=1.0, color="red", linestyle="--", linewidth=1.5, alpha=0.7)

    ax.set_xlim(0, max(1.3, ur * 1.1))
    ax.set_xlabel("Stress Utilization Ratio")
    ax.set_title("Stress Utilization Gauge", fontsize=12, fontweight="bold")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3, axis="x")

    # 数值标注
    ax.text(ur / 2, 0, f"{ur*100:.1f}%", ha="center", va="center",
            fontsize=14, fontweight="bold", color="white" if ur > 0.35 else "black")

    status_text = "✅ PASS" if result.passed else "❌ FAIL"
    status_color = "green" if result.passed else "red"
    ax.text(0.98, 0.85, status_text, transform=ax.transAxes, ha="right",
            fontsize=16, fontweight="bold", color=status_color)

    path2 = output_dir / "utilization_gauge.png"
    fig.savefig(path2, dpi=150, bbox_inches="tight")
    plt.close(fig)
    files.append(path2)

    return files


# ═══════════════════════════════════════════════════════════════
# 5. CSV 导出 (16-csv-export)
# ═══════════════════════════════════════════════════════════════

def export_results_csv(result: BeamResult, output_dir: Path) -> Path:
    """导出分布结果到 CSV。"""
    path = output_dir / "beam_distribution.csv"

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # 元数据
        writer.writerow(["# Cantilever Beam Distribution Data"])
        writer.writerow(["# Generated:", datetime.now().isoformat()])
        writer.writerow(["# Config:", json.dumps({
            "length_m": result.config.length_m,
            "width_mm": result.config.width_mm,
            "height_mm": result.config.height_mm,
            "material": result.config.material_key,
            "force_N": result.config.force_N,
        })])
        writer.writerow([])

        # 数据表头
        writer.writerow([
            "Position (mm)", "Moment (kN·m)",
            "Stress (MPa)", "Deflection (mm)"
        ])

        for i, x_m in enumerate(result.x_positions_m):
            writer.writerow([
                f"{x_m*1000:.2f}",
                f"{result.moment_distribution_Nm[i]/1000:.4f}",
                f"{result.stress_distribution_Pa[i]/1e6:.3f}",
                f"{result.deflection_distribution_m[i]*1000:.4f}",
            ])

    return path


# ═══════════════════════════════════════════════════════════════
# 6. 参数扫描 (06-loops, 07-lists-tuples)
# ═══════════════════════════════════════════════════════════════

def parameter_sweep(
    base_config: BeamConfig,
    param_name: str,
    values: List[float],
    logger: logging.Logger,
) -> List[Tuple[float, BeamResult]]:
    """参数扫描 — 改变一个参数，收集所有结果。"""
    results = []
    total = len(values)

    for i, val in enumerate(values):
        cfg = BeamConfig(
            length_m=val if param_name == "length" else base_config.length_m,
            width_mm=base_config.width_mm,
            height_mm=base_config.height_mm,
            material_key=base_config.material_key,
            force_N=val if param_name == "force" else base_config.force_N,
            safety_factor=base_config.safety_factor,
            n_evaluation_points=base_config.n_evaluation_points,
        )

        try:
            result = compute_beam(cfg)
            results.append((val, result))
            status = "✅" if result.passed else "❌"
            logger.info(
                f"  [{i+1:3d}/{total}] {param_name}={val:<8.4g}  "
                f"σ={result.max_stress_Pa/1e6:7.2f} MPa  "
                f"δ={result.max_deflection_m*1000:7.3f} mm  "
                f"UR={result.utilization:.3f}  {status}"
            )
        except Exception as e:
            logger.error(f"  [{i+1:3d}/{total}] {param_name}={val}: 计算失败 — {e}")

    return results


def export_sweep_csv(
    sweep_results: List[Tuple[float, BeamResult]],
    param_name: str,
    output_dir: Path,
) -> Path:
    """导出参数扫描汇总 CSV。"""
    path = output_dir / f"sweep_{param_name}.csv"

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([f"# Parameter Sweep: {param_name}"])
        writer.writerow([])
        writer.writerow([
            param_name, "Max Stress (MPa)", "Max Deflection (mm)",
            "Utilization", "Pass/Fail", "Compute Time (s)"
        ])

        for val, result in sweep_results:
            writer.writerow([
                f"{val:.4g}",
                f"{result.max_stress_Pa/1e6:.3f}",
                f"{result.max_deflection_m*1000:.4f}",
                f"{result.utilization:.4f}",
                "PASS" if result.passed else "FAIL",
                f"{result.compute_time_s:.6f}",
            ])

    return path


def plot_sweep_results(
    sweep_results: List[Tuple[float, BeamResult]],
    param_name: str,
    output_dir: Path,
) -> Path:
    """绘制参数扫描图。"""
    values = [v for v, _ in sweep_results]
    stresses = [r.max_stress_Pa/1e6 for _, r in sweep_results]
    deflections = [r.max_deflection_m*1000 for _, r in sweep_results]
    utilizations = [r.utilization for _, r in sweep_results]
    allowable = sweep_results[0][1].config.allowable_stress_Pa / 1e6

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # 应力 + 许用应力
    ax1.plot(values, stresses, "b-o", linewidth=2, markersize=4, label="Max Stress")
    ax1.axhline(y=allowable, color="red", linestyle="--", linewidth=1.5,
                label=f"Allowable: {allowable:.0f} MPa")
    ax1.set_ylabel("Stress (MPa)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title(f"Parameter Sweep: {param_name} — Stress & Deflection", fontweight="bold")

    # 挠度
    ax2.plot(values, deflections, "g-s", linewidth=2, markersize=4, label="Max Deflection")
    ax2.set_xlabel(param_name)
    ax2.set_ylabel("Deflection (mm)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 标注临界点（利用率 = 1.0 附近）
    for i, ur in enumerate(utilizations):
        if 0.95 <= ur <= 1.05:
            ax1.annotate(f'UR={ur:.2f}', (values[i], stresses[i]),
                        textcoords="offset points", xytext=(0, 15),
                        fontsize=8, color="red", ha="center")

    fig.tight_layout()
    path = output_dir / f"sweep_{param_name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


# ═══════════════════════════════════════════════════════════════
# 7. main() 入口 (18-script-structure)
# ═══════════════════════════════════════════════════════════════

def build_cli() -> argparse.ArgumentParser:
    """构建命令行接口 (12-modules: argparse)。"""
    parser = argparse.ArgumentParser(
        description="悬臂梁强度与挠度校核工具 v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                                           # 默认参数
  %(prog)s -L 2.0 -F 5000 -m aluminum                # 指定参数
  %(prog)s --sweep --sweep-param force --sweep-range 1000 20000 20
  %(prog)s --config beam_config.json                 # 从 JSON 加载
  %(prog)s -v                                        # 详细日志
        """,
    )

    # 几何
    parser.add_argument("--length", "-L", type=float, default=1.5,
                        help="梁长 [m] (默认: 1.5)")
    parser.add_argument("--width", "-W", type=float, default=100.0,
                        help="截面宽度 [mm] (默认: 100)")
    parser.add_argument("--height", "-H", type=float, default=200.0,
                        help="截面高度 [mm] (默认: 200)")

    # 材料与载荷
    parser.add_argument("--material", "-m", choices=list(MATERIAL_DB.keys()),
                        default="steel", help="材料 (默认: steel)")
    parser.add_argument("--force", "-F", type=float, default=10000.0,
                        help="集中力 [N] (默认: 10000)")
    parser.add_argument("--safety-factor", "-sf", type=float, default=1.5,
                        help="安全系数 (默认: 1.5)")

    # 扫描模式
    parser.add_argument("--sweep", action="store_true",
                        help="参数扫描模式")
    parser.add_argument("--sweep-param", choices=["length", "force"],
                        default="force", help="扫描参数 (默认: force)")
    parser.add_argument("--sweep-range", nargs=3, type=float,
                        metavar=("START", "STOP", "N"),
                        help="扫描范围: 起始 终止 点数")

    # 配置文件
    parser.add_argument("--config", "-c", type=Path,
                        help="JSON 配置文件路径")

    # 输出
    parser.add_argument("--output", "-o", type=Path, default=Path("./output"),
                        help="输出目录 (默认: ./output)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出")
    parser.add_argument("--no-plot", action="store_true",
                        help="跳过绘图")

    return parser


def setup_logging(verbose: bool = False) -> logging.Logger:
    """配置日志系统。"""
    logger = logging.getLogger("cantilever")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)-7s] %(message)s",
            datefmt="%H:%M:%S",
        ))
        logger.addHandler(handler)

    return logger


def load_config_from_json(path: Path, logger: logging.Logger) -> BeamConfig:
    """从 JSON 文件加载配置 (10-file-io)。"""
    logger.info(f"从配置文件加载: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"配置文件不存在: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析错误: {e}")
        raise

    return BeamConfig(
        length_m=data.get("length_m", 1.5),
        width_mm=data.get("width_mm", 100.0),
        height_mm=data.get("height_mm", 200.0),
        material_key=data.get("material", "steel"),
        force_N=data.get("force_N", 10000.0),
        force_location_m=data.get("force_location_m"),
        safety_factor=data.get("safety_factor", 1.5),
        n_evaluation_points=data.get("n_points", 50),
    )


def main(argv: Optional[List[str]] = None) -> int:
    """主入口函数。

    Returns:
        0 = 成功, 1 = 校核失败, 2 = 运行错误
    """
    # ── Phase 1: SETUP ──
    parser = build_cli()
    args = parser.parse_args(argv)
    logger = setup_logging(args.verbose)

    logger.info("╔════════════════════════════════════════╗")
    logger.info("║  悬臂梁强度与挠度校核工具 v1.0       ║")
    logger.info("╚════════════════════════════════════════╝")

    # 输出目录
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    # 构建配置
    if args.config:
        try:
            config = load_config_from_json(args.config, logger)
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            return 2
    else:
        config = BeamConfig(
            length_m=args.length,
            width_mm=args.width,
            height_mm=args.height,
            material_key=args.material,
            force_N=args.force,
            safety_factor=args.safety_factor,
        )

    # CLI 参数覆盖 JSON 配置
    if not args.config:
        pass  # 已用 CLI 参数
    else:
        # 允许 CLI 参数覆盖 JSON
        if args.length != 1.5:
            config.length_m = args.length
        if args.width != 100.0:
            config.width_mm = args.width
        if args.height != 200.0:
            config.height_mm = args.height
        if args.material != "steel":
            config.material_key = args.material
        if args.force != 10000.0:
            config.force_N = args.force
        if args.safety_factor != 1.5:
            config.safety_factor = args.safety_factor

    # 验证配置
    errors = config.validate()
    if errors:
        for e in errors:
            logger.error(f"配置错误: {e}")
        return 2

    material_info = config.get_material()
    logger.info(f"材料: {material_info['name']}")
    logger.info(f"梁长: {config.length_m} m, "
                f"截面: {config.width_mm}×{config.height_mm} mm, "
                f"力: {config.force_N} N")

    # ── Phase 2: SOLVE ──
    try:
        if args.sweep:
            # 参数扫描模式
            if args.sweep_range:
                start, stop, n = args.sweep_range
                values = list(np.linspace(start, stop, int(n)))
            else:
                # 默认扫描范围
                if args.sweep_param == "force":
                    values = list(np.linspace(1000, 20000, 20))
                else:
                    values = list(np.linspace(0.5, 3.0, 20))

            logger.info(f"\n参数扫描: {args.sweep_param} 从 {values[0]} 到 {values[-1]} ({len(values)} 点)")

            sweep_results = parameter_sweep(config, args.sweep_param, values, logger)

            # 导出扫描结果
            csv_path = export_sweep_csv(sweep_results, args.sweep_param, output_dir)
            logger.info(f"\n扫描结果已导出: {csv_path}")

            # 扫描图
            if not args.no_plot:
                plot_path = plot_sweep_results(sweep_results, args.sweep_param, output_dir)
                logger.info(f"扫描图表已保存: {plot_path}")

            # 汇总
            passed = sum(1 for _, r in sweep_results if r.passed)
            logger.info(f"\n扫描完成: {passed}/{len(sweep_results)} 通过")
            return 0 if passed == len(sweep_results) else 1

        else:
            # 单点分析模式
            logger.info("\n开始求解...")
            result = compute_beam(config)

            # ── Phase 3: POST ──
            # 控制台报告
            report = format_report(result)
            logger.info(f"\n{report}")

            # 保存文本报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = output_dir / f"beam_report_{timestamp}.txt"
            report_path.write_text(report, encoding="utf-8")
            logger.info(f"报告已保存: {report_path}")

            # 保存 JSON 结果
            json_path = output_dir / f"beam_result_{timestamp}.json"
            result_dict = {
                "config": {
                    "length_m": config.length_m,
                    "width_mm": config.width_mm,
                    "height_mm": config.height_mm,
                    "material": config.material_key,
                    "force_N": config.force_N,
                    "safety_factor": config.safety_factor,
                },
                "results": {
                    "max_stress_MPa": result.max_stress_Pa / 1e6,
                    "max_deflection_mm": result.max_deflection_m * 1000,
                    "max_moment_kNm": result.max_moment_Nm / 1000,
                    "utilization": result.utilization,
                    "passed": result.passed,
                    "compute_time_s": result.compute_time_s,
                },
            }
            json_path.write_text(json.dumps(result_dict, indent=2, ensure_ascii=False),
                                encoding="utf-8")
            logger.info(f"JSON 结果已保存: {json_path}")

            # CSV 分布数据
            csv_path = export_results_csv(result, output_dir)
            logger.info(f"CSV 分布数据已导出: {csv_path}")

            # 图表
            if not args.no_plot:
                try:
                    fig_paths = create_report_figures(result, output_dir)
                    for p in fig_paths:
                        logger.info(f"图表已保存: {p}")
                except Exception as e:
                    logger.warning(f"图表生成失败: {e}")

            return 0 if result.passed else 1

    except Exception as e:
        logger.exception(f"分析失败: {e}")
        return 2


# ═══════════════════════════════════════════════════════════════
# 8. 示例配置文件生成
# ═══════════════════════════════════════════════════════════════

def generate_example_config(output_dir: Path) -> None:
    """生成示例 JSON 配置文件。"""
    example_config = {
        "_comment": "悬臂梁分析配置文件 — 修改此文件后运行 python cantilever_analysis.py --config beam_config.json",
        "length_m": 1.5,
        "width_mm": 100.0,
        "height_mm": 200.0,
        "material": "steel",
        "force_N": 10000.0,
        "force_location_m": None,
        "safety_factor": 1.5,
        "n_points": 50,
    }
    config_path = output_dir / "beam_config_example.json"
    config_path.write_text(json.dumps(example_config, indent=2, ensure_ascii=False),
                           encoding="utf-8")
    print(f"示例配置已生成: {config_path}")


# ═══════════════════════════════════════════════════════════════
# 模块入口
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 带参数：走完整 CLI
        exit_code = main()
        sys.exit(exit_code)
    else:
        # 演示模式：展示完整功能
        print("\n" + "=" * 60)
        print("  🔬 综合项目实战 — 悬臂梁分析演示")
        print("=" * 60)
        print()

        logger = setup_logging(verbose=True)

        # 生成示例配置
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)
        generate_example_config(output_dir)

        # 演示 1: 默认参数分析
        print("\n── 演示 1: 默认参数分析 ──")
        config = BeamConfig()
        result = compute_beam(config)
        print(format_report(result))

        # 演示 2: 材料对比
        print("\n── 演示 2: 四种材料对比 ──")
        print(f"  {'材料':<20} {'σ_max':>10} {'δ_max':>10} {'UR':>8} {'判定':>6}")
        print(f"  {'─'*20} {'─'*10} {'─'*10} {'─'*8} {'─'*6}")
        for mat_key in ["steel", "aluminum", "titanium", "stainless"]:
            cfg = BeamConfig(material_key=mat_key)
            res = compute_beam(cfg)
            print(f"  {MATERIAL_DB[mat_key]['name']:<20} "
                  f"{res.max_stress_Pa/1e6:>8.2f} MPa "
                  f"{res.max_deflection_m*1000:>8.3f} mm "
                  f"{res.utilization:>8.3f} "
                  f"{'✅' if res.passed else '❌':>6}")

        # 演示 3: 参数扫描
        print("\n── 演示 3: 力参数扫描 (1000-20000 N, 10 点) ──")
        sweep_vals = list(np.linspace(1000, 20000, 10))
        sweep_results = parameter_sweep(config, "force", sweep_vals, logger)

        # 图表
        try:
            fig_paths = create_report_figures(result, output_dir)
            print(f"\n✅ 图表已保存到 {output_dir}/")
            for p in fig_paths:
                print(f"   {p.name}")
        except Exception as e:
            print(f"\n⚠ 图表生成失败: {e}")

        print("\n✅ 综合项目实战完成！")
        print("  前 19 个知识点全部融入了这个完整的分析工具。")
