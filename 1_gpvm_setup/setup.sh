#!/bin/bash

source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup cmake v3_27_4
setup root v6_28_06b -q e26:p3915:prof
setup libtorch v2_1_1b -q e26
export LIBTORCH="/cvmfs/larsoft.opensciencegrid.org/products/libtorch/v2_1_1b/Linux64bit+3.10-2.17-e26"

export MY_TEST_AREA=`pwd`

export FW_SEARCH_PATH=$MY_TEST_AREA:$MY_TEST_AREA/LArReco/settings:$MY_TEST_AREA/LArMachineLearningData:$FW_SEARCH_PATH
