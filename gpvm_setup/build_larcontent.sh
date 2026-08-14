#!/bin/bash

cd $MY_TEST_AREA/LArContent
cmake -S . -B build -D CMAKE_PREFIX_PATH="$MY_TEST_AREA/PandoraSDK/build/install;$MY_TEST_AREA/PandoraMonitoring/build/install;${LIBTORCH}/share/cmake" -D PANDORA_LIBTORCH=ON
cmake --build build --target install --parallel 2
cd -
