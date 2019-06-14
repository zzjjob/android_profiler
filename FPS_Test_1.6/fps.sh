#!/system/bin/sh

show_help() {
echo "
Usage: sh fps.sh [ -t target_FPS ] [ -w monitor_window ] [ -k KPI ] [ -f csv_path ] [ -h ]

Show: FU(s) LU(s) Date FPS Frames jank MFS(ms) OKT SS(%)

	FU(s): Uptime of the first frame.
	LU(s): Uptime of the last frame.
	Date: The date and time of LU.
	FPS: Frames Per Second.
	Frames: All frames of a loop.
	jank: When the frame latency crosses a refresh period, jank is added one.
	MFS(ms): Max Frame Spacing.
	OKT: Over KPI Times. The KPI is the used time of one frame.
	SS(%): Smoothness Score. SS=(FPS/target FPS)*60+(KPI/MFS)*20+(1-OKPIT/Frames)*20
	       IF FPS > target FPS: FPS/The target FPS=1
		   IF KPI > MFS: KPI/MFS=1
	WN: the window number of same name's window. Eg. SurfaceView

POSIX options | GNU long options

	-t   | --target         The target FPS of the choosed window. Default: 60
	-w   | --window         The choosed window. Default: no window.
	-k   | --KPI            The used time of a frame. Default: KPI=1000/The target FPS.
	-f   | --file           The path of the csv file. Default: output result to console.
	-h   | --help           Display this help and exit
"
}

file=""
window=""
target=60
KPI=16
while :
do
    case $1 in
        -h | --help)
            show_help
            exit 0
            ;;
        -t | --target)
            shift
			target=$1
			KPI=$((1000/$1))
			shift
            ;;
        -w | --window)
            shift
			window="$1"
			shift
            ;;
        -k | --KPI)
            shift
			KPI=$1
			shift
            ;;
        -f | --file)
            shift
			file="$1"
			shift
            ;;
        --) # End of all options
            shift
            break
            ;;
        *)  # no more options. Stop while loop
            break
            ;;	
    esac
done

if [ -f /data/local/tmp/busybox ];then
	export bb="/data/local/tmp/busybox"
else
	echo "No /data/local/tmp/busybox"
	exit
fi
if [ -f /data/local/tmp/stop ];then
	$bb rm /data/local/tmp/stop
fi

if [ -f /data/local/tmp/FPS.pid ];then
	pid=`cat /data/local/tmp/FPS.pid`
	if [ -f /proc/$pid/cmdline ];then
		if [ `$bb awk 'NR==1{print $1}' /proc/$pid/cmdline`"a" == "sha" ];then
			echo "The $pid is sh command."
			exit
		fi
	fi
fi
echo $$ >/data/local/tmp/FPS.pid

if [ $target -le 60 -a $target -gt 0 ];then
	sleep_t=1600000
else
	echo "$target is out of (0-60]"
	exit
fi
mac=`cat /sys/class/net/*/address|$bb sed -n '1p'|$bb tr -d ':'`
model=`getprop ro.product.model|$bb sed 's/ /_/g'`
build=`getprop ro.build.fingerprint`
if [ -z $build ];then
	build=`getprop ro.build.description`
fi

