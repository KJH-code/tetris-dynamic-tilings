#include <bits/stdc++.h>
using namespace std;
typedef unsigned __int128 bb;

int w, hcap, totclear;
vector<vector<int>> oricell;
vector<int> oripiece, oriwidth;

int basecell[7][8] = {
    {0,0, 0,1, 0,2, 0,3}, {0,0, 0,1, 1,0, 1,1}, {0,0, 0,1, 0,2, 1,1},
    {0,0, 0,1, 1,1, 1,2}, {0,1, 0,2, 1,0, 1,1}, {0,0, 0,1, 0,2, 1,0},
    {0,0, 0,1, 0,2, 1,2}
};

void buildorientations() {
    for (int p = 0; p < 7; p++) {
        set<vector<int>> seen;
        vector<int> cur;
        for (int k = 0; k < 8; k++) cur.push_back(basecell[p][k]);
        for (int rot = 0; rot < 4; rot++) {
            int minr = 100, minc = 100;
            for (int k = 0; k < 4; k++) { minr = min(minr, cur[2*k]); minc = min(minc, cur[2*k+1]); }
            vector<pair<int,int>> pts;
            for (int k = 0; k < 4; k++) pts.push_back(make_pair(cur[2*k]-minr, cur[2*k+1]-minc));
            sort(pts.begin(), pts.end());
            vector<int> key;
            for (int k = 0; k < 4; k++) { key.push_back(pts[k].first); key.push_back(pts[k].second); }
            if (seen.count(key) == 0) {
                seen.insert(key); oricell.push_back(key); oripiece.push_back(p);
                int mw = 0;
                for (int k = 0; k < 4; k++) mw = max(mw, key[2*k+1]+1);
                oriwidth.push_back(mw);
            }
            vector<int> nxt;
            for (int k = 0; k < 4; k++) { nxt.push_back(cur[2*k+1]); nxt.push_back(-cur[2*k]); }
            cur = nxt;
        }
    }
}

int bitindex(int r, int c) { return r*w + c; }

bool collides(bb board, int oi, int col, int r) {
    for (int k = 0; k < 4; k++) {
        int rr = r + oricell[oi][2*k], cc = col + oricell[oi][2*k+1];
        if (rr >= hcap) continue;
        if ((board >> bitindex(rr,cc)) & (bb)1) return true;
    }
    return false;
}

int lastcl;
bb clearlines(bb board) {
    bb full = ((bb)1 << w) - (bb)1, out = 0;
    int outrow = 0, cnt = 0;
    for (int r = 0; r < hcap; r++) {
        bb row = (board >> (r*w)) & full;
        if (row == full) { cnt++; continue; }
        out = out | (row << (outrow*w));
        outrow++;
    }
    lastcl = cnt;
    return out;
}

int heightof(bb board) {
    int h = 0;
    for (int r = 0; r < hcap; r++)
        if (((board >> (r*w)) & (((bb)1 << w)-(bb)1)) != 0) h = r+1;
    return h;
}

set<pair<pair<unsigned long long,unsigned long long>,int>> memo;
int cnt7[7];

int packcounts() {
    int v = 0;
    for (int i = 0; i < 7; i++) v = v*4 + cnt7[i];
    return v;
}

bool rec(bb board, int clears) {
    pair<pair<unsigned long long,unsigned long long>,int> key =
        make_pair(make_pair((unsigned long long)(board>>64), (unsigned long long)board), packcounts());
    if (memo.count(key)) return false;
    memo.insert(key);
    int tot = 0;
    for (int i = 0; i < 7; i++) tot += cnt7[i];
    if (tot == 0) return board == 0;
    for (size_t oi = 0; oi < oricell.size(); oi++) {
        int p = oripiece[oi];
        if (cnt7[p] == 0) continue;
        for (int col = 0; col + oriwidth[oi] <= w; col++) {
            int r = hcap;
            while (r > 0 && !collides(board, (int)oi, col, r-1)) r--;
            bool over = false;
            bb b2 = board;
            for (int k = 0; k < 4; k++) {
                int rr = r + oricell[oi][2*k], cc = col + oricell[oi][2*k+1];
                if (rr >= hcap) { over = true; break; }
                b2 = b2 | ((bb)1 << bitindex(rr,cc));
            }
            if (over) continue;
            b2 = clearlines(b2);
            int nc = clears + lastcl;
            if (nc > totclear) continue;
            if (heightof(b2) > totclear - nc) continue;
            cnt7[p]--;
            bool ok = rec(b2, nc);
            cnt7[p]++;
            if (ok) return true;
        }
    }
    return false;
}

int main(int argc, char **argv) {
    // argv[1] = width, argv[2] = 7 digits giving the count of I O T S Z J L
    w = atoi(argv[1]);
    string cs = argv[2];
    int n = 0;
    for (int i = 0; i < 7; i++) { cnt7[i] = cs[i]-'0'; n += cnt7[i]; }
    if ((4*n) % w != 0) { printf("%s : cell count not divisible by w\n", argv[2]); return 0; }
    totclear = 4*n/w;
    hcap = totclear + 4;
    buildorientations();
    bool ok = rec((bb)0, 0);
    printf("w=%d counts=%s n=%d R=%d : %s\n", w, argv[2], n, totclear, ok ? "PC POSSIBLE" : "no PC");
    return 0;
}
