import numpy as np, cv2, json, sys
from PIL import Image
from skimage.morphology import skeletonize
im=np.array(Image.open(sys.argv[1] if len(sys.argv)>1 else 'assets/reference/logo-master.png').convert('L')).astype(float)
m=(im<128).astype(np.uint8)
def rowrun(y,x0,x1):
    xs=np.nonzero(m[y,x0:x1])[0]+x0; return xs.min(),xs.max()
def colrun(x,y0,y1):
    ys=np.nonzero(m[y0:y1,x])[0]+y0; return ys.min(),ys.max()
# left dot: widest row and tallest column
best=None
for y in range(705,760):
    xs=np.nonzero(m[y,250:305])[0]
    if len(xs) and (best is None or len(xs)>best[0]): best=(len(xs),y,xs.min()+250,xs.max()+250)
lw=best; ly0,ly1=colrun(lw[2]+ (lw[3]-lw[2])//2 - 5,690,780)
L={'cx':(lw[2]+lw[3]+1)/2,'cy':best[1],'r':(lw[3]-lw[2]+1)/2}
best=None
for y in range(700,780):
    xs=np.nonzero(m[y,900:1010])[0]
    if len(xs) and (best is None or len(xs)>best[0]): best=(len(xs),y,xs.min()+900,xs.max()+900)
cx=(best[2]+best[3]+1)/2; _,yb=colrun(int(cx),700,800)
R={'cx':cx,'r':(best[3]-best[2]+1)/2}; R['cy']=yb+1-R['r']
# left dot cy from bottom
_,lb=colrun(int(L['cx']),700,800); L['cy']=lb+1-L['r']
print(L,R)
# stroke = mask minus dots
yy,xx=np.mgrid[:m.shape[0],:m.shape[1]]
s=m.copy()
s[(xx-L['cx'])**2+(yy-L['cy'])**2 < (L['r']-1.5)**2]=0
s[(xx-R['cx'])**2+(yy-R['cy'])**2 < (R['r']-1.5)**2]=0
# remove tiny residues
n,lab,st,_=cv2.connectedComponentsWithStats(s)
k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); s=(lab==k).astype(np.uint8)
# upsample for smoother contour
S=4
big=cv2.resize(im,None,fx=S,fy=S,interpolation=cv2.INTER_CUBIC)
bm=(big<128).astype(np.uint8)*cv2.resize(s,None,fx=S,fy=S,interpolation=cv2.INTER_NEAREST)
cs,_=cv2.findContours(bm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cs,key=cv2.contourArea)[:,0,:].astype(float)/S
# smooth & resample
from scipy.ndimage import gaussian_filter1d
c=np.stack([gaussian_filter1d(c[:,0],3,mode='wrap'),gaussian_filter1d(c[:,1],3,mode='wrap')],1)
ap=cv2.approxPolyDP((c*100).astype(np.int32).reshape(-1,1,2),45,True)[:,0,:]/100.0
print('contour pts',len(c),'approx',len(ap))
def catmull(pts,closed=True):
    n=len(pts); d=f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n if closed else n-1):
        p0=pts[(i-1)%n] if (closed or i>0) else pts[i]; p1=pts[i]; p2=pts[(i+1)%n]; p3=pts[(i+2)%n] if (closed or i+2<n) else pts[i+1]
        c1=p1+(p2-p0)/6; c2=p2-(p3-p1)/6
        d+=f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d+"Z"
outline=catmull(ap)
# centerline via skeleton
s2=s.copy(); s2[(xx-L['cx'])**2+(yy-L['cy'])**2 < (L['r']+3)**2]=0; s2[(xx-R['cx'])**2+(yy-R['cy'])**2 < (R['r']+3)**2]=0
n2,lab2,st2,_=cv2.connectedComponentsWithStats(s2.astype(np.uint8)); k2=1+np.argmax(st2[1:,cv2.CC_STAT_AREA]); s2=(lab2==k2)
sk=skeletonize(s2); ys,xs=np.nonzero(sk)
pts=np.stack([xs,ys],1).astype(float)
# order by walking from leftmost
start=pts[np.argmin(pts[:,0])]; order=[start]; rem=list(map(tuple,pts)); rem.remove(tuple(start))
rem=np.array(rem)
cur=start
while len(rem):
    d=np.hypot(*(rem-cur).T); i=np.argmin(d)
    if d[i]>6: break
    cur=rem[i]; order.append(cur); rem=np.delete(rem,i,0)
order=np.array(order)
sub=order[::25]; sub=np.vstack([[L['cx']+L['r']*0.0,L['cy']] if False else sub[0], sub[1:], order[-1]])
# extend centerline: start at left dot center, end at right dot center
sub=order[::30][:-2]
cl=np.vstack([[L['cx'],L['cy']],sub,[956.0,680.0],[R['cx'],R['cy']]])
center=catmull(cl,False).replace('Z','')
json.dump({'left':L,'right':R,'outline':outline,'center':center,'viewBox':[0,0,1254,1254]},open('scripts/logo_trace.json','w'),indent=1)
print(center); print(len(order), order[0], order[-1])
