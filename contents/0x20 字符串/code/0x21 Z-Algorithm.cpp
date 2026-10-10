// Z[i]：lcp(s, s[i:n])
auto Zalgo(const auto &s) {
    int n = s.size() - 1; // s 下标从 1 开始
    std::vector<int> Z(n + 1);
    Z[1] = n;
    for (int i = 2, l = 0, r = 0; i <= n; i ++) {
        int &x = Z[i] = i <= r ? std::min(Z[i - l + 1], r - i + 1) : 0;
        while (i + x <= n && s[1 + x] == s[i + x]) {
            x ++;
        }
        if (i + x - 1 > r) {
            l = i, r = i + x - 1;
        }
    }
    return Z;
}

// p[i]：lcp(s, t[i:m])
auto Zalgo_match(const auto &s, const auto &t, const auto &Z) {
    int n = s.size() - 1, m = t.size() - 1; // s, t 下标从 1 开始
    std::vector<int> p(m + 1);
    for (int i = 1, l = 0, r = 0; i <= m; i ++) {
        int &x = p[i] = i <= r ? std::min(Z[i - l + 1], r - i + 1) : 0;
        while (1 + x <= n && i + x <= m && s[1 + x] == t[i + x]) {
            x ++;
        }
        if (i + x - 1 > r) {
            l = i, r = i + x - 1;
        }
    }
    return p;
}