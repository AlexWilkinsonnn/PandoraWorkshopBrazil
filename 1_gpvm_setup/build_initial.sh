#!/bin/bash

cd $MY_TEST_AREA/PandoraSDK
cmake -S . -B build
cmake --build build --parallel 2
cmake --install build

cd $MY_TEST_AREA/PandoraMonitoring
cmake -S . -B build -D CMAKE_PREFIX_PATH=$MY_TEST_AREA/PandoraSDK/build/install
cmake --build build --target install --parallel 2

cd $MY_TEST_AREA
wget https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz
tar -xf eigen-3.4.0.tar.gz
mv eigen-3.4.0 Eigen3
cd Eigen3
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=$MY_TEST_AREA/Eigen3/ ..
make -j2 install

cd $MY_TEST_AREA/LArContent
cmake -S . -B build -D CMAKE_PREFIX_PATH="$MY_TEST_AREA/PandoraSDK/build/install;$MY_TEST_AREA/PandoraMonitoring/build/install;${LIBTORCH}/share/cmake" -D PANDORA_LIBTORCH=ON
cmake --build build --target install --parallel 2

cd $MY_TEST_AREA/LArReco
cmake -S . -B build -D CMAKE_PREFIX_PATH="$MY_TEST_AREA/PandoraSDK/build/install;$MY_TEST_AREA/PandoraMonitoring/build/install;$MY_TEST_AREA/LArContent/build/install;${LIBTORCH}/share/cmake" -D PANDORA_LIBTORCH=ON
cmake --build build --target install --parallel 2

cd $MY_TEST_AREA/LArMachineLearningData
./download.sh dune lbl
./download.sh dune atmos

cd $MY_TEST_AREA
