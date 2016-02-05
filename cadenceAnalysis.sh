
mockdir=("2_1_zwick")
basedir=("Research/LSST/Cadence")
#script to test several LSST cadence patterns 
cd ~/${basedir}/${mockdir}/


mkdir {g_r_enigma1189std,g_r_enigma1189ddf,allbands_enigma1189std,allbands_enigma1189ddf}
scp -r ~/${basedir}/${mockdir}/*ini ~/${basedir}/${mockdir}/g_r_enigma1189std/ 
scp -r ~/${basedir}/${mockdir}/*ini ~/${basedir}/${mockdir}/g_r_enigma1189ddf/ 
scp -r ~/${basedir}/${mockdir}/*ini ~/${basedir}/${mockdir}/allbands_enigma1189std/ 
scp -r ~/${basedir}/${mockdir}/*ini ~/${basedir}/${mockdir}/allbands_enigma1189ddf/

for object in *enigma1189*; do
maskfile=("Users/Jackster/Research/LSST/LSST-AGNCadenceStrategy/masks/"${object}".txt")
python ~/${basedir}/applymask_irregular.py ~/${basedir}/${mockdir}/${object}/ Config.ini /${maskfile}
echo "ran routine"
done

