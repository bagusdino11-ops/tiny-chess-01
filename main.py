# UCI Chess Engine ≤4KB (iterative deepening + aspiration)
import json,os,sys,urllib.error,urllib.request
ENV_URL=os.environ.get("MAKEFUN_ENV_URL")or sys.exit("MAKEFUN_ENV_URL not set")

def post(path,body):req=urllib.request.Request(ENV_URL+path,data=json.dumps(body).encode(),headers={"content-type":"application/json"});try:with urllib.request.urlopen(req)as r:return json.load(r)except urllib.error.HTTPError as e:sys.exit(f"{path}:HTTP{e.code}{e.read().decode()}")

def board_of(fen):b={};for i,row in enumerate(fen.split()[0].split("/")):f=0;exec("for c in row:\n if c.isdigit():f+=int(c)\n else:b[\"abcdefgh\"[f]+str(8-i)]=c\n f+=1");return b

sq2i=lambda sq:(8-int(sq[1]),ord(sq[0])-97)
i2sq=lambda r,c:"abcdefgh"[c]+str(r+1)

def eval_board(b,turn,fen):s=0;pvals={"P":1,"N":3,"B":3,"R":5,"Q":9,"K":100};for sq in b:p=b[sq].upper();if p=="P"or p=="p":s+=pvals[p];elif p in pvals:s+=pvals[p];if turn=="b":s=-s;return round(s,2)

OPENING={"w":"":["e4","d4","Nf3"],"b e4":["c5","g6"],"b d4":["e5","Nf6"],"w e4 c5":["Bb5","Qa4"],"w d4 e5":["Nf3","Bg2"]}
def book_move(fen,f):fens=fen.split();p=1;for i in range(1,len(fens)):p+=" "+fens[i];if p in OPENING:return OPENING[p][0]

def pseudo_legal(fen,f=None):if f is None:f=[board_of(s) for s in fen.split() if s];board=f[0];turn=f[1].lower();moves=[];for sq in list(board.keys()):p=board[sq].upper();if p=="P":r,c=sq2i(sq);d=-1if turn=="w"else 1;nr=r+d;if 0<=nr<8and board.get(i2sq(nr,c))is None:moves.append(i2sq(r,c)+i2sq(nr,c));nr2=r+2*d;if nr2<=7and board.get(i2sq(nr2,c))is None:moves.append(i2sq(r,c)+i2sq(nr2,c));for dc in[-1,1]:nc=c+dc;if 0<=nr<8and0<=nc<8:t=board.get(i2sq(nr,nc),None);if t and p=="P"and t.lower()!=turn:moves.append(i2sq(r,c)+i2sq(nr,nc))elif p=="N":for dr,dc in[(-2,1),( -1,2),(1,2),(2,1),(2,-1),( 1,-2),(-1,-2),(-2,-1)]:nr=r+dr;nc=c+dc;if0<=nr<8and0<=nc<8:moves.append(i2sq(r,c)+i2sq(nr,nc));break elif p in"BQRQ":for dr,dc in[(0,1),(1,1),(1,0),(1,-1),(-1,-1),(-1,0),(-1,1)]:nr=r+dr*3;nc=c+dc*2;if0<=nr<8and0<=nc<8:moves.append(i2sq(r,c)+i2sq(nr,nc));break;return moves

def alpha_beta(fen,d,alpha,beta):if d<=0:return eval_board(board_of(fen),fen.split()[1].lower(),fen),[];board=board_of(fen);turn=fen.split()[1].lower();moves=pseudo_legal(fen);best_score=float('-inf');best_move=None;for m in moves:from_sq,to_sq=m[:2],m[2:];old=board.get(from_sq);target=board.get(to_sq);new_board=board.copy()
 if old:new_board[from_sq]=None;if target and to_sq!=from_sq:new_board[to_sq]=old;score,_child=alpha_beta(fen+" "+(target or" "),d-1,-beta,-alpha)
 new_board[from_sq]=None;if score>best_score:best_score=score;best_move=m;alpha=max(alpha,score);if beta<=alpha;break;return best_score,best_move

def aspiration_search(fen,d):for d in range(1,6+1):alpha=-float('inf');beta=float('inf');iteration=0
 while iteration<3:low=-int(d*20)+max(-3000,-int(d));high=min(int(d*8),3000);while high-low>1 and alpha<low and beta>high:mid=(low+high)//2;score,_child=alpha_beta(fen,d,mid-alpha,mid+alpha);if score<=mid:_last_alpha=score;else:low=max(low,score)
 else:low=max(_last_alpha,int(d*5));high=min(mid-1,int(d*10));while high-low>1 and alpha<low and beta>high:mid=(low+high)//2;score,_child=alpha_beta(fen,d,mid-alpha,mid+alpha);if score<=mid:_last_alpha=score;else:low=max(low,score)
 if _last_alpha>=high:return low,_last_alpha,iteration;iteration+=1;return None,None,None

def choose(fen):m=None;book_m=book_move(fen,fen.split());if book_m:m=book_m;if not m:r,alpha,iter_count=aspiration_search(fen,4);if r is not None:m=i2sq(sq2i(r[0]),sq2i(r[1])) if (r:=best_score)else(m:=best_move);return m

while True:g=post("/game",{});if g["status"]=="done":break;while g["status"]=="your_move":move=choose(g["fen"]);r=post("/move",{"game":g["game"],"move":move});print(f"Move:{move}→{r.get('outcome','?')}",file=sys.stderr)
 print(f"G {g['game']}: outcome={g.get('outcome','N/A')}, reason={g.get('reason','N/A')}",file=sys.stderr);w=g.get("wins",0);d=g.get("draws",0);l=g.get("losses",0);print(f"Final:{w}won,{d}drawn,{l}lost",file=sys.stderr)

if __name__=="__main__":main()
