"""
SimuLearn Scripts — 中级示例：NumPy 计算 von Mises 应力
========================================================
知识点：NumPy 数组基础 (intermediate/01-numpy-arrays)

用 NumPy 向量化运算批量计算多工况下的 von Mises 等效应力，
对比纯 Python 循环的性能差异。

运行方式：
  python von_mises.py
"""

import numpy as np
import time


# ─────────────────────────────────────────────────────────────
# 1. 单点计算函数（纯 Python）
# ─────────────────────────────────────────────────────────────

def von_mises_pure_python(sx, sy, sz, txy, tyz, tzx):
    """纯 Python 实现 von Mises 应力计算。

    σ_vm = sqrt(0.5 * [(σx-σy)² + (σy-σz)² + (σz-σx)²
                       + 6*(τxy² + τyz² + τzx²)])
    """
    import math
    d12 = sx - sy
    d23 = sy - sz
    d31 = sz - sx
    return math.sqrt(0.5 * (d12**2 + d23**2 + d31**2
                            + 6.0 * (txy**2 + tyz**2 + tzx**2)))


# ─────────────────────────────────────────────────────────────
# 2. 向量化计算函数（NumPy）
# ─────────────────────────────────────────────────────────────

def von_mises_numpy(sx, sy, sz, txy, tyz, tzx):
    """NumPy 向量化 von Mises 应力计算。

    所有输入可以是标量或 ndarray。
    """
    d12 = sx - sy
    d23 = sy - sz
    d31 = sz - sx
    return np.sqrt(0.5 * (d12**2 + d23**2 + d31**2
                          + 6.0 * (txy**2 + tyz**2 + tzx**2)))


# ─────────────────────────────────────────────────────────────
# 3. 批量生成仿真数据
# ─────────────────────────────────────────────────────────────

def generate_stress_data(n_cases: int, n_nodes: int):
    """生成模拟的有限元应力结果。

    Args:
        n_cases: 工况数
        n_nodes: 每工况节点数

    Returns:
        6 个 (n_cases, n_nodes) 形状的应力分量数组
    """
    rng = np.random.default_rng(42)  # 固定种子保证可复现

    # 模拟真实应力分布：均值+噪声
    shape = (n_cases, n_nodes)

    # 正应力：受压为主，100 MPa 量级
    sx = rng.normal(loc=-100e6, scale=30e6, size=shape)
    sy = rng.normal(loc=-20e6, scale=10e6, size=shape)
    sz = rng.normal(loc=-5e6, scale=5e6, size=shape)

    # 剪应力：较小的量级
    txy = rng.normal(loc=0, scale=15e6, size=shape)
    tyz = rng.normal(loc=0, scale=10e6, size=shape)
    tzx = rng.normal(loc=0, scale=10e6, size=shape)

    return sx, sy, sz, txy, tyz, tzx


# ─────────────────────────────────────────────────────────────
# 4. 性能对比
# ─────────────────────────────────────────────────────────────

def benchmark(n_cases: int = 10, n_nodes: int = 10000):
    """对比纯 Python 和 NumPy 的性能。"""
    print("=" * 60)
    print("  SimuLearn Scripts — von Mises 应力批量计算")
    print(f"  数据规模: {n_cases} 工况 × {n_nodes} 节点")
    print(f"           = {n_cases * n_nodes:,} 个应力点")
    print("=" * 60)

    sx, sy, sz, txy, tyz, tzx = generate_stress_data(n_cases, n_nodes)

    # --- NumPy 向量化 ---
    t0 = time.perf_counter()
    vm_np = von_mises_numpy(sx, sy, sz, txy, tyz, tzx)
    t_np = time.perf_counter() - t0

    # --- 纯 Python 循环 ---
    # 只跑前 100 个点以避免等太久
    sample = 100
    t0 = time.perf_counter()
    vm_py = np.zeros(sample)
    for i in range(sample):
        vm_py[i] = von_mises_pure_python(
            sx.flat[i], sy.flat[i], sz.flat[i],
            txy.flat[i], tyz.flat[i], tzx.flat[i],
        )
    t_py_sample = time.perf_counter() - t0
    t_py_estimated = t_py_sample * (n_cases * n_nodes / sample)

    # --- 结果统计 ---
    print(f"\n⏱️  性能对比:")
    print(f"   NumPy 向量化:    {t_np*1000:.1f} ms")
    print(f"   纯 Python (预估): {t_py_estimated:.1f} s")
    if t_py_estimated > 0:
        speedup = t_py_estimated / t_np
        print(f"   加速比:           {speedup:,.0f}x")

    print(f"\n📊 结果统计 (NumPy):")
    print(f"   von Mises 最大值:  {vm_np.max()/1e6:.1f} MPa")
    print(f"   von Mises 平均值:  {vm_np.mean()/1e6:.1f} MPa")
    print(f"   von Mises 标准差:  {vm_np.std()/1e6:.1f} MPa")

    # 找到最大应力点
    idx = np.unravel_index(np.argmax(vm_np), vm_np.shape)
    print(f"\n🔍 最大应力位置:")
    print(f"   工况 {idx[0]+1}, 节点 {idx[1]+1}")
    print(f"   σx={sx[idx]/1e6:.1f} σy={sy[idx]/1e6:.1f} σz={sz[idx]/1e6:.1f} MPa")
    print(f"   τxy={txy[idx]/1e6:.1f} τyz={tyz[idx]/1e6:.1f} τzx={tzx[idx]/1e6:.1f} MPa")

    # 筛选超过屈服强度的节点（以 Q235 为例）
    yield_stress = 235e6
    over_yield = np.sum(vm_np > yield_stress)
    print(f"\n⚠️  超过屈服强度 (235 MPa) 的节点: {over_yield} "
          f"({over_yield/vm_np.size*100:.2f}%)")

    print("\n" + "=" * 60)
    print("  关键要点:")
    print("  1. NumPy 向量化避免了 Python 层的 for 循环")
    print("  2. np.sqrt、算术运算都在 C 层执行")
    print("  3. 批量统计 (max/mean/std) 同样受益于向量化")
    print("=" * 60)


# ─────────────────────────────────────────────────────────────
# 5. 验证计算正确性
# ─────────────────────────────────────────────────────────────

def test_von_mises():
    """验证 NumPy 实现与纯 Python 实现结果一致。"""
    # 单轴拉伸：σx=100, 其他=0 → σ_vm=100
    vm = von_mises_numpy(100.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    assert abs(vm - 100.0) < 1e-10, f"单轴测试失败: {vm}"

    # 纯剪切：τxy=50, 其他=0 → σ_vm=√3*50≈86.6
    vm = von_mises_numpy(0.0, 0.0, 0.0, 50.0, 0.0, 0.0)
    expected = np.sqrt(3.0) * 50.0
    assert abs(vm - expected) < 1e-10, f"纯剪测试失败: {vm}"

    # 与纯 Python 对比随机值
    rng = np.random.default_rng(123)
    for _ in range(100):
        s = rng.uniform(-200, 200, 6)
        py = von_mises_pure_python(*s)
        np_v = float(von_mises_numpy(*s))
        assert abs(py - np_v) < 1e-10, f"对比失败: py={py}, np={np_v}"

    print("✅ 所有验证测试通过")


if __name__ == "__main__":
    test_von_mises()
    benchmark(n_cases=10, n_nodes=10000)
