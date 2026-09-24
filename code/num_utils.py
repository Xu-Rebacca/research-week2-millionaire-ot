"""num_utils.py - 数论工具：Miller-Rabin 素性检测与随机素数生成。

实验二：百万富翁问题与不经意传输问题（基础工具）
"""

import random

# 小素数试除表
_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_probable_prime(n: int, rounds: int = 40) -> bool:
    """Miller-Rabin 素性检测（概率算法，rounds 轮错误概率 < 4^-rounds）。"""
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n % p == 0:
            return n == p
    # 写成 n - 1 = d * 2^r
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime(bits: int) -> int:
    """生成一个 bits 位的随机素数。"""
    while True:
        n = random.getrandbits(bits)
        # 设置最高位与最低位，保证为 bits 位奇数
        n |= (1 << (bits - 1)) | 1
        if is_probable_prime(n):
            return n
