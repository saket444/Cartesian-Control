# Cartesian-Control

ROS 2 Humble + MoveIt 2 Cartesian control for the UR10e, in Gazebo simulation.
Includes MoveIt Cartesian path planning (drag-and-plan in RViz) and MoveIt Servo
real-time jogging via keyboard teleop.

## Structure

- `src/ur10e_teleop/` — this repo's own package: MoveIt Servo config, launch file,
  and a keyboard-to-Servo twist relay node
- `src/Universal_Robots_ROS2_Driver/`, `src/Universal_Robots_ROS2_Description/`,
  `src/Universal_Robots_ROS2_GZ_Simulation/` — Universal Robots' official packages,
  included as git submodules (not duplicated in this repo)

## Setup

### 1. Clone with submodules

```bash
git clone --recurse-submodules https://github.com/saket444/Cartesian-Control.git ~/ur10e_ws
```

If you already cloned without `--recurse-submodules`:
```bash
cd ~/ur10e_ws
git submodule update --init --recursive
```

### 2. Install dependencies

```bash
sudo apt update
sudo apt install -y \
  ros-humble-moveit \
  ros-humble-moveit-servo \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-ros-gz \
  ros-humble-teleop-twist-keyboard

cd ~/ur10e_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### 3. Build

```bash
cd ~/ur10e_ws
colcon build --symlink-install
```

## Running

Source in every new terminal:
```bash
source /opt/ros/humble/setup.bash
source ~/ur10e_ws/install/setup.bash
```

**Terminal 1 — Gazebo sim**
```bash
ros2 launch ur_simulation_gz ur_sim_control.launch.py ur_type:=ur10e launch_rviz:=false
```

**Terminal 2 — MoveIt + RViz**
```bash
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur10e use_sim_time:=true launch_rviz:=true
```

Before starting Servo, move the arm to a bent (non-singular) pose in RViz — drag
the interactive marker, click **Plan**, then **Execute**. The default home pose
is a wrist singularity and will make Servo emergency-stop on startup.

**Terminal 3 — MoveIt Servo**
```bash
ros2 launch ur10e_teleop servo.launch.py
```

**Terminal 4 — start Servo + twist relay**
```bash
ros2 service call /servo_node/start_servo std_srvs/srv/Trigger {}
ros2 run ur10e_teleop twist_relay
```

**Terminal 5 — keyboard teleop**
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/keyboard_cmd_vel
```

Keys: `i`/`,` forward/back, `j`/`l` rotate left/right, `t`/`b` up/down. Press
`x` a few times first to reduce linear speed — default values are tuned for a
mobile base, not a 6-DOF arm.

## Known issues / gotchas

- **Servo parameter YAML requires the `ros__parameters` wrapper** — a flat YAML
  without `/**:` / `ros__parameters:` nesting will crash the node on launch.
- **Servo and MoveGroup can't both command the controller at once.** If RViz's
  Plan/Execute stops working after Servo is running, stop Servo, execute via
  RViz, then restart Servo.
- **Singular poses (e.g. straight-up home) halt Servo** — status code `2` on
  `/servo_node/status` means "decelerate/halt for singularity." Always bend the
  arm into a non-singular pose before starting Servo.
- No kinematics plugin is currently configured for Servo, so it falls back to
  inverse-Jacobian IK. Pointing it at `ur_moveit_config`'s `kinematics.yaml`
  would give more accurate singularity detection — not yet done in this repo.
