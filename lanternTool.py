import maya.cmds as cmds
import math
import random

lanternTool = cmds.window(title='Floating Lantern Editor', width=500, height=500)
cmds.columnLayout(adj=True)

cmds.separator(h=10)
cmds.text("Build your base lantern.")
cmds.separator(h=10)

radius = cmds.floatSliderGrp(l='Radius', v=1, min=0, field=True)
height = cmds.floatSliderGrp(l='Height', v=2, min=0, field=True)
baseColor = cmds.colorSliderGrp(l='Color', rgb=[0.9,0.6,0.3])

cmds.separator(h=10)
cmds.text("Build your field.")
cmds.separator(h=10)

xCenter = cmds.floatSliderGrp(l='Center of field (x)', min=0, field=True)
zCenter = cmds.floatSliderGrp(l='Center of field (z)', min=0, field=True)
yBottom = cmds.floatSliderGrp(l='Bottom of field (y)', min=0, field=True)
yApex = cmds.floatSliderGrp(l='Top of field (y)', v=40, min=0, field=True)


cmds.separator(h=10)
cmds.text("Release the lanterns.")
cmds.separator(h=10)

rowcol = cmds.intSliderGrp(l='Rows and columns', v=10, min=0, field=True)

r = cmds.floatSliderGrp(radius, q=True, value=True)
a = cmds.floatSliderGrp(yApex, q=True, value=True)
dist = cmds.floatSliderGrp(l='Distance between lanterns', v=5, min=1.5*r+a/10, field=True) # min distance between lantern ensures no collisions upon floating

frames = cmds.intSliderGrp(l='Number of frames', v=400, min=0, max=1000, field=True)

cmds.separator(h=10)
cmds.button(l="Display", c='floatingLanterns()')
cmds.button(l="Render", c='rend()')

cmds.showWindow(lanternTool)