uptime=`$bb awk -v T="$EPOCHREALTIME" 'NR==3{printf("%.6f",T-$3/1000000000+8*3600)}' /proc/timer_list`
if [ -z "$file" ];then
	echo ""
	echo `date +%Y/%m/%d" "%H:%M:%S`": $window"
	if [ `$bb awk -F. '{print $1}' /proc/uptime` -lt 1000 ];then
		echo -e "FU(s) \tLU(s) \tDate \t\t\tFPS:$target\tFrames\tjank\tjank2\tMFS(ms)\tOKT:$KPI\tSS(%)\tWN"
	else
		echo -e "FU(s) \t\tLU(s) \t\tDate \t\t\tFPS:$target\tFrames\tjank\tjank2\tMFS(ms)\tOKT:$KPI\tSS(%)\tWN"
	fi
	while true;do
		dumpsys SurfaceFlinger --latency-clear
		$bb usleep $sleep_t
		dumpsys SurfaceFlinger --latency "$window"|$bb awk -v time=$uptime -v target=$target -v kpi=$KPI '{if(NR==1){r=$1/1000000;if(r<0)r=$1/1000;b=0;n=0;w=1}else{if(n>0&&$0=="")O=1;if(NF==3&&$2!=0&&$2!=9223372036854775807){x=($3-$1)/1000000/r;if(b==0){b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}else{c=($2-b)/1000000;if(c>500){O=1}else{n+=1;if(c>=r){C+=c;if(c>kpi)o+=1;if(c>=m)m=c;if(x>1)d+=1;if(x>2)D+=1;b=$2}else{C+=r;b=sprintf("%.0f",b+r*1000000)}}};if(n==1)s=sprintf("%.3f",$2/1000000000)};if(n>0&&O==1){O=0;if(n==1)t=sprintf("%.3f",s+C/1000);else t=sprintf("%.3f",b/1000000000);T=strftime("%F %T",time+t)"."sprintf("%.0f",(time+t)%1*1000);f=sprintf("%.2f",n*1000/C);m=sprintf("%.0f",m);g=f/target;if(g>1)g=1;h=kpi/m;if(h>1)h=1;e=sprintf("%.2f",g*60+h*20+(1-o/n)*20);print s"\t"t"\t"T"\t"f+0"\t"n"\t"d"\t"D"\t"m"\t"o"\t"e"\t"w;n=0;if($0==""){b=0;w+=1}else{b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}}}}'
		if [ -f /data/local/tmp/stop ];then
			break
		fi
	done
else
	start_time="`date +%Y/%m/%d" "%H:%M:%S`"
	echo "PID:$$\nWindow:$window\nT-FPS:$target\nKPI:$KPI\nStart time:$start_time\nmodel:$model\nmac:$mac\nbuild:$build"
	echo "FU(s),LU(s),Date:$window,FPS:$target,Frames,jank,jank2,MFS(ms),OKT:$KPI,SS(%),WN" >$file
	while true;do
		dumpsys SurfaceFlinger --latency-clear
		if [ -f /data/local/tmp/stop ];then
			echo "Stop Time:`date +%Y/%m/%d" "%H:%M:%S`"
			break
		fi
		$bb usleep $sleep_t
		dumpsys SurfaceFlinger --latency "$window"|$bb awk -v time=$uptime -v target=$target -v kpi=$KPI '{if(NR==1){r=$1/1000000;if(r<0)r=$1/1000;b=0;n=0;w=1}else{if(n>0&&$0=="")O=1;if(NF==3&&$2!=0&&$2!=9223372036854775807){x=($3-$1)/1000000/r;if(b==0){b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}else{c=($2-b)/1000000;if(c>500){O=1}else{n+=1;if(c>=r){C+=c;if(c>kpi)o+=1;if(c>=m)m=c;if(x>1)d+=1;if(x>2)D+=1;b=$2}else{C+=r;b=sprintf("%.0f",b+r*1000000)}}};if(n==1)s=sprintf("%.3f",$2/1000000000)};if(n>0&&O==1){O=0;if(n==1)t=sprintf("%.3f",s+C/1000);else t=sprintf("%.3f",b/1000000000);T=strftime("%F %T",time+t)"."sprintf("%.0f",(time+t)%1*1000);f=sprintf("%.2f",n*1000/C);m=sprintf("%.0f",m);g=f/target;if(g>1)g=1;h=kpi/m;if(h>1)h=1;e=sprintf("%.2f",g*60+h*20+(1-o/n)*20);print s","t","T","f+0","n","d","D","m","o","e","w;n=0;if($0==""){b=0;w+=1}else{b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}}}}' >>$file
	done
fi
