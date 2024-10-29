make clean

cd CAKE_on_CPU
source env.sh
sudo ldconfig $CAKE_HOME
cd ..


# Generate Rosko Kernels based on CPU arch. Only Haswell and armv8 currently supported

if uname -m | grep -q 'aarch64'; 
then
  	python3 $CAKE_HOME/python/kernel_gen.py armv8 20 72 sparse
  	mv sparse.cpp src/kernels/armv8
else
	python3 $CAKE_HOME/python/kernel_gen.py haswell 8 32 sparse
  	mv sparse.cpp src/kernels/haswell
fi



# install Rosko

source ./env.sh
make -f rosko_kernels.mk
make 
sudo ldconfig $ROSKO_HOME
export LD_LIBRARY_PATH