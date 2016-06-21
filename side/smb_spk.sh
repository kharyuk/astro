# ############!/usr/local/bin/expect --
#
# Automate the Horizons session required to produce a small-body SPK file.
# This script is available at ftp://ssd.jpl.nasa.gov/pub/ssd/smb_spk
#
# Version 1.4                                              (Expect v.5.18)
#
# Modification History:
#
#  DATE         Who  Change
#  -----------  ---  ---------------------------------------------------------
#  2000-Jan-14  JDG  V1.0
#  2000-Mar-13  JDG  V1.1: Non-specified local file name defaults to SPICE ID.
#  2001-Nov-20  JDG  Added comment-header, pointer to electronic version.
#  2002-May-31  JDG  Allowed 50 year SPK files.
#  2002-Oct-14  JDG  Add pattern match for "interval too small".
#  2003-Mar-19  JDG  Expand matching pattern for "interval too small" to avoid
#                     match on possible integration diagnostic message.
#                    Update comments on binary file compatibility and "CAP;"
#  2003-Mar-24  JDG  Extend SPK interval to 200 years.
#  2003-Aug-05  JDG  Add detection for "no such object record" error.
#  2004-Jan-23  JDG  V1.3: Add process for Kerberos passive FTP detection.
#                    Update SPK interval error message.
#                    Remove semi-colon detection check (now opt. in Horizons)
#                    SPK ID option added for MASL.
#  2004-Aug-09  JDG  Version 1.4: Add override range check.
#                    Add more timeout handling.
#                    Add I/O model code
#  2012-Aug-14  JDG  Updated comments slightly to reflect server move to
#                     little-endian byte-order Linux server.
#
# Key:
#  JDG= Jon.Giorgini@jpl.nasa.gov
#
# COMMAND LINE:
# -------------
#
#   smb_spk [-t|-b] [small-body] [start] [stop] [email address] {file name}
#
# EXPLANATION:
# ------------
#
#    [-t|-b] 
#             A singular flag, either "-t" or "-b"
#
#            -t create file in temporary text TRANSFER format. You
#                must later convert the file to a binary SPK form compatible
#                with your platform using utilities "tobin" or "spacit".
#
#            -b create file in native little-endian binary format.
#                Note that SPICE Toolkit versions N0052 and later have  
#                binary file reader subroutines that are platform independent 
#                and can read files regardless of the byte-order of the 
#                platform they were created on. See section "Transferring 
#                Files" below.
#
#   [small-body] 
# 
#            Horizons command to select single ASTEROID or COMET. 
#            See Horizons doc. ENCLOSE STRING IN QUOTES.
#              Examples: "DES= 1999 JM8;" (Object with designation 1999 JM8) 
#                        "12084;"         (Unnumbered ast. in record 12084)
#                        "4179;"          (Numbered asteroid 4179 Toutatis)
#                        "Golevka;"       (Named asteroid 6489 Golevka)
#
#   [start]
# 
#            Date the SPK file is to begin.
#              Examples:  2003-Feb-1 
#                         "2003-Feb-1 16:00"
#
#   [stop]
# 
#            Date the SPK file is to end. Must be more than 32 days later 
#            than [start]. 
#              Examples:  2006-Jan-12
#                         "2006-Jan-12 12:00"
#
#   [email address]
#
#            User's Internet e-mail contact address.
#              Example: joe@your.domain.name
#
#   {file name}
#
#            Optional name to give the file on your system. If not
#            specified, it uses the SPICE ID to assign a local file 
#            name in the current directory. Default form:
#               
#                 #######.bsp  (binary SPK          ... -b argument)
#                 #######.xsp  (transfer format SPK ... -t argument)
# 
#            ... where "#######" is the SPICE ID integer. For example,
#            "1000003.bsp" for 47P/Ashbrook-Jackson.
#
# EXAMPLE:
# --------
#
#   smb_spk -t "Eros;" 2000-Jan-1 2005-JAN-1 jdg@tycho.jpl.nasa.gov a433.tsp
#
#    The above generates a transfer format file called "a433.tsp" for 
# asteroid 433 Eros over the time span. 
#
#    Quotation marks are strictly necessary only for the small-body command 
# argument, which will always contain a semi-colon. This Horizons semi-colon
# notation conflicts with the UNIX shell command-line meaning, so must be
# enclosed in quotes to be passed literally into the script.
#
#    The other arguments only need quotes if they contain spaces. In such a
# case, the quotes again insure the whole argument is passed literally to the
# script without being improperly parsed into components.
#
#    For example, the date 2000-Jan-1 does NOT need quotes on the command
# line, but "2000-Jan-1 10:00" does, since the argument contains a space
# delimiter. Instead of remembering this, one could also just enclose all
# command-line arguments in quotes.
#
#    Since this example creates a text transfer file, one would then
# convert it to a binary for use on the local host machine:
#
#  tobin a433.tsp   
#
#   This command creates a binary SPK file called a433.bsp. If the "-b" 
# option had been appropriate, this step would be skipped.
#
#    To summarize the SPK file, one could then type the commands ...
#
#  commnt -r a433.bsp   (Display internal Horizons file summary)
#  brief a433.bsp       (Display file time-span)
#
# BACKGROUND:
# -----------
#
#   This script ("smb_spk") allows a user to type a single command on a 
# workstation to cause the creation of a binary OR text transfer format SPK 
# file for a comet or asteroid on that same machine. Planet and satellite
# SPK files cannot be generated this way, but are available separately. 
#
#   The script offers network transparency by connecting to the JPL Horizons
# ephemeris system, automating the interaction with it, then transferring the 
# file by FTP back to the user's local machine.
#
# REQUIREMENTS
# ------------
#
#   smb_spk is written in the Expect automation language. The Expect
# interpretation program must be present on any computer system before 
# smb_spk can run.
#
#   The Expect language is available for download at the URL:
#
#                      http://expect.nist.gov/
#
#   Expect is an extension of the TCL/TK languages, which are also required.
# The web site provides appropriate links. Installation procedures are
# provided and all packages can typically be installed and their self-check
# tests completed in about 45 minutes by following the directions.
#
#   Expect is primarily supported on UNIX platforms, but versions for other 
# systems do exist. A useful book on the language is "Exploring Expect" by
# Don Libes (ISBN 1-56592-090-2)
# 
#   Once the Expect language is installed on your machine, you may need to
# alter the very first line of this script ("#!/usr/local/bin/expect") to
# point to the installation location on that machine.  The script will then
# be able to execute.
#
#   The user's machine must be able to resolve Internet domain names and
# support FTP.
#
# USAGE
# -----
# 
#   The script will handle most errors and respond with an indicator message.
#
#   Things to keep in mind:
#
#  1) If the search parameters given on the command-line don't match 
# anything in the Horizons database, the script will cancel. Similarly, if
# several objects match, the script will also cancel.
#
#   This latter case occurs most often with comets. The Horizons database
# typically stores orbital elements for the same comet at more than one epoch
# (the different apparitions), because non-gravitational parameters such as
# outgassing may change from apparition to apparition. Thus, if requesting 
# "DES=1P;", while that does uniquely specify Halley's comet, it does not 
# indicate which of the several apparition records to use. Thus, the script 
# will cancel with a "non-unique match" message.  
#
#   Therefore, for comets, one must give the specific database record number 
# of the desired apparition. For example, "201819;" selects the 1986 Halley
# apparition. "201820;" selects the 2061 apparition. ALTERNATIVELY, one may
# add the "CAP;" specification to the command line. This will allow Horizons
# to automatically select the closest prior comet apparition solution in the 
# database. For example, "DES=1P; CAP;" will uniquely return the last comet
# Halley apparition orbit.
#
#   It may be necessary to manually connect to Horizons and look at the list
# of records it provides so as to narrow your selection.  Object selection is 
# discussed in detail in the Horizons documentation. This script doesn't 
# function any differently, but its' deliberately non-interactive approach
# doesn't provide the same level of feedback. One can check the comments 
# section of the returned SPK file to verify the object is the one expected.  
#
#   Examples of ways to specify objects:
# 
#      "DES= 1999 JM8;"
#      "Ceres"
#      "3;"    (request numbered asteroid 3 Juno)
#
#   See Horizons documentations for additional information.
#
#  2)  It takes several seconds to look up an object, then up to a couple 
# minutes to generate and transfer the SPK, depending on how much numerical 
# integration is required and the network state. 
#
#  3)  The script returns a standard exit status code (0=OK, 1=FAILED) which 
# can be checked by other calling programs. 
#
#  4)  The Horizons SPK file contains the target object with respect to the 
# Sun only. This SPK file is intended to be combined with other SPK files 
# (i.e. loaded into a kernel pool) containing the Earth, Moon, and other 
# planets to derive the ultimately required data. 
#
#  5)  File formats (adapted from Horizons documentation):
#
# Transferring SPK files:
# -----------------------
#   Within the Horizons system, SPK files are created as binary files on a  
# Linux platform. These files can be used on several popular platforms,
# but may be unreadable on others. Reasons for this include:
# 
#            1) Data-type representation (machine word-size) 
#            2) Floating point representations (IEEE or not)
#            3) Byte order (least significant byte first vs. last)
# 
#   The machine you intend to use the SPK file on thus falls into one of two
# possible categories as far as binary files:
# 
# Little-endian system:
# ---------------------
# If your system has IEEE floating-point, and is "little-endian" (stores lowest
# order byte first) like the Intel series, VAX, and Dec Alpha (for example), 
# you can use "-b"  and avoid any file conversion or speed issues.
#     
# Big-endian systems:
# -------------------
# To obtain a native SPK on a "big-endian" system (Sun Sparc, SGI, HP), use "-t" 
# on the command-line.  The binary file will be converted to a transfer file.
# Once the script completes, you must run the program 'spacit' or 'tobin' 
# convert the transfer format to a binary-compatible SPK for your machine.
#
# Platform independence:
# ----------------------
# Recent versions of the SPICE Toolkit (N0052 and higher) contain byte-order
# independent reader subroutines that translate binary SPK files created on 
# "incompatible" systems. If you are using such a version of the Toolkit, 
# there may be a small (~10%) slow-down when reading a binary file not native 
# to your platform, but there is otherwise no need to be concerned about the 
# compatibility issues described above.
#
#-----------------------------------------------------------------------------
#
 
