#!/bin/bash
# V-06 procedure on the bench: record, publish TWIST(v_r, 0) at f_cmd, stop the publisher, three times.
source /opt/ros/jazzy/setup.bash && source ~/robot_ws/install/setup.bash && source ~/final_v1.0/install/setup.bash && export FASTDDS_BUILTIN_TRANSPORTS=UDPv4
BAG=~/final_v1.0/bags/v06
rm -rf $BAG
AGENT_BIN=$(ros2 pkg prefix micro_ros_agent)/lib/micro_ros_agent/micro_ros_agent
$AGENT_BIN serial --dev /dev/ttyAMA0 -b 921600 > /dev/null 2>&1 & AGENT=$!
sleep 4
ros2 bag record -s mcap --storage-preset-profile zstd_fast -o $BAG /controller/command /controller/state /controller/instrumentation > ~/final_v1.0/bags/v06_record.log 2>&1 & RECORD=$!
sleep 3
for run in $(seq 30); do
  ros2 topic pub -w 2 -r 20 --qos-reliability best_effort --qos-durability volatile --qos-depth 1 \
    /controller/command robot_interfaces/msg/Command "{behavior: 0, linear: 0.2, angular: 0.0}" > /dev/null 2>&1 & PUB=$!
  sleep 5                       # step 2: steady state
  kill -TERM $PUB; wait $PUB 2>/dev/null   # step 3: stop the publisher
  sleep 3                       # step 4: wait for the stop
done
kill -TERM $RECORD; wait $RECORD 2>/dev/null
kill -TERM $AGENT; wait $AGENT 2>/dev/null
ls -la $BAG; du -sh $BAG
ros2 run robot_verification check_v06 $BAG; echo "exit=$?"
