mkdir -p .pngtmp
for i in $(grep -Eo 'tpl[[:alnum:]_]*.png' object.py)
do
#cp ../WZRY_AirtestIDE_emulator/$i .
#cp ../IOS/$i .
cp $i .pngtmp/
done
echo rm tpl*png
echo cp .pngtmp/* .
 
