struct Info {
    int mx, md;
    int cnt;
    Info() {}
    Info(int mx, int md, int cnt) : mx(mx), md(md), cnt(cnt) {}

    friend Info operator + (Info l, Info r) {
        if (l.mx == r.mx) {
            return Info(l.mx, std::max(l.md, r.md), l.cnt + r.cnt);
        } else if (l.mx > r.mx) {
            return Info(l.mx, std::max(l.md, r.mx), l.cnt);
        } else {
            return Info(r.mx, std::max(l.mx, r.md), r.cnt);
        }
    }
};

// 吉老师线段树
namespace SGT {
    struct node {
        int len;
        i64 sum;
        Info info;

        int add; // 加法标记（初始值等于 0）
        int tag; // 区间取 min 标记（初始值等于 +inf，需要根据数据范围修改）
        void mk_add(int x) {
            sum += 1ll * x * len;
            info.mx += x, info.md += x;
            add += x;
            if (tag < inf) tag += x;
        }
        void mk_tag(int x) {
            if (info.mx <= x) return;
            sum -= 1ll * (info.mx - x) * info.cnt;
            info.mx = x;
            tag = x;
        }
    } t[N * 4];

    void upd(int p) {
        t[p].sum = t[p * 2].sum + t[p * 2 + 1].sum;
        t[p].info = t[p * 2].info + t[p * 2 + 1].info;
    }

    void spread(int p) {
        if (t[p].add) {
            t[p * 2].mk_add(t[p].add), t[p * 2 + 1].mk_add(t[p].add);
            t[p].add = 0;
        }
        if (t[p].tag < inf) {
            t[p * 2].mk_tag(t[p].tag), t[p * 2 + 1].mk_tag(t[p].tag);
            t[p].tag = inf;
        }
    }

    void build(int p, int l, int r) {
        t[p].add = 0, t[p].tag = inf, t[p].len = r - l + 1;
        if (l == r) {
            t[p].sum = a[l], t[p].info = Info(a[l], -inf, 1);
            return;
        }
        int mid = (l + r) >> 1;
        build(p * 2, l, mid), build(p * 2 + 1, mid + 1, r);
        upd(p);
    }

    void change_add(int p, int l, int r, int s, int e, int x) {
        if (s <= l && r <= e) {
            t[p].mk_add(x);
            return;
        }
        spread(p);
        int mid = (l + r) >> 1;
        if (s <= mid) {
            change_add(p * 2, l, mid, s, e, x);
        }
        if (mid < e) {
            change_add(p * 2 + 1, mid + 1, r, s, e, x);
        }
        upd(p);
    }

    void change_min(int p, int l, int r, int s, int e, int x) {
        if (s <= l && r <= e && t[p].info.md < x) {
            t[p].mk_tag(x);
            return;
        }
        spread(p);
        int mid = (l + r) >> 1;
        if (s <= mid) {
            change_min(p * 2, l, mid, s, e, x);
        }
        if (mid < e) {
            change_min(p * 2 + 1, mid + 1, r, s, e, x);
        }
        upd(p);
    }
}