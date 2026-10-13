"""FreeCAD GUI-thread kinematic player. No hardware commands, OBS or external proxies.
Use show_panel(); tests may call Engine.apply() directly. All units mm/degrees.
"""
import math, json, time, os
from pathlib import Path
import FreeCAD as App, FreeCADGui as Gui, Part
from PySide import QtCore, QtWidgets
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
CAD=ROOT/'FNK0031_V3_Movimento.FCStd'
V=App.Vector
def repair_frame(doc):
    """Restore nominal frame datums; earlier explosion generator mutated live placements."""
    t=doc.Dimensions.AcrylicThickness.Value;gap=doc.Dimensions.ChassisGap.Value
    r=App.Rotation(V(0,0,1),90)
    for ident,z,cx,cy in [('AC02',0,59.4,58.4),('AC01',gap+t,57.4,56.4)]:
        doc.getObject('Installed_'+ident).LinkPlacement=App.Placement(V(0,0,z)-r.multVec(V(cx,cy,0)),r)
    for k,geo in enumerate(doc.AC02_Profile.Geometry):
        obj=doc.getObject('BaseHornBolt'+str(k))
        if obj:obj.LinkPlacement=doc.Installed_AC02.LinkPlacement.multiply(App.Placement(V(geo.Center.x,geo.Center.y,t),App.Rotation()))
    doc.recompute()
def pack(v):return [v.x,v.y,v.z]
def fk(origin,angles,dims):
    a,b,g=map(math.radians,angles);c,d,e,f=dims
    u=d+e*math.sin(b)+f*math.sin(g-b)
    return (origin[0]+u*math.cos(a),origin[1]+u*math.sin(a),c+e*math.cos(b)-f*math.cos(g-b))
def ik(origin,target,dims,alpha_reference):
    c,d,e,f=dims;dx=target[0]-origin[0];dy=target[1]-origin[1]
    u=math.hypot(dx,dy)-d;v=target[2]-c
    cosg=(e*e+f*f-u*u-v*v)/(2*e*f)
    if not -1-1e-9<=cosg<=1+1e-9:raise ValueError('Alvo fora do alcance da perna')
    g=math.acos(max(-1,min(1,cosg)))
    b=math.atan2(u,v)-math.atan2(f*math.sin(g),e-f*math.cos(g))
    a=math.degrees(math.atan2(dy,dx));a+=360*round((alpha_reference-a)/360)
    return (a,math.degrees(b),math.degrees(g))
def gait(phase,stride,lift,duty=.6):
    s=phase%1
    if s<duty:return (stride*(duty/2-s),0,True)
    q=(s-duty)/(1-duty);start=-stride*duty/2;end=-start;m=-stride*(1-duty)
    y=(2*q**3-3*q*q+1)*start+(q**3-2*q*q+q)*m+(-2*q**3+3*q*q)*end+(q**3-q*q)*m
    return y,lift*16*q*q*(1-q)*(1-q),False
def transform(new_point,rotation,old_point):
    return App.Placement(new_point-rotation.multVec(old_point),rotation)
def owned_doc():
    for doc in App.listDocuments().values():
        if Path(doc.FileName)==CAD:return doc
    return App.openDocument(str(CAD))
