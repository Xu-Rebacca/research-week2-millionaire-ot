"""ot.py - 任务二第一部分：n 选 1 不经意传输（1-out-of-n Oblivious Transfer）。

协议（RSA 实现，Even-Goldreich-Micali 思路推广到 n 个消息）：
  1. Sender 生成 RSA 密钥 (n, e, d)，选取 n 个互不相同的随机数 x_1..x_n，
     把 (n, e, x_1..x_n) 发送给 Receiver；
  2. Receiver 选择下标 sigma（保密），随机数 k，计算
        v = (x_sigma + k^e) mod n
     并发送给 Sender；
  3. Sender 对每个 i 计算 k_i = (v - x_i)^d mod n：
     仅当 i = sigma 时 (v - x_i) = k^e，故 k_sigma = k，其余 k_i 为随机值；
  4. Sender 发送 m_i' = (m_i + k_i) mod n（i = 1..n）；
  5. Receiver 恢复 m_sigma = (m_sigma' - k) mod n。

  安全性：Sender 看不到 sigma（v 被随机 k^e 盲化）；Receiver 无法从 m_i'
  恢复其它消息（k_i 是随机值）。本演示要求 m_i 满足 0 <= m_i < n。
"""

import random
import sys
import time

from num_utils import random_prime


class RSA:
    """RSA 密钥对。"""

    def __init__(self, bits: int = 256):
        p, q = random_prime(bits), random_prime(bits)
        while q == p:
            q = random_prime(bits)
        self.n = p * q
        self.e = 65537
        self.d = pow(self.e, -1, (p - 1) * (q - 1))

    def enc(self, m: int) -> int:
        return pow(m, self.e, self.n)

    def dec(self, c: int) -> int:
        return pow(c, self.d, self.n)


def ot_n(messages, sigma: int, rsa_bits: int = 256):
    """执行一次 1-out-of-n OT。

    返回: (received, stats)，received 为 Receiver 收到的消息；
    stats 含 rounds / bytes / sender_cannot_know_sigma 等信息。
    """
    n_msgs = len(messages)
    assert 0 <= sigma < n_msgs

    rsa = RSA(bits=rsa_bits)
    n_mod, e = rsa.n, rsa.e

    # Sender: 选取 n 个互不相同的随机盲化数
    blinds = []
    while len(blinds) < n_msgs:
        v = random.randrange(2, n_mod - 1)
        if v not in blinds:
            blinds.append(v)

    # Receiver: 选择 sigma，随机 k，盲化发送
    k = random.randrange(2, n_mod - 1)
    v_sent = (blinds[sigma] + pow(k, e, n_mod)) % n_mod

    # Sender: 解出每个位置的密钥
    keys = [pow((v_sent - x) % n_mod, rsa.d, n_mod) for x in blinds]

    # Sender: 加密发送所有消息
    cipher = [(messages[i] + keys[i]) % n_mod for i in range(n_msgs)]

    # Receiver: 只恢复自己选中的消息
    received = (cipher[sigma] - k) % n_mod

    bytes_sent = (
        len(str(n_mod).encode()) * 2 + sum(len(str(x).encode()) for x in blinds)
        + len(str(v_sent).encode()) + sum(len(str(c).encode()) for c in cipher)
    )
    stats = {
        "rounds": 2,                       # v 一次 + 密文列表一次
        "bytes": bytes_sent,
        "n_msgs": n_msgs,
        "sigma": sigma,
    }
    return received, stats


def main() -> None:
    print("=" * 60)
    print("任务二第一部分：n 选 1 不经意传输（1-out-of-n OT, RSA）")
    print("=" * 60)

    # 演示 1-out-of-2 OT
    m0, m1 = 2024, 2026
    sigma = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    msgs = [m0, m1]
    t0 = time.perf_counter()
    received, stats = ot_n(msgs, sigma)
    elapsed = time.perf_counter() - t0

    print(f"Sender 持有消息：m0 = {m0}, m1 = {m1}")
    print(f"Receiver 选择下标 sigma = {sigma}（对 Sender 保密）")
    print(f"Receiver 收到的消息 = {received}  （应等于 m{sigma}）")
    assert received == msgs[sigma]
    print(f"其他消息（m{1 - sigma} = {msgs[1 - sigma]}）对 Receiver 保持不可恢复")
    print(f"耗时：{elapsed:.4f} s | 通信字节数：{stats['bytes']} B | 交互轮数：{stats['rounds']} 轮")
    print()

    # 演示 1-out-of-4 OT
    msgs4 = [101, 202, 303, 404]
    sigma4 = 2
    received4, stats4 = ot_n(msgs4, sigma4)
    print(f"1-out-of-4 OT：消息 {msgs4}，Receiver 选择下标 {sigma4}，收到 {received4}（应等于 {msgs4[sigma4]}）")
    assert received4 == msgs4[sigma4]
    print(f"通信字节数：{stats4['bytes']} B | 交互轮数：{stats4['rounds']} 轮")
    print("-" * 60)
    print("安全性：")
    print("  * Receiver 的 v 被随机数 k^e 盲化，Sender 无法得知 sigma；")
    print("  * 除选中消息外，其余 k_i 为随机值，Receiver 无法恢复未选消息；")
    print("  * 双向保护（对发送方消息、对接收方选择）。")


if __name__ == "__main__":
    main()
