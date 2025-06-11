#!/bin/zsh

# Kill children on exit
trap "trap - SIGTERM && pkill -P $$ && exit" SIGINT SIGTERM EXIT

unset DISPLAY
unset WAYLAND_DISPLAY
mkdir -p /tmp/fuzz-logs
outerlog=/tmp/fuzz-logs/outerlog-$(date '+%Y%m%d%H%M%S').log

WLR_RENDER_DRM_DEVICE=/dev/dri/renderD128 WLR_BACKENDS=headless wayfire -c miniconfig.ini &> $outerlog &
sleep 2
display=$(grep "Using socket name" $outerlog | cut -d ' ' -f 9)

rm -rf $1/**/*.png
rm -rf $1/**/*.log
WAYLAND_DISPLAY=$display ./run_tests.sh "$@"

