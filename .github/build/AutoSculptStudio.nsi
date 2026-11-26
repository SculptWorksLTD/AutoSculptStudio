; AutoSculpt Studio - Windows installer (NSIS 3, zlib licence: commercial use allowed)
; (c) 2026 Enrico Migliorati. All rights reserved.
; Build with:  makensis /INPUTCHARSET UTF8 /DVERSION=x.y.z .github\build\AutoSculptStudio.nsi   (after .github\build\build_windows.py)
; Languages: English, Italian, German, French, Spanish, Brazilian Portuguese, Japanese, chosen from the Windows
; language (a dialog lets the user change it).
; To add a language: one more MUI_LANGUAGE, its LicenseLangString (build_windows.py writes license_<code>.txt
; from installer/<code>.lproj/license.html) and a LangString for every message below.

Unicode true
ManifestDPIAware true
SetCompressor /SOLID lzma
RequestExecutionLevel user

!ifndef VERSION
  !define VERSION "0.0.0"
!endif
!define APPNAME "AutoSculpt Studio"
!define STAGE "..\..\build\win\stage"
!define EXE "$INSTDIR\python\AutoSculptStudio.exe"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\AutoSculptStudio"
!define WEBVIEW2_ID "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"

Name "${APPNAME}"
OutFile "..\..\download\AutoSculptStudio-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\AutoSculpt Studio"
InstallDirRegKey HKCU "${UNINST_KEY}" "InstallLocation"
BrandingText "AutoSculpt Studio ${VERSION} · © 2026 Enrico Migliorati"

VIProductVersion "${VERSION}.0"
VIAddVersionKey /LANG=1033 "ProductName" "${APPNAME}"
VIAddVersionKey /LANG=1033 "FileDescription" "${APPNAME} setup - From dream to reality"
VIAddVersionKey /LANG=1033 "Comments" "From dream to reality"
VIAddVersionKey /LANG=1033 "CompanyName" "Enrico Migliorati"
VIAddVersionKey /LANG=1033 "LegalCopyright" "© 2026 Enrico Migliorati. All rights reserved."
VIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"
VIAddVersionKey /LANG=1033 "ProductVersion" "${VERSION}"

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"

!define MUI_ICON "..\..\build\win\AutoSculptStudio.ico"
!define MUI_UNICON "..\..\build\win\AutoSculptStudio.ico"
!define MUI_ABORTWARNING
!define MUI_LANGDLL_ALLLANGUAGES
!define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
!define MUI_LANGDLL_REGISTRY_KEY "Software\AutoSculptStudio"
!define MUI_LANGDLL_REGISTRY_VALUENAME "InstallerLanguage"
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "$(MsgRun)"
!define MUI_FINISHPAGE_RUN_FUNCTION StartApp
!define MUI_FINISHPAGE_SHOWREADME
!define MUI_FINISHPAGE_SHOWREADME_TEXT "$(MsgDesktop)"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION DesktopShortcut

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "$(LicenseFile)"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Italian"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "PortugueseBR"
!insertmacro MUI_LANGUAGE "Japanese"
!insertmacro MUI_RESERVEFILE_LANGDLL

LicenseLangString LicenseFile ${LANG_ENGLISH} "..\..\build\win\license_en.txt"
LicenseLangString LicenseFile ${LANG_ITALIAN} "..\..\build\win\license_it.txt"
LicenseLangString LicenseFile ${LANG_GERMAN} "..\..\build\win\license_de.txt"
LicenseLangString LicenseFile ${LANG_FRENCH} "..\..\build\win\license_fr.txt"
LicenseLangString LicenseFile ${LANG_SPANISH} "..\..\build\win\license_es.txt"
LicenseLangString LicenseFile ${LANG_PORTUGUESEBR} "..\..\build\win\license_pt_BR.txt"
LicenseLangString LicenseFile ${LANG_JAPANESE} "..\..\build\win\license_ja.txt"

