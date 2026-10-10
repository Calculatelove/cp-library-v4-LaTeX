std::mt19937_64 mtrand{std::random_device{}()};

// 生成区间 [l, r] 中的随机整数
int rand(int l, int r) {
    std::uniform_int_distribution<int> range(l, r);
    return range(mtrand);
}