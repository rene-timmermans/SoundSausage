CXX ?= c++
CXXFLAGS ?= -O2 -std=c++20 -Wall -Wextra -Wpedantic

.PHONY: all run test demo clean

all: build/libsoundsausage_dsp.so build/libsoundsausage_vst3.so

build/libsoundsausage_vst3.so: native/vst3_host.cpp $(wildcard third_party/vst3/pluginterfaces/base/*) $(wildcard third_party/vst3/pluginterfaces/vst/*)
	mkdir -p build
	$(CXX) $(CXXFLAGS) -fPIC -shared -Ithird_party/vst3 native/vst3_host.cpp third_party/vst3/pluginterfaces/base/funknown.cpp -ldl -o $@.tmp
	mv -f $@.tmp $@

build/libsoundsausage_dsp.so: native/dsp.cpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) -fPIC -shared $< -o $@.tmp
	mv -f $@.tmp $@

run: all
	PYTHONPATH=src python3 -m soundsausage

test: all
	SOUNDSAUSAGE_LANGUAGE=en SOUNDSAUSAGE_CACHE_DIR="$(CURDIR)/build/test-cache" QT_QPA_PLATFORM=offscreen PYTHONPATH=src python3 -m unittest discover -s tests -v

demo: all
	PYTHONPATH=src python3 tools/make_demo.py

clean:
	rm -f build/libsoundsausage_dsp.so
	rm -f build/libsoundsausage_vst3.so