# Establish defaults, turn debugging on or off
# --------------------------------------------
  set spk_ID_override ""
  exp_internal 0
  set timeout  60
  remove_nulls 0

# Set Horizons constants
# ----------------------
  set horizons_machine ssd.jpl.nasa.gov
  set horizons_ftp_dir pub/ssd/

# Cancel terminal negotiation (Horizons specific)
# -----------------------------------------------
  set env(TERM) no-resize-vt100

# Turn off output (set quiet 0; set quiet 1 to observe process)
# -------------------------------------------------------------
  set quiet 0
  log_user $quiet

# Command line values; check for input problems
# ---------------------------------------------
  set argc [llength $argv]
  set flag [string tolower [lindex $argv 0]]
#
# Retrieve possible SPK ID override value
# ---------------------------------------
  scan $flag "%2s%s" file_flag spk_ID_override
  set spkidlen [string length $spk_ID_override]
  if { $spkidlen != 0 } {
   if { [string match "\[1-9]\[0-9]*" $spk_ID_override] == 0 } {
     puts "\SPK ID must be positive integer!"
     exit 1
}  elseif { $spk_ID_override < 1000000 || $spk_ID_override > 9999999 } {
     puts "\SPK ID must be between 1000000 and 10000000!"
     exit 1
}  else {
     set spk_ID_override ",$spk_ID_override"
    }
}
  if {$argc < 4} {
    puts "\nMissing arguments. Usage:"
    puts { smb_spk [-t|-b] [small-body] [start] [stop] [e-mail] {file name}}
    puts " "
    exit 1 
} elseif {$argc > 6} {
    puts "\nToo many arguments. May need to use quotes.  Usage:"
    puts { smb_spk [-t|-b] [small-body] [start] [stop] [e-mail] {file name}}
    puts "Example --"
    puts { smb_spk -t "DES=1999 JM8;" "1999-JAN-2 10:00" "2015-JAN-1" "jdg@tycho.jpl.nasa.gov" 1999jm8.tsp}
    puts " "
    exit 1 
} elseif { [string first "@" [lindex $argv 4] ] < 1 } {
    puts "\nNot Internet e-mail syntax: [lindex $argv 4] " 
    puts " "
    exit 1
} elseif { $file_flag == "-t" } {
    set file_type YES 
    set ftp_type ascii
    set ftp_sufx .xsp
} elseif { $file_flag == "-b" } {
    set file_type NO
    set ftp_type binary
    set ftp_sufx .bsp
} else { 
    puts "Unknown file type: [lindex $argv 0]"
    puts { smb_spk [-t|-b] [small-body] [start] [stop] [e-mail] {file name}}
    puts " "
    exit 1
  }

  set local_file [lindex $argv 5]

