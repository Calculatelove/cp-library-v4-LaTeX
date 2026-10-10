// 扩展欧几里得算法
std::array<i64, 3> exgcd(i64 a, i64 b) {
    if (b == 0) return {a, 1, 0};
    auto [d, x, y] = exgcd(b, a % b);
    return {d, y, x - (a / b) * y};
}