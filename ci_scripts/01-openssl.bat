cd ..

if "%PLATFORM%"=="x86" (
    set COMPILER=VC-WIN32
    set DO_MS_SCRIPT=ms\do_ms.bat
) else (
    set COMPILER=VC-WIN64A
    set DO_MS_SCRIPT=ms\do_win64a.bat
)

if exist "openssl/Release/lib/ssleay32.lib" goto ALREADY_BUILT

echo Building OpenSSL...
git clone https://github.com/openssl/openssl.git
cd openssl
git checkout OpenSSL_1_0_1-stable
perl Configure no-shared --prefix=Release --openssldir=%PREFIX% "%COMPILER%"
call %DO_MS_SCRIPT%
nmake -f ms\nt.mak
nmake -f ms\nt.mak install
xcopy tmp32\lib.pdb Release\lib\
nmake -f ms\nt.mak clean
cd ..
goto FINISH

:ALREADY_BUILT
echo OpenSSL is already built

:FINISH
cd libtgvoip