# Connect to Horizons 
# -------------------
  spawn telnet $horizons_machine 6775

# Get main prompt, set up, proceed. 
# ---------------------------------
  expect { 
    timeout        {puts "No response from $horizons_machine"; exit 1} 
    "unknown host" {puts "This system cannot find $horizons_machine"; exit 1}
    "Horizons> "   {send PAGE\r} }
  set timeout 15
  expect { 
     timeout       {puts "Horizons timed out (LEVEL=1). Try later or notify JPL." ; send x\r;  exit 1} 
    "Horizons> "   {send "##1DS\r"} }
  expect { 
     timeout       {puts "Horizons timed out (LEVEL=2). Try later or notify JPL." ; send x\r;  exit 1} 
    "Horizons> "   {send [lindex $argv 1]\r} }

# Handle prompt search/select
# ---------------------------
  expect {
     timeout       {puts "Horizons timed out (LEVEL=3). Try later or notify JPL." ; send x\r;  exit 1} 
    -re ".*Continue.*: $"   { 
       send yes\r 
       expect {
          -re ".*PK.*: $"   { send S$spk_ID_override\r  }
          -re ".*lay.*: $"  { 
             send x\r 
             puts "\nCancelled -- unique small-body not found: [lindex $argv 1]"
             puts "\nObject not matched to database OR multiple matches found."
             puts " "
             exit 1
           }
      }
    }
    -re ".*such object record.*" {
       send x/r
       puts "\nNo such object record found: [lindex $argv 1]"
       puts " "
       exit 1 }
    -re ".*Select.*<cr>: $" { send S\r   }
  }

