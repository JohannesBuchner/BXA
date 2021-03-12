# export PYTHONPATH=../../:$PYTHONPATH:../../npyinterp/ LD_LIBRARY_PATH=$LD_LIBRARY_PATH:../../npyinterp/ 

echo 1.680000e+20 > swift/interval0pc.pi.nh

coverage run -p example_simplest.py || exit 1
coverage run -p example_pcabackground.py || exit 2
coverage run -p example_automatic_background_model.py || exit 3

rm testmodel.npz  && coverage run -p example_rebinning.py || exit 4
coverage run -p example_rebinning.py || exit 5

coverage run -p model_compare.py superfit/ tbabs_noz/

mkdir -p reference-output
convert simplest/plots/corner.pdf reference-output/corner.png
