// net[i]：s[1:i] 真前缀与真后缀匹配的最大长度（s[1:i] 的 border）
auto kmp(const auto &s) {
    int n = s.size() - 1; // s 下标从 1 开始
    std::vector<int> net(n + 1);
    net[1] = 0;
    for (int i = 2, j = 0; i <= n; i ++) {
        while (j > 0 && s[j + 1] != s[i]) j = net[j];
        if (s[j + 1] == s[i]) j ++;
        net[i] = j;
    }
    return net;
}

// f[i]：t[1:i] 后缀与 s 前缀匹配的最大长度
auto kmp_match(const auto &s, const auto &t, const auto &net) {
    int n = s.size() - 1, m = t.size() - 1; // s, t 下标从 1 开始
    std::vector<int> f(m + 1);
    for (int i = 1, j = 0; i <= m; i ++) {
        while (j > 0 && (j == n || s[j + 1] != t[i])) j = net[j];
        if (s[j + 1] == t[i]) j ++;
        f[i] = j;
    }
    return f;
}