def floatingLanterns():

    h = cmds.floatSliderGrp(height, q=True, value=True) # radius of lantern
    r = cmds.floatSliderGrp(radius, q=True, value=True) # height of lantern
    x = cmds.floatSliderGrp(xCenter, q=True, value=True) # center of field
    y = cmds.floatSliderGrp(yBottom, q=True, value=True) # bottom of field
    z = cmds.floatSliderGrp(zCenter, q=True, value=True) # center of field
    a = cmds.floatSliderGrp(yApex, q=True, value=True) # highest floating height
    n = cmds.intSliderGrp(rowcol, q=True, value=True) # number of rows/columns of lanterns
    m = cmds.floatSliderGrp(dist, q=True, value=True) # initial distance between vertices of cylinders
    f = cmds.intSliderGrp(frames, q=True, value=True) # number of frames in animation
    bc = cmds.colorSliderGrp(baseColor, q=True, rgb=True) # base color of lanterns

    random.seed(12345)
    cmds.select(all=True)
    cmds.delete()
    
    
    paper = cmds.polyCylinder(r=r, h=h, sx=50, sy=1, sz=1, ax=(0,1,0), rcp=0, cuv=3, ch=1, n='myPaper')
    cmds.select(cl=True)
    for i in range (50,100):
        cmds.select(paper[0] + '.f[' + str(i) + ']', tgl=True)
    cmds.delete() # deletes bottom faces of cylinder for opening of lantern
    cmds.select(paper[0])
    cmds.move(0,h/2,0) # moves lantern paper so that it sit on mirror

    wick = cmds.polyCube(w=0.5*r, h=0.01*r, d=0.5*r, n='myWick')
    cmds.rotate(0,45,0)
    wickShader = cmds.shadingNode('lambert', asShader=True, n='myWickShader')    
    SG1 = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
    cmds.connectAttr((wickShader +'.outColor'), (SG1+'.surfaceShader'), f=1)
    cmds.setAttr('myWickShader.color', 0.2, 0.2, 0.2)
    cmds.setAttr('myWickShader.ambientColor', 0.2, 0.2, 0.2)
    cmds.sets(wick[0], e=1, forceElement=SG1)
    
    rim = cmds.polyTorus(r=r, sr=0.02*r, sx=50)

    len = r - 0.25*r*math.sqrt(2) # length of strings = dist between rim and wick
    stringGroup = cmds.group(empty=True, name='myStringGroup')
    for i in range (0,4):
        mv = len/2 + 0.25*r*math.sqrt(2)
        string = cmds.polyCylinder(r=0.01*r, h=len, n='myString#')
        cmds.select(string[0])
        xRotate = [90,90,0,0]
        zRotate = [0,0,90,90]
        xMove = [0,0,mv,-mv]
        zMove = [mv,-mv,0,0]
        cmds.rotate(xRotate[i], 0, zRotate[i], string)
        cmds.move(xMove[i], 0, zMove[i], string)
        cmds.parent(string, stringGroup)
    strings = cmds.polyUnite(rim, stringGroup, n='myStrings') # unites rim and strings into one poly object
    stringShader = cmds.shadingNode('lambert', asShader=True, n='myStringShader')
    SG2 = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
    cmds.connectAttr((stringShader +'.outColor'), (SG2+'.surfaceShader'), f=1)    
    cmds.setAttr('myStringShader.color', 1, 1, 1)
    cmds.setAttr('myStringShader.ambientColor', 1, 1, 1)
    cmds.sets(strings[0], e=1, forceElement=SG2)

    fire = cmds.polyUnite(wick, strings, n='myFire') # unites wick and strings (rim + strings) into one object
    cmds.move(0,0.01,0, fire) # moves fire items to sit on top of mirror

    lanternGroup = cmds.group(paper, fire, n='myLanternGroup')
    lanternInstanceGroup = cmds.group(empty=True, name='myLanternInstanceGroup')

    for i in range(0,n*n):
    
        instanceLanternGroup = cmds.group(empty=True, n='myLanternGroupInstance#')
    
        instancePaper = cmds.duplicate(paper[0], n='paperInstance#')
        
        # randomize color of lanterns
        r = random.uniform(bc[0]-0.1,bc[0])
        g = random.uniform(bc[1]-0.1,bc[1]+0.1)
        b = random.uniform(bc[2]-0.2,bc[2]+0.2)
    
        paperShader = cmds.shadingNode('lambert', asShader=True, n='myPaperShader#')
        SG3 = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr((paperShader +'.outColor'), (SG3+'.surfaceShader'), f=1)
        cmds.setAttr('myPaperShader' + str(i+1) + '.color', r, g, b)
        cmds.setAttr('myPaperShader' + str(i+1) + '.ambientColor', r, g, b)
        cmds.sets(instancePaper[0], e=1, forceElement=SG3)
        cmds.parent(instancePaper, instanceLanternGroup)
    
        instanceFire = cmds.duplicate(fire, n='fireInstance#')
        cmds.parent(instanceFire, instanceLanternGroup)
    
        instanceLantern = cmds.polyUnite(instanceLanternGroup, n='myLanternInstance#')
        cmds.parent(instanceLantern, instanceLanternGroup)
        cmds.parent(instanceLanternGroup, lanternInstanceGroup)
    
        cmds.rotate(0, random.uniform(0,360), 0, instanceLantern)
    
        scalingFactorXZ = random.uniform(1,1.5)
        scalingFactorY = random.uniform(1,1.5)
        cmds.scale(scalingFactorXZ, scalingFactorY, scalingFactorXZ, instanceLantern)
        
        cmds.setAttr('myLanternInstance' + str(i+1) + '.castsShadows', 0)
        cmds.setAttr('myLanternInstance' + str(i+1) + '.receiveShadows', 0)
    
        # variables for placement of lanterns in rows/colums on mirror
        nf = float(n)
        mf = float(m)
        s = (nf-1)/2*mf # starting point of random placement
        xMove = float(x - s + mf*(int(i/nf))) # determines lantern row
        zMove = float(z - s + mf*(i%nf)) # determines lantern column
        
        yMove = y + 0.02
        
        # sets lantern's floating path 
        ran = random.uniform(-a/10,a/10)
        path = cmds.curve(p=[(xMove,yMove,zMove),(xMove,yMove+a/5,zMove),(xMove+ran,yMove+2*a/5,zMove+ran),(xMove,yMove+3*a/5,zMove),(xMove-ran,yMove+4*a/5,zMove-ran),(xMove,yMove+a,zMove)], n='myPath#')
        cmds.parent(path, instanceLanternGroup)
        cmds.select(instanceLantern, path)
        cmds.pathAnimation(fm=True, f=True, fa='y', ua='x', wut='objectrotation', wu=(0,1,0), iu=False, inverseFront=False, b=False, stu=random.uniform(0,f/2), etu=random.uniform(f,2*f))
        cmds.setAttr ('myPath' + str(i+1) + '.visibility', 0)
    
    lantern = cmds.polyUnite(lanternGroup, n='myLantern')
    cmds.hide(lantern[0]) # hides initial lantern
    cmds.xform(instanceLanternGroup, centerPivots=True)

    mirror = cmds.polyPlane(ax=(0,1,0), n='myMirror')
    cmds.scale(n*m+m/2, n*m+m/2, mirror, xz=True) # mirror side length = (# of lantern rows/columns)*(dist b/t lanterns)+half*(dist b/t lanterns)

    mirrorShader = cmds.shadingNode('blinn', asShader=True, name='myMirrorShader')
    cmds.setAttr('myMirrorShader.reflectivity', 1)
    cmds.setAttr('myMirrorShader.refractions', 1)
    cmds.setAttr('myMirrorShader.refractiveIndex', 5)
    SG4 = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
    cmds.connectAttr((mirrorShader+'.outColor'), (SG4+'.surfaceShader'), f=1)
    cmds.sets(mirror[0], e=1, forceElement=SG4)
    cmds.setAttr('myMirror.castsShadows', 0)
    cmds.setAttr('myMirror.receiveShadows', 0)

    cmds.select(cl=True)

def rend():
    
    cmds.setAttr('defaultRenderQuality.enableRaytracing', 1)
    cmds.render()
