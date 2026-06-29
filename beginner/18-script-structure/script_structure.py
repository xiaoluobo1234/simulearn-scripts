"""
SimuLearn Scripts — 初级 #18：脚本工程化结构
=============================================
知识点：script-structure

从"一个文件写完"到"可维护的工程化脚本"，
关键差异不是代码量，而是组织方式。

本节涵盖：
  1. 脚本生命周期模式
  2. 配置与逻辑分离
  3. 参数化命令行
  4. 日志代替 print
  5. 入口函数模式
  6. 实战：完整分析脚本

运行方式：
  python script_structure.py
  python script_structure.py --help
  python script_structure.py --length 2.0 --force 5000
  python script_structure.py --verbose

前置依赖：
  pip install numpy
"""

import argparse
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

# ═══════════════════════════════════════════════════════════════
# 1. 脚本生命周期模式
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 脚本生命周期模式")
print("=" * 60)

print("""
  优秀仿真脚本的三个阶段：

  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │  1. SETUP   │ ──→ │  2. SOLVE   │ ──→ │ 3. POST     │
  │  参数解析    │     │  核心计算    │     │  结果输出    │
  │  配置加载    │     │  调用求解器  │     │  图表/报告   │
  │  输入验证    │     │  异常处理    │     │  数据导出    │
  └─────────────┘     └─────────────┘     └─────────────┘

  而不是把所有代码堆在文件顶层从上往下执行。
""")


# ═══════════════════════════════════════════════════════════════
# 2. 配置与逻辑分离
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  2. 配置与逻辑分离")
print("=" * 60)

# ❌ 坏做法：配置和逻辑混在一起
def bad_example():
    """配置散落在逻辑中 — 难以修改和复用。"""
    # 这些数字散落在代码各处，修改时容易遗漏
    length = 1.5       # ← 配置
    width = 0.1        # ← 配置
    E = 210e9          # ← 配置
    force = 10000      # ← 配置
    # ... 200 行计算逻辑 ...
    return length * width * E / force  # 虚构

# ✅ 好做法：用 dataclass 集中配置
@dataclass
class BeamConfig:
    """简支梁分析配置 — 单一事实来源。

    所有可调参数集中在此，便于：
    - 命令行覆盖
    - JSON/YAML 加载
    - 版本控制 diff
    """

    # 几何
    length_m: float = 1.5
    width_m: float = 0.1
    height_m: float = 0.2

    # 材料
    elastic_modulus_Pa: float = 210e9
    poisson_ratio: float = 0.3
    density_kgm3: float = 7850.0
    yield_stress_Pa: float = 235e6  # Q235

    # 载荷
    force_N: float = 10000.0
    safety_factor: float = 1.5

    # 网格
    n_elements: int = 100

    @property
    def area_m2(self) -> float:
        """截面积 [m²]"""
        return self.width_m * self.height_m

    @property
    def inertia_m4(self) -> float:
        """截面惯性矩 I = b·h³/12 [m⁴]"""
        return self.width_m * self.height_m**3 / 12.0

    @property
    def allowable_stress_Pa(self) -> float:
        """许用应力 [Pa]"""
        return self.yield_stress_Pa / self.safety_factor

    def validate(self) -> list:
        """验证配置合法性，返回错误列表。"""
        errors = []
        if self.length_m <= 0:
            errors.append("length_m must be positive")
        if self.width_m <= 0:
            errors.append("width_m must be positive")
        if self.height_m <= 0:
            errors.append("height_m must be positive")
        if self.elastic_modulus_Pa <= 0:
            errors.append("elastic_modulus_Pa must be positive")
        if self.force_N < 0:
            errors.append("force_N must be non-negative")
        if self.safety_factor <= 0:
            errors.append("safety_factor must be positive")
        return errors


print("✅ BeamConfig 定义完成")
print(f"   默认梁: {BeamConfig().length_m} m × {BeamConfig().width_m} m")
print(f"   截面积: {BeamConfig().area_m2:.4f} m²")


# ═══════════════════════════════════════════════════════════════
# 3. 参数化命令行
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 参数化命令行")
print("=" * 60)

