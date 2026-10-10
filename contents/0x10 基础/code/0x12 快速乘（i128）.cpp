constexpr i64 qmul(i64 a, i64 b, i64 p) {
    return i128(a) * b % p;
}