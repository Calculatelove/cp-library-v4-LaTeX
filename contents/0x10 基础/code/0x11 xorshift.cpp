u64 mask = std::mt19937_64(std::random_device{}())();
u64 xorshift(u64 x) {
    x ^= mask;
    x ^= x << 13, x ^= x >> 7, x ^= x << 17;
    x ^= mask;
    return x;
}