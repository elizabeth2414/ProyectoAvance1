[Setup]
AppName=GestiVentas
AppVersion=1.0
DefaultDirName={autopf}\GestiVentas
DefaultGroupName=GestiVentas
OutputBaseFilename=setup_GestiVentas
Compression=lzma
SolidCompression=yes

[Files]
Source: "C:\Users\USER\Documents\GitHub\ProyectoAvance1\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\USER\Documents\GitHub\ProyectoAvance1\vistas\assets\store.png"; DestDir: "{app}\vistas\assets"; Flags: ignoreversion
Source: "C:\Users\USER\Documents\GitHub\ProyectoAvance1\sistema_ventas.db"; DestDir: "{localappdata}\GestiVentas"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\Sistema de Ventas"; Filename: "{app}\main.exe"
Name: "{commondesktop}\Sistema de Ventas"; Filename: "{app}\main.exe"

[Run]
Filename: "{app}\main.exe"; Description: "Ejecutar Sistema de Ventas"; Flags: nowait postinstall skipifsilent