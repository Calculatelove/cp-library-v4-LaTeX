std::mt19937_64 mtrand{std::random_device{}()};

// 生成区间 [l, r) 中的随机浮点数
double rand(double l, double r) {
    std::uniform_real_distribution<double> range(l, r);
    return range(mtrand);
}