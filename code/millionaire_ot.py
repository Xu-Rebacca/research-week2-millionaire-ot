"""millionaire_ot.py - 任务二第二部分：使用 OT 解决百万富翁问题。

方法：逐位安全比较。
  将财富 a、b 写成 bits 位二进制。从最高位向最低位逐位比较，
  每一轮使用一次 1-out-of-2 OT 传递比较状态，隐藏 Alice 的选择位 a_i。

状态编码（相对 Alice）：0 = LESS（Alice 更穷），1 = EQUAL，2 = GREATER。
每一轮 Bob 依据自己的位 b_i 与当前状态构造两个 OT 消息：
  - 若当前状态为 EQUAL（需要继续比较）：
        b_i = 0  ->  m0 = EQUAL(1)（Alice 位为 0 则持平），m1 = GREATER(2)（Alice 位为 1 则更大）
        b_i = 1  ->  m0 = LESS(0)  （Alice 位为 0 则更小），m1 = EQUAL(1)（Alice 位为 1 则持平）
  - 若当前状态已确定（LESS/GREATER），两个消息均等于当前状态（流程照常执行以隐藏状态）。
Alice 通过 1-out-of-2 OT 选择下标 a_i 拿到 m_{a_i}，得到新的比较状态。
比较结束后状态即最终结果：GREATER -> Alice 更富有；LESS -> Bob 更富有；EQUAL -> 财富相等。

安全性：OT 保证 Bob 不知道 Alice 每轮的选择位 a_i（及最终结果），
Alice 每轮只拿到与自身位对应的消息，无法得知 Bob 的位 b_i 与未选消息。
"""

import random
import sys
import time

from ot import ot_n, RSA

LESS, EQUAL, GREATER = 0, 1, 2
LABELS = {LESS: "Bob 更富有    (a < b)", EQUAL: "双方财富相等  (a == b)", GREATER: "Alice 更富有  (a > b)"}


def make_messages(b_i: int, state: int):
    """Bob 构造本轮 OT 的两个消息 m0, m1（Alice 以自身位 a_i 作为选择下标）。"""
    if state != EQUAL:                    # 状态已定，两个消息相同（流程不泄露）
        return state, state
    if b_i == 0:
        return EQUAL, GREATER             # m0(Alice 位 0): 持平;  m1(Alice 位 1): 更大
    else:
        return LESS, EQUAL                # m0(Alice 位 0): 更小;  m1(Alice 位 1): 持平


def secure_compare_ot(a: int, b: int, bits: int = 8):
    """基于 OT 的安全比较，返回 (结果字符串, 统计 dict)。"""
    assert 0 <= a < (1 << bits) and 0 <= b < (1 << bits)
    state = EQUAL
    total_bytes, total_rounds = 0, 0
    for i in range(bits - 1, -1, -1):     # 高位到低位
        a_i = (a >> i) & 1                # Alice 的选择位（对 Bob 保密）
        b_i = (b >> i) & 1
        m0, m1 = make_messages(b_i, state)
        received, stats = ot_n((m0, m1), a_i, rsa_bits=256)
        total_bytes += stats["bytes"]
        total_rounds += stats["rounds"]
        state = received
    return LABELS[state], {"bytes": total_bytes, "rounds": total_rounds, "state": state}


def main() -> None:
    if len(sys.argv) >= 3:
        a, b = int(sys.argv[1]), int(sys.argv[2])
    else:
        a, b = 37, 42
    bits = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    assert 0 <= a < (1 << bits) and 0 <= b < (1 << bits)

    print("=" * 60)
    print("任务二第二部分：基于 OT 的百万富翁问题（逐位安全比较）")
    print(f"机制：{bits} 位二进制逐位比较，每轮 1-out-of-2 OT（RSA 256 位）")
    print("=" * 60)
    print(f"Alice 财富 a = {a}   （保密，仅以选择位形式参与 OT）")
    print(f"Bob   财富 b = {b}   （保密，仅体现在 OT 消息构造中）")
    print("-" * 60)

    t0 = time.perf_counter()
    result, stats = secure_compare_ot(a, b, bits)
    elapsed = time.perf_counter() - t0

    print(f"比较结果：{result}")
    print(f"耗时：{elapsed:.4f} s | 通信字节数：{stats['bytes']} B | "
          f"交互轮数：{stats['rounds']} 轮（{bits} 轮 OT）")
    print("-" * 60)
    print("隐私说明：")
    print("  * OT 使 Bob 无法得知 Alice 每轮的选择位（即无法得知 a 与比较走向）；")
    print("  * Alice 每轮只拿到与自身位对应的状态消息，无法得知 Bob 的位 b_i；")
    print("  * 双方最终只知道比较结果，不知道对方财富与差值。")


if __name__ == "__main__":
    main()
