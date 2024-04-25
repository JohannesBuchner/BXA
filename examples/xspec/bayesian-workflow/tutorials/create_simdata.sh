#!/bin/bash

# -0- Setup storage directories
ATHDL='example_data/athena'
XMMDL='example_data/xmm'
EXMDL='example_output'

for dn in "example_data" "$ATHDL" "$XMMDL" "$EXMDL"; do
    if [ ! -d $dn ]; then
        mkdir $dn
    fi
done

# -1- Create the test spectra
#
# -1a- Absorbed AGN spectrum using Athena modelled response

# slow generating, to let us see what we did
cp ../../athenapp_ir_b4c_wfi_withfilter_fov40.0arcmin_avg.rsp .
cat gen_ath.xspec | { 
	while read line; do echo "$line"; sleep 0.1; done; sleep 3;
} | xspec

# store files in appropriate directory
mv athenapp_ir_b4c_wfi_withfilter_fov40.0arcmin_avg.rsp $ATHDL
mv example-file.fak $ATHDL

#
# -1b-  (pn, MOS1, MOS2)

# start clean
rm -f "${XMMDL}/epic_pn.rsp" "${XMMDL}/epic_mos1.rsp" "${XMMDL}/epic_mos2.rsp"

# download response files
echo "Downloading canned pn RMF"
wget -O epic_pn.rsp https://sasdev-xmm.esac.esa.int/pub/ccf/constituents/extras/responses/PN/epn_e4_ff20_sdY7_v21.0.rmf
if [[ "$?" != 0 ]]; then
    echo "Error downloading file";
    exit 1
fi

echo "Downloading canned MOS1 RMF"
wget -O epic_mos1.rsp https://sasdev-xmm.esac.esa.int/pub/ccf/constituents/extras/responses/MOS/15eV/m1_e19_im_p0_c.rmf
if [[ "$?" != 0 ]]; then
    echo "Error downloading file";
    exit 1
fi

echo "Downloading canned MOS2 RMF"
wget -O epic_mos2.rsp https://sasdev-xmm.esac.esa.int/pub/ccf/constituents/extras/responses/MOS/15eV/m2_e19_im_p0_c.rmf
if [[ "$?" != 0 ]]; then
    echo "Error downloading file";
    exit 1
fi

echo "Finished downloading XMM-Newton data"

# generate spectra
cat gen_xmm.xspec | { 
	while read line; do echo "$line"; sleep 0.1; done; sleep 3;
} | xspec

# store files in appropriate directory
mv epic*.rsp $XMMDL
mv epic*.fak $XMMDL


