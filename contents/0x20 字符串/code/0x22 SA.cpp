// 后缀数组
struct SuffixArray {
    int n, t;
    std::vector<int> sa, rk, height;
    std::vector<std::vector<int>> f;

    SuffixArray() {}
    SuffixArray(const auto &s) {
        build(s);
    }

    void build(const auto &s) {
        n = s.size() - 1; // s 下标从 1 开始
        int m = 256;
        sa.resize(n + 1), rk.resize(n + 1), height.resize(n + 1);
        std::vector<int> cnt(std::max(n, m) + 1), id(n + 1), px(n + 1), tmp(2 * n + 1);

        auto same = [&] (int x, int y, int k) {
            return tmp[x] == tmp[y] && tmp[x + k] == tmp[y + k];
        };

        for (int i = 1; i <= n; i ++) cnt[rk[i] = s[i]] ++;
        for (int i = 1; i <= m; i ++) cnt[i] += cnt[i - 1];
        for (int i = n; i >= 1; i --) sa[cnt[rk[i]] --] = i;

        for (int k = 1, p = 0; k < n; k <<= 1, m = p) {
            p = 0;
            for (int i = n - k + 1; i <= n; i ++) id[++ p] = i;
            for (int i = 1; i <= n; i ++)
                if (sa[i] > k) id[++ p] = sa[i] - k;
            
            for (int i = 1; i <= m; i ++) cnt[i] = 0;
            for (int i = 1; i <= n; i ++) cnt[px[i] = rk[id[i]]] ++;
            for (int i = 1; i <= m; i ++) cnt[i] += cnt[i - 1];
            for (int i = n; i >= 1; i --) sa[cnt[px[i]] --] = id[i];

            p = 0;
            for (int i = 1; i <= n; i ++) tmp[i] = rk[i];
            for (int i = 1; i <= n; i ++) rk[sa[i]] = same(sa[i - 1], sa[i], k) ? p : ++ p;
            if (p == n) break;
        }
        if (n == 1) rk[1] = 1;

        for (int i = 1, h = 0; i <= n; i ++) {
            int j = sa[rk[i] - 1];
            if (h) h --;
            while (i + h <= n && j + h <= n && s[i + h] == s[j + h]) h ++;
            height[rk[i]] = h;
        }

        t = std::__lg(n);
        f.assign(t + 1, std::vector<int>(n + 1));
        for (int i = 1; i <= n; i ++) {
            f[0][i] = height[i];
        }
        for (int j = 1; j <= t; j ++) {
            for (int i = 1; i <= n - (1 << j) + 1; i ++) {
                f[j][i] = std::min(f[j - 1][i], f[j - 1][i + (1 << (j - 1))]);
            }
        }
    }

    int ask(int l, int r) {
        int k = std::__lg(r - l + 1);
        return std::min(f[k][l], f[k][r - (1 << k) + 1]);
    }
    int lcp(int i, int j) {
        if (i == j) return n - i + 1;
        auto [l, r] = std::minmax(rk[i], rk[j]);
        return ask(l + 1, r);
    }
};