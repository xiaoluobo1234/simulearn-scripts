# SimuLearn Scripts

**从 Python 基础到 ANSYS 接口开发的工程级脚本库**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![SimuLearn](https://img.shields.io/badge/SimuLearn-工具脚本-6C5CE7)](https://simulearn.cn/tools)

---

## 概述

本仓库是 [SimuLearn](https://simulearn.cn) 平台「工具脚本」模块的配套代码库，覆盖从 Python 基础语法到高级 ANSYS 接口开发的完整技能树。

**90 个知识点 · 7 个综合项目 · 全部原创 · 全程穿插 ANSYS 工程案例**

```
beginner/   (20 topics)   Python 基础 → 简单工程脚本
intermediate/ (30 topics) 科学计算栈 + ANSYS 接口开发
advanced/   (40 topics)   工程级 Python + 多物理场自动化
projects/   (7 projects)  综合实战项目
exercises/                分级习题
data/                     示例数据
utils/                    通用工具函数
```

---

## 快速开始

### 环境要求

- Python 3.10+
- 推荐使用 [Anaconda](https://www.anaconda.com/) 或 venv 管理环境
- 部分高级主题需要 ANSYS 2024 R1+ 及对应 Python 包

### 安装

```bash
git clone https://github.com/xiaoluobo1234/simulearn-scripts.git
cd simulearn-scripts
pip install -r requirements.txt
```

### 运行示例

```bash
# 初级：你的第一个工程脚本
python beginner/01-python-intro/hello_simu.py

# 中级：用 NumPy 计算等效应力
python intermediate/01-numpy-arrays/von_mises.py

# 高级：热—结构耦合自动化流水线
python advanced/12-thermal-structural/run_pipeline.py
```

---

## 目录结构

```
simulearn-scripts/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
│
├── beginner/              # 初级 — Python 基础 + 简单工程脚本
│   ├── 01-python-intro/      安装与概览
│   ├── 02-variables-types/   变量与数据类型
│   ├── 03-operators/         运算符与表达式
│   ├── 04-strings/           字符串处理
│   ├── 05-conditionals/      条件判断
│   ├── 06-loops/             循环结构
│   ├── 07-lists-tuples/      列表与元组
│   ├── 08-dicts-sets/        字典与集合
│   ├── 09-functions/         函数定义与调用
│   ├── 10-file-io/           文件读写
│   ├── 11-error-handling/    异常处理
│   ├── 12-modules/           模块与包
│   ├── 13-virtual-env/       虚拟环境
│   ├── 14-ansys-data-types/  ANSYS 数据类型
│   ├── 15-apdl-parse/        APDL 输出解析
│   ├── 16-csv-export/        CSV 结果导出
│   ├── 17-matplotlib-basics/ 基础绘图
│   ├── 18-script-structure/  脚本工程化
│   ├── 19-unit-conversion/   单位换算
│   └── 20-project-review/    综合回顾
│
├── intermediate/           # 中级 — 科学计算栈 + ANSYS 接口
│   ├── 01-numpy-arrays/      NumPy 数组
│   ├── 02-numpy-linalg/      NumPy 线性代数
│   ├── 03-scipy-interp/      SciPy 插值与拟合
│   ├── 04-pandas-intro/      Pandas 数据处理
│   ├── 05-matplotlib-advanced/ 高级绘图
│   ├── 06-pymapdl-intro/     PyMAPDL 入门
│   ├── 07-dpf-intro/         DPF 后处理
│   ├── 08-apdl-macro/        APDL 宏自动化
│   ├── 09-workbench-scripting/ Workbench 脚本
│   ├── 10-3d-visualization/  三维可视化
│   ├── 11-report-automation/ 报告自动生成
│   ├── 12-sqlite-basics/     SQLite 数据库
│   ├── 13-material-db/       材料数据库
│   ├── 14-contact-scripting/ 接触分析脚本
│   ├── 15-optimization-loop/ 参数优化
│   ├── 16-result-validation/ 结果验证
│   ├── 17-version-control/   Git 基础
│   ├── 18-debugging-logging/ 调试与日志
│   ├── 19-testing-pytest/    单元测试
│   ├── 20-profiling/         性能剖析
│   ├── 21-parallel-processing/ 并行处理
│   ├── 22-fluent-udf/        Fluent UDF
│   ├── 23-abaqus-python/     Abaqus 脚本
│   ├── 24-comsol-python/     COMSOL Python
│   ├── 25-hdf5-netcdf/       HDF5/NetCDF
│   ├── 26-data-pipeline/     数据处理管道
│   ├── 27-ansys-remote/      ANSYS 远程求解
│   ├── 28-streamlit-dash/    交互看板
│   ├── 29-conda-env-repro/   环境可复现
│   └── 30-regex-engineering/ 正则工程解析
│
├── advanced/               # 高级 — 工程级 Python + 多物理场
│   ├── 01-oop-classes/       面向对象
│   ├── 02-design-patterns/   设计模式
│   ├── 03-decorators/        装饰器
│   ├── 04-generators/        生成器
│   ├── 05-context-managers/  上下文管理器
│   ├── 06-asyncio/           异步 I/O
│   ├── 07-job-scheduler/     任务调度
│   ├── 08-cython-numba/      Cython/Numba
│   ├── 09-gpu-computing/     GPU 加速
│   ├── 10-custom-element/    自定义单元
│   ├── 11-system-coupling/   System Coupling
│   ├── 12-thermal-structural/ 热—结构耦合
│   ├── 13-fsi-automation/    流固耦合
│   ├── 14-multiphysics-pipeline/ 多物理场流水线
│   ├── 15-api-development/   仿真 API
│   ├── 16-ci-cd/             CI/CD
│   ├── 17-documentation/     文档生成
│   ├── 18-ml-surrogate/      ML 代理模型
│   ├── 19-hpc-scripting/     HPC 作业
│   ├── 20-digital-twin/      数字孪生
│   ├── 21-project-structural-opt/ 结构优化项目
│   ├── 22-project-thermal-pipeline/ 热分析流水线
│   ├── 23-project-fsi-cooling/ 液冷板 FSI
│   ├── 24-project-custom-workflow/ 自定义工作流
│   ├── 25-abc-interfaces/    ABC 接口
│   ├── 26-pydantic/          Pydantic 验证
│   ├── 27-mqtt-iot/          MQTT
│   ├── 28-property-testing/  属性测试
│   ├── 29-sim-benchmark/     仿真基准
│   ├── 30-secrets-management/ 密钥管理
│   ├── 31-input-sanitization/ 输入安全
│   ├── 32-llm-reporting/     LLM 报告
│   ├── 33-ml-surrogate-deploy/ 代理模型部署
│   ├── 34-opc-ua/            OPC UA
│   ├── 35-modbus/            Modbus
│   ├── 36-project-modbus-monitor/ 数据采集项目
│   ├── 37-project-api-platform/   API 平台项目
│   ├── 38-project-script-migration/ 脚本迁移项目
│   ├── 39-quantum-computing/ 量子计算
│   └── 40-sim-lifecycle/     生命周期管理
│
├── projects/               # 综合实战项目
│   ├── 01-structural-optimization/  结构参数优化
│   ├── 02-thermal-pipeline/         封装热分析流水线
│   ├── 03-fsi-cooling/              液冷板流固耦合
│   ├── 04-custom-workflow/          自定义分析工作流
│   ├── 05-modbus-monitor/           试验数据采集系统
│   ├── 06-api-platform/             仿真 API 平台
│   └── 07-script-migration/         MATLAB → Python 迁移
│
├── exercises/              # 分级习题
│   ├── beginner/
│   ├── intermediate/
│   └── advanced/
│
├── data/                   # 示例数据
│   ├── sample-results/        ANSYS 输出示例
│   └── material-db/           材料数据库
│
└── utils/                  # 通用工具函数
    ├── unit_converter.py       单位换算
    ├── apdl_parser.py          APDL 解析
    ├── result_validator.py     结果验证
    └── report_builder.py       报告生成
```

---

## 学习路径

### 🔰 初级（面向零编程基础的仿真工程师）
1. Python 环境安装 → 变量/运算符/字符串
2. 条件判断 → 循环 → 列表/字典
3. 函数 → 文件读写 → 异常处理 → 模块
4. ANSYS 数据交互 → CSV 导出 → 基础绘图
5. 脚本工程化 → 单位换算 → **产出：独立完成仿真数据处理脚本**

### 🔧 中级（面向有 Python 基础的仿真工程师）
1. NumPy/SciPy/Pandas 科学计算栈
2. PyMAPDL → DPF → APDL 宏 → Workbench 脚本
3. 高级可视化 → 报告自动化 → SQLite/材料库
4. 接触脚本 → 参数优化 → 结果自动验证
5. 版本控制 → 测试 → 性能优化 → 并行处理
6. 多求解器扩展 + 数据管理 + 环境可复现

### 🚀 高级（面向仿真工具开发者）
1. OOP → 设计模式 → 高级 Python 特性
2. 并发编程 → 性能加速 → GPU 计算
3. ANSYS 深度集成 → 多物理场自动化
4. 仿真 API → CI/CD → 文档生成
5. ML 代理模型 → HPC → 数字孪生
6. 工业协议 → 安全工程 → AI 集成
7. 7 个综合项目实战

---

## 技术栈

| 类别 | 工具/库 |
|------|---------|
| **核心语言** | Python 3.10+ |
| **科学计算** | NumPy, SciPy, Pandas |
| **可视化** | Matplotlib, PyVista, Streamlit |
| **ANSYS 接口** | PyMAPDL, DPF, PySystemCoupling, PyFluent |
| **其他求解器** | Abaqus Python API, COMSOL Python API |
| **数据库** | SQLite, HDF5 (h5py), NetCDF (xarray) |
| **Web/API** | FastAPI, MQTT (paho-mqtt), OPC UA (opcua) |
| **测试/质量** | pytest, Hypothesis, cProfile |
| **性能** | Numba, Cython, multiprocessing, asyncio |
| **ML** | scikit-learn, ONNX Runtime |
| **文档** | Sphinx, MkDocs |

---

## 贡献

本仓库为 [SimuLearn](https://simulearn.cn) 学习平台配套代码库，暂不接受外部 PR。

问题反馈和功能建议请通过 [Issues](https://github.com/xiaoluobo1234/simulearn-scripts/issues) 提交。

---

## 许可证

MIT License © 2026 SimuLearn
