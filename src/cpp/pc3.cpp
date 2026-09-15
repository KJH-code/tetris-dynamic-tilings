#include <bits/stdc++.h>
using namespace std;
typedef unsigned __int128 bb;
int mircol[16];
bb mirror(bb b, int w, int hcap){ bb o=0; for(int r=0;r<hcap;r++) for(int c=0;c<w;c++) if((b>>(r*w+c))&(bb)1) o=o|((bb)1<<(r*w+(w-1-c))); return o; }

int w, hcap, target, totclear, pmask, wantpar, mirrorok;

vector<vector<int>> oricell;
vector<int> oripiece;
vector<int> oriwidth;

int basecell[7][8] = {
    {0,0, 0,1, 0,2, 0,3},
    {0,0, 0,1, 1,0, 1,1},
    {0,0, 0,1, 0,2, 1,1},
    {0,0, 0,1, 1,1, 1,2},
    {0,1, 0,2, 1,0, 1,1},
    {0,0, 0,1, 0,2, 1,0},
    {0,0, 0,1, 0,2, 1,2}
};

void buildorientations() {
    for (int p = 0; p < 7; p++) {
        set<vector<int>> seen;
        vector<int> cur;
        for (int k = 0; k < 8; k++) cur.push_back(basecell[p][k]);
        for (int rot = 0; rot < 4; rot++) {
            int minr = 100, minc = 100;
            for (int k = 0; k < 4; k++) {
                minr = min(minr, cur[2*k]);
                minc = min(minc, cur[2*k+1]);
            }
            vector<pair<int,int>> pts;
            for (int k = 0; k < 4; k++)
                pts.push_back(make_pair(cur[2*k] - minr, cur[2*k+1] - minc));
            sort(pts.begin(), pts.end());
            vector<int> key;
            for (int k = 0; k < 4; k++) { key.push_back(pts[k].first); key.push_back(pts[k].second); }
            if (seen.count(key) == 0) {
                seen.insert(key);
                oricell.push_back(key);
                oripiece.push_back(p);
                int mw = 0;
                for (int k = 0; k < 4; k++) mw = max(mw, key[2*k+1] + 1);
                oriwidth.push_back(mw);
            }
            vector<int> nxt;
            for (int k = 0; k < 4; k++) {
                nxt.push_back(cur[2*k+1]);
                nxt.push_back(-cur[2*k]);
            }
            cur = nxt;
        }
    }
}

int bitindex(int r, int c) { return r * w + c; }

bool collides(bb board, int oi, int col, int r) {
    for (int k = 0; k < 4; k++) {
        int rr = r + oricell[oi][2*k];
        int cc = col + oricell[oi][2*k+1];
        if (rr >= hcap) continue;
        if ((board >> bitindex(rr, cc)) & 1ULL) return true;
    }
    return false;
}

int lastclearcount;

bb clearlines(bb board) {
    bb full = ((bb)1 << w) - 1ULL;
    bb out = 0;
    int outrow = 0, cnt = 0;
    for (int r = 0; r < hcap; r++) {
        bb row = (board >> (r * w)) & full;
        if (row == full) { cnt++; continue; }
        out = out | (row << (outrow * w));
        outrow++;
    }
    lastclearcount = cnt;
    return out;
}

int heightof(bb board) {
    int h = 0;
    for (int r = 0; r < hcap; r++) {
        bb row = (board >> (r * w)) & (((bb)1 << w) - 1ULL);
        if (row != 0) h = r + 1;
    }
    return h;
}

