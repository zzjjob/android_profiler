# -*- coding: utf-8 -*-
import os
import sys
import threading
import time

import datetime as dt
import pandas as pd


reload(sys)
sys.setdefaultencoding( "utf-8" )

def check_csv(csvPath):
    with open(r'%s'%(csvPath), 'rb') as fh:
        first = next(fh)
        offs = -100
        while True:
            fh.seek(offs, 2)
            lines = fh.readlines()
            if len(lines)>1:
                last = lines[-1]
                break
            offs *= 2
        L_first=len(first.split(','))
        L_last=len(last.split(','))
    if L_last != L_first:
        print("Delete the last line.")
        with open(r'%s'%(csvPath)) as f:
            lines = f.readlines()
            curr = lines[:-1]
        f = open(r'%s'%(csvPath), 'w')
        f.writelines(curr)
        f.close()

def copyFiles(sourceDir, targetDir):
    copyFileCounts = 0
    print(sourceDir)
    print('%s copy %s the %sth file'%(dt.datetime.now(), sourceDir,copyFileCounts))
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)
        
        if os.path.isfile(sourceF):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            copyFileCounts += 1
            if not os.path.exists(targetF) or (os.path.exists(targetF) and (os.path.getsize(targetF) != os.path.getsize(sourceF))):
                open(targetF, "wb").write(open(sourceF, "rb").read())
                print('%s %s finish copying'%(dt.datetime.now(), targetF))
            else:
                print('%s %s exist'%(dt.datetime.now(), targetF))
           
        if os.path.isdir(sourceF):
            copyFiles(sourceF, targetF)
    
class csvtojsthread(threading.Thread):
    def __init__(self, csvtojs):
        threading.Thread.__init__(self, name = 'FPStoJS')
        self.csvtojs=csvtojs
    def run(self):
        self.csvtojs

