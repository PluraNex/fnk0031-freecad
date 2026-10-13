import Part,json,itertools
def world_shape(obj):
    parent=obj.getParentGeoFeatureGroup()
    # Pass ancestor transform only; getShape includes the object's own placement.
    return Part.getShape(obj,mat=parent.getGlobalPlacement().toMatrix(),transform=True)
def interference_samples():
    records=[];feet=[]
    pairs=[('L1_Link','L1_ServoA'),('L1_Link','L1_SupportB'),('L1_Link','L1_ServoB'),('L1_Link','L1_ServoC'),('L1_Foot','L1_Link'),('L1_SupportA','L1_ServoA'),('L1_SupportB','L1_ServoB'),('L1_Foot','L1_ServoC')]
    outer=['L'+str(n)+'_'+s for n in range(1,7) for s in ['Link','Foot','ServoC']]
    cross_pairs=[(a,b) for a,b in itertools.combinations(outer,2) if a.split('_')[0]!=b.split('_')[0]]
    for phase in [0,.2,.4,.6,.8,1]:
        eng.apply(phase,'Caminhar')
        names=set(sum(([a,b] for a,b in pairs+cross_pairs),[]));shapes={name:world_shape(eng.doc.getObject(name)) for name in names}
        for a,b in pairs+cross_pairs:
            sa,sb=shapes[a],shapes[b]
            volume=sa.common(sb).Volume if sa.BoundBox.intersect(sb.BoundBox) else 0
            if volume>1e-6:records.append({'phase':phase,'a':a,'b':b,'intersection_mm3':volume,'type':'between_legs' if (a,b) in cross_pairs else 'interface_or_same_leg'})
        for n in range(1,7):feet.append({'phase':phase,'leg':n,'geometry_bbox_min_z_mm':shapes['L'+str(n)+'_Foot'].BoundBox.ZMin})
    result={'phases':6,'pairs_per_phase':len(pairs+cross_pairs),'intersections':records,'foot_bbox_samples':feet,'note':'Sampling only; estimated commercial interfaces. Floor test is geometric bbox, not physical contact. No cable collision analysis.'}
    json.dump(result,open(fnk_motion.HERE/'interferencias_movimento.json','w'),indent=2)
    print('Pairs',len(pairs+cross_pairs),'intersections',len(records),'between legs',sum(x['type']=='between_legs' for x in records),'min foot Z',min(x['geometry_bbox_min_z_mm'] for x in feet))
    eng.apply(0,'Repouso')
