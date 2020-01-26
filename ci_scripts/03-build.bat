xcopy /E /I /C ..\openssl_1_1_1\out64 ..\openssl_1_1_1\out32
xcopy /E /I /C ..\opus\win32\VS2015\x64 ..\opus\win32\VS2015\Win32
python setup.py build
python setup.py bdist_wheel
