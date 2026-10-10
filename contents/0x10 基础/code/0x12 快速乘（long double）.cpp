constexpr i64 qmul(i64 a, i64 b, i64 p) {
    i64 c = static_cast<long double>(a) * b / p + 1e-8;
    i64 ans = a * b - c * p;
    if (ans < 0) ans += p;
    if (ans >= p) ans -= p;
    return ans;
}