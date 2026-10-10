// 子集卷积
std::vector<int> subset_conv(std::vector<int> a, std::vector<int> b) {
    int n = a.size(), m = std::__lg(n);
    std::vector<std::vector<int>> A(m + 1, std::vector<int>(n, 0));
    std::vector<std::vector<int>> B(m + 1, std::vector<int>(n, 0));
    std::vector<std::vector<int>> C(m + 1, std::vector<int>(n, 0));
    
    for (int i = 0; i < n; i ++) {
        int s = __builtin_popcount(i);
        A[s][i] = a[i], B[s][i] = b[i];
    }
    for (int i = 0; i <= m; i ++) {
        dwtOr(A[i], +1), dwtOr(B[i], +1);
    }
    for (int i = 0; i <= m; i ++) {
        for (int j = 0; j <= i; j ++) {
            for (int k = 0; k < n; k ++) {
                add(C[i][k], 1ll * A[j][k] * B[i - j][k] % mod);
            }
        }
    }
    for (int i = 0; i <= m; i ++) {
        dwtOr(C[i], -1);
    }

    std::vector<int> c(n);
    for (int i = 0; i < n; i ++) {
        c[i] = C[__builtin_popcount(i)][i];
    }
    return c;
}