def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。

    每个 CLI 参数映射到 BeamConfig 的一个字段，
    形成"命令行 → 配置 → 计算"的清晰数据流。
    """
    parser = argparse.ArgumentParser(
        description="简支梁弯曲分析",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                                    # 使用默认参数
  %(prog)s --length 2.0 --force 5000          # 指定长度和载荷
  %(prog)s --material steel --verbose         # 选择材料，详细输出
        """,
    )

    # 几何参数
    parser.add_argument("--length", "-L", type=float, default=1.5,
                        help="梁长度 [m] (默认: 1.5)")
    parser.add_argument("--width", "-W", type=float, default=0.1,
                        help="截面宽度 [m] (默认: 0.1)")
    parser.add_argument("--height", "-H", type=float, default=0.2,
                        help="截面高度 [m] (默认: 0.2)")

    # 载荷参数
    parser.add_argument("--force", "-F", type=float, default=10000.0,
                        help="集中力 [N] (默认: 10000)")

    # 材料预设
    parser.add_argument("--material", "-m", choices=["steel", "aluminum", "titanium"],
                        default="steel", help="材料预设 (默认: steel)")

    # 安全系数
    parser.add_argument("--safety-factor", "-sf", type=float, default=1.5,
                        help="安全系数 (默认: 1.5)")

    # 输出控制
    parser.add_argument("--output", "-o", type=Path, default=Path("./output"),
                        help="输出目录 (默认: ./output)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出")

    return parser


# 材料预设库
MATERIAL_PRESETS = {
    "steel": {
        "elastic_modulus_Pa": 210e9,
        "poisson_ratio": 0.3,
        "density_kgm3": 7850.0,
        "yield_stress_Pa": 235e6,
    },
    "aluminum": {
        "elastic_modulus_Pa": 70e9,
        "poisson_ratio": 0.33,
        "density_kgm3": 2700.0,
        "yield_stress_Pa": 275e6,
    },
    "titanium": {
        "elastic_modulus_Pa": 110e9,
        "poisson_ratio": 0.34,
        "density_kgm3": 4500.0,
        "yield_stress_Pa": 880e6,
    },
}

print("✅ CLI parser 定义完成")
print("   试试: python script_structure.py --help")
print("   试试: python script_structure.py --length 2.0 --material aluminum")


# ═══════════════════════════════════════════════════════════════
# 4. 日志代替 print
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 日志代替 print")
print("=" * 60)

def setup_logging(verbose: bool = False) -> logging.Logger:
    """配置日志系统。

    print 的问题：
      - 无法控制输出级别
      - 不能同时输出到文件和终端
      - 没有时间戳和模块名

    logging 的优势：
      - DEBUG / INFO / WARNING / ERROR / CRITICAL 五级
      - Handler 机制：一个日志可同时去文件、终端、网络
      - 自动包含时间戳、行号等上下文
    """
    level = logging.DEBUG if verbose else logging.INFO

    # 根 logger
    logger = logging.getLogger("beam_analysis")
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 终端 handler — 简洁格式
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(
        "%(levelname)-8s %(message)s"
    ))
    logger.addHandler(console)

    return logger


# 演示日志级别
demo_logger = setup_logging(verbose=False)
print("\n  日志级别演示 (当前 INFO):")
demo_logger.debug("这是 DEBUG — 调试细节")       # 不会显示
demo_logger.info("这是 INFO — 关键步骤")         # 会显示
demo_logger.warning("这是 WARNING — 需要注意")    # 会显示
demo_logger.error("这是 ERROR — 出错但可继续")    # 会显示

print("\n💡 日志格式: 级别 + 消息，可随时切换 DEBUG 看细节。")


# ═══════════════════════════════════════════════════════════════
# 5. 入口函数模式
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 入口函数模式")
print("=" * 60)

# ❌ 反模式：所有代码在模块顶层
# if __name__ == "__main__":
#     # 300 行代码全在这里...
#     pass

# ✅ 推荐：main() 函数 + 模块顶层只有 if __name__
# 好处：
#   1. main() 可被测试
#   2. 可被其他脚本 import 后调用
#   3. 变量不会污染全局命名空间

@dataclass
class BeamResult:
    """简支梁分析结果。"""
    max_deflection_m: float
    max_stress_Pa: float
    utilization: float
    passed: bool
    config: BeamConfig
    compute_time_s: float = 0.0


def solve_beam(config: BeamConfig, logger: logging.Logger) -> BeamResult:
    """核心求解逻辑 — 纯函数，无副作用。

    简支梁中心受集中力 P：
      δ_max = P·L³ / (48·E·I)
      σ_max = M_max·c / I = (P·L/4)·(h/2) / I

    Args:
        config: 梁配置
        logger: 日志记录器

    Returns:
        BeamResult 包含所有计算结果
    """
    t0 = time.perf_counter()

    L = config.length_m
    P = config.force_N
    E = config.elastic_modulus_Pa
    I = config.inertia_m4
    c = config.height_m / 2  # 中性轴到外表面距离

    # 最大挠度（中心点）
    deflection = P * L**3 / (48 * E * I)

    # 最大弯矩 M_max = P·L / 4（中心集中力）
    M_max = P * L / 4.0

    # 最大弯曲正应力
    stress = M_max * c / I

    # 利用率
    allowable = config.allowable_stress_Pa
    utilization = stress / allowable

    # 判断
    passed = utilization <= 1.0

    elapsed = time.perf_counter() - t0

    result = BeamResult(
        max_deflection_m=deflection,
        max_stress_Pa=stress,
        utilization=utilization,
        passed=passed,
        config=config,
        compute_time_s=elapsed,
    )

    logger.debug(f"求解耗时: {elapsed:.4f}s")
    return result


