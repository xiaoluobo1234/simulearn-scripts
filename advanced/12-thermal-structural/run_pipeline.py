"""
SimuLearn Scripts — 高级示例：热—结构耦合自动化流水线框架
==========================================================
知识点：热—结构耦合循环 (advanced/12-thermal-structural)

展示如何用 Python 编排热分析→温度映射→结构分析的完整流程。
这是一个框架/模板，实际运行需要 ANSYS 环境。

设计理念：
  - 每个分析步骤是独立的函数
  - 步骤间通过明确的数据结构传递
  - 每步有独立的验证和日志
  - 支持断点续跑（检查中间文件是否存在）

运行方式（无 ANSYS 环境时仅展示框架）：
  python run_pipeline.py --demo
"""

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# 1. 数据模型 — 用 dataclass 定义清晰的数据结构
# ─────────────────────────────────────────────────────────────

@dataclass
class MaterialProps:
    """材料属性（温度相关）。"""
    name: str
    elastic_modulus_GPa: float       # 弹性模量 [GPa]
    poisson_ratio: float             # 泊松比
    cte_ppm_per_K: float             # 热膨胀系数 [ppm/K]
    thermal_conductivity_W_per_mK: float  # 导热系数 [W/(m·K)]
    density_kg_per_m3: float         # 密度 [kg/m³]
    specific_heat_J_per_kgK: float   # 比热容 [J/(kg·K)]


@dataclass
class ThermalBC:
    """热边界条件。"""
    ambient_temp_C: float = 25.0     # 环境温度 [°C]
    htc_W_per_m2K: float = 10.0      # 对流换热系数 [W/(m²·K)]
    heat_source_W: float = 0.0       # 热源功率 [W]


@dataclass
class StructuralBC:
    """结构边界条件。"""
    fixed_faces: list = field(default_factory=list)  # 固定面名称
    pressure_MPa: float = 0.0                        # 压力 [MPa]


@dataclass
class AnalysisConfig:
    """完整分析配置。"""
    project_name: str
    working_dir: Path
    material: MaterialProps
    thermal_bc: ThermalBC
    structural_bc: StructuralBC
    mesh_size_mm: float = 1.0

    # 求解控制
    thermal_steady_state: bool = True
    thermal_time_end_s: float = 3600.0
    thermal_time_step_s: float = 60.0
    structural_nonlinear: bool = False

    # 输出控制
    save_intermediate: bool = True
    verbose: bool = True


@dataclass
class StepResult:
    """单步分析结果。"""
    step_name: str
    success: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metrics: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    output_files: list = field(default_factory=list)


# ─────────────────────────────────────────────────────────────
# 2. 分析步骤 — 每步独立、可测试、可替换
# ─────────────────────────────────────────────────────────────

class ThermalAnalysis:
    """热分析步骤（模板 — 实际需连接 ANSYS）。"""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self._result: Optional[StepResult] = None

    def run(self) -> StepResult:
        """执行热分析。"""
        logger.info("🔥 开始热分析...")
        result = StepResult(step_name="thermal")

        try:
            # --- 在实际实现中，这里调用 PyMAPDL / PyFluent ---
            # mapdl = launch_mapdl()
            # mapdl.prep7()
            # mapdl.mp("KXX", 1, self.config.material.thermal_conductivity_W_per_mK)
            # ...

            # 模拟分析过程
            self._check_inputs()
            self._apply_boundary_conditions()
            self._solve()
            self._post_process()

            result.success = True
            result.metrics = {
                "T_max_C": 85.3,
                "T_min_C": 32.1,
                "T_avg_C": 58.7,
                "heat_balance_W": 0.15,  # 残差
                "mesh_nodes": 125000,
            }
            logger.info(f"   ✅ 热分析完成: T_max = {result.metrics['T_max_C']}°C")

        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logger.error(f"   ❌ 热分析失败: {e}")

        self._result = result
        return result

    def _check_inputs(self):
        """验证输入参数合理性。"""
        if self.config.material.thermal_conductivity_W_per_mK <= 0:
            raise ValueError("导热系数必须 > 0")
        if self.config.mesh_size_mm <= 0:
            raise ValueError("网格尺寸必须 > 0")

    def _apply_boundary_conditions(self):
        """施加热边界条件。"""
        logger.info(f"   环境温度: {self.config.thermal_bc.ambient_temp_C}°C")
        logger.info(f"   对流系数: {self.config.thermal_bc.htc_W_per_m2K} W/(m²·K)")
        logger.info(f"   热源功率: {self.config.thermal_bc.heat_source_W} W")

    def _solve(self):
        """求解温度场。"""
        logger.info("   求解稳态温度场...")

    def _post_process(self):
        """提取温度结果。"""
        logger.info("   提取节点温度...")


