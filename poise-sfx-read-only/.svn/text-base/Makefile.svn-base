# basic makefile to build cython extension.


# My OSX install has probs and can't find the numpy headers. So I have this little makefile to help
osx:
	cython buffers.pyx
	gcc -arch ppc -arch i386 -isysroot /Developer/SDKs/MacOSX10.4u.sdk -fno-strict-aliasing -DSTACKLESS_FRHACK=1 -Wno-long-double -no-cpp-precomp -mno-fused-madd -fno-common -dynamic -DNDEBUG -g -O3 -I/Library/Frameworks/Python.framework/Versions/2.5/include/python2.5 -I/Library/Frameworks/Python.framework/Versions/2.5/Extras/lib/python/numpy/core/include/ -c buffers.c -o build/temp.macosx-10.3-i386-2.5/buffers.o
	python setup.py build_ext --inplace
	
	
