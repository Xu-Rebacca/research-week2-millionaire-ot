"""benchmark.py - 实验要求 4：两种方案性能比较与正确率验证。

在相同输入（a、b 随机，同一范围 [0, M)）与可比密码参数（RSA 256 位）下，
分别运行任务一（Yao 原始方案）与任务二（基于 OT 的逐位比较），统计：
  * 正确率（与直接比较 ground truth 对照）
  * 平均耗时
  * 平均通信字节数
  * 交互轮数

输出：result/benchmark.txt（供实验报告引用）。
"""

import random
import statistics
import time

from millionaire import secure_compare as yao_compare
from millionaire_ot import secure_compare_ot

M = 100          # 财富范围 [0, M)
BITS = 8         # 任务二二进制位数（2^8 = 256 >= M）
TRIALS = 20      # 每组测试轮数


def ground_truth(a: int, b: int) -> str:
    if a > b:
        return "Alice 更富有  (a > b)"
    if a < b:
        return "Bob 更富有    (a < b)"
    return "双方财富相等  (a == b)"


def run_benchmark() -> dict:
    random.seed(2026)

    yao_correct, yao_times, yao_bytes = 0, [], []
    ot_correct, ot_times, ot_bytes = 0, [], []
    pairs = []

    for _ in range(TRIALS):
        a = random.randrange(0, M)
        b = random.randrange(0, M)
        pairs.append((a, b))
        expect = ground_truth(a, b)

        # 任务一
        t0 = time.perf_counter()
        r1, s1 = yao_compare(a, b, M)
        yao_times.append(time.perf_counter() - t0)
        yao_bytes.append(s1["bytes"])
        if r1 == expect:
            yao_correct += 1

        # 任务二
        t0 = time.perf_counter()
        r2, s2 = secure_compare_ot(a, b, BITS)
        ot_times.append(time.perf_counter() - t0)
        ot_bytes.append(s2["bytes"])
        if r2 == expect:
            ot_correct += 1

    return {
        "yao": {
            "accuracy": yao_correct / TRIALS,
            "time": statistics.mean(yao_times),
            "bytes": statistics.mean(yao_bytes),
            "rounds": 4,                       # 交换角色共 2 次，每次 2 轮
        },
        "ot": {
            "accuracy": ot_correct / TRIALS,
            "time": statistics.mean(ot_times),
            "bytes": statistics.mean(ot_bytes),
            "rounds": BITS * 2,                # BITS 轮 OT，每轮 2 次消息
        },
        "trials": TRIALS,
        "pairs": pairs,
    }


def main() -> None:
    print("=" * 64)
    print("实验要求 4：两种方案性能比较（相同输入与可比密码参数 RSA-256）")
    print(f"输入范围 M = {M}，任务二位数 bits = {BITS}，测试组数 = {TRIALS}")
    print("=" * 64)

    res = run_benchmark()

    header = f"{'指标':<12}{'任务一：Yao 原始方案':>22}{'任务二：基于 OT':>20}"
    print(header)
    print("-" * 64)
    rows = [
        ("正确率", f"{res['yao']['accuracy']*100:.0f}%", f"{res['ot']['accuracy']*100:.0f}%"),
        ("平均耗时 (s)", f"{res['yao']['time']:.4f}", f"{res['ot']['time']:.4f}"),
        ("平均通信 (B)", f"{res['yao']['bytes']:.0f}", f"{res['ot']['bytes']:.0f}"),
        ("交互轮数", f"{res['yao']['rounds']}", f"{res['ot']['rounds']}"),
    ]
    for name, v1, v2 in rows:
        print(f"{name:<12}{v1:>22}{v2:>20}")
    print("-" * 64)

    # 输出到 result/benchmark.txt
    out = "\n".join([
        "实验二：两种方案性能比较",
        f"输入范围 [0, {M})，任务二位数 bits = {BITS}，测试组数 = {TRIALS}",
        header,
        "-" * 64,
    ] + [f"{name:<12}{v1:>22}{v2:>20}" for name, v1, v2 in rows])
    out += "\n" + "-" * 64 + "\n"
    out += "说明：任务一交互轮数 = 交换角色比较 2 次 x 每次 2 轮；任务二 = bits 轮 OT x 每轮 2 次消息。\n"
    with open("result/benchmark.txt", "w", encoding="utf-8") as f:
        f.write(out)
    print("结果已保存到 result/benchmark.txt")


if __name__ == "__main__":
    main()
