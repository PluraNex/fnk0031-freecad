"""Extended kinematic controls and geometric diagnostics. GUI-thread only."""
import math, json, time, csv, itertools
from pathlib import Path
import FreeCAD as App, FreeCADGui as Gui, Part
from PySide import QtCore, QtWidgets
import fnk_motion as base
V=App.Vector
HERE=base.HERE
MODES=['Caminhar','Andar para tras','Lado direito','Lado esquerdo','Girar esquerda','Girar direita','Uma perna','Subir e abaixar','Repouso']
MOVES={'Caminhar':(0,1,0),'Andar para tras':(0,-1,0),'Lado direito':(1,0,0),'Lado esquerdo':(-1,0,0),'Girar esquerda':(0,0,1),'Girar direita':(0,0,-1)}

class Engine(base.Engine):
    def __init__(self,doc):
        super().__init__(doc)
        for typ,name,value in [('App::PropertyFloat','HeightOffset',0),('App::PropertyFloat','Roll',0),('App::PropertyFloat','Pitch',0),('App::PropertyFloat','TurnPerCycle',10)]:
            if name not in self.motion.PropertiesList:self.motion.addProperty(typ,name,'Postura');setattr(self.motion,name,value)
        self.limits={}
        with open(base.ROOT/'firmware-joints.csv',encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):self.limits[(int(r['leg']),r['joint'])]=(float(r['software_min_deg']),float(r['software_max_deg']))
        self.body_rotation=App.Rotation()
        self.mechanics=doc.getObject('Mechanics') or doc.addObject('App::DocumentObjectGroup','Mechanics')
        self.mechanics.Label='Mecanica — eixos, trajetorias e interferencias'
        for name,label in [('JointAxes','Eixos A azul / B verde / C laranja'),('FootPaths','Trajetorias previstas das seis patas'),('CollisionMarks','Volumes de interferencia da pose verificada')]:
            obj=doc.getObject(name) or doc.addObject('App::DocumentObjectGroup',name);obj.Label=label;self.mechanics.addObject(obj)
        for n in range(1,7):
            for joint,color in [('A',(.15,.4,1.)),('B',(.1,.8,.35)),('C',(1.,.5,.08))]:
                obj=self.feature('Axis%d%s'%(n,joint),doc.JointAxes);obj.ViewObject.LineColor=color;obj.ViewObject.LineWidth=3;obj.Visibility=False
            path=self.feature('FootPath%d'%n,doc.FootPaths);path.ViewObject.LineColor=(.15,.6,.95) if n in (1,3,5) else (.85,.25,.65);path.ViewObject.LineWidth=2;path.Visibility=False
        self.axes_visible=False;self.paths_visible=False
    def feature(self,name,parent):
        obj=self.doc.getObject(name) or self.doc.addObject('Part::Feature',name);parent.addObject(obj);return obj
    def planar(self,t,mode):
        dx,dy,turn=MOVES.get(mode,(0,0,0))
        return App.Placement(V(dx*t*self.motion.Stride.Value,dy*t*self.motion.Stride.Value,0),App.Rotation(V(0,0,1),turn*t*self.motion.TurnPerCycle))
    def pose(self,phase,mode):
        planar=self.planar(phase,mode);z=self.height+self.motion.HeightOffset
        if mode=='Subir e abaixar':z+=self.motion.BodyAmplitude.Value*math.sin(2*math.pi*phase)
        tilt=App.Rotation(V(0,1,0),self.motion.Pitch).multiply(App.Rotation(V(1,0,0),self.motion.Roll))
        return App.Placement(planar.Base+V(0,0,z),planar.Rotation.multiply(tilt))
    def world_targets(self,phase,mode):
        targets=[];contact=[]
        for i,ref in enumerate(self.refs['legs']):
            neutral=V(ref['tip'][0],ref['tip'][1],0);p=V(neutral);stance=True
            if mode in MOVES:
                offset=0 if i in (0,2,4) else .5;s=(phase+offset)%1;start=phase-s
                p0=self.planar(start+.3,mode).multVec(neutral)
                if s<.6:p=p0
                else:
                    q=(s-.6)/.4;ease=10*q**3-15*q**4+6*q**5
                    p1=self.planar(start+1.3,mode).multVec(neutral)
                    p=p0+(p1-p0)*ease;p.z=self.motion.Lift.Value*16*q*q*(1-q)*(1-q);stance=False
            elif mode=='Uma perna' and i==0:
                dy,dz,stance=base.gait(phase,self.motion.Stride.Value,self.motion.Lift.Value);p+=V(0,dy,dz)
            targets.append(p);contact.append(stance)
        return targets,contact
    def frame(self,phase,mode='Caminhar'):
        if mode not in MODES:raise ValueError('Movimento desconhecido')
        if not 0<=self.motion.Stride.Value<=45 or not 0<=self.motion.Lift.Value<=25:raise ValueError('Passo ou elevacao fora da faixa')
        if not -12<=self.motion.HeightOffset<=12 or max(abs(self.motion.Roll),abs(self.motion.Pitch))>8 or not 0<=self.motion.TurnPerCycle<=20:raise ValueError('Postura fora da faixa do painel')
        pose=self.pose(phase,mode);inverse=pose.inverse();world,contact=self.world_targets(phase,mode)
        targets=[inverse.multVec(p) for p in world];angles=[]
        for i,(ref,p) in enumerate(zip(self.refs['legs'],targets)):
            ang=base.ik(ref['A'],base.pack(p),self.dims,ref['angles'][0])
            for j,v in zip('ABC',ang):
                lo,hi=self.limits[(i+1,j)];wrapped=v+360*round(((lo+hi)/2-v)/360)
                if not lo-1e-6<=wrapped<=hi+1e-6:raise ValueError('Perna %d, eixo %s: %.1f graus excede o limite do firmware'%(i+1,j,wrapped))
            angles.append(ang)
        self.body_rotation=pose.Rotation
        return pose.Base,angles,targets,contact
    def apply(self,phase,mode='Caminhar',cables=True):
        result=super().apply(phase,mode,cables);self.update_axes();return result
    def update_axes(self):
        pose=self.doc.Robot.Placement
        for i,ref in enumerate(self.refs['legs']):
            leg=self.doc.getObject('Leg%d'%(i+1));a=math.radians(leg.Alpha.Value);normal=V(math.sin(a),-math.cos(a),0)
            for joint,center,direction in [('A',V(*ref['A']),V(0,0,1)),('B',leg.AxisB,normal),('C',leg.AxisC,normal)]:
                obj=self.doc.getObject('Axis%d%s'%(i+1,joint));obj.Visibility=self.axes_visible
                if self.axes_visible:
                    p=pose.multVec(center);d=pose.Rotation.multVec(direction)*10
                    obj.Shape=Part.makePolygon([p-d,p+d]);obj.Label='Perna %d / %s: %.1f graus'%(i+1,joint,getattr(leg,{'A':'Alpha','B':'Beta','C':'Gamma'}[joint]).Value)
    def paths(self,mode,total):
        samples=[self.world_targets(total*k/180,mode)[0] for k in range(181)]
        for i in range(6):
            points=[]
            for row in samples:
                if not points or (row[i]-points[-1]).Length>1e-7:points.append(row[i])
            obj=self.doc.getObject('FootPath%d'%(i+1))
            obj.Shape=Part.makePolygon(points) if len(points)>1 else Part.Vertex(points[0]);obj.Label='Trajetoria prevista — perna %d'%(i+1);obj.Visibility=self.paths_visible