# Pick out SPICE ID
# -----------------
  if { $argc < 6 } {
    expect { 
     timeout       {puts "Horizons timed out (LEVEL=4). Try later or notify JPL." ; send x\r;  exit 1} 
     -re " Assigned SPK object ID:  (.*)\r\r\n \r\r\n Enter your" {
         scan $expect_out(1,string) "%i" spkid
         set local_file $spkid$ftp_sufx }
      } 
  }

# Process prompt for email address
# --------------------------------
  expect {
     timeout       {puts "Horizons timed out (LEVEL=5). Try later or notify JPL." ; send x\r;  exit 1} 
    -re ".*address.*: $" {
        send [lindex $argv 4]\r }
     }

# Process email confirmation
# --------------------------
  expect { 
     timeout       {puts "Horizons timed out (LEVEL=6). Try later or notify JPL." ; send x\r;  exit 1} 
    -re ".*yes.*: $"  {
       send yes\r }
     }

# Process file type
# -----------------
  expect {
     timeout       {puts "Horizons timed out (LEVEL=7). Try later or notify JPL." ; send x\r;  exit 1} 
    -re ".*YES.*: $"  {
       send $file_type\r }
     } 

# Set start date 
# --------------
  expect {
     timeout       {puts "Horizons timed out (LEVEL=8). Try later or notify JPL." ; send x\r;  exit 1} 
    -re ".*START.*: $"  {
       send [lindex $argv 2]\r }
     } 

