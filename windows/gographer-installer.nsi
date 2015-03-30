; Script to install GOGrapher python library.  More information at http://projects.dbbe.musc.edu/trac/GOGrapher


!define NAME GOGrapher
!define PYTHON "python.exe"

Name "${NAME}"
Caption "${NAME} Windows Installer"
DirText "${NAME} Windows Installer"
ComponentText  "${NAME} Windows Installer"
CompletedText "${NAME} windows Installer is finished"

OutFile "${NAME}-install.exe"
InstallDir "C:\Python25\Lib\${NAME}"

; Request application privileges for Windows Vista
RequestExecutionLevel user

Page directory
Page instfiles
ShowInstDetails show
WindowIcon on
SetOverwrite on
SetCompress auto
SetDatablockOptimize on
SetDateSave off
AutoCloseWindow true

Section "" ;No components page, name is not important 
  SetOutPath "$INSTDIR"
  File /r "..\${NAME}\*"
  DetailPrint "Compiling ${NAME} sources..."
  IfFileExists "$INSTDIR\__init__.py" NoAbort ErrorMSG
  IfFileExists "$INSTDIR\__init__.pyc" NoAbort ErrorMSG
  ErrorMSG:
    MessageBox MB_OK|MB_ICONEXCLAMATION "Unable to install GOGrapher to $INSTDIR."
    Abort
  NoAbort:
SectionEnd

Function .onInit
  ClearErrors
  ExecShell "open" "${PYTHON}" `-c "print 'Ah ha!'"` SW_SHOWMINIMIZED
  IfErrors 0 NoAbort
    MessageBox MB_OK|MB_ICONEXCLAMATION "Unable to find Python interpreter. Please install Python first, and make sure ${PYTHON} is in your path."
    Abort
  NoAbort:
FunctionEnd

Function .onInstSuccess
  MessageBox MB_OK "${NAME} was successfully installed.  Go get a coffee to celebrate."
FunctionEnd