// key = board<<8 | clears<<1 | tparity
int main(int argc, char **argv) {
    w = atoi(argv[1]);
    target = atoi(argv[2]);
    pmask = 127; wantpar = 1;
    if (argc > 3) pmask = atoi(argv[3]);
    if (argc > 4) wantpar = atoi(argv[4]);
    // mirror canonicalization is only valid when the piece set is closed under reflection
    mirrorok = (((pmask>>3)&1) == ((pmask>>4)&1)) && (((pmask>>5)&1) == ((pmask>>6)&1));
    if ((4 * target) % w != 0) {
        printf("w=%d n=%d: impossible (4n not divisible by w)\n", w, target);
        return 0;
    }
    totclear = 4 * target / w;
    hcap = totclear + 4;
    buildorientations();

    vector<bb> frontier;
    vector<unsigned long long> fmeta;   // clears<<1 | tparity
    vector<int> fpar;
    vector<int> fmove;
    vector<vector<bb>> allb;
    vector<vector<unsigned long long>> allm;
    vector<vector<int>> allp;
    vector<vector<int>> allmv;

    frontier.push_back((bb)0);
    fmeta.push_back(0ULL);
    fpar.push_back(-1);
    fmove.push_back(-1);

    int foundidx = -1;

    for (int depth = 0; depth < target; depth++) {
        allb.push_back(frontier);
        allm.push_back(fmeta);
        allp.push_back(fpar);
        allmv.push_back(fmove);

        vector<bb> nb2; vector<unsigned long long> nm2;
        vector<int> np2, nmv2;
        set<pair<unsigned long long,unsigned long long>> seen;
        

        for (size_t fi = 0; fi < frontier.size(); fi++) {
            bb board = frontier[fi];
            int clears = (int)(fmeta[fi] >> 1);
            int tpar = (int)(fmeta[fi] & 1ULL);
            for (size_t oi = 0; oi < oricell.size(); oi++) {
                if (((pmask >> oripiece[oi]) & 1) == 0) continue;
                for (int col = 0; col + oriwidth[oi] <= w; col++) {
                    int r = hcap;
                    while (r > 0 && !collides(board, (int)oi, col, r - 1)) r--;
                    bool over = false;
                    bb b2 = board;
                    for (int k = 0; k < 4; k++) {
                        int rr = r + oricell[oi][2*k];
                        int cc = col + oricell[oi][2*k+1];
                        if (rr >= hcap) { over = true; break; }
                        b2 = b2 | ((bb)1 << bitindex(rr, cc));
                    }
                    if (over) continue;
                    b2 = clearlines(b2);
                    int nclears = clears + lastclearcount;
                    if (nclears > totclear) continue;
                    // KEY PRUNE: remaining clears must cover remaining height
                    if (heightof(b2) > totclear - nclears) continue;
                    int ntpar = tpar;
                    if (oripiece[oi] == 2) ntpar = 1 - ntpar;
                    unsigned long long meta = ((unsigned long long)nclears << 1) | (unsigned long long)ntpar;
                    if (mirrorok) { bb mb=mirror(b2,w,hcap); if(mb<b2) b2=mb; }
                    bb kk=(b2<<8)|(bb)meta; pair<unsigned long long,unsigned long long> key=make_pair((unsigned long long)(kk>>64),(unsigned long long)kk);
                    if (seen.count(key) > 0) continue;
                    seen.insert(key);
                    nb2.push_back(b2);
                    nm2.push_back(meta);
                    np2.push_back((int)fi);
                    nmv2.push_back((int)(oi * 100 + col));
                    if (depth + 1 == target && b2 == 0 && ntpar == wantpar) foundidx = (int)nb2.size() - 1;
                }
            }
        }
        frontier = nb2; fmeta = nm2; fpar = np2; fmove = nmv2;
        fprintf(stderr, "  depth %d: %zu states\n", depth + 1, frontier.size());
        if (foundidx >= 0) break;
        if (frontier.empty()) break;
    }

    if (foundidx < 0) {
        printf("w=%d n=%d: NO perfect clear\n", w, target);
        return 0;
    }
    allb.push_back(frontier); allm.push_back(fmeta); allp.push_back(fpar); allmv.push_back(fmove);

    printf("w=%d n=%d: FOUND perfect clear\n", w, target);
    vector<int> moves;
    int lvl = (int)allb.size() - 1, idx = foundidx;
    while (lvl > 0) {
        moves.push_back(allmv[lvl][idx]);
        idx = allp[lvl][idx];
        lvl--;
    }
    reverse(moves.begin(), moves.end());

    const char *names = "IOTSZJL";
    bb board = 0;
    for (size_t i = 0; i < moves.size(); i++) {
        int oi = moves[i] / 100, col = moves[i] % 100;
        int r = hcap;
        while (r > 0 && !collides(board, oi, col, r - 1)) r--;
        for (int k = 0; k < 4; k++)
            board = board | ((bb)1 << bitindex(r + oricell[oi][2*k], col + oricell[oi][2*k+1]));
        board = clearlines(board);
        printf("step %d: %c col%d -> cleared %d\n", (int)i + 1, names[oripiece[oi]], col, lastclearcount);
        for (int rr = hcap - 1; rr >= 0; rr--) {
            printf("        ");
            for (int cc = 0; cc < w; cc++) {
                if ((board >> bitindex(rr, cc)) & 1ULL) printf("#");
                else printf(".");
            }
            printf("\n");
        }
    }
    return 0;
}