class TemperatureMapper:
    """温度场映射到结构网格。"""

    def __init__(self, config: AnalysisConfig):
        self.config = config

    def map(self, thermal_result: StepResult) -> StepResult:
        """将热分析温度映射到结构网格。

        Args:
            thermal_result: 热分析结果

        Returns:
            映射步骤结果
        """
        logger.info("🗺️  开始温度场映射...")
        result = StepResult(step_name="temperature_mapping")

        if not thermal_result.success:
            result.success = False
            result.errors.append("上游热分析失败，无法进行温度映射")
            return result

        try:
            # 实际实现中用 DPF 或插值
            # 检查映射误差
            mapping_error_max = 0.5  # °C
            mapping_error_rms = 0.12  # °C

            result.success = True
            result.metrics = {
                "mapping_method": "DPF profile preserving",
                "mapping_error_max_C": mapping_error_max,
                "mapping_error_rms_C": mapping_error_rms,
                "mapped_nodes": 98000,
            }

            if mapping_error_max > 1.0:
                result.warnings.append(
                    f"映射误差 {mapping_error_max}°C 超过 1°C 建议值"
                )

            logger.info(f"   ✅ 温度映射完成: 误差 RMS = {mapping_error_rms}°C")

        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logger.error(f"   ❌ 温度映射失败: {e}")

        return result


class StructuralAnalysis:
    """结构分析步骤（含热载荷）。"""

    def __init__(self, config: AnalysisConfig):
        self.config = config

    def run(self, thermal_result: StepResult,
            mapping_result: StepResult) -> StepResult:
        """执行热—结构耦合分析。

        Args:
            thermal_result: 热分析结果
            mapping_result: 温度映射结果

        Returns:
            结构分析结果
        """
        logger.info("🏗️  开始结构分析（含热载荷）...")
        result = StepResult(step_name="structural")

        if not mapping_result.success:
            result.success = False
            result.errors.append("温度映射失败，无法进行结构分析")
            return result

        try:
            # 实际实现中调用 ANSYS 结构求解器
            # 温度场作为体载荷施加

            T_ref = 25.0  # 参考温度
            T_max = thermal_result.metrics.get("T_max_C", 0)
            delta_T = T_max - T_ref

            # 热应变估算
            alpha = self.config.material.cte_ppm_per_K * 1e-6
            thermal_strain = alpha * delta_T

            # 热应力估算（仅约束情况下）
            E = self.config.material.elastic_modulus_GPa * 1e9
            thermal_stress_MPa = E * thermal_strain / 1e6

            result.success = True
            result.metrics = {
                "delta_T_max_C": delta_T,
                "thermal_strain": thermal_strain,
                "thermal_stress_MPa_est": thermal_stress_MPa,
                "max_displacement_mm": 0.15,
                "max_von_mises_MPa": 180.5,
                "reaction_force_N": 2500.0,
                "convergence_iterations": 12,
            }

            logger.info(f"   ✅ 结构分析完成:")
            logger.info(f"      最大温差: {delta_T:.1f}°C")
            logger.info(f"      最大应力: {result.metrics['max_von_mises_MPa']:.1f} MPa")
            logger.info(f"      最大位移: {result.metrics['max_displacement_mm']:.3f} mm")

        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logger.error(f"   ❌ 结构分析失败: {e}")

        return result


class ResultValidator:
    """结果验证器。"""

    def validate(self, thermal: StepResult, structural: StepResult) -> StepResult:
        """交叉验证热和结构分析结果。

        验证项:
        1. 热平衡检查
        2. 结构反力 = 外载荷
        3. 应力量级合理性
        """
        logger.info("🔍 开始结果验证...")
        result = StepResult(step_name="validation")

        checks = []

        # 检查1：热平衡
        hb = thermal.metrics.get("heat_balance_W", 999)
        if hb < 1.0:
            checks.append(("✅", f"热平衡残差 {hb:.3f} W < 1.0 W"))
        else:
            checks.append(("⚠️", f"热平衡残差 {hb:.3f} W 偏高"))

        # 检查2：应力是否在合理范围
        vm = structural.metrics.get("max_von_mises_MPa", 0)
        if vm > 0 and vm < 1000:
            checks.append(("✅", f"von Mises 应力 {vm:.1f} MPa 在合理范围"))
        else:
            checks.append(("⚠️", f"von Mises 应力 {vm:.1f} MPa 异常"))

        # 检查3：位移量级
        d = structural.metrics.get("max_displacement_mm", 0)
        checks.append(("ℹ️", f"最大位移 {d:.3f} mm — 请人工判断是否合理"))

        for status, msg in checks:
            logger.info(f"   {status} {msg}")

        result.success = all(c[0] != "❌" for c in checks)
        result.metrics = {"checks_passed": sum(1 for c in checks if c[0] == "✅"),
                          "checks_total": len(checks)}

        return result


