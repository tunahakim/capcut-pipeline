# session.ps1 v3 - tu dinh vi, khong can sua khi chuyen may
$T = if ($env:CAPCUT_LAB) { $env:CAPCUT_LAB } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:CAPCUT_LAB = $T
$DR  = "$env:LOCALAPPDATA\CapCut\User Data\Projects\com.lveditor.draft"
$SRC = Join-Path $T "Test_tool_v3"

function Stop-CapCut {
  $p = Get-Process *CapCut* -ErrorAction SilentlyContinue
  if ($p) {
    Write-Host "Dang tat CapCut ($($p.Count) process)..." -ForegroundColor Yellow
    $p | Stop-Process -Force
    Start-Sleep 3
  }
  if (Get-Process *CapCut* -ErrorAction SilentlyContinue) { throw "CapCut VAN CHAY - DUNG LAI" }
  Write-Host "OK - CapCut da tat hoan toan" -ForegroundColor Green
}

function Assert-CapCutOff {
  if (Get-Process *CapCut* -ErrorAction SilentlyContinue) { throw "CapCut VAN CHAY - dong han roi chay lai" }
  Write-Host "OK - CapCut khong chay" -ForegroundColor Green
}

function N([double]$x) { $x.ToString("0.###", [cultureinfo]::InvariantCulture) }

function Get-TID([string]$proj) {
  $f = Join-Path $proj "Timelines\project.json"
  if (-not (Test-Path $f)) { throw "Khong thay $f" }
  ([regex]'"main_timeline_id"\s*:\s*"([^"]+)"').Match([System.IO.File]::ReadAllText($f)).Groups[1].Value
}

function Use-Project([string]$name) {
  $script:P = Join-Path $DR $name
  if (-not (Test-Path $script:P)) { throw "Khong thay project: $script:P" }
  $script:TID = Get-TID $script:P
  Write-Host "P   = $script:P" -ForegroundColor Cyan
  Write-Host "TID = $script:TID" -ForegroundColor Cyan
}

function Show-Projects {
  Get-ChildItem $DR -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 8 | ForEach-Object {
    $meta = Join-Path $_.FullName "draft_meta_info.json"
    $name = "-"
    if (Test-Path $meta) {
      $raw = [System.IO.File]::ReadAllText($meta)
      if ($raw -match '"draft_name"\s*:\s*"([^"]*)"') { $name = $matches[1] }
    }
    [pscustomobject]@{
      Folder = $_.Name; DraftName = $name
      Modified = $_.LastWriteTime.ToString("MM-dd HH:mm")
      HasTimelines = (Test-Path (Join-Path $_.FullName "Timelines"))
    }
  } | Format-Table -AutoSize
}

function Test-Kit {
  $core = @("kb_apply.py","filter_apply.py","strip_filters.py","clone_project.py",
            "patchpath.py","fx_audit.py","check_sync.py","diff_timing.py",
            "find_ph.py","oracle_read.py","snap.py","chk_fx.py",
            "grab_frames.py","tr_profile3.py","parity_build.py")
  $tool = @("syntax.py","enum_list.py","fx_list.py","filt_enum.py","v4_mold.py",
            "lab_patch.py","audit_kit.py","cache_probe.py","patch_v8.py","pack_vendor.ps1")
  $miss = @(); $misst = @()
  foreach ($f in $core) { if (-not (Test-Path (Join-Path $T $f))) { $miss  += $f } }
  foreach ($f in $tool) { if (-not (Test-Path (Join-Path $T $f))) { $misst += $f } }
  if ($miss)  { Write-Host ("THIEU SCRIPT COT LOI: " + ($miss  -join ", ")) -ForegroundColor Red }
  else        { Write-Host "OK - du 15 script cot loi" -ForegroundColor Green }
  if ($misst) { Write-Host ("thieu cong cu tra cuu: " + ($misst -join ", ")) -ForegroundColor Yellow }
  foreach ($d in @("Test_tool_v3","snapshots","frames","testV3_CLEAN","_vendor")) {
    $p = Join-Path $T $d
    Write-Host ("  {0,-14} {1}" -f $d, $(if (Test-Path $p) {"OK"} else {"THIEU"}))
  }
  $known = $core + $tool + @("session.ps1")
  $stray = @(Get-ChildItem $T -File | Where-Object {
               ($_.Extension -eq ".py" -or $_.Extension -eq ".ps1") -and $known -notcontains $_.Name })
  if ($stray) {
    Write-Host ("  FILE LA (chua co trong Phu luc B): " + (($stray | ForEach-Object Name) -join ", ")) -ForegroundColor Yellow
    Write-Host "  -> them vao Phu luc B hoac chuyen sang _deprecated\ truoc khi dong goi kit"
  }
}

Write-Host "LAB = $T" -ForegroundColor Cyan
Write-Host "Lenh: Use-Project <ten> | Show-Projects | Stop-CapCut | Assert-CapCutOff | Test-Kit" -ForegroundColor Green