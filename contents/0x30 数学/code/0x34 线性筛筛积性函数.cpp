// 线性筛筛积性函数
int primeCount, prime[MaxV], low[MaxV];
int f[MaxV];
void sieve(int n) {
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
}