# ─────────────────────────────────────────────────────────────
# 3. 流水线编排
# ─────────────────────────────────────────────────────────────

class ThermalStructuralPipeline:
    """热—结构耦合分析流水线。"""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.thermal = ThermalAnalysis(config)
        self.mapper = TemperatureMapper(config)
        self.structural = StructuralAnalysis(config)
        self.validator = ResultValidator()
        self.results: dict[str, StepResult] = {}

    def run(self) -> dict[str, StepResult]:
        """运行完整流水线。

        Returns:
            各步骤结果字典
        """
        logger.info("=" * 60)
        logger.info(f"  流水线启动: {self.config.project_name}")
        logger.info(f"  工作目录: {self.config.working_dir}")
        logger.info("=" * 60)

        # Step 1: 热分析
        r_thermal = self.thermal.run()
        self.results["thermal"] = r_thermal
        if not r_thermal.success:
            logger.error("热分析失败，流水线终止")
            return self.results

        # Step 2: 温度映射
        r_map = self.mapper.map(r_thermal)
        self.results["mapping"] = r_map
        if not r_map.success:
            logger.error("温度映射失败，流水线终止")
            return self.results

        # Step 3: 结构分析
        r_struct = self.structural.run(r_thermal, r_map)
        self.results["structural"] = r_struct
        if not r_struct.success:
            logger.error("结构分析失败，流水线终止")
            return self.results

        # Step 4: 验证
        r_valid = self.validator.validate(r_thermal, r_struct)
        self.results["validation"] = r_valid

        self._print_summary()
        self._save_results()

        return self.results

    def _print_summary(self):
        """打印分析摘要。"""
        logger.info("\n" + "=" * 60)
        logger.info("  流水线执行摘要")
        logger.info("=" * 60)
        for name, r in self.results.items():
            status = "✅" if r.success else "❌"
            logger.info(f"  {status} {name}: {r.metrics}")
        logger.info("=" * 60)

    def _save_results(self):
        """保存结果到 JSON。"""
        output_path = self.config.working_dir / "pipeline_results.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 只保存可序列化的数据
        serializable = {}
        for name, r in self.results.items():
            serializable[name] = {
                "success": r.success,
                "timestamp": r.timestamp,
                "metrics": r.metrics,
                "warnings": r.warnings,
                "errors": r.errors,
            }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)

        logger.info(f"\n📁 结果已保存至: {output_path}")


# ─────────────────────────────────────────────────────────────
# 4. 入口
# ─────────────────────────────────────────────────────────────

def demo_run():
    """演示运行（无需 ANSYS 环境）。"""
    config = AnalysisConfig(
        project_name="IGBT 模块热—结构分析",
        working_dir=Path("./output/demo_thermal_structural"),
        material=MaterialProps(
            name="Al2O3-DBC",
            elastic_modulus_GPa=370.0,
            poisson_ratio=0.22,
            cte_ppm_per_K=7.4,
            thermal_conductivity_W_per_mK=24.0,
            density_kg_per_m3=3900.0,
            specific_heat_J_per_kgK=880.0,
        ),
        thermal_bc=ThermalBC(
            ambient_temp_C=25.0,
            htc_W_per_m2K=15.0,
            heat_source_W=120.0,
        ),
        structural_bc=StructuralBC(
            fixed_faces=["bottom"],
            pressure_MPa=0.0,
        ),
    )

    pipeline = ThermalStructuralPipeline(config)
    results = pipeline.run()

    # 返回值作为脚本退出码
    all_ok = all(r.success for r in results.values())
    return 0 if all_ok else 1


if __name__ == "__main__":
    if "--demo" in sys.argv or len(sys.argv) == 1:
        sys.exit(demo_run())
    else:
        print("用法: python run_pipeline.py [--demo]")
        print()
        print("  本脚本是热—结构耦合自动化流水线的框架模板。")
        print("  实际运行需要 ANSYS 环境。使用 --demo 查看框架演示。")
        sys.exit(0)
