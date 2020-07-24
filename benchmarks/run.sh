#!/usr/bin/env bash
#
# run.sh
#
# Run the benchmarks for containerlog and generate a plot.
#

containerlog_version=$(python -c 'import containerlog; print(containerlog.__version__)')

echo "Running benchmarks for containerlog@${containerlog_version}, this may take a few minutes"

echo "  • benchmark std logger"
python benchmark_std.py > std_results.txt

echo "  • benchmark containerlog"
python benchmark_containerlog.py > containerlog_results.txt

echo "  • benchmark std proxy"
python benchmark_std_proxy.py > std_proxy_results.txt

echo "  • generating artifacts"
python plot.py "${containerlog_version}"
retVal=$?
if [ $retVal -ne 0 ]; then
    echo "Error"
    exit 1
fi

rm std_results.txt
rm containerlog_results.txt
rm std_proxy_results.txt

echo ""
echo "Done. The following artifacts have been generated:"
echo " • benchmark-containerlog-${containerlog_version}.png : Plot comparing benchmark data"
echo " • benchmark-containerlog-${containerlog_version}.md  : Table comparing benchmark data"
