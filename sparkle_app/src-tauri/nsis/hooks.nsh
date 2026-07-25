!macro customHeader
  !macro customCheckRunning
    DetailPrint "Terminating any running instances of sparkle_app or sidecars..."
    nsExec::ExecToLog 'taskkill /F /IM sparkle_app.exe /T'
    nsExec::ExecToLog 'taskkill /F /IM VIBE.exe /T'
    nsExec::ExecToLog 'taskkill /F /IM blyskawica_backend.exe /T'
    Sleep 1000
  !macroend
!macroend

!macro customInstall
  !insertmacro customCheckRunning
!macroend

!macro customUninstall
  !insertmacro customCheckRunning
  DetailPrint "Performing clean recursive directory removal..."
  RMDir /r "$INSTDIR"
!macroend