def format_result(result: BeamResult) -> str:
    """格式化结果报告（纯函数）。"""
    cfg = result.config
    lines = [
        "=" * 60,
        "  简支梁弯曲分析结果",
        "=" * 60,
        "",
        f"  配置:",
        f"    梁长 L = {cfg.length_m:.3f} m",
        f"    截面 b×h = {cfg.width_m*1000:.0f}×{cfg.height_m*1000:.0f} mm",
        f"    惯性矩 I = {cfg.inertia_m4:.6e} m⁴",
        f"    弹性模量 E = {cfg.elastic_modulus_Pa/1e9:.1f} GPa",
        f"    集中力 P = {cfg.force_N:.0f} N",
        "",
        f"  结果:",
        f"    最大挠度 δ_max = {result.max_deflection_m*1000:.4f} mm",
        f"    最大应力 σ_max = {result.max_stress_Pa/1e6:.2f} MPa",
        f"    许用应力 σ_allow = {cfg.allowable_stress_Pa/1e6:.2f} MPa",
        f"    利用率 UR = {result.utilization:.3f}",
        "",
        f"  判定: {'✅ PASS' if result.passed else '❌ FAIL'}",
        f"  计算时间: {result.compute_time_s:.4f} s",
        "=" * 60,
    ]
    return "\n".join(lines)


def run_analysis(
    config: BeamConfig,
    logger: logging.Logger,
    output_dir: Path,
) -> BeamResult:
    """完整的分析流程编排。

    这是最高层的编排函数，协调所有子步骤。
    每个子步骤都是独立可测试的函数。
    """
    logger.info("=" * 50)
    logger.info("  简支梁弯曲分析")
    logger.info("=" * 50)

    # ── Phase 1: 验证 ──
    logger.info("Phase 1/3: 输入验证...")
    errors = config.validate()
    if errors:
        for e in errors:
            logger.error(f"  配置错误: {e}")
        raise ValueError(f"配置验证失败: {errors}")
    logger.info("  配置验证通过 ✓")

    # ── Phase 2: 求解 ──
    logger.info("Phase 2/3: 求解...")
    logger.info(f"  梁长: {config.length_m} m, 力: {config.force_N} N")
    logger.info(f"  材料: E={config.elastic_modulus_Pa/1e9:.1f} GPa, "
                f"σ_y={config.yield_stress_Pa/1e6:.0f} MPa")
    result = solve_beam(config, logger)
    logger.info(f"  求解完成: δ_max={result.max_deflection_m*1000:.4f} mm, "
                f"σ_max={result.max_stress_Pa/1e6:.2f} MPa")

    # ── Phase 3: 输出 ──
    logger.info("Phase 3/3: 结果输出...")
    output_dir.mkdir(parents=True, exist_ok=True)

    report = format_result(result)
    logger.info(f"\n{report}")

    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"beam_report_{timestamp}.txt"
    report_path.write_text(report, encoding="utf-8")
    logger.info(f"  报告已保存: {report_path}")

    # 保存参数化结果 (CSV)
    import csv
    csv_path = output_dir / f"beam_result_{timestamp}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Parameter", "Value", "Unit"])
        writer.writerow(["Length", f"{config.length_m:.4f}", "m"])
        writer.writerow(["Width", f"{config.width_m*1000:.2f}", "mm"])
        writer.writerow(["Height", f"{config.height_m*1000:.2f}", "mm"])
        writer.writerow(["Force", f"{config.force_N:.1f}", "N"])
        writer.writerow(["E", f"{config.elastic_modulus_Pa/1e9:.2f}", "GPa"])
        writer.writerow(["Max Deflection", f"{result.max_deflection_m*1000:.4f}", "mm"])
        writer.writerow(["Max Stress", f"{result.max_stress_Pa/1e6:.2f}", "MPa"])
        writer.writerow(["Allowable Stress", f"{config.allowable_stress_Pa/1e6:.2f}", "MPa"])
        writer.writerow(["Utilization", f"{result.utilization:.4f}", "-"])
        writer.writerow(["Status", "PASS" if result.passed else "FAIL", "-"])
    logger.info(f"  CSV 已保存: {csv_path}")

    return result


# ═══════════════════════════════════════════════════════════════
# 6. 参数扫描 — 复用结构
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 参数扫描 — 复用分析结构")
print("=" * 60)

