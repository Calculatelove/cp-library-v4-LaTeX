i64 inverse(i64 a, i64 m) {
    auto [d, x, y] = exgcd(a, m);
    return (x % m + m) % m;
}

using equ = std::pair<i64, i64>; // {a, m} 表示方程 x = a (mod m)

// 中国剩余定理
equ CRT(std::vector<equ> seq) {
    i64 M = 1;
    for (auto [a, m] : seq) {
        M *= m;
    }
    i64 x = 0;
    for (auto [a, m] : seq) {
        i64 Mi = M / m;
        i64 Vi = inverse(Mi, m);
        x = (x + a * Mi * Vi) % M; // 必要时，使用“快速乘”防止爆 long long
    }
    x = (x % M + M) % M;
    return {x, M};
}