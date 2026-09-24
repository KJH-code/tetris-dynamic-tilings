// fix4.cpp 와 같은 고정 수열 7-bag 솔버인데, 메모 키를 지문 없이 완전한 128 비트로 쓴다 (교차검증용).
// 입력: argv[1]=도착 수열, argv[2]=상태 상한 (기본 3000000).
// 출력: "<수열> : PC POSSIBLE | no PC | INCONCLUSIVE (cap)   (states N)".
//
// 표가 2^26 슬롯이라 내부 적재율 한계가 TSIZE/10*7 = 46,976,202 다. 이 한계에 걸리면
// 보고되는 상태 수가 46,976,203 으로 고정되는데, 그 값을 보면 "탐색 실패" 가 아니라
// "표가 찼다" 로 읽어야 한다. 그때는 표가 두 배인 fix4 로 다시 돌린다.
#include <bits/stdc++.h>
using namespace std;
typedef unsigned __int128 u128;

int w = 10, hcap = 8, totclear = 4, target = 10;
vector<vector<int>> oricell;
vector<int> oripiece, oriwidth;
vector<vector<int>> byPiece;   // orientation indices per piece type

int basecell[7][8] = {
    {0,0, 0,1, 0,2, 0,3}, {0,0, 0,1, 1,0, 1,1}, {0,0, 0,1, 0,2, 1,1},
    {0,0, 0,1, 1,1, 1,2}, {0,1, 0,2, 1,0, 1,1}, {0,0, 0,1, 0,2, 1,0},
    {0,0, 0,1, 0,2, 1,2}
};
void buildorientations() {
    byPiece.assign(7, vector<int>());
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
                seen.insert(key);
                byPiece[p].push_back((int)oricell.size());
                oricell.push_back(key); oripiece.push_back(p);
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
inline int bitindex(int r, int c) { return r*w + c; }
inline bool collides(u128 b, int oi, int col, int r) {
    for (int k = 0; k < 4; k++) {
        int rr = r + oricell[oi][2*k], cc = col + oricell[oi][2*k+1];
        if (rr >= hcap) continue;
        if ((b >> bitindex(rr,cc)) & (u128)1) return true;
    }
    return false;
}
int lastcl;
u128 clearlines(u128 b) {
    u128 full = ((u128)1 << w) - (u128)1, out = 0;
    int outrow = 0, cnt = 0;
    for (int r = 0; r < hcap; r++) {
        u128 row = (b >> (r*w)) & full;
        if (row == full) { cnt++; continue; }
        out |= row << (outrow*w);
        outrow++;
    }
    lastcl = cnt;
    return out;
}
inline int holesof(u128 b) {
    int n = 0;
    for (int c = 0; c < w; c++) {
        bool seenfill = false;
        for (int r = hcap-1; r >= 0; r--) {
            bool f = ((b >> bitindex(r,c)) & (u128)1) != 0;
            if (f) seenfill = true;
            else if (seenfill) n++;
        }
    }
    return n;
}
inline int heightof(u128 b) {
    for (int r = hcap-1; r >= 0; r--)
        if (((b >> (r*w)) & (((u128)1<<w)-(u128)1)) != 0) return r+1;
    return 0;
}

int perm[16]; int arrlen;
// open-addressing table of 64-bit fingerprints.
// key is 87 bits (board 80 + i 4 + hold 3); we store a 64-bit mix.
// collision probability over ~4e7 entries is ~1e-4, negligible.
static const size_t TBITS = 26, TSIZE = (size_t)1 << TBITS, TMASK = TSIZE - 1;
vector<u128> tab;
long long tabcount = 0;
long long CAP = 3000000; bool capped=false;

inline unsigned long long mix64(unsigned long long x) {
    x ^= x >> 33; x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL;
    x ^= x >> 33; return x;
}
// exact 128-bit key, no fingerprinting
inline bool seen_or_insert(u128 board, int i, int hold) {
    u128 key = board | ((u128)(((i << 4) | hold) + 1) << 80);
    unsigned long long h = mix64((unsigned long long)key ^ mix64((unsigned long long)(key >> 64)));
    size_t p = (size_t)(h & TMASK);
    while (true) {
        u128 v = tab[p];
        if (v == 0) { tab[p] = key; tabcount++; return false; }
        if (v == key) return true;
        p = (p + 1) & TMASK;
    }
}

bool rec(u128 board, int i, int hold, int mask2, int placed, int clears) {
    if (placed == target) return board == 0;
    if (i > 11) return false;
    if (tabcount > CAP || tabcount > (long long)(TSIZE/10*7)) { capped = true; return false; }
    if (seen_or_insert(board, i, hold)) return false;

    if (i >= arrlen) return false;
    vector<pair<int,pair<u128,int> > > cand;
    { int arr = perm[i];
        int nmask = mask2;
        // stash into an empty hold: consumes an arrival, places nothing
        if (hold == 7) { if (rec(board, i+1, arr, nmask, placed, clears)) return true; }
        for (int opt = 0; opt < 2; opt++) {
            int toplace, nhold;
            if (opt == 0) { toplace = arr; nhold = hold; }
            else { if (hold == 7) continue; toplace = hold; nhold = arr; }
            for (size_t z = 0; z < byPiece[toplace].size(); z++) {
                int oi = byPiece[toplace][z];
                for (int col = 0; col + oriwidth[oi] <= w; col++) {
                    int r = hcap;
                    while (r > 0 && !collides(board, oi, col, r-1)) r--;
                    bool over = false; u128 b2 = board;
                    for (int k = 0; k < 4; k++) {
                        int rr = r + oricell[oi][2*k], cc = col + oricell[oi][2*k+1];
                        if (rr >= hcap) { over = true; break; }
                        b2 |= (u128)1 << bitindex(rr,cc);
                    }
                    if (over) continue;
                    b2 = clearlines(b2);
                    int nc = clears + lastcl;
                    if (nc > totclear) continue;
                    if (heightof(b2) > totclear - nc) continue;
                    cand.push_back(make_pair(holesof(b2)*64 + heightof(b2),
                                   make_pair(b2, (nhold<<8) | nc)));
                }
            }
        }
    }
    sort(cand.begin(), cand.end());
    for (size_t z = 0; z < cand.size(); z++) {
        int nh = (cand[z].second.second >> 8) & 0xff;
        int nc = cand[z].second.second & 0xff;
        if (rec(cand[z].second.first, i+1, nh, mask2 | ((i>=7)?(1<<perm[i]):0), placed+1, nc)) return true;
    }
    return false;
}

int main(int argc, char **argv) {
    buildorientations();
    const char *names = "IOTSZJL";
    if (argc > 1) {   // full arrival sequence, e.g. 11 letters (bag1 + bag2 prefix)
        string s = argv[1];
        arrlen = (int)s.size();
        if (argc > 2) CAP = atoll(argv[2]);
        for (int k = 0; k < arrlen; k++) perm[k] = (int)(strchr(names, s[k]) - names);
        tab.assign(TSIZE, (u128)0); tabcount = 0; capped=false;
        bool ok = rec(0, 0, 7, 0, 0, 0);
        printf("%s : %s   (states %lld)\n", argv[1], ok ? "PC POSSIBLE" : (capped ? "INCONCLUSIVE (cap)" : "no PC"), tabcount);
        return 0;
    }
    printf("usage: ./fix <arrival sequence>\n");
    return 0;
}
