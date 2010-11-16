
set -e # Break on error
shopt -s nullglob # Expand foo* to nothing if nothing matches

# Names of database backends that can be benchmarked.
BACKENDS="filesystem postgresql"

# Location of the CalendarServer source.  Will automatically be
# updated to the appropriate version, config edited to use the right
# backend, and PID files will be discovered beneath it.
SOURCE=~/Projects/CalendarServer/trunk

# The plist the server will respect.
CONF=$SOURCE/conf/caldavd-dev.plist

# Names of benchmarks we can run.
BENCHMARKS="find_calendars event_move event_delete_attendee event_add_attendee event_change_date event_change_summary event_delete vfreebusy event"

# Names of metrics we can collect.
STATISTICS=(HTTP SQL read write pagein pageout)

# Codespeed add-result location.
ADDURL=http://localhost:8000/result/add/

EXTRACT=$(PWD)/extractconf

# Change the config beneath $SOURCE to use a particular database backend.
function setbackend() {
  ./setbackend $SOURCE/conf/caldavd-test.plist $1 > $CONF
}

# Clean up $SOURCE, update to the specified revision, and build the
# extensions (in-place).
function update_and_build() {
  pushd $SOURCE
  stop
  svn st --no-ignore | grep '^[?I]' | cut -c9- | xargs rm -r
  svn up -r$1 .
  python setup.py build_ext -i
  popd
}

# Start a CalendarServer in the current directory.  Only return after
# the specified number of slave processes have written their PID files
# (which is only a weak metric for "the server is ready to use").
function start() {
  NUM_INSTANCES=$1
  PIDDIR=$SOURCE/$($EXTRACT $CONF ServerRoot)/$($EXTRACT $CONF RunRoot)

  shift
  ./run -d -n $*
  while sleep 2; do
    instances=($PIDDIR/*instance*)
    if [ "${#instances[*]}" -eq "$NUM_INSTANCES" ]; then
      echo "instance pid files: ${instances[*]}"
      break
    fi
  done
}

# Stop the CalendarServer in the current directory.  Only return after
# it has exited.
function stop() {
  PIDFILE=$SOURCE/$($EXTRACT $CONF ServerRoot)/$($EXTRACT $CONF RunRoot)/$($EXTRACT $CONF PIDFile)
  ./run -k || true
  while :; do
      pid=$(cat $PIDFILE 2>/dev/null || true)
      if [ ! -e $PIDFILE ]; then
	  break
      fi
      if ! $(kill -0 $pid); then
	  break
      fi
    echo "Waiting for server to exit..."
    sleep 1
  done
}
