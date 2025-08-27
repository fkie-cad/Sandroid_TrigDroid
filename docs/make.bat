@ECHO OFF

REM Command file for Sphinx documentation

pushd %~dp0

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help
if "%1" == "help" goto help
if "%1" == "clean" goto clean
if "%1" == "html" goto html
if "%1" == "livehtml" goto livehtml
if "%1" == "install" goto install
if "%1" == "serve" goto serve
if "%1" == "dev" goto dev

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
echo.
echo.Additional commands:
echo.  clean      Remove build directory
echo.  html       Build HTML documentation
echo.  livehtml   Build HTML with auto-reload
echo.  install    Install documentation dependencies
echo.  serve      Start development server with auto-reload
echo.  dev        Quick development build
goto end

:clean
rmdir /s /q "%BUILDDIR%" 2>nul
echo.Removed build directory %BUILDDIR%.
goto end

:html
%SPHINXBUILD% -b html %SOURCEDIR% %BUILDDIR%\html %SPHINXOPTS% %O%
echo.
echo.Build finished. The HTML pages are in %BUILDDIR%\html.
goto end

:livehtml
sphinx-autobuild %SOURCEDIR% %BUILDDIR%\html --open-browser
goto end

:install
pip install -r requirements.txt
goto end

:serve
call :install
call :livehtml
goto end

:dev
call :html
echo.Development build completed. Open %BUILDDIR%\html\index.html in your browser.
goto end

:end
popd