LangString MsgRun ${LANG_ENGLISH} "Start AutoSculpt Studio"
LangString MsgRun ${LANG_ITALIAN} "Avvia AutoSculpt Studio"
LangString MsgRun ${LANG_GERMAN} "AutoSculpt Studio starten"
LangString MsgRun ${LANG_FRENCH} "Lancer AutoSculpt Studio"
LangString MsgRun ${LANG_SPANISH} "Iniciar AutoSculpt Studio"
LangString MsgRun ${LANG_PORTUGUESEBR} "Abrir o AutoSculpt Studio"
LangString MsgRun ${LANG_JAPANESE} "AutoSculpt Studio を起動"
LangString MsgDesktop ${LANG_ENGLISH} "Create a desktop shortcut"
LangString MsgDesktop ${LANG_ITALIAN} "Crea un collegamento sul desktop"
LangString MsgDesktop ${LANG_GERMAN} "Verknüpfung auf dem Desktop erstellen"
LangString MsgDesktop ${LANG_FRENCH} "Créer un raccourci sur le bureau"
LangString MsgDesktop ${LANG_SPANISH} "Crear un acceso directo en el escritorio"
LangString MsgDesktop ${LANG_PORTUGUESEBR} "Criar um atalho na área de trabalho"
LangString MsgDesktop ${LANG_JAPANESE} "デスクトップにショートカットを作成"
LangString Msg64 ${LANG_ENGLISH} "AutoSculpt Studio requires 64-bit Windows."
LangString Msg64 ${LANG_ITALIAN} "AutoSculpt Studio richiede Windows a 64 bit."
LangString Msg64 ${LANG_GERMAN} "AutoSculpt Studio erfordert ein 64-Bit-Windows."
LangString Msg64 ${LANG_FRENCH} "AutoSculpt Studio nécessite Windows 64 bits."
LangString Msg64 ${LANG_SPANISH} "AutoSculpt Studio necesita Windows de 64 bits."
LangString Msg64 ${LANG_PORTUGUESEBR} "O AutoSculpt Studio requer o Windows de 64 bits."
LangString Msg64 ${LANG_JAPANESE} "AutoSculpt Studio には 64 ビット版 Windows が必要です。"
LangString MsgClose ${LANG_ENGLISH} "AutoSculpt Studio is open and will be closed to continue.$\n$\nSave your work, then press OK."
LangString MsgClose ${LANG_ITALIAN} "AutoSculpt Studio è aperto e verrà chiuso per continuare.$\n$\nSalva il lavoro, poi premi OK."
LangString MsgClose ${LANG_GERMAN} "AutoSculpt Studio ist geöffnet und wird zum Fortfahren geschlossen.$\n$\nSpeichere deine Arbeit und klicke dann auf OK."
LangString MsgClose ${LANG_FRENCH} "AutoSculpt Studio est ouvert et va être fermé pour continuer.$\n$\nEnregistrez votre travail, puis cliquez sur OK."
LangString MsgClose ${LANG_SPANISH} "AutoSculpt Studio está abierto y se cerrará para continuar.$\n$\nGuarda tu trabajo y pulsa Aceptar."
LangString MsgClose ${LANG_PORTUGUESEBR} "O AutoSculpt Studio está aberto e será fechado para continuar.$\n$\nSalve seu trabalho e clique em OK."
LangString MsgClose ${LANG_JAPANESE} "AutoSculpt Studio が開いているため、続行するには終了します。$\n$\n作業を保存してから OK を押してください。"
LangString MsgWebView ${LANG_ENGLISH} "To show its window, AutoSculpt Studio uses Microsoft Edge WebView2, which does not seem to be installed on this computer.$\n$\nIt is usually already present on Windows 10 and 11. Do you want to open Microsoft's page to download it (free)?"
LangString MsgWebView ${LANG_ITALIAN} "Per mostrare la finestra, AutoSculpt Studio usa Microsoft Edge WebView2, che su questo computer non risulta installato.$\n$\nDi solito è già presente su Windows 10 e 11. Vuoi aprire la pagina di Microsoft per scaricarlo (gratuito)?"
LangString MsgWebView ${LANG_GERMAN} "Zum Anzeigen des Fensters verwendet AutoSculpt Studio Microsoft Edge WebView2, das auf diesem Computer anscheinend nicht installiert ist.$\n$\nUnter Windows 10 und 11 ist es meist schon vorhanden. Möchtest du die Microsoft-Seite zum (kostenlosen) Herunterladen öffnen?"
LangString MsgWebView ${LANG_FRENCH} "Pour afficher sa fenêtre, AutoSculpt Studio utilise Microsoft Edge WebView2, qui ne semble pas installé sur cet ordinateur.$\n$\nIl est généralement déjà présent sous Windows 10 et 11. Voulez-vous ouvrir la page de Microsoft pour le télécharger (gratuit) ?"
LangString MsgWebView ${LANG_SPANISH} "Para mostrar su ventana, AutoSculpt Studio usa Microsoft Edge WebView2, que no parece estar instalado en este ordenador.$\n$\nNormalmente ya viene con Windows 10 y 11. ¿Quieres abrir la página de Microsoft para descargarlo (gratis)?"
LangString MsgWebView ${LANG_PORTUGUESEBR} "Para mostrar sua janela, o AutoSculpt Studio usa o Microsoft Edge WebView2, que parece não estar instalado neste computador.$\n$\nGeralmente ele já vem no Windows 10 e 11. Quer abrir a página da Microsoft para baixá-lo (grátis)?"
LangString MsgWebView ${LANG_JAPANESE} "AutoSculpt Studio はウィンドウの表示に Microsoft Edge WebView2 を使いますが、このコンピュータにはインストールされていないようです。$\n$\n通常は Windows 10 と 11 に含まれています。ダウンロード用の Microsoft のページ（無料）を開きますか？"
LangString MsgTagline ${LANG_ENGLISH} "3D models for your sculptures"
LangString MsgTagline ${LANG_ITALIAN} "Modelli 3D per le tue sculture"
LangString MsgTagline ${LANG_GERMAN} "3D-Modelle für deine Skulpturen"
LangString MsgTagline ${LANG_FRENCH} "Des modèles 3D pour tes sculptures"
LangString MsgTagline ${LANG_SPANISH} "Modelos 3D para tus esculturas"
LangString MsgTagline ${LANG_PORTUGUESEBR} "Modelos 3D para suas esculturas"
LangString MsgTagline ${LANG_JAPANESE} "彫刻のための 3D モデル"

