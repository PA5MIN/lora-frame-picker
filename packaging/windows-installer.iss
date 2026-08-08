#define AppVersion GetEnv("APP_VERSION")

[Setup]
AppId={{6C232BAC-3AC4-4D65-80A2-A86603407FF4}
AppName=LoRA Frame Picker
AppVersion={#AppVersion}
AppPublisher=PA5MIN
AppPublisherURL=https://github.com/PA5MIN/lora-frame-picker
AppSupportURL=https://github.com/PA5MIN/lora-frame-picker/issues
DefaultDirName={localappdata}\Programs\LoRA Frame Picker
DefaultGroupName=LoRA Frame Picker
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE
OutputDir=..\release-assets
OutputBaseFilename=LoRA-Frame-Picker-Windows-x64-Setup
UninstallDisplayIcon={app}\LoRA-Frame-Picker.exe
SetupLogging=yes

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："; Flags: unchecked

[Files]
Source: "..\dist\LoRA-Frame-Picker.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\LoRA-Phone-WebUI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README_EN.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SECURITY.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\LoRA Frame Picker"; Filename: "{app}\LoRA-Frame-Picker.exe"
Name: "{group}\LoRA 手机 WebUI"; Filename: "{app}\LoRA-Phone-WebUI.exe"
Name: "{group}\卸载 LoRA Frame Picker"; Filename: "{uninstallexe}"
Name: "{autodesktop}\LoRA Frame Picker"; Filename: "{app}\LoRA-Frame-Picker.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LoRA-Frame-Picker.exe"; Description: "立即启动 LoRA Frame Picker"; Flags: nowait postinstall skipifsilent
