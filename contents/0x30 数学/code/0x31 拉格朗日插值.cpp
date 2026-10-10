// 拉格朗日插值
int lagrange(std::vector<std::pair<int, int>> seq, int k) {
    int n = seq.size(); // seq 下标从 0 开始，至多 n-1 次的多项式需要 n 个点值
    int ans = 0;
    for (int i = 0; i < n; i ++) {
        int p = 1, q = 1;
        for (int j = 0; j < n; j ++) {
            if (i == j) continue;
            mul(p, k - seq[j].first);
            mul(q, seq[i].first - seq[j].first);
        }
        ans = (ans + 1ll * p * qpow(q, mod - 2, mod) % mod * seq[i].second) % mod;
    }
    return norm(ans);
}