# Handle start date error or STOP date
# ------------------------------------
  expect {
     timeout       {puts "Horizons timed out (LEVEL=9). Try later or notify JPL." ; send x\r;  exit 1} 
    -re ".*try.*: $" {
       send x\r
       puts "\nError in START date: [lindex $argv 2]"
       puts "Must be in 1900 to 2100 time span. Example: '2003-JAN-1'"
       puts " "
       exit 1 }
    -re ".*STOP.*: $" {
       send [lindex $argv 3]\r }
     }

# Handle stop date error
# ----------------------
  set timeout -1
  expect {
     timeout       {puts "Horizons timed out (LEVEL=10). Try later or notify JPL." ; send x\r;  exit 1} 
    -re ".*large.*" {
       send x\r
       puts "\nError in STOP date: [lindex $argv 3]"
       puts "Stop date must not be more than 200 years after start."
       puts " "
       exit 1 }
    -re ".*try.*" {
       send x\r
       puts "\nError in STOP date: [lindex $argv 3]"
       puts "Must be in 1900 to 2100 time span. Example: '2006-JAN-1'"
       puts " "
       exit 1 }
    -re ".*time-span too small.*" {
       send x\r
       puts "\nError in requested length: [lindex $argv 2] to [lindex $argv 3]"
       puts "Time span of file must be >= 32 days."
       puts " "
       exit 1 }
    -re ".*YES.*" {
       send NO\r }
   }

# Pick out ftp file name
# ----------------------
  set timeout 15
  expect { 
    timeout       {puts "Horizons timed out (LEVEL=11). Try later or notify JPL." ; send x\r;  exit 1} 
   -re "File name   : (.*)\r\r\n   File type" {
       set ftp_name $expect_out(1,string) }
       send "x\r"
    } 

# Retrieve file by anonymous FTP
# ------------------------------
  set timeout 30
  spawn ftp $horizons_machine
  expect {
     timeout {puts "Cancelled -- FTP server not responding."; exit 1 }
     -re "Name.*: $"
   } 
  send "anonymous\r"
  expect "Password:"

# Next bit is HP-UNIX work-around
# -------------------------------
  set oldpw [lindex $argv 4]
  if [regsub @ $oldpw '\134@' pw] {
    set newpw $pw
  } else {
    set newpw $oldpw
  }
  send $newpw\r

  expect {
    "Login failed." { 
       send "quit\r" 
       puts "\nFTP login failed -- must use full Internet e-mail address."
       puts "Example:  'joe@your.domain.name'"
       puts " "
       exit 1 }
    "ftp> " { send $ftp_type\r    } 
   }
  expect "ftp> " { send "cd pub/ssd\r" }

  set timeout -1
  expect "ftp> " { send "get $ftp_name $local_file\r" }
  expect {
     -re ".*No such.*" {
       puts "\nError -- cannot find $ftp_name on server."
       puts " "
       exit 1 }
     -re ".*425 Can't build data connection.*" {
       expect "ftp> " { send passive\r }
       expect "ftp> " { send "get $ftp_name $local_file\r" }
       exit 0 }
     "ftp> " { send "quit\r" }
   }

# Finished, set status code 
# -------------------------
  exit 0
