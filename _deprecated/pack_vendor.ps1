# pack_vendor.ps1 - dong goi vendor kit day du, chay tren MAY CU
$ErrorActionPreference = "Stop"
$LAB = if ($env:CAPCUT_LAB) { $env:CAPCUT_LAB } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$V = Join-Path $LAB "_vendor"
New-Item -ItemType Directory -Force -Path $V | Out-Null
Write-Host "LAB = $LAB`nKIT = $V`n" -ForegroundColor Cyan

if (-not (Get-ChildItem $V -Filter "capcut-cli-*.tgz" -EA SilentlyContinue)) {
  Write-Host "-- npm pack capcut-cli@0.15.0" -ForegroundColor Yellow
  Push-Location $V; npm pack capcut-cli@0.15.0; Pop-Location
} else { Write-Host "-- tarball npm da co" -ForegroundColor Green }

foreach ($d in @("testV3_CLEAN","Test_tool_v3","snapshots","frames")) {
  $from = Join-Path $LAB $d
  if (Test-Path $from) {
    robocopy $from (Join-Path $V $d) /E /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
    Write-Host ("   {0,-16} OK" -f $d) -ForegroundColor Green
  } else { Write-Host ("   {0,-16} KHONG THAY" -f $d) -ForegroundColor Yellow }
}

robocopy $LAB (Join-Path $V "scripts") *.py *.ps1 /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
$nsc = (Get-ChildItem (Join-Path $V "scripts") -File).Count
Write-Host ("   {0,-16} OK ({1} file)" -f "scripts", $nsc) -ForegroundColor Green

robocopy "$env:LOCALAPPDATA\CapCut\User Data\Cache\effect" (Join-Path $V "Cache_effect") /E /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
$ncache = (Get-ChildItem (Join-Path $V "Cache_effect") -Directory).Count
Write-Host ("   {0,-16} OK ({1} muc)" -f "Cache_effect", $ncache) -ForegroundColor Green

Copy-Item (Join-Path $LAB "enums_backup.json") $V -Force -EA SilentlyContinue

$L = New-Object System.Collections.Generic.List[string]
$L.Add("VENDOR KIT - pipeline CapCut 9.1.0 + capcut-cli 0.15.0")
$L.Add("tao ngay : " + (Get-Date -Format 'yyyy-MM-dd HH:mm') + "   tren may: " + $env:COMPUTERNAME)
$L.Add("")
$L.Add("-- FILE QUAN TRONG --")
foreach ($f in (Get-ChildItem $V -File | Sort-Object Name)) {
  $h = if ($f.Length -lt 700MB) { (Get-FileHash $f.FullName -Algorithm SHA256).Hash } else { "(bo qua)" }
  $L.Add(("{0,-46} {1,10:N2} MB  {2}" -f $f.Name, ($f.Length/1MB), $h))
}
$L.Add("")
$L.Add("-- THU MUC --")
foreach ($d in (Get-ChildItem $V -Directory | Sort-Object Name)) {
  $n = (Get-ChildItem $d.FullName -Recurse -File).Count
  $mb = [math]::Round(((Get-ChildItem $d.FullName -Recurse -File | Measure-Object Length -Sum).Sum)/1MB,1)
  $L.Add(("{0,-46} {1,7} file  {2,9:N1} MB" -f $d.Name, $n, $mb))
}
$L.Add("")
$L.Add("-- PHIEN BAN DA KIEM CHUNG --")
$L.Add("CapCut 9.1.0.3879 | capcut-cli 0.15.0 | schema_int 360000")
$L.Add("Python 3.13 (python.org) | Node 24.x | ffmpeg 8.1.2 Gyan full")
$L.Add("Cache\effect: " + $ncache + " muc")
$L.Add("")
$L.Add("-- CAI IM LANG --")
$L.Add('CapCut_9.1.0.3879_*.exe /silent_install=1 /install_path="C:\CapCut910"')
$L.Add("protocol handler: capcut:   |   ProductCode: CapCut   |   scope: user")
$L.Add("")
$L.Add("-- UPDATER (xac dinh 29/07/2026 tren may goc) --")
$L.Add("Thu muc cai: %LOCALAPPDATA%\CapCut\Apps\<version>\   <-- co SO PHIEN BAN")
$L.Add("  CHAN : CapCut-DiffUpgrade.exe   hpatchz.exe")
$L.Add("  NGHI : ttdaemon.exe   (chua xac nhan, chi chan khi can)")
$L.Add("  GIU  : VEHelper.exe   VECrashHandler.exe   CapCutService.exe")
$L.Add("Khong co scheduled task, khong co muc trong HKCU Run.")
[System.IO.File]::WriteAllText((Join-Path $V "MANIFEST.txt"), ($L -join "`r`n"), (New-Object System.Text.UTF8Encoding($false)))

Write-Host "`n-- MANIFEST --" -ForegroundColor Cyan
Get-Content (Join-Path $V "MANIFEST.txt")
$tot = [math]::Round(((Get-ChildItem $V -Recurse -File | Measure-Object Length -Sum).Sum)/1GB,2)
Write-Host "`nTONG KIT: $tot GB" -ForegroundColor Green