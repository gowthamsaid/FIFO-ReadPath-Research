# Independent physical-placement fingerprint for paired-seed verification.
# This script writes ONLY to the runner's temporary file, which the caller
# hashes and deletes before uploading any artifacts.
set db_path $::env(READPATH_PLACE_DB)
set output_path $::env(READPATH_PLACE_LIST)
if {![file exists $db_path]} {error "Placement database missing"}
read_db $db_path
set block [ord::get_db_block]
set rows {}
foreach inst [$block getInsts] {
  set location [$inst getLocation]
  if {[llength $location] != 2} {error "Missing instance coordinates"}
  lappend rows "[$inst getName]\t[lindex $location 0]\t[lindex $location 1]\t[$inst getOrient]"
}
if {[llength $rows] == 0} {error "Empty placed design"}
set fd [open $output_path w]
foreach r [lsort -ascii $rows] {puts $fd $r}
close $fd
puts "PLACEMENT_FINGERPRINT: [llength $rows] instances; coordinates hashed and deleted by caller"
