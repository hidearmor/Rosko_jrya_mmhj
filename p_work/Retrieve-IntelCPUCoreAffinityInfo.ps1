# source: https://gist.github.com/vdepagter/7e08f6ff148f48780879d91f7052ebd4#file-retrieve-intelcpucoreaffinityinfo-ps1

# Retrieve-IntelCPUCoreAffinityInfo.ps1, 20240524 VdP
# This script queries Intel ARK website for processor information,
# then uses retrieved Performance & Efficiency Core counts to calculate some common affinity masks and decimal values:
#   Only Perf Cores
#   Only Perf Cores (without hyperthreading)
#   Only Efficiency Cores
# These values can then be used to limit a process to use only particular CPU cores (set CPU affinity)
If (-not (Get-Module -ErrorAction Ignore -ListAvailable PowerHTML)) { Install-Module PowerHTML -Force }
$ProcessorSearchString = (Get-CimInstance -ClassName Win32_Processor | Select -ExpandProperty Name) -Replace ' CPU @.*' -Replace '.* ' #'.* (i[0-9]\-)?'
#$ProcessorSearchString = '12th Gen Intel(R) Core(TM) i7-1255U' -Replace '.* ' #'.* (i[0-9]\-)?'
#$ProcessorSearchString = 'i9-13900'
#$ProcessorSearchString = '13900K'
#$Uri = 'https://www.intel.com/content/www/us/en/search.html?ws=typeahead#q=$($ProcessorSearchString)&sort=relevancy&f:@tabfilter=[Products]&f:Products=[Processors]'
#$Uri = "https://ark.intel.com/search/AutoComplete?term=$($ProcessorSearchString)"
$Uri = "https://ark.intel.com/content/www/us/en/ark/search.html?_charset_=UTF-8&q=$($ProcessorSearchString)"
$UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
$ProgressPreference = 'SilentlyContinue'
Write-Host -b black -f yellow "ProcessorSearchString: $ProcessorSearchString`nQuerying $Uri`n"
$wrSearch = Invoke-WebRequest -Uri $Uri -Headers @{"accept"="text/html";"accept-language"="en-US,en";"referer"=$Uri} -UserAgent $UserAgent -UseBasicParsing
If ($wrSearch.InputFields | ? value -match '^/content/www/us/en/ark/products') {
	$productPage = $wrSearch.InputFields | ? value -match '^/content/www/us/en/ark/products' | Select -ExpandProperty value
	Write-Host -b black -f yellow  "Exact product match found, using: $productPage"
} ElseIf ($wrSearch.Links | ? href -match '^/content/www/us/en/ark/products') {
	Write-Host -b black -f yellow "Multiple product matches found:"
	$wrSearch.Links | ? href -match '^/content/www/us/en/ark/products' | %{ Write-Host "`t$($_.href)" }
	$productPage = $wrSearch.Links | ?{$_.href -match ($ProcessorSearchString -Replace '.* ' -Replace '\-')+'-'} | Select -ExpandProperty href
	If (!$productPage) { $productPage = $wrSearch.Links | ? href -match '^/content/www/us/en/ark/products' | Select -First 1 | Select -ExpandProperty href }
	Write-Host -b black -f yellow "Using $($productPage)"
} Else {
	Write-Host -b black -f red "Could not find product match!"
	Clear-Variable productPage -ea 0
}
If ($productPage) {
	try {
		If (Test-Path $env:tmp\$(Split-Path $productPage -Leaf)) {
			Write-Host -b black -f yellow "Previously queried this CPU. Reading from file $($env:tmp)\$(Split-Path $productPage -Leaf)`n"
			$wr = @{Content=Get-Content -Raw $env:tmp\$(Split-Path $productPage -Leaf)}
		} Else {
			$wr = Invoke-WebRequest -Uri "$($Uri -Replace '(?<![:/])/.*')$productPage" -Headers @{"accept"="text/html";"accept-language"="en-US,en";"referer"=$Uri} -UserAgent $UserAgent -UseBasicParsing
		}
		$doc = ConvertFrom-Html $wr.Content
		$ProductName = $doc.SelectNodes("/html/body//div[contains(@class,'product-family-title-text')]/h1").innerText.Trim()
		$CoreCount   = [int]$doc.SelectNodes("/html/body//span[@data-key='CoreCount']").innerText.Trim()
		$PerfCores   = [int]$doc.SelectNodes("/html/body//span[@data-key='PerfCoreCount']").innerText.Trim()
		$EffCores    = [int]$doc.SelectNodes("/html/body//span[@data-key='EffCoreCount']").innerText.Trim()
		$ThreadCount = [int]$doc.SelectNodes("/html/body//span[@data-key='ThreadCount']").innerText.Trim()
		If ($CoreCount -gt 0 -and -not (Test-Path $env:tmp\$(Split-Path $productPage -Leaf))) {
			Write-Host -b black -f yellow "Looks like we successfully read out CoreCount. Saving product page for future re-use.`n"
			$wr.Content | Out-File $env:tmp\$(Split-Path $productPage -Leaf)
		}
		If ($ThreadCount -gt $CoreCount) { $HyperThreading = $True }
		If (($PerfCores*2+$EffCores) -eq $ThreadCount) { # We're expecting P-cores to provide HT (2 threads), while E-cores should only have 1 thread.
			If ($HyperThreading) {
				$OnlyPCoresAffinityMask          = ((1..($PerfCores*2) | %{'1'}) -Join '').PadLeft($ThreadCount,'0')
				$OnlyPCoresWithoutHTAffinityMask = ((1..$PerfCores | %{'01'}) -Join '').PadLeft($ThreadCount,'0')
				$OnlyEffCoresAffinityMask        = ((1..$PerfCores | %{'00'}) -Join '').PadLeft($ThreadCount,'1')
			} Else {
				$OnlyPCoresAffinityMask          = ((1..$PerfCores | %{'1'}) -Join '').PadLeft($ThreadCount,'0')
				$OnlyPCoresWithoutHTAffinityMask = $OnlyPCoresAffinityMask
				$OnlyEffCoresAffinityMask        = ((1..$PerfCores | %{'0'}) -Join '').PadLeft($ThreadCount,'1')
			}
			$OnlyPCoresAffinity          = [Convert]::ToInt64($OnlyPCoresAffinityMask,2)
			$OnlyPCoresWithoutHTAffinity = [Convert]::ToInt64($OnlyPCoresWithoutHTAffinityMask,2)
			$OnlyEffCoresAffinity        = [Convert]::ToInt64($OnlyEffCoresAffinityMask,2)
		} Else { Write-Host -b black -f red "ERROR: Logic validation check failed. P-Cores*2 + EffCores doesn't equal ThreadCount." }
		'ProcessorSearchString','ProductName','CoreCount','PerfCores','EffCores','ThreadCount','HyperThreading',`
			'OnlyPCoresAffinityMask','OnlyPCoresWithoutHTAffinityMask','OnlyEffCoresAffinityMask',`
			'OnlyPCoresAffinity','OnlyPCoresWithoutHTAffinity','OnlyEffCoresAffinity' | %{ Write-Host -b black -f yellow "$($_.PadLeft(32)): $(Get-Variable $_ | Select -ExpandProperty Value)" }
	} catch { Write-Host "Error: $($Error[0])" }
} Else {
	Write-Host -b black -f red "Did not find product page, can't continue."
}

# Get-Process WmiPrvSE | %{ $_.ProcessorAffinity = $OnlyEffCoresAffinityMask }