// O(n)-O(1) gcd
struct flashGCD {
    int b;
    std::vector<int> prime, fac;
    std::vector<std::array<int, 3>> s;
    std::vector<std::vector<int>> g;

    flashGCD() {}
    flashGCD(int n) {
        init(n);
    }

    void init(int n) {
        b = sqrt(n);
        prime.clear(), fac.assign(n + 1, 0);
        s.assign(n + 1, {});
        g.assign(b + 1, std::vector<int>(b + 1, 0));

        for (int i = 2; i <= n; i ++) {
            if (!fac[i]) {
                prime.push_back(i), fac[i] = i;
            }
            for (int p : prime) {
                if (p > fac[i] || p > n / i) break;
                fac[i * p] = p;
            }
        }

        s[1] = {1, 1, 1};
        for (int i = 2; i <= n; i ++) {
            s[i] = s[i / fac[i]], s[i][0] *= fac[i];
            if (s[i][0] > s[i][1]) {
                std::swap(s[i][0], s[i][1]);
            }
            if (s[i][1] > s[i][2]) {
                std::swap(s[i][1], s[i][2]);
            }
        }

        for (int i = 0; i <= b; i ++) {
            g[i][0] = g[0][i] = i;
            for (int j = 1; j <= i; j ++) {
                g[i][j] = g[j][i] = g[i - j][j];
            }
        }
    }

    int gcd(int p, int q) {
        if (p == 0 || q == 0) {
            return p ^ q;
        }
        int ans = 1;
        for (int x : s[q]) {
            int t = x <= b ? g[x][p % x] : (p % x ? 1 : x);
            p /= t, ans *= t;
        }
        return ans;
    }
} fg;