"""millionaire.py - 任务一：百万富翁问题原始求解方案（Yao, 1982）。

协议流程（半诚实模型）：
  1. Alice 选取随机数 x（保密），用 Bob 的公钥 RSA 加密得到 C = x^e mod n 发给 Bob；
  2. Bob 用私钥解密得到 x' = x；
  3. Bob 选取随机素数 p（p > M 避免余数歧义），构造序列
        z_j = (x - b + j) mod p ,  j = 1 .. M
     并把序列 z_1..z_M 与素数 p 发送给 Alice；
  4. Alice 计算 z = (x - a) mod p，检验 z 是否出现在 Bob 的序列中：
        - 若 z ∈ {z_j}，则存在 j 使 x-a ≡ x-b+j (mod p)，即 j ≡ b-a (mod p)，
          因 1 <= j <= M 且 p > M，这等价于 b > a，即 a < b；
        - 否则 a >= b。
  原始单次判断只区分 a>=b 与 a<b。为区分相等，交换角色、使用全新随机数
  再比较一次：两次结果均为“>=”时即 a == b。

  隐私：Alice 只知道随机数 x 与序列，序列经模素数压缩后不泄露 b 的具体值；
  Bob 只看到密文 C，无法得知 x，从而无法得知 a。双方只获得比较结果。
"""

import random
import sys
import time

from num_utils import random_prime


class RSA:
    """RSA 密钥对（本协议用于公钥变换，隐藏随机数 x）。"""

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


def compare_once(alice_a: int, bob_b: int, M: int, rsa: RSA):
    """单次判断：返回 (结论, 通信字节数, 交互轮数)。

    结论: 'a_ge_b' 表示 alice_a >= bob_b；'a_lt_b' 表示 alice_a < bob_b。
    """
    # --- Alice 端：随机 x 并用 Bob 公钥加密 ---
    x = random.randrange(2, rsa.n)          # 随机数 x（Alice 保密）
    C = rsa.enc(x)                          # C = x^e mod n

    # --- Bob 端：解密得到 x，构造模素数序列 ---
    xp = rsa.dec(C)                         # x' = x
    p = random_prime(32)                    # 随机素数 p（> 2M 保证无歧义）
    while p <= 2 * M:
        p = random_prime(32)
    seq = [(xp - bob_b + j) % p for j in range(1, M + 1)]

    # --- Alice 端：检验自己的位置 ---
    z = (x - alice_a) % p
    found = z in seq                        # 命中 => a < b

    # 统计：Alice->Bob 一次（密文 C），Bob->Alice 一次（序列 + p）
    bytes_sent = len(str(C).encode()) + (sum(len(str(v).encode()) for v in seq) + len(str(p).encode()))
    return ('a_lt_b' if found else 'a_ge_b'), bytes_sent, 2


def secure_compare(a: int, b: int, M: int):
    """完整比较（含相等处理）：交换角色、全新随机数再比较一次。"""
    rsa = RSA(bits=256)                     # 双方共享一次密钥生成（协议外）

    # 第一轮：Bob 构造序列，Alice 判断  a vs b
    r1, bytes1, rounds1 = compare_once(a, b, M, rsa)
    # 第二轮：交换角色（原 Alice 构造序列，原 Bob 判断）b vs a，全新随机数
    r2, bytes2, rounds2 = compare_once(b, a, M, rsa)

    if r1 == 'a_ge_b' and r2 == 'a_ge_b':   # a>=b 且 b>=a
        result = "双方财富相等  (a == b)"
    elif r1 == 'a_ge_b':                    # a>=b 且 b<a
        result = "Alice 更富有  (a > b)"
    else:                                   # a<b 且 b>=a
        result = "Bob 更富有    (a < b)"

    stats = {
        "rounds": rounds1 + rounds2,
        "bytes": bytes1 + bytes2,
    }
    return result, stats


def main() -> None:
    if len(sys.argv) >= 3:
        a, b = int(sys.argv[1]), int(sys.argv[2])
    else:
        a, b = 37, 42
    M = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    assert 0 <= a < M and 0 <= b < M, "a、b 必须在 [0, M) 范围内"

    print("=" * 60)
    print("任务一：百万富翁问题原始求解方案（Yao, 1982）")
    print("机制：RSA 公钥变换 + 随机数 + 模素数序列 + 位置检验")
    print("=" * 60)
    print(f"Alice 财富 a = {a}   （保密，不参与明文传输）")
    print(f"Bob   财富 b = {b}   （保密，经序列隐藏）")
    print(f"财富取值范围 M = {M}")
    print("-" * 60)

    t0 = time.perf_counter()
    result, stats = secure_compare(a, b, M)
    elapsed = time.perf_counter() - t0

    print("-" * 60)
    print(f"比较结果：{result}")
    print(f"耗时：{elapsed:.4f} s | 通信字节数：{stats['bytes']} B | 交互轮数：{stats['rounds']} 轮")
    print("-" * 60)
    print("隐私说明（半诚实模型）：")
    print("  * Bob 只收到密文 C，无法得知随机数 x，也就无法得知 a；")
    print("  * Alice 收到的序列 z_j 经模素数压缩，不泄露 b 的具体位置与差值；")
    print("  * 比较结束后双方只得到大小关系，不知道对方财富与差值。")


if __name__ == "__main__":
    main()
