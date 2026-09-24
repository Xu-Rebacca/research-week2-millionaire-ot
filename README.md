# research-week2-millionaire-ot

数据安全与隐私保护课程实验二：百万富翁问题与不经意传输

本仓库实现隐私计算中的两个经典问题：

- `code/millionaire.py`   任务一：百万富翁问题原始求解方案（Yao, 1982）
- `code/ot.py`            任务二第一部分：n 选 1 不经意传输（1-out-of-n OT, RSA）
- `code/millionaire_ot.py` 任务二第二部分：基于 OT 的百万富翁问题（逐位安全比较）
- `code/benchmark.py`     两种方案性能比较（正确率 / 耗时 / 通信字节 / 交互轮数）
- `code/num_utils.py`     数论工具（Miller-Rabin 素性检测、随机素数生成）
- `result/`               运行结果与性能对比
- `report/`               实验报告（LaTeX, SYSUReport 模板）

## 快速开始

```bash
# 任务一：Yao 原始方案（默认 Alice=37, Bob=42, M=100）
python code/millionaire.py

# 任务二第一部分：n 选 1 OT 演示
python code/ot.py

# 任务二第二部分：基于 OT 的百万富翁问题
python code/millionaire_ot.py

# 性能对比（20 组随机输入）
python code/benchmark.py
```

运行输出仅给出"Alice 更富有 / Bob 更富有 / 双方财富相等"，不泄露双方财富与差值。

## 环境

Python 3.9+（仅标准库，无第三方依赖）。实验报告用 XeLaTeX + SYSUReport 模板编译。