def parameter_sweep(
    base_config: BeamConfig,
    param_name: str,
    values: list,
    logger: logging.Logger,
) -> list:
    """参数扫描 — 展示工程化结构的复用性。

    只需改变一个参数，复用完整的分析流程。
    """
    logger.info(f"\n  参数扫描: {param_name} = {values}")
    results = []

    for val in values:
        # 复制配置并修改
        cfg = BeamConfig(
            length_m=val if param_name == "length_m" else base_config.length_m,
            width_m=base_config.width_m,
            height_m=base_config.height_m,
            elastic_modulus_Pa=base_config.elastic_modulus_Pa,
            poisson_ratio=base_config.poisson_ratio,
            density_kgm3=base_config.density_kgm3,
            yield_stress_Pa=base_config.yield_stress_Pa,
            force_N=val if param_name == "force_N" else base_config.force_N,
            safety_factor=base_config.safety_factor,
        )

        try:
            result = solve_beam(cfg, logger)
            results.append((val, result))
            logger.info(f"    {param_name}={val}: UR={result.utilization:.3f} "
                        f"{'✅' if result.passed else '❌'}")
        except Exception as e:
            logger.error(f"    {param_name}={val}: 计算失败 — {e}")

    return results


# 演示参数扫描
demo_config = BeamConfig()
demo_logger2 = setup_logging(verbose=False)

print("\n  扫描梁长 L = [1.0, 1.5, 2.0, 2.5, 3.0] m:")
sweep_results = parameter_sweep(demo_config, "length_m", [1.0, 1.5, 2.0, 2.5, 3.0], demo_logger2)

# 找到临界长度
for val, result in sweep_results:
    if not result.passed:
        print(f"  ⚠  L ≥ {val} m 时失效 (UR={result.utilization:.3f} > 1.0)")


# ═══════════════════════════════════════════════════════════════
# 7. main() — 入口函数
# ═══════════════════════════════════════════════════════════════

def main(argv: Optional[list] = None) -> int:
    """主入口 — 命令行程序的标准入口。

    Args:
        argv: 命令行参数列表 (None = sys.argv)

    Returns:
        0 表示成功，非零表示失败
    """
    # ── Phase 1: SETUP ──
    parser = build_parser()
    args = parser.parse_args(argv)

    logger = setup_logging(verbose=args.verbose)

    # 构建配置
    material = MATERIAL_PRESETS[args.material]
    config = BeamConfig(
        length_m=args.length,
        width_m=args.width,
        height_m=args.height,
        elastic_modulus_Pa=material["elastic_modulus_Pa"],
        poisson_ratio=material["poisson_ratio"],
        density_kgm3=material["density_kgm3"],
        yield_stress_Pa=material["yield_stress_Pa"],
        force_N=args.force,
        safety_factor=args.safety_factor,
    )

    # ── Phase 2: SOLVE ──
    try:
        result = run_analysis(config, logger, args.output)
    except ValueError as e:
        logger.error(f"分析中止: {e}")
        return 1
    except Exception as e:
        logger.exception(f"未预期的错误: {e}")
        return 2

    # ── Phase 3: 退出 ──
    logger.info(f"\n分析{'通过' if result.passed else '未通过'}。")
    return 0 if result.passed else 1


# ═══════════════════════════════════════════════════════════════
# 8. 练习
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  8. 练习")
print("=" * 60)

print("""
  [练习 1] 扩展 BeamConfig，支持：
           - 分布载荷 q (N/m) 替代集中力
           - 添加端点弯矩 M_end (N·m)
           - 更新 validate() 检查新参数

  [练习 2] 将 parameter_sweep 改进为生成器：
           - 用 yield 而非列表返回
           - 支持断点续扫（从 CSV 读取已计算的参数）
           - 每扫一个工况就写入 CSV 一行（防止中断丢数据）

  [练习 3] 添加 JSON 配置文件支持：
           - python script_structure.py --config beam_config.json
           - JSON 包含所有 BeamConfig 字段
           - CLI 参数覆盖 JSON 中的值（优先级：CLI > JSON > 默认）

  [练习 4] 添加并行扫描：
           - 使用 concurrent.futures.ProcessPoolExecutor
           - 扫描 100 个长度值
           - 对比串行/并行性能
""")

print("✅ 知识点 18 完成: 脚本工程化结构")


# ═══════════════════════════════════════════════════════════════
# 模块入口 — 只在直接运行时执行
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # 不带参数运行 → 展示默认分析
    # 带参数运行 → 走完整 CLI 流程
    import sys as _sys
    if len(_sys.argv) > 1:
        exit_code = main()
        _sys.exit(exit_code)
    else:
        # 演示模式：用默认参数走一遍完整流程
        print("\n" + "=" * 60)
        print("  🔬 演示模式 — 默认参数完整分析")
        print("=" * 60)
        logger = setup_logging(verbose=True)
        config = BeamConfig()
        try:
            result = run_analysis(config, logger, Path("./output"))
        except Exception as e:
            print(f"演示失败: {e}")
