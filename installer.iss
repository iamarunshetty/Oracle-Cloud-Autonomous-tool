; ============================================================
; Inno Setup Script – Oracle Fusion Access Manager Installer
; Run Inno Setup Compiler on this file after building the exe
; ============================================================

#define AppName    "Oracle Fusion Access Manager"
#define AppVersion "0.1.0"
#define AppExe     "FusionAccessManager.exe"
#define Publisher  "Your Organisation"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#Publisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputBaseFilename=FusionAccessManagerSetup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Require Windows 10 or later
MinVersion=10.0
PrivilegesRequired=lowest

[Files]
; Main executable (built by PyInstaller)
Source: "dist\{#AppExe}"; DestDir: "{app}"; Flags: ignoreversion

; Config template
Source: ".env.example";          DestDir: "{app}"; DestName: ".env.example"; Flags: ignoreversion

; Excel templates
Source: "templates\*";           DestDir: "{app}\templates"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}";    Filename: "{app}\{#AppExe}"
Name: "{group}\Uninstall";      Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
