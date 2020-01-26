cd ..

if "%PYTHON_ARCH%"=="32" (
    set BUILD_PLATFORM=Win32
) else (
    set BUILD_PLATFORM=x64
)

if exist "opus" goto ALREADY_BUILT

echo Building Opus...
git clone https://github.com/telegramdesktop/opus.git
cd opus
git checkout tdesktop
cd win32\VS2015
msbuild opus.sln /property:Configuration=Release /property:Platform="%BUILD_PLATFORM%"
cd ..\..\..
goto FINISH

:ALREADY_BUILT
echo Opus is already built

:FINISH
cd pytgvoip
