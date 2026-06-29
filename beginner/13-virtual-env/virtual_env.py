"""
SimuLearn Scripts — 初级 #13：虚拟环境管理
===========================================
知识点：virtual-env

不同项目依赖不同版本的 numpy、ansys 库等。
虚拟环境隔离依赖，避免"依赖地狱"。

本节涵盖：
  1. 为什么需要虚拟环境
  2. venv 基本使用
  3. requirements.txt 管理
  4. conda 环境概览
  5. 最佳实践

运行方式：
  python virtual_env.py
  （本脚本是教学演示，实际操作见注释中的命令）
"""

import sys
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
# 1. 为什么需要虚拟环境？
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 为什么需要虚拟环境？")
print("=" * 60)

print(f"当前 Python 解释器: {sys.executable}")
print(f"Python 版本: {sys.version}")

# 查看全局安装的包
import importlib.metadata as metadata
installed = {dist.name: dist.version for dist in metadata.distributions()}
print(f"\n全局安装的包数量: {len(installed)}")

# 场景还原：
print("""
  没有虚拟环境时的问题：

  项目A → 需要 numpy==1.24
  项目B → 需要 numpy==1.26  ← 冲突！

  全局装一个版本 → 另一个项目崩溃。
  虚拟环境解决：每个项目独立的包空间。
""")


# ═══════════════════════════════════════════════════════════════
# 2. venv 虚拟环境
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  2. venv 虚拟环境")
print("=" * 60)

print("""
  创建虚拟环境：
    # Windows
    python -m venv simu_env

    # Linux/macOS
    python3 -m venv simu_env

  激活虚拟环境：
    # Windows (CMD)
    simu_env\\Scripts\\activate.bat

    # Windows (PowerShell)
    simu_env\\Scripts\\Activate.ps1

    # Linux/macOS / Git Bash
    source simu_env/bin/activate

  确认已激活：
    终端前缀变为 (simu_env)
    执行 which python 应指向 simu_env/

  退出虚拟环境：
    deactivate

  删除虚拟环境：
    直接删除 simu_env/ 目录即可
""")

# 检查当前是否在虚拟环境中
in_venv = hasattr(sys, "real_prefix") or (
    hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
)
print(f"当前是否在虚拟环境中: {'是' if in_venv else '否'}")
if in_venv:
    print(f"虚拟环境路径: {sys.prefix}")


# ═══════════════════════════════════════════════════════════════
# 3. requirements.txt 管理
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. requirements.txt 管理")
print("=" * 60)

# 演示：生成本脚本的依赖列表
print("生成 requirements.txt:")
print("  pip freeze > requirements.txt")

# 安装依赖
print("\n安装依赖:")
print("  pip install -r requirements.txt")

# 最佳实践：开发 vs 生产
print("""
  推荐的项目文件结构：

  requirements/
  ├── base.txt          # 所有环境共有的依赖
  ├── dev.txt           # 开发工具 (pytest, black, ...)
  │   -r base.txt       # 继承 base
  └── prod.txt          # 生产环境
      -r base.txt       # 继承 base

  安装:
    pip install -r requirements/dev.txt    # 开发
    pip install -r requirements/prod.txt   # 生产
""")

# 版本锁定策略
print("版本锁定策略:")
print("""
  ✅ 应用程序 (你的仿真脚本):
     pip freeze > requirements.txt
     → 锁定精确版本，确保可复现

  ✅ 库 (你发布的工具包):
     setup.py 或 pyproject.toml 中指定范围
     numpy>=1.24,<2.0
     → 兼容范围，不锁死用户环境
""")


# ═══════════════════════════════════════════════════════════════
# 4. conda 环境
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  4. conda 环境")
print("=" * 60)

print("""
  创建 conda 环境:
    conda create -n simu_env python=3.10

  激活:
    conda activate simu_env

  安装包:
    conda install numpy scipy matplotlib
    pip install ansys-mapdl-core  # conda 没有的用 pip

  导出环境:
    conda env export > environment.yml

  从文件创建:
    conda env create -f environment.yml

  venv vs conda:
    venv:
      + 轻量，Python 自带
      + 只用 pip
      - 不管理 Python 版本
      - 科学计算包可能需要手动装系统依赖

    conda:
      + 管理 Python 版本 + 包 + 系统库
      + 科学计算包预编译，安装更快
      - 更重，安装慢
      - 包版本可能滞后 PyPI
""")


# ═══════════════════════════════════════════════════════════════
# 5. 工程最佳实践
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  5. 工程最佳实践")
print("=" * 60)

print("""
  每个仿真项目 = 独立虚拟环境:

  1. 项目初始化
     mkdir project_name
     cd project_name
     python -m venv .venv    ← 用 .venv 作为环境目录名
     source .venv/bin/activate

  2. 安装依赖
     pip install numpy scipy matplotlib pandas
     pip freeze > requirements.txt

  3. 版本控制
     git init
     echo ".venv/" >> .gitignore    ← 不提交虚拟环境
     git add requirements.txt
     git commit -m "init"

  4. 团队交接
     git clone <repo>
     cd project
     python -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     python main.py

  目录约定:
    .venv/          ← 虚拟环境 (不提交)
    requirements.txt ← 依赖声明 (提交)
    src/            ← 源代码
    tests/          ← 测试
""")


# ═══════════════════════════════════════════════════════════════
# 6. 检查当前环境
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  6. 当前环境信息")
print("=" * 60)

# 列出几个关键包
key_packages = ["numpy", "scipy", "pandas", "matplotlib"]
for pkg_name in key_packages:
    try:
        version = metadata.version(pkg_name)
        print(f"  ✅ {pkg_name}: {version}")
    except metadata.PackageNotFoundError:
        print(f"  ❌ {pkg_name}: 未安装")


# ═══════════════════════════════════════════════════════════════
# 7. 练习
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 在终端创建一个虚拟环境 simu_practice，激活它，
     安装 numpy 和 matplotlib，运行 pip freeze > requirements.txt。
     然后 deactivate。

  2. 用 git init 初始化一个新项目，创建 .gitignore 文件，
     确保 .venv/ 和 __pycache__/ 不被提交。

  3. 解释以下两个命令的区别：
     - pip freeze > requirements.txt
     - pip install -r requirements.txt

  4. 为什么不应该把所有包都装在全局 Python 环境中？
""")
