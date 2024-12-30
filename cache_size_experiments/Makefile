.PHONY: all compile clean

ifneq ($(strip $(BLIS_INSTALL_PATH)),)
BLIS_INC_PATH   := $(BLIS_INSTALL_PATH)/include/blis
endif

# g++ rosko_sgemm_test.cpp -I/usr/local/include/blis -I/tmp/ROSKO_on_CPU/include -L/tmp/ROSKO_on_CPU  -lrosko -o testing

TEST_OBJ_PATH  := .

# Use the "framework" CFLAGS for the configuration family.
CFLAGS_tmp         := $(call get-user-cflags-for,$(CONFIG_NAME))

# # Add local header paths to CFLAGS
# CFLAGS_tmp        += -I$(ROSKO_HOME)/include -I$(CAKE_HOME)/include

# # rosko shared library
# LIBS      := -L$(ROSKO_HOME) -lrosko -L$(CAKE_HOME) -lcake
# # LIBS := -Wl,-rpath,$(ROSKO_HOME) -L$(ROSKO_HOME) -lrosko -Wl,-rpath,$(CAKE_HOME) -L$(CAKE_HOME) -lcake
# ROSKO_SRC := $(ROSKO_HOME)/src

# Add local header paths to CFLAGS
CFLAGS_tmp        += -I$(ROSKO_HOME)/include -I$(CAKE_HOME)/include -I$(CNPY_INCLUDE_PATH) # Jonas added this in bashrc subscript

CFLAGS_blis := $(CFLAGS)
CFLAGS_blis		  += -I$(BLIS_INC_PATH)

# rosko shared library
LIBS      := -L$(ROSKO_HOME) -lrosko -L$(CAKE_HOME) -lcake -L$(CNPY_PATH) -lcnpy # Jonas added this in bashrc subscript
ROSKO_SRC := $(ROSKO_HOME)/src




UNAME_P := $(shell uname -p)
SRC_FILES =  $(wildcard $(ROSKO_HOME)/src/*.cpp)

ifeq ($(UNAME_P),aarch64)
	TARGETS = rosko_armv8
	CFLAGS_tmp		  += -fopenmp
else ifeq ($(UNAME_P),x86_64)
	TARGETS = rosko_haswell
	CFLAGS_tmp		  += -O3 -g -mavx -mfma -fopenmp
else
	TARGETS = rosko_blis
endif

CFLAGS 	:= $(filter-out -std=c99, $(CFLAGS_tmp))





# --- Targets/rules ------------------------------------------------------------

all: $(TARGETS)

rosko_haswell: $(wildcard *.h) $(wildcard *.c)
	g++ $(CFLAGS) rosko_sgemm_test.cpp $(LIBS) -o rosko_sgemm_test
	g++ $(CFLAGS) correctness_test_cache.cpp $(LIBS) -o correctness_test_cache

clean:
	rm -rf *.o *.so

