namespace du {
    const int V = 1e6; // 预处理的范围（需根据实际问题调整）
    const int MaxV = V + 10;

    int primeCount, prime[MaxV], low[MaxV];
    int f[MaxV];

    i64 f1[MaxV];
    std::map<int, i64> f2;

    void init(const int &n = V) {
        f[1] = 1;
        for (int i = 2; i <= n; i ++) {
            if (!low[i]) {
                prime[++ primeCount] = i, low[i] = i;
                for (i64 v = i, c = 1; v <= n; v *= i, c ++) {
                    // 计算 f[v]
                }
            }
            for (int j = 1; j <= primeCount; j ++) {
                if (prime[j] > n / i) break;
                low[i * prime[j]] = i % prime[j] ? prime[j] : low[i] * prime[j];

                if (i % prime[j] == 0) break;
            }
            if (low[i] < i) {
                f[i] = f[low[i]] * f[i / low[i]];
            }
        }

        for (int i = 1; i <= n; i ++) {
            f1[i] = f1[i - 1] + f[i];
        }
    }

    i64 fSum(int n) {
        if (n <= V) return f1[n];
        if (f2.contains(n)) return f2[n];

        i64 ans = 0; // 初始计算函数 f*g 第 1~n 项的和
        for (int x = 2, nx; x <= n; x = nx + 1) {
            nx = n / (n / x);
            i64 sum = 0; // 计算函数 g 第 x~nx 项的和
            ans -= sum * fSum(n / x);
        }
        return f2[n] = ans;
    }
}