class FPStoJS():
    def main(self,csvPath):
        if len(open('%s'%csvPath).readlines()) > 1:
            thread = csvtojsthread(self.FPS('%s'%csvPath))
            thread.setDaemon(True)
            thread.start()
            
    def FPS(self,csvPath):
        print('%s FPS Start'%dt.datetime.now())
        data=pd.read_csv(r'%s'%csvPath,warn_bad_lines=False,error_bad_lines=False).fillna(value='null')
        t_window=data.columns[2].replace('Date:','')
        t_FPS=data.columns[3].replace('FPS:','')
        t_KPI=data.columns[7].replace('OKT:','')
        D_FU=data['FU(s)'].values.tolist()
        D_LU=data['LU(s)'].values.tolist()
        D_Date=data[data.columns[2]].values.tolist()
        D_FPS=data[data.columns[3]].values.tolist()
        D_Frames=data['Frames'].tolist()
        D_jank=data['jank'].tolist()
        D_MFS=data['MFS(ms)'].tolist()
        D_OKT=data[data.columns[7]].tolist()
        D_SS=data['SS(%)'].values.tolist()
        x_min=D_FU[0]
        x_max=D_LU[len(D_LU)-1]
        T_D=(data['LU(s)']-data['FU(s)']).values.tolist()
        T_ms=[]
        for l in range(len(D_FU)):
            if l == 0 :
                tmp=T_D[0]
            else:
                if D_FU[l]-D_LU[l-1] < 0.5 :
                    tmp+=T_D[l]
                else:
                    T_ms.append(round(tmp,3))
                    tmp=T_D[l]
            D_FU[l]=round(D_FU[l],3)
            D_LU[l]=round(D_LU[l],3)
        T_ms.append(round(tmp,3))
        T_min=min(T_ms)
        T_max=max(T_ms)
        print(T_ms)
        result="""function isHasElement(arr,value){
    var str=arr.toString(),index=str.indexOf(value);
    if(index >= 0){
        var reg1=new RegExp("((^|,)"+value+"(,|$))","gi");
        return str.replace(reg1,"$2@$3").replace(/[^,@]/g,"").indexOf("@");
    }else{
        return -1;
    }
}

function accMul(arg1,arg2){
    var m=0,s1=arg1.toString(),s2=arg2.toString();
    try {m += s1.split(".")[1].length;}
    catch (e){}
    try {m += s2.split(".")[1].length;}
    catch (e){}
    return Number(s1.replace(".","")) * Number(s2.replace(".","")) / Math.pow(10,m);
}

Number.prototype.mul=function (arg){return accMul(arg, this);};

function accDiv(arg1,arg2){
    var t1=0,t2=0,r1,r2;
    try {t1=arg1.toString().split(".")[1].length;}
    catch (e){}
    try {t2 = arg2.toString().split(".")[1].length;}
    catch (e){}
    with (Math){
        r1=Number(arg1.toString().replace(".",""));
        r2=Number(arg2.toString().replace(".",""));
        return (r1/r2)*pow(10,t2-t1);
    }
}

Number.prototype.div=function (arg){return accDiv(this,arg);};

function decimal(num,v){  
    var vv=Math.pow(10,v);  
    return Math.round(num*vv)/vv;  
}

var x_min=%s,x_max=%s,FPS_chart_min=x_min,FPS_chart_max=x_min,t_window="%s",t_FPS=%s,t_KPI=%s,T_min=%s,T_max=%s,
T_ms=%s;
function getdata(type,arg){
    var D_FU=%s,
        D_LU=%s,
        D_Date=%s,
        D_FPS=%s,
        D_Frames=%s,
        D_jank=%s,
        D_MFS=%s,
        D_OKT=%s,
        D_SS=%s;
    switch (type){
        case 'point':
            var p=isHasElement(D_LU,arg);
            if(p != -1){
                return [D_FU[p],D_LU[p],D_Date[p],D_Frames[p],D_jank[p],D_MFS[p],D_OKT[p]];
            }else{
                var p=isHasElement(D_FU,arg);
                return [D_FU[p],D_LU[p],D_Date[p],D_Frames[p],D_jank[p],D_MFS[p],D_OKT[p]];
            }
            break;
        case 'line':
            var L_FPS=[],L_OKTPF=[],L_SS=[],D_OKTPF=[];
            switch (arg){
                case 0:
                    L_FPS.push([D_FU[0],D_FPS[0]]);
                    L_FPS.push([D_LU[0],D_FPS[0]]);
                    D_OKTPF=D_OKT[0].mul(100).div(D_Frames[0]);
                    D_OKTPF=decimal(D_OKTPF,2)
                    L_OKTPF.push([D_FU[0],D_OKTPF]);
                    L_OKTPF.push([D_LU[0],D_OKTPF]);
                    L_SS.push([D_FU[0],D_SS[0]]);
                    L_SS.push([D_LU[0],D_SS[0]]);
                    for (var i = 1; i < D_FU.length; i++){
                        var check=D_FU[i]-D_LU[i-1]
                        if(check > 1){
                            L_FPS.push(null);
                            L_OKTPF.push(null);
                            L_SS.push(null);
                        }
                        L_FPS.push([D_FU[i],D_FPS[i]]);
                        L_FPS.push([D_LU[i],D_FPS[i]]);
                        D_OKTPF=D_OKT[i].mul(100).div(D_Frames[i]);
                        D_OKTPF=decimal(D_OKTPF,2)
                        L_OKTPF.push([D_FU[i],D_OKTPF]);
                        L_OKTPF.push([D_LU[i],D_OKTPF]);
                        L_SS.push([D_FU[i],D_SS[i]]);
                        L_SS.push([D_LU[i],D_SS[i]]);
                    }
                    break;
                case 1:
                    var max_x=0;
                    L_FPS.push([D_FU[0],D_FPS[0]]);
                    L_FPS.push([D_LU[0],D_FPS[0]]);
                    D_OKTPF=D_OKT[0].mul(100).div(D_Frames[0]);
                    D_OKTPF=decimal(D_OKTPF,2)
                    L_OKTPF.push([D_FU[0],D_OKTPF]);
                    L_OKTPF.push([D_LU[0],D_OKTPF]);
                    L_SS.push([D_FU[0],D_SS[0]]);
                    L_SS.push([D_LU[0],D_SS[0]]);
                    for (var i = 1; i < D_FU.length; i++){
                        var check=D_FU[i]-D_LU[i-1]
                        if(check > 1){
                            L_FPS.push(null);
                            L_OKTPF.push(null);
                            L_SS.push(null);
                        }
                        L_FPS.push([D_FU[i],D_FPS[i]]);
                        L_FPS.push([D_LU[i],D_FPS[i]]);
                        D_OKTPF=D_OKT[i].mul(100).div(D_Frames[i]);
                        D_OKTPF=decimal(D_OKTPF,2)
                        L_OKTPF.push([D_FU[i],D_OKTPF]);
                        L_OKTPF.push([D_LU[i],D_OKTPF]);
                        L_SS.push([D_FU[i],D_SS[i]]);
                        L_SS.push([D_LU[i],D_SS[i]]);
                        max_x=D_LU[i]-x_min;
                        FPS_chart_max=D_LU[i];
                        if(max_x >= 600){break;}
                    }
                    break;
            }
            return [L_FPS,L_OKTPF,L_SS];
            break;
    }
}"""%(x_min,x_max,t_window,t_FPS,t_KPI,T_min,T_max,T_ms,D_FU,D_LU,D_Date,D_FPS,D_Frames,D_jank,D_MFS,D_OKT,D_SS)
        f=open(r'%s/head/data.js'%csvPath.replace('csv',''),'a')
        f.write('%s'%result)
        f.close()
        print('%s FPS Finish'%dt.datetime.now())
                
if __name__ == '__main__':
    csvPath=sys.argv[1]
    resultPath=os.path.dirname(csvPath)
    import shutil
    if os.path.exists(r'%s'%csvPath.replace('csv','')):
        try:
            shutil.rmtree(r'%s'%csvPath.replace('csv',''))
        except os.error:#err:
            time.sleep(0.5)
            try:
                shutil.rmtree(r'%s'%csvPath.replace('csv',''))
            except os.error:#, err:
                print("Delete FPS_HTML Error!!!")
    else:
        os.mkdir(r'%s'%csvPath.replace('csv',''))
    print('%s Copying BTM_HTML'%dt.datetime.now())
    copyFiles('%s/FPS_HTML'%os.path.dirname(sys.argv[0]), '%s'%csvPath.replace('csv',''))
    print('%s Finish Copying FPS_HTML'%dt.datetime.now())
    check_csv(r'%s'%csvPath)
    test=FPStoJS()
    test.main(r'%s'%csvPath)
