#!/usr/bin/env bash
set -euo pipefail

echo "Python: $(python3 --version 2>&1)"
echo "Java: $(java -version 2>&1 | head -1)"
echo "Hadoop: $(hadoop version 2>&1 | head -1)"
echo "Spark: $(spark-submit --version 2>&1 | awk '/version [0-9]/{print; exit}')"
echo "Default filesystem: $(hdfs getconf -confKey fs.defaultFS 2>/dev/null)"
echo
echo "Java daemons:"
jps
echo

if jps | grep -Eq 'NameNode|DataNode'; then
  echo "HDFS daemons detected."
else
  echo "HDFS daemons are not running. Start the configured Hadoop cluster before HDFS jobs."
fi

