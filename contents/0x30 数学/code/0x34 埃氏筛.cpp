// 埃氏筛
std::bitset<MaxV> vis;
void sieve(int n) {
    for (int i = 2; i <= n; i ++) {
        if (vis[i]) {
            continue;
        }
        for (int j = 2; j <= n / i; j ++) {
            vis[i * j] = 1;
        }
    }
}