cd ..

if "%PYTHON_ARCH%"=="32" (
    set COMPILER=VC-WIN32
) else (
    set COMPILER=VC-WIN64A
)

if exist "openssl_1_1_1/libssl.lib" goto ALREADY_BUILT

echo Building OpenSSL...
git clone https://github.com/openssl/openssl.git openssl_1_1_1
cd openssl_1_1_1
git checkout OpenSSL_1_1_1-stable

perl Configure no-shared "%COMPILER%"
nmake
mkdir "out%PYTHON_ARCH%"
move libcrypto.lib "out%PYTHON_ARCH%"
move libssl.lib "out%PYTHON_ARCH%"
move ossl_static.pdb "out%PYTHON_ARCH%"

cd ..
goto FINISH

:ALREADY_BUILT
echo OpenSSL is already built

:FINISH
cd pytgvoip