class Engine:
    def __init__(self,doc):
        self.doc=doc;self.cfg=doc.Dimensions
        repair_frame(doc)
        self.motion=doc.getObject('Motion') or doc.addObject('App::FeaturePython','Motion')
        for typ,name,default in [('App::PropertyLength','Stride',20),('App::PropertyLength','Lift',10),('App::PropertyFloat','Period',4),('App::PropertyLength','BodyAmplitude',8),('App::PropertyInteger','Cycles',3),('App::PropertyFloat','Phase',0),('App::PropertyString','Mode','Caminhar'),('App::PropertyString','Reference',''),('App::PropertyString','Status','Cinematica demonstrativa; interfaces fisicas provisorias')]:
            if name not in self.motion.PropertiesList:self.motion.addProperty(typ,name,'Movimento');setattr(self.motion,name,default)
        self.motion.Label='Movimento — controles da demonstracao'
        if not self.motion.Reference:self.setup()
        self.refs=json.loads(self.motion.Reference)
        self.dims=tuple(getattr(self.cfg,'Length'+n).Value for n in 'CDEF')
        self.height=-self.refs['legs'][0]['tip'][2]
        self.last=None
    def setup(self):
        refs={'legs':[]}
        for n in range(1,7):
            leg=self.doc.getObject('Leg'+str(n))
            refs['legs'].append({'A':pack(leg.AxisA),'B':pack(leg.AxisB),'C':pack(leg.AxisC),'tip':pack(leg.FootTarget),'angles':[leg.Alpha.Value,leg.Beta.Value,leg.Gamma.Value]})
            members=list(leg.Group)
            groups={}
            for key,label in [('Coxa','Conjunto A — suporte e servo B'),('Upper','Ligacao e bracos B/C'),('Terminal','Terminal e corpo do servo C')]:
                obj=self.doc.addObject('App::Part','MotionL'+str(n)+key);obj.Label=label;leg.addObject(obj);groups[key]=obj
            for obj in members:
                suffix=obj.Name.split('_',1)[-1]
                if suffix in ('HornA','AxisBoltA'):continue # anchored to the fixed chassis
                if suffix.startswith('Foot') or suffix=='ServoC':key='Terminal'
                elif suffix in ('Link','HornB','HornC','AxisBoltB','AxisBoltC') or '_HornBolt' in suffix:key='Upper'
                else:key='Coxa'
                groups[key].addObject(obj)
        self.motion.Reference=json.dumps(refs)
        cables=self.doc.addObject('App::Part','MotionCables');cables.Label='Cabos esquematicos durante o movimento';self.doc.Robot.addObject(cables)
        for n in range(1,7):
            for c,color in enumerate([(0.85,.1,.08),(.1,.1,.1),(.85,.65,.05)]):
                line=self.doc.addObject('Part::Feature','MovingCable'+str(n)+'_'+str(c));cables.addObject(line);line.ViewObject.LineColor=color;line.ViewObject.LineWidth=2
        floor=self.doc.addObject('Part::Feature','MotionFloor');floor.Label='Plano de apoio de referencia — sem fisica de contato'
        floor.Shape=Part.makePlane(380,460,V(-190,-190,0));floor.ViewObject.ShapeColor=(.88,.90,.92);floor.ViewObject.Transparency=75
        self.doc.Wiring.Visibility=False;self.doc.Exploded.Visibility=False;self.doc.Remote.Visibility=False;self.doc.Library.Visibility=False
        self.doc.recompute()
    def frame(self,phase,mode='Caminhar'):
        stride=self.motion.Stride.Value;lift=self.motion.Lift.Value
        if not 0<=stride<=45 or not 0<=lift<=25:raise ValueError('Use passo de 0 a 45 mm e elevacao de 0 a 25 mm')
        body=V(0,phase*stride if mode=='Caminhar' else 0,self.height)
        if mode=='Subir e abaixar':body.z+=self.motion.BodyAmplitude.Value*math.sin(2*math.pi*phase)
        targets=[];angles=[];contact=[]
        for i,ref in enumerate(self.refs['legs']):
            p=V(*ref['tip']);stance=True
            if mode=='Caminhar':
                dy,dz,stance=gait(phase+(0 if i in (0,2,4) else .5),stride,lift)
                p.y+=dy;p.z+=dz
            elif mode=='Uma perna' and i==0:
                # Single closed foot cycle; other legs stay at rest.
                dy,dz,stance=gait(phase,stride,lift);p.y+=dy;p.z+=dz
            elif mode=='Subir e abaixar':p.z-=body.z-self.height
            a=ik(ref['A'],pack(p),self.dims,ref['angles'][0]);angles.append(a);targets.append(p);contact.append(stance)
        return body,angles,targets,contact
    def apply(self,phase,mode='Caminhar',cables=True):
        body,angles,targets,contact=self.frame(phase,mode)
        rotation=getattr(self,'body_rotation',App.Rotation())
        self.doc.Robot.Placement=App.Placement(body,rotation)
        for i,(ref,ang) in enumerate(zip(self.refs['legs'],angles)):
            n=i+1;A,B0,C0=map(lambda x:V(*x),(ref['A'],ref['B'],ref['C']))
            a,b,g=ang;a0,b0,g0=ref['angles']
            qa=App.Rotation(V(0,0,1),a-a0)
            radial=V(math.cos(math.radians(a0)),math.sin(math.radians(a0)),0);normal=radial.cross(V(0,0,1))
            qb=App.Rotation(normal,-(b-b0));qt=App.Rotation(normal,(g-b)-(g0-b0))
            B=A+qa.multVec(B0-A);C=B+qa.multVec(qb.multVec(C0-B0))
            self.doc.getObject('MotionL'+str(n)+'Coxa').Placement=transform(A,qa,A)
            self.doc.getObject('MotionL'+str(n)+'Upper').Placement=transform(B,qa.multiply(qb),B0)
            self.doc.getObject('MotionL'+str(n)+'Terminal').Placement=transform(C,qa.multiply(qt),C0)
            leg=self.doc.getObject('Leg'+str(n));leg.Alpha=a;leg.Beta=b;leg.Gamma=g;leg.AxisB=B;leg.AxisC=C;leg.FootTarget=targets[i]
            if cables:
                for channel,off in enumerate([-1.3,0,1.3]):
                    points=[C+V(off,0,-16),B+V(off,0,-21),A+V(off,0,-14),V(math.copysign(20,A.x)+off,A.y*.45,self.cfg.PCBHeight.Value+5)]
                    self.doc.getObject('MovingCable'+str(n)+'_'+str(channel)).Shape=Part.makePolygon(points)
        self.motion.Phase=phase;self.motion.Mode=mode
        self.doc.recompute()
        self.last={'phase':phase,'mode':mode,'body':pack(body),'angles':angles,'targets':[pack(rotation.multVec(p)+body) for p in targets],'contact':contact}
        return self.last
    def save(self):
        self.doc.recompute();self.doc.saveAs(str(CAD))