; the uninstaller keeps a language-neutral file name
!define UNINSTALLER "$INSTDIR\Uninstall AutoSculpt Studio.exe"

Function .onInit
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP "$(Msg64)" /SD IDOK
    Abort
  ${EndIf}
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Function un.onInit
  !insertmacro MUI_UNGETLANGUAGE
FunctionEnd

; if the app is open it is closed (autosave has already saved the work)
!macro CloseApp
  nsExec::ExecToStack 'cmd /c tasklist /NH /FI "IMAGENAME eq AutoSculptStudio.exe" | find /I "AutoSculptStudio.exe"'
  Pop $0
  ${If} $0 == 0
    MessageBox MB_OKCANCEL|MB_ICONINFORMATION "$(MsgClose)" /SD IDOK IDOK +2
    Abort
    nsExec::Exec 'taskkill /IM AutoSculptStudio.exe /F'
    Sleep 1000
  ${EndIf}
!macroend

Section "AutoSculpt Studio" SecMain
  SectionIn RO
  !insertmacro CloseApp
  ; a new version fully replaces program and interface (data and engines stay in %APPDATA%)
  RMDir /r "$INSTDIR\app"
  SetOutPath "$INSTDIR"
  File /r "${STAGE}\*.*"
  WriteUninstaller "${UNINSTALLER}"

  SetOutPath "$INSTDIR"
  CreateShortcut "$SMPROGRAMS\AutoSculpt Studio.lnk" "${EXE}" '"$INSTDIR\app\main.py"' "$INSTDIR\AutoSculptStudio.ico" 0 SW_SHOWNORMAL "" "$(MsgTagline)"

  WriteRegStr HKCU "${UNINST_KEY}" "DisplayName" "${APPNAME}"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKCU "${UNINST_KEY}" "Publisher" "Enrico Migliorati"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayIcon" "$INSTDIR\AutoSculptStudio.ico"
  WriteRegStr HKCU "${UNINST_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "${UNINST_KEY}" "UninstallString" '"${UNINSTALLER}"'
  WriteRegStr HKCU "${UNINST_KEY}" "QuietUninstallString" '"${UNINSTALLER}" /S'
  WriteRegDWORD HKCU "${UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKCU "${UNINST_KEY}" "NoRepair" 1
  WriteRegDWORD HKCU "${UNINST_KEY}" "EstimatedSize" 120000


  Call CheckWebView2
SectionEnd

Function CheckWebView2
  SetRegView 32
  ReadRegStr $0 HKLM "SOFTWARE\Microsoft\EdgeUpdate\Clients\${WEBVIEW2_ID}" "pv"
  ${If} $0 == ""
    ReadRegStr $0 HKCU "Software\Microsoft\EdgeUpdate\Clients\${WEBVIEW2_ID}" "pv"
  ${EndIf}
  SetRegView 64
  ${If} $0 == ""
  ${OrIf} $0 == "0.0.0.0"
    MessageBox MB_YESNO|MB_ICONQUESTION "$(MsgWebView)" /SD IDNO IDNO +2
    ExecShell "open" "https://developer.microsoft.com/microsoft-edge/webview2/"
  ${EndIf}
FunctionEnd

Function StartApp
  SetOutPath "$INSTDIR"
  Exec '"${EXE}" "$INSTDIR\app\main.py"'
FunctionEnd

Function DesktopShortcut
  SetOutPath "$INSTDIR"
  CreateShortcut "$DESKTOP\AutoSculpt Studio.lnk" "${EXE}" '"$INSTDIR\app\main.py"' "$INSTDIR\AutoSculptStudio.ico" 0 SW_SHOWNORMAL "" "$(MsgTagline)"
FunctionEnd

Section "Uninstall"
  !insertmacro CloseApp
  Delete "$SMPROGRAMS\AutoSculpt Studio.lnk"
  Delete "$DESKTOP\AutoSculpt Studio.lnk"
  RMDir /r "$INSTDIR\app"
  RMDir /r "$INSTDIR\python"
  Delete "$INSTDIR\AutoSculptStudio.ico"
  Delete "${UNINSTALLER}"
  RMDir "$INSTDIR"
  DeleteRegKey HKCU "${UNINST_KEY}"
  DeleteRegKey HKCU "Software\AutoSculptStudio"
  ; your models and the engines in %APPDATA%\AutoSculptStudio are kept: delete them by hand if no longer needed
SectionEnd
