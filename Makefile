CXX ?= c++
CXXFLAGS ?= -O2 -std=c++20 -Wall -Wextra -Wpedantic

.PHONY: all run test demo clean

all: build/libsoundsausage_dsp.so

build/libsoundsausage_dsp.so: native/dsp.cpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) -fPIC -shared $< -o $@.tmp
	mv -f $@.tmp $@

run: all
	PYTHONPATH=src python3 -m soundsausage

test: all
	QT_QPA_PLATFORM=offscreen PYTHONPATH=src python3 -m unittest discover -s tests -v

demo: all
	PYTHONPATH=src python3 tools/make_demo.py

clean:
	rm -f build/libsoundsausage_dsp.so
