// 闵可夫斯基和（默认：逆时针）
auto minkowski(std::vector<point> a, std::vector<point> b) {
    std::vector<point> c{a[0] + b[0]};
    a.push_back(a[0]), b.push_back(b[0]); // 若 a, b 均为凸壳，省去此行
    for (int i = 0; i + 1 < a.size(); i ++) {
        a[i] = a[i + 1] - a[i];
    }
    for (int i = 0; i + 1 < b.size(); i ++) {
        b[i] = b[i + 1] - b[i];
    }
    a.pop_back(), b.pop_back();
    c.resize(a.size() + b.size() + 1);
    std::merge(a.begin(), a.end(), b.begin(), b.end(), c.begin() + 1, [] (point l, point r) {
        return cross(l, r) > 0; // 若 a, b 均为逆时针凸包（或凸壳）则写 >0，顺时针则写 <0
    });
    for (int i = 1; i < c.size(); i ++) {
        c[i] = c[i] + c[i - 1];
    }
    return c;
}