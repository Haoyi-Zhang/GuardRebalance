"""Vector drawing primitives; copied into each independent project generator."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix',
                     'font.size':9, 'pdf.fonttype':42, 'ps.fonttype':42,
                     'text.usetex':False, 'axes.unicode_minus':False})
CM = 1 / 2.54

class Drawing:
    def __init__(self, bounds):
        x0,y0,x1,y1 = bounds
        self.fig = plt.figure(figsize=((x1-x0)*CM,(y1-y0)*CM))
        self.ax = self.fig.add_axes([0,0,1,1], xlim=(x0,x1), ylim=(y0,y1))
        self.ax.set_aspect('equal'); self.ax.axis('off')
        self.nodes = {}
        self.labels = []

    def text(self,x,y,label,size=9,ha='center',va='center'):
        artist=self.ax.text(x,y,label,fontsize=size,ha=ha,va=va,
                            linespacing=1.15,clip_on=False,zorder=4)
        self.labels.append([artist,None])
        return artist

    def box(self,name,x,y,w,h,label,dashed=False,shape='rect',size=9):
        style = {'edgecolor':'black','facecolor':'white','linewidth':.55,
                 'linestyle':(0,(4,3)) if dashed else 'solid', 'zorder':2}
        if shape == 'diamond':
            obj = Polygon([(x-w/2,y),(x,y+h/2),(x+w/2,y),(x,y-h/2)],**style)
        elif shape == 'circle': obj = Circle((x,y),w/2,**style)
        else: obj = Rectangle((x-w/2,y-h/2),w,h,**style)
        self.ax.add_patch(obj); self.text(x,y,label,size)
        self.labels[-1][1]=(x-w/2,y-h/2,x+w/2,y+h/2)
        self.nodes[name] = (x,y,w,h,shape)

    def point(self,name,side):
        x,y,w,h,_ = self.nodes[name]
        return {'n':(x,y+h/2),'s':(x,y-h/2),'e':(x+w/2,y),
                'w':(x-w/2,y),'nw':(x-w/2,y+h/2),
                'ne':(x+w/2,y+h/2),'c':(x,y)}[side]

    def line(self,points,dashed=False):
        xs,ys=zip(*points)
        self.ax.plot(xs,ys,color='black',linewidth=.55,
                     linestyle=(0,(4,3)) if dashed else 'solid',zorder=1)

    def arrow(self,p,q,dashed=False,via=()):
        points=[p,*via,q]
        if via:self.line(points[:-1],dashed)
        self.ax.add_patch(FancyArrowPatch(points[-2],points[-1],
                         arrowstyle='-|>',mutation_scale=7.5,linewidth=.55,
                         color='black',shrinkA=0,shrinkB=0,
                         linestyle=(0,(4,3)) if dashed else 'solid',zorder=1))

    def edge(self,a,b,sa='s',sb='n',**kwargs):
        self.arrow(self.point(a,sa),self.point(b,sb),**kwargs)

    def frame(self,x,y,w,h):
        self.ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='black',
                                   linewidth=.55,linestyle=(0,(4,3)),zorder=0))

    def save(self,out,name):
        # Fixed physical canvas: do not enlarge or rasterize the scientific figure.
        self.fig.canvas.draw()
        renderer=self.fig.canvas.get_renderer()
        x0,x1=self.ax.get_xlim();y0,y1=self.ax.get_ylim()
        for artist,node in self.labels:
            b=artist.get_window_extent(renderer).transformed(self.ax.transData.inverted())
            if b.x0<x0-.02 or b.x1>x1+.02 or b.y0<y0-.02 or b.y1>y1+.02:
                raise ValueError(name+': clipped label '+repr(artist.get_text()))
            if node and (b.x0<node[0]-.02 or b.x1>node[2]+.02 or b.y0<node[1]-.02 or b.y1>node[3]+.02):
                raise ValueError(name+': label exceeds node '+repr(artist.get_text()))
        self.fig.savefig(out/(name+'.pdf'),format='pdf',
                         metadata={'Creator':'Python Matplotlib','Producer':None,
                                   'CreationDate':None,'ModDate':None})
        plt.close(self.fig)

NAMES=('fault-frontier','checker-pipeline')
def draw_all(out):
    out.mkdir(parents=True,exist_ok=True)
    d=Drawing((-.1,-1.9,11.2,3.05))
    for name,x,label in [('a',1.5,r'$a$'+'\n'+r'$\mathsf{fault}(\kappa)$'),('b',5.4,r'$b$'+'\n'+r'$\mathsf{fault}(\kappa)$'),('z',9.3,r'$z$'+'\n'+r'$\mathsf{emit}(z,v)$')]:d.box(name,x,2,2.2,1,label)
    d.text(3.45,.25,r'$\vee$');d.line([d.point('a','s'),(3.15,.5)],dashed=True);d.line([d.point('b','s'),(3.75,.5)],dashed=True)
    d.arrow((3.8,.25),(8.2,1.5));d.text(6.9,.05,'one predecessor suffices',size=8.5)
    d.text(5.4,-1.15,r'Safe: $abz,azb,baz,bza$.   Unsafe: $zab,zba$.');d.save(out,'fault-frontier')
    d=Drawing((-.1,-.8,10.7,3.55))
    for name,x,y,label in [('model',1.6,2.7,'finite model\nsource rows'),('summary',5.3,2.7,'prefixes, faults,\ngood sets, barriers'),('search',9,2.7,'exact leaf search\nand tree DP'),('object',9,0,'canonical object\nand certificate'),('checker',5.3,0,'separate decode\nand frontier replay'),('verdict',1.6,0,'accept / reject\nactual budget')]:d.box(name,x,y,2.9,1,label)
    d.edge('model','summary','e','w');d.edge('summary','search','e','w');d.edge('search','object','s','n');d.edge('object','checker','w','e');d.edge('checker','verdict','w','e')
    d.arrow(d.point('model','s'),d.point('checker','n'),via=[(1.6,1.4),(5.3,1.4)]);d.save(out,'checker-pipeline')

def main():
    import tempfile
    ap=argparse.ArgumentParser(description='Direct Python vector drawings of the manuscript relationships.')
    ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'figures');ap.add_argument('--check',action='store_true');a=ap.parse_args()
    if a.check:
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);draw_all(out)
            for name in NAMES:
                p=a.output/(name+'.pdf')
                if not p.is_file() or p.read_bytes()!=(out/(name+'.pdf')).read_bytes():raise SystemExit('Missing/stale schematic: '+name)
        print('All schematics reproduce byte-for-byte.')
    else:draw_all(a.output)
if __name__=='__main__':main()
