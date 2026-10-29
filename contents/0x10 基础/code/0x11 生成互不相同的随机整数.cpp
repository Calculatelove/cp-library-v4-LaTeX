// 生成 n 个在区间 [l, r] 中互不相同的随机整数
auto GenSeq(int n, int l, int r) {
    assert(n <= r - l + 1);
    std::map<int, int> buc;
    std::vector<int> res(n);
    for (int i = 0; i < n; i ++) {
        do {
            res[i] = rand(l, r);
        } while (buc.contains(res[i]));
        buc[res[i]] = 1;
    }
    return res;
}