// 多项式多点求值（多项式取模做法），作为 poly 的成员函数
std::vector<int> eval(std::vector<int> x) const {
    if (empty()) return std::vector<int>(x.size(), 0);
    if (x.empty()) return {};

    int n = x.size();
    std::vector<poly> t(n * 4);
    std::vector<int> ans(n);

    std::function<void(int, int, int)> build = [&] (int p, int l, int r) {
        if (l == r) {
            t[p] = poly{norm(-x[l]), 1};
            return;
        }
        int mid = (l + r) >> 1;
        build(p * 2, l, mid), build(p * 2 + 1, mid + 1, r);
        t[p] = t[p * 2] * t[p * 2 + 1];
    };
    build(1, 0, n - 1);

    std::function<void(int, int, int, const poly &)> solve = [&] (int p, int l, int r, const poly &f) {
        if (l == r) {
            ans[l] = f[0];
            return;
        }
        int mid = (l + r) >> 1;
        solve(p * 2, l, mid, divmod(f, t[p * 2]).second);
        solve(p * 2 + 1, mid + 1, r, divmod(f, t[p * 2 + 1]).second);
    };
    solve(1, 0, n - 1, divmod(*this, t[1]).second);

    return ans;
}