class Panel(QtWidgets.QDockWidget):
    def __init__(self,engine):
        super().__init__('FNK0031 | Movimento');self.setObjectName('FNK0031MotionPanel');self.engine=engine;self.phase=0;self.running=False;self.last_tick=0
        w=QtWidgets.QWidget();layout=QtWidgets.QVBoxLayout(w);self.setWidget(w)
        note=QtWidgets.QLabel('Cinematica demonstrativa\nMedidas fisicas ainda provisorias');layout.addWidget(note)
        self.mode=QtWidgets.QComboBox();self.mode.addItems(['Caminhar','Uma perna','Subir e abaixar','Repouso']);layout.addWidget(self.mode)
        form=QtWidgets.QFormLayout();layout.addLayout(form)
        self.stride=QtWidgets.QDoubleSpinBox();self.stride.setRange(0,45);self.stride.setValue(engine.motion.Stride.Value);self.stride.setSuffix(' mm');form.addRow('Passo',self.stride)
        self.lift=QtWidgets.QDoubleSpinBox();self.lift.setRange(0,25);self.lift.setValue(engine.motion.Lift.Value);self.lift.setSuffix(' mm');form.addRow('Levantar pata',self.lift)
        self.period=QtWidgets.QDoubleSpinBox();self.period.setRange(1,20);self.period.setValue(engine.motion.Period);self.period.setSuffix(' s');form.addRow('Tempo por ciclo',self.period)
        self.slider=QtWidgets.QSlider(QtCore.Qt.Horizontal);self.slider.setRange(0,3000);layout.addWidget(self.slider)
        row=QtWidgets.QHBoxLayout();layout.addLayout(row)
        self.play=QtWidgets.QPushButton('Iniciar');self.pause=QtWidgets.QPushButton('Pausar');self.reset=QtWidgets.QPushButton('Reiniciar')
        for b in [self.play,self.pause,self.reset]:row.addWidget(b)
        self.status=QtWidgets.QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        save=QtWidgets.QPushButton('Salvar pose no CAD');layout.addWidget(save);save.clicked.connect(self.save)
        layout.addStretch()
        self.timer=QtCore.QTimer(self);self.timer.setInterval(50);self.timer.timeout.connect(self.tick)
        self.play.clicked.connect(self.start);self.pause.clicked.connect(self.stop);self.reset.clicked.connect(self.restart)
        self.mode.currentTextChanged.connect(self.restart);self.slider.sliderPressed.connect(self.stop);self.slider.valueChanged.connect(self.scrub)
        for control in [self.stride,self.lift,self.period]:control.valueChanged.connect(self.settings)
        self.restart()
    def total(self):return 3 if self.mode.currentText()=='Caminhar' else 1
    def settings(self,*args):
        self.engine.motion.Stride=self.stride.value();self.engine.motion.Lift=self.lift.value();self.engine.motion.Period=self.period.value();self.draw()
    def draw(self):
        try:
            result=self.engine.apply(self.phase,self.mode.currentText());self.status.setText('Ciclo %.2f / %d | Patas apoiadas: %d'%(self.phase,self.total(),sum(result['contact'])))
            self.slider.blockSignals(True);self.slider.setValue(round(self.phase*1000));self.slider.blockSignals(False)
        except Exception as exc:self.stop();self.status.setText('Nao aplicado: '+str(exc))
    def start(self):
        if self.phase>=self.total():self.phase=0
        self.running=True;self.last_tick=time.monotonic();self.timer.start()
    def stop(self):self.running=False;self.timer.stop()
    def restart(self,*args):
        self.stop();self.phase=0;self.slider.setMaximum(self.total()*1000);self.draw()
    def scrub(self,value):
        self.phase=value/1000;self.draw()
    def tick(self):
        now=time.monotonic();dt=now-self.last_tick;self.last_tick=now
        self.phase=min(self.total(),self.phase+min(dt,.2)/self.period.value());self.draw()
        if self.phase>=self.total():self.stop()
    def save(self):self.stop();self.engine.save();self.status.setText('Pose salva no arquivo de movimento.')
    def closeEvent(self,event):self.stop();super().closeEvent(event)
def show_panel():
    old=getattr(App,'_fnk_motion_panel',None)
    if old is not None:old.stop();old.close();old.deleteLater()
    doc=owned_doc();App.setActiveDocument(doc.Name);engine=Engine(doc)
    panel=Panel(engine);Gui.getMainWindow().addDockWidget(QtCore.Qt.RightDockWidgetArea,panel);panel.show()
    App._fnk_motion_panel=panel
    Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
    return panel