def world_shape(obj):
    parent=obj.getParentGeoFeatureGroup()
    return Part.getShape(obj,mat=parent.getGlobalPlacement().toMatrix() if parent else App.Matrix(),transform=True)

class CollisionScan(QtCore.QObject):
    """Snapshot pose, then one candidate boolean per timer tick. Never runs with playback."""
    def __init__(self,panel):
        super().__init__(panel);self.panel=panel;self.timer=QtCore.QTimer(self);self.timer.setInterval(10);self.timer.timeout.connect(self.step);self.records=[];self.completed=False
    def clear(self):
        self.timer.stop();self.completed=False
        for obj in list(self.panel.engine.doc.CollisionMarks.Group):self.panel.engine.doc.removeObject(obj.Name)
    def start(self):
        self.panel.stop()
        if not self.panel.draw():return
        self.clear();eng=self.panel.engine;doc=eng.doc
        names=['Installed_AC01','Installed_AC02']+['L%d_%s'%(n,s) for n in range(1,7) for s in ['SupportA','SupportB','Link','Foot','ServoA','ServoB','ServoC']]
        self.shapes={name:world_shape(doc.getObject(name)) for name in names}
        self.pairs=[];self.tested=0;self.records=[];self.scope_pairs=0
        known={frozenset(('L%d_%s'%(n,a),'L%d_%s'%(n,b))) for n in range(1,7) for a,b in [('SupportA','ServoA'),('SupportB','ServoB'),('Foot','ServoC')]}
        for a,b in itertools.combinations(names,2):
            estimated=frozenset((a,b)) in known
            if doc.getObject(a).getParentGeoFeatureGroup()==doc.getObject(b).getParentGeoFeatureGroup() and not estimated:continue
            self.scope_pairs+=1
            if self.shapes[a].BoundBox.intersect(self.shapes[b].BoundBox):self.pairs.append((a,b,estimated))
        self.pose={'phase':eng.last['phase'],'mode':eng.last['mode'],'parameters':{n:getattr(eng.motion,n) for n in ['HeightOffset','Roll','Pitch','TurnPerCycle']},'stride_mm':eng.motion.Stride.Value,'lift_mm':eng.motion.Lift.Value}
        self.panel.collision_status.setText('Verificando %d pares candidatos...'%len(self.pairs));self.timer.start()
    def step(self):
        if self.tested>=len(self.pairs):self.finish();return
        a,b,estimated=self.pairs[self.tested];self.tested+=1
        try:
            shape=self.shapes[a].common(self.shapes[b]);volume=shape.Volume
            if volume>1e-5:
                kind='interface_provisoria' if estimated else 'possivel_colisao'
                self.records.append({'a':a,'b':b,'volume_mm3':volume,'type':kind})
                obj=self.panel.engine.feature('Interference%03d'%len(self.records),self.panel.engine.doc.CollisionMarks);obj.Shape=shape;obj.Label='%s / %s — %.3f mm3'%(a,b,volume);obj.ViewObject.ShapeColor=(1.,.6,.05) if estimated else (1.,.05,.12);obj.ViewObject.LineColor=obj.ViewObject.ShapeColor;obj.ViewObject.DisplayMode='Flat Lines';obj.ViewObject.LineWidth=3
        except Exception as exc:
            self.records.append({'a':a,'b':b,'error':str(exc),'type':'falha_de_verificacao'})
        self.panel.collision_status.setText('Verificando %d / %d pares candidatos...'%(self.tested,len(self.pairs)))
    def finish(self):
        self.timer.stop();self.completed=True
        # Outline involved components: intersection volumes can lie inside opaque parts.
        colors={}
        for record in self.records:
            if 'volume_mm3' not in record:continue
            for name in [record['a'],record['b']]:
                if name not in colors or record['type']=='possivel_colisao':colors[name]=record['type']
        for name,kind in colors.items():
            bb=self.shapes[name].BoundBox;pad=.8
            obj=self.panel.engine.feature('Warning_'+name,self.panel.engine.doc.CollisionMarks)
            obj.Shape=Part.makeBox(bb.XLength+2*pad,bb.YLength+2*pad,bb.ZLength+2*pad,V(bb.XMin-pad,bb.YMin-pad,bb.ZMin-pad))
            obj.Label='Destaque de componente — '+name;obj.ViewObject.DisplayMode='Wireframe';obj.ViewObject.LineWidth=2;obj.ViewObject.LineColor=(1.,.6,.05) if kind=='interface_provisoria' else (1.,.05,.12)
        result={'pose':self.pose,'scoped_pairs':self.scope_pairs,'bbox_candidates':len(self.pairs),'records':self.records,'scope':'44 componentes: chapas do chassi e suportes/ligacoes/pes/servos das seis pernas. Pares rigidamente ligados excluidos, salvo 18 interfaces provisorias conhecidas. Cabos, fixadores e eletronica nao incluidos. Apenas a pose indicada, nao todo o movimento.'}
        (HERE/'ultima_verificacao_colisoes.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
        possible=sum(r['type']=='possivel_colisao' for r in self.records);known=sum(r['type']=='interface_provisoria' for r in self.records);errors=sum(r['type']=='falha_de_verificacao' for r in self.records)
        self.panel.collision_status.setText('Pose verificada: %d possiveis colisoes (vermelho), %d interfaces provisorias (laranja), %d falhas.\nDetalhes abaixo; cabos, fixadores e eletronica fora desta verificacao.'%(possible,known,errors))
        self.panel.collision_list.setPlainText('\n'.join('%s ↔ %s: %s'%(r['a'],r['b'],r.get('error','%.3f mm3 — %s'%(r.get('volume_mm3',0),r['type']))) for r in self.records) or 'Nenhuma intersecao volumetrica nos pares verificados.')
        self.panel.engine.doc.recompute()

class Panel(QtWidgets.QDockWidget):
    def __init__(self,engine):
        super().__init__('FNK0031 | Controle e mecanica');self.setObjectName('FNK0031MotionPanel');self.engine=engine;self.phase=0;self.running=False;self.last_tick=0
        content=QtWidgets.QWidget();layout=QtWidgets.QVBoxLayout(content);scroll=QtWidgets.QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(content);self.setWidget(scroll)
        note=QtWidgets.QLabel('Simulacao cinematica • medidas provisorias');note.setWordWrap(True);layout.addWidget(note)
        self.mode=QtWidgets.QComboBox();self.mode.addItems(MODES);layout.addWidget(self.mode)
        form=QtWidgets.QFormLayout();layout.addLayout(form)
        self.controls={}
        for name,label,lo,hi,value,suffix in [('Stride','Passo',0,45,engine.motion.Stride.Value,' mm'),('Lift','Elevacao da pata',0,25,engine.motion.Lift.Value,' mm'),('Period','Tempo por ciclo',1,20,engine.motion.Period,' s'),('TurnPerCycle','Giro por ciclo',0,20,engine.motion.TurnPerCycle,' °'),('HeightOffset','Ajuste de altura',-12,12,engine.motion.HeightOffset,' mm'),('Roll','Inclinacao lateral (X)',-8,8,engine.motion.Roll,' °'),('Pitch','Inclinacao frontal (Y)',-8,8,engine.motion.Pitch,' °')]:
            control=QtWidgets.QDoubleSpinBox();control.setRange(lo,hi);control.setValue(value);control.setSuffix(suffix);control.setKeyboardTracking(False);form.addRow(label,control);self.controls[name]=control
        self.period=self.controls['Period'];self.stride=self.controls['Stride'];self.lift=self.controls['Lift']
        self.slider=QtWidgets.QSlider(QtCore.Qt.Horizontal);layout.addWidget(self.slider)
        row=QtWidgets.QHBoxLayout();layout.addLayout(row)
        for name,title,slot in [('play','Iniciar',self.start),('pause','Pausar',self.stop),('reset','Reiniciar',self.restart)]:
            button=QtWidgets.QPushButton(title);setattr(self,name,button);row.addWidget(button);button.clicked.connect(slot)
        neutral=QtWidgets.QPushButton('Zerar altura e inclinacoes');layout.addWidget(neutral);neutral.clicked.connect(self.neutral)
        self.status=QtWidgets.QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        row=QtWidgets.QHBoxLayout();layout.addLayout(row)
        self.axes=QtWidgets.QCheckBox('Eixos');self.paths=QtWidgets.QCheckBox('Trajetorias');self.angles=QtWidgets.QCheckBox('Angulos');self.angles.setChecked(True)
        for box in [self.axes,self.paths,self.angles]:row.addWidget(box)
        self.table=QtWidgets.QTableWidget(6,5);self.table.setHorizontalHeaderLabels(['Perna','A °','B °','C °','Apoio']);self.table.verticalHeader().hide();self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers);self.table.setMaximumHeight(190);self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch);layout.addWidget(self.table)
        self.scan_button=QtWidgets.QPushButton('Verificar colisoes nesta pose');layout.addWidget(self.scan_button)
        self.collision_status=QtWidgets.QLabel('Colisoes ainda nao verificadas nesta pose.');self.collision_status.setWordWrap(True);layout.addWidget(self.collision_status)
        self.collision_list=QtWidgets.QPlainTextEdit();self.collision_list.setReadOnly(True);self.collision_list.setMaximumHeight(110);layout.addWidget(self.collision_list)
        save=QtWidgets.QPushButton('Salvar pose no CAD');layout.addWidget(save);save.clicked.connect(self.save);layout.addStretch()
        self.scan=CollisionScan(self);self.scan_button.clicked.connect(self.scan.start)
        self.timer=QtCore.QTimer(self);self.timer.setInterval(50);self.timer.timeout.connect(self.tick)
        self.mode.currentTextChanged.connect(self.restart);self.slider.sliderPressed.connect(self.stop);self.slider.valueChanged.connect(self.scrub)
        for control in self.controls.values():control.valueChanged.connect(self.settings)
        self.axes.toggled.connect(self.visuals);self.paths.toggled.connect(self.visuals);self.angles.toggled.connect(self.table.setVisible)
        self.mode.setCurrentText('Repouso');self.restart()
    def total(self):return 3 if self.mode.currentText() in MOVES else 1
    def settings(self,*args):
        self.stop()
        for name,control in self.controls.items():setattr(self.engine.motion,name,control.value())
        self.engine.paths(self.mode.currentText(),self.total());self.draw()
    def neutral(self):
        for name in ['HeightOffset','Roll','Pitch']:
            self.controls[name].blockSignals(True);self.controls[name].setValue(0);self.controls[name].blockSignals(False)
        self.settings()
    def visuals(self,*args):
        self.engine.axes_visible=self.axes.isChecked();self.engine.paths_visible=self.paths.isChecked();self.engine.update_axes();self.engine.paths(self.mode.currentText(),self.total());self.engine.doc.recompute()
    def draw(self):
        self.scan.clear();self.collision_status.setText('Colisoes ainda nao verificadas nesta pose.');self.collision_list.clear()
        try:
            result=self.engine.apply(self.phase,self.mode.currentText());self.status.setText('Ciclo %.2f / %d | %d patas em apoio | Altura do referencial: %.1f mm'%(self.phase,self.total(),sum(result['contact']),result['body'][2]))
            for i,angles in enumerate(result['angles']):
                row=[str(i+1)]+['%.1f'%((v+180)%360-180 if j==0 else v) for j,v in enumerate(angles)]+['Sim' if result['contact'][i] else 'Nao']
                for j,value in enumerate(row):self.table.setItem(i,j,QtWidgets.QTableWidgetItem(value))
            self.slider.blockSignals(True);self.slider.setValue(round(self.phase*1000));self.slider.blockSignals(False)
            return True
        except Exception as exc:self.stop();self.status.setText('Pose nao aplicada: '+str(exc));return False
    def start(self):
        self.scan.clear()
        if self.phase>=self.total():self.phase=0
        if not self.draw():return
        self.running=True;self.last_tick=time.monotonic();self.timer.start()
    def stop(self):self.running=False;self.timer.stop()
    def restart(self,*args):
        self.stop();self.phase=0;self.slider.setMaximum(self.total()*1000);self.engine.paths(self.mode.currentText(),self.total());self.draw()
    def scrub(self,value):self.stop();self.phase=value/1000;self.draw()
    def tick(self):
        now=time.monotonic();dt=now-self.last_tick;self.last_tick=now;self.phase=min(self.total(),self.phase+min(dt,.2)/self.period.value());self.draw()
        if self.phase>=self.total():self.stop()
    def save(self):
        self.stop()
        try:
            self.engine.frame(self.phase,self.mode.currentText());self.engine.save();self.status.setText('Pose e visualizacoes salvas no CAD.')
        except Exception as exc:self.status.setText('Nao salvo: '+str(exc))
    def closeEvent(self,event):self.stop();self.scan.timer.stop();super().closeEvent(event)

def show_panel():
    old=getattr(App,'_fnk_motion_panel',None)
    if old is not None:old.stop();old.close();old.deleteLater()
    doc=base.owned_doc();App.setActiveDocument(doc.Name);panel=Panel(Engine(doc));Gui.getMainWindow().addDockWidget(QtCore.Qt.RightDockWidgetArea,panel);panel.show();App._fnk_motion_panel=panel
    return panel
