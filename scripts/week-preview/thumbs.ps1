# Makes small JPEG thumbnails of every slide for the weekly review page.
# Usage: powershell -File thumbs.ps1 -Start 2026-10-19 [-Days 7]
# Reads posts/<date>/<n>_916.jpg (falls back to <n>.jpg), writes thumbs/<date>/<n>.jpg (540 px wide).
param([Parameter(Mandatory = $true)][string]$Start, [int]$Days = 7, [int]$Width = 540)
Add-Type -AssemblyName System.Drawing
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path (Join-Path $here "..\..")
$enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
$p = New-Object System.Drawing.Imaging.EncoderParameters 1
$p.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 82L
$thumbs = Join-Path $here "thumbs"
if (Test-Path $thumbs) { Remove-Item -Recurse -Force $thumbs }
$d0 = [datetime]::ParseExact($Start, "yyyy-MM-dd", $null)
for ($i = 0; $i -lt $Days; $i++) {
  $date = $d0.AddDays($i).ToString("yyyy-MM-dd")
  $src = Join-Path $root "posts\$date"
  if (-not (Test-Path $src)) { continue }
  $out = Join-Path $thumbs $date
  New-Item -ItemType Directory -Force $out | Out-Null
  $nums = Get-ChildItem $src -Filter "*.jpg" | ForEach-Object { if ($_.BaseName -match '^(\d+)') { [int]$Matches[1] } } | Sort-Object -Unique
  foreach ($n in $nums) {
    $f = Join-Path $src "${n}_916.jpg"
    if (-not (Test-Path $f)) { $f = Join-Path $src "$n.jpg" }
    $img = [System.Drawing.Image]::FromFile($f)
    $h = [int][Math]::Round($img.Height * $Width / $img.Width)
    $bmp = New-Object System.Drawing.Bitmap $Width, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.DrawImage($img, 0, 0, $Width, $h)
    $g.Dispose(); $img.Dispose()
    $bmp.Save((Join-Path $out ("{0:D2}.jpg" -f $n)), $enc, $p); $bmp.Dispose()
  }
  "thumbs $date : $($nums.Count) slides"
}
