cd ..

if "%PYTHON_ARCH%"=="32" (
    set COMPILER=VC-WIN32
) else (
    set COMPILER=VC-WIN64A
)

if exist "openssl_1_1_1" goto ALREADY_BUILT

echo Building OpenSSL...

curl -L -o nasminst.exe http://libgd.blob.core.windows.net/nasm/nasm-2.07-installer.exe
start /wait nasminst.exe /S
set PATH=C:\Program Files (x86)\nasm;%PATH%

choco install strawberryperl -y
set PATH=C:\strawberry\c\bin;C:\strawberry\perl\site\bin;C:\strawberry\perl\bin;%PATH%

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
