// 凸包（默认：逆时针）
auto gethull(std::vector<point> s) {
    std::sort(s.begin(), s.end(), [] (point l, point r) -> bool {
        return l.x != r.x ? l.x < r.x : l.y < r.y;
    });
    s.erase(std::unique(s.begin(), s.end(), [] (point l, point r) -> bool {
        return l.x == r.x && l.y == r.y;
    }), s.end());

    std::vector<point> h;
    for (int i = 0; i < s.size(); i ++) {
        while (h.size() >= 2 && cross(h.rbegin()[1], h.back(), s[i]) <= 0) {
            h.pop_back();
        }
        h.push_back(s[i]);
    }
    for (int i = (int)s.size() - 2, t = h.size(); i >= 0; i --) {
        while (h.size() > t && cross(h.rbegin()[1], h.back(), s[i]) <= 0) {
            h.pop_back();
        }
        h.push_back(s[i]);
    }
    if (h.size() > 1) {
        h.pop_back();
    }
    return h;
}