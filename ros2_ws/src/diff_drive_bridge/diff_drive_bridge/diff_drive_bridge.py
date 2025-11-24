#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32

import tf_transformations
from tf2_ros import TransformBroadcaster

import math

class DiffDriveController(Node):
    def __init__(self):
        super().__init__("diff_drive_controller")

        # ---------------------------
        #  Declare and retrieve parameters
        # ---------------------------

        # Robot geometry
        self.declare_parameter("wheel_separation", 0.41)
        self.declare_parameter("wheel_radius", 0.122)

        # Robot center offset along the x-axis relative to the wheel axle midpoint
        # Positive if the "base_link" is ahead of the wheel axis.
        self.declare_parameter("rotation_offset_x", 0.165)

        # Joints
        self.declare_parameter("left_wheel_joint", "base_left_wheel_joint")
        self.declare_parameter("right_wheel_joint", "base_right_wheel_joint")

        # Frames
        self.declare_parameter("odom_frame_id", "odom")
        self.declare_parameter("base_frame_id", "base_link")
        self.declare_parameter("left_wheel_frame_id", "left_wheel_link")
        self.declare_parameter("right_wheel_frame_id", "right_wheel_link")

        # Wheel link offsets relative to base_frame_id (used for TF)
        self.declare_parameter("left_wheel_offset_x", 0.15)
        self.declare_parameter("left_wheel_offset_y", 0.21)
        self.declare_parameter("left_wheel_offset_z", 0.0)
        self.declare_parameter("right_wheel_offset_x", 0.15)
        self.declare_parameter("right_wheel_offset_y", -0.21)
        self.declare_parameter("right_wheel_offset_z", 0.0)

        # Topics
        self.declare_parameter("cmd_vel_topic", "/diff_drive_controller/cmd_vel")
        self.declare_parameter("left_encoder_topic", "/left_wheel/encoder")
        self.declare_parameter("right_encoder_topic", "/right_wheel/encoder")
        self.declare_parameter("left_cmd_vel_topic", "/left_wheel/cmd_vel")
        self.declare_parameter("right_cmd_vel_topic", "/right_wheel/cmd_vel")
        self.declare_parameter("joint_states_topic", "/joint_states")
        self.declare_parameter("odom_topic", "/odom")

        # Update internal variables from parameters
        self.wheel_separation = self.get_parameter("wheel_separation").value
        self.wheel_radius = self.get_parameter("wheel_radius").value
        self.rotation_offset_x = self.get_parameter("rotation_offset_x").value

        self.left_wheel_joint = self.get_parameter("left_wheel_joint").value
        self.right_wheel_joint = self.get_parameter("right_wheel_joint").value

        self.odom_frame_id = self.get_parameter("odom_frame_id").value
        self.base_frame_id = self.get_parameter("base_frame_id").value
        self.left_wheel_frame_id = self.get_parameter("left_wheel_frame_id").value
        self.right_wheel_frame_id = self.get_parameter("right_wheel_frame_id").value

        self.left_wheel_offset_x = self.get_parameter("left_wheel_offset_x").value
        self.left_wheel_offset_y = self.get_parameter("left_wheel_offset_y").value
        self.left_wheel_offset_z = self.get_parameter("left_wheel_offset_z").value
        self.right_wheel_offset_x = self.get_parameter("right_wheel_offset_x").value
        self.right_wheel_offset_y = self.get_parameter("right_wheel_offset_y").value
        self.right_wheel_offset_z = self.get_parameter("right_wheel_offset_z").value

        self.cmd_vel_topic = self.get_parameter("cmd_vel_topic").value
        self.left_encoder_topic = self.get_parameter("left_encoder_topic").value
        self.right_encoder_topic = self.get_parameter("right_encoder_topic").value
        self.left_cmd_vel_topic = self.get_parameter("left_cmd_vel_topic").value
        self.right_cmd_vel_topic = self.get_parameter("right_cmd_vel_topic").value
        self.joint_states_topic = self.get_parameter("joint_states_topic").value
        self.odom_topic = self.get_parameter("odom_topic").value

        # Print out all parameters for debugging
        self.get_logger().info(
            f"Parameters:\n"
            f"  wheel_separation: {self.wheel_separation}\n"
            f"  wheel_radius: {self.wheel_radius}\n"
            f"  rotation_offset_x: {self.rotation_offset_x}\n"
            f"  left_wheel_joint: {self.left_wheel_joint}\n"
            f"  right_wheel_joint: {self.right_wheel_joint}\n"
            f"  odom_frame_id: {self.odom_frame_id}\n"
            f"  base_frame_id: {self.base_frame_id}\n"
            f"  left_wheel_frame_id: {self.left_wheel_frame_id}\n"
            f"  right_wheel_frame_id: {self.right_wheel_frame_id}\n"
            f"  left_wheel_offset: ({self.left_wheel_offset_x},"
            f" {self.left_wheel_offset_y}, {self.left_wheel_offset_z})\n"
            f"  right_wheel_offset: ({self.right_wheel_offset_x},"
            f" {self.right_wheel_offset_y}, {self.right_wheel_offset_z})\n"
            f"  cmd_vel_topic: {self.cmd_vel_topic}\n"
            f"  left_encoder_topic: {self.left_encoder_topic}\n"
            f"  right_encoder_topic: {self.right_encoder_topic}\n"
            f"  left_cmd_vel_topic: {self.left_cmd_vel_topic}\n"
            f"  right_cmd_vel_topic: {self.right_cmd_vel_topic}\n"
            f"  joint_states_topic: {self.joint_states_topic}\n"
            f"  odom_topic: {self.odom_topic}\n"
        )

        # -----------------------------------------------------
        # Subscriptions and Publications
        # -----------------------------------------------------

        # Subscribe to cmd_vel
        self.create_subscription(Twist, self.cmd_vel_topic, self.cmd_vel_callback, 10)

        # Subscribe to encoders
        self.create_subscription(Float32, self.left_encoder_topic, self.left_encoder_callback, 10)
        self.create_subscription(Float32, self.right_encoder_topic, self.right_encoder_callback, 10)

        # Create publishers
        self.left_cmd_pub = self.create_publisher(Float32, self.left_cmd_vel_topic, 10)
        self.right_cmd_pub = self.create_publisher(Float32, self.right_cmd_vel_topic, 10)
        self.joint_state_pub = self.create_publisher(JointState, self.joint_states_topic, 10)
        self.odom_pub = self.create_publisher(Odometry, self.odom_topic, 10)

        # TF broadcaster (odom → base_link)
        self.tf_broadcaster = TransformBroadcaster(self)

        # -----------------------------------------------------
        # Internal state
        # -----------------------------------------------------
        self.left_wheel_position = 0.0
        self.right_wheel_position = 0.0
        self.left_wheel_velocity = 0.0
        self.right_wheel_velocity = 0.0
        self.left_last_encoder = 0.0
        self.right_last_encoder = 0.0
        self.last_time_encoders = self.get_clock().now()

        # Odometry state
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        # Timer to publish joint states & odometry (20 Hz)
        self.timer_period = 0.05  # seconds
        self.publish_timer = self.create_timer(self.timer_period, self.update_and_publish)

        self.get_logger().info("DiffDriveController node has been initialized.")

    def cmd_vel_callback(self, msg: Twist):
        """
        Convert cmd_vel (which is interpreted as the desired velocity/omega
        of the robot’s 'center' frame) into left and right wheel velocity 
        commands (in m/s at the wheel perimeter).

        If rotation_offset_x > 0, it means the base_link is ahead of the 
        wheel axle, so the wheels must move a bit faster than the 
        commanded linear.x to achieve that center velocity.
        """
        linear_speed = msg.linear.x
        angular_speed = msg.angular.z

        # Half the distance between wheels
        half_base = 0.5 * self.wheel_separation

        # Add the offset contribution: v_effective = v_center + offset_x * w
        # Then apply ± half_base * angular_speed for left/right wheels
        effective_linear = linear_speed + self.rotation_offset_x * angular_speed

        left_speed = effective_linear - half_base * angular_speed
        right_speed = effective_linear + half_base * angular_speed

        # Publish wheel velocity commands
        self.left_cmd_pub.publish(Float32(data=left_speed))
        self.right_cmd_pub.publish(Float32(data=right_speed))

    def left_encoder_callback(self, msg: Float32):
        """ Update left wheel position from encoder (in meters or radians, 
            but be consistent across your system). """
        self.left_wheel_position = msg.data

    def right_encoder_callback(self, msg: Float32):
        """ Update right wheel position from encoder (in meters or radians). """
        self.right_wheel_position = msg.data

    def update_and_publish(self):
        """ 
        Update wheel velocities, compute odometry, publish joint states and odometry,
        then broadcast TF transforms.
        """
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time_encoders).nanoseconds * 1e-9

        # Avoid division by zero
        if dt <= 0.0:
            return

        # Compute wheel velocities based on change in encoder positions
        delta_left = self.left_wheel_position - self.left_last_encoder
        delta_right = self.right_wheel_position - self.right_last_encoder
        self.left_wheel_velocity = delta_left / dt
        self.right_wheel_velocity = delta_right / dt

        # Update last encoder readings
        self.left_last_encoder = self.left_wheel_position
        self.right_last_encoder = self.right_wheel_position
        self.last_time_encoders = current_time

        # -----------------------------------------------------
        # Odometry calculation
        # -----------------------------------------------------
        # Assuming the encoders already give linear distance in meters.
        dist_left = delta_left   # in meters
        dist_right = delta_right # in meters

        # Distance traveled by the midpoint between wheels
        dist_mid = 0.5 * (dist_left + dist_right)

        # Heading change
        dtheta = (dist_right - dist_left) / self.wheel_separation

        # The base link is offset by rotation_offset_x from the midpoint
        # => The center displacement = dist_mid - (rotation_offset_x * dtheta)
        dist_center = dist_mid - self.rotation_offset_x * dtheta

        # Update heading
        old_yaw = self.yaw
        self.yaw += dtheta
        self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))  # normalize

        # Compute incremental pose update
        heading = old_yaw + 0.5 * dtheta
        self.x += dist_center * math.cos(heading)
        self.y += dist_center * math.sin(heading)

        # -----------------------------------------------------
        # Publish joint states
        # -----------------------------------------------------
        self.publish_joint_states(current_time)

        # -----------------------------------------------------
        # Publish odometry
        # -----------------------------------------------------
        vx = dist_center / dt
        vy = 0.0
        vtheta = dtheta / dt
        self.publish_odometry(current_time, vx, vy, vtheta)

        # -----------------------------------------------------
        # Publish TF transforms
        # -----------------------------------------------------
        self.publish_tf(current_time)

    def publish_joint_states(self, current_time):
        """
        Publish the joint states. If your encoders are in meters, convert to radians
        by dividing by the wheel radius. If your encoders are already in radians,
        you can publish directly.
        """
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = current_time.to_msg()
        joint_state_msg.name = [self.left_wheel_joint, self.right_wheel_joint]

        # Convert position from meters to radians if needed
        left_wheel_angle = self.left_wheel_position / self.wheel_radius
        right_wheel_angle = self.right_wheel_position / self.wheel_radius

        # Convert velocity from m/s to rad/s if needed
        left_wheel_velocity = self.left_wheel_velocity / self.wheel_radius
        right_wheel_velocity = self.right_wheel_velocity / self.wheel_radius

        joint_state_msg.position = [left_wheel_angle, right_wheel_angle]
        joint_state_msg.velocity = [left_wheel_velocity, right_wheel_velocity]
        joint_state_msg.effort = [0.0, 0.0]

        self.joint_state_pub.publish(joint_state_msg)

    def publish_odometry(self, current_time, vx, vy, vtheta):
        """ Publish odometry message in the chosen odom frame. """
        odom_msg = Odometry()
        odom_msg.header.stamp = current_time.to_msg()
        odom_msg.header.frame_id = self.odom_frame_id
        odom_msg.child_frame_id = self.base_frame_id

        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y

        q = tf_transformations.quaternion_from_euler(0.0, 0.0, self.yaw)
        odom_msg.pose.pose.orientation.x = q[0]
        odom_msg.pose.pose.orientation.y = q[1]
        odom_msg.pose.pose.orientation.z = q[2]
        odom_msg.pose.pose.orientation.w = q[3]

        odom_msg.twist.twist.linear.x = vx
        odom_msg.twist.twist.linear.y = vy
        odom_msg.twist.twist.angular.z = vtheta

        self.odom_pub.publish(odom_msg)

    def publish_tf(self, current_time):
        """
        Publish transforms:
          1) odom_frame_id -> base_frame_id
          2) base_frame_id -> left_wheel_frame_id
          3) base_frame_id -> right_wheel_frame_id
        """
        # odom -> base_link
        t = TransformStamped()
        t.header.stamp = current_time.to_msg()
        t.header.frame_id = self.odom_frame_id
        t.child_frame_id = self.base_frame_id

        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0

        q = tf_transformations.quaternion_from_euler(0.0, 0.0, self.yaw)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        self.tf_broadcaster.sendTransform(t)

        # Wheel rotations (convert from meters to rad if needed)
        left_wheel_rotation = self.left_wheel_position / self.wheel_radius
        right_wheel_rotation = self.right_wheel_position / self.wheel_radius

        # base -> left wheel
        left_tf = TransformStamped()
        left_tf.header.stamp = current_time.to_msg()
        left_tf.header.frame_id = self.base_frame_id
        left_tf.child_frame_id = self.left_wheel_frame_id
        left_tf.transform.translation.x = self.left_wheel_offset_x
        left_tf.transform.translation.y = self.left_wheel_offset_y
        left_tf.transform.translation.z = self.left_wheel_offset_z

        q_left = tf_transformations.quaternion_from_euler(0.0, left_wheel_rotation, 0.0)
        left_tf.transform.rotation.x = q_left[0]
        left_tf.transform.rotation.y = q_left[1]
        left_tf.transform.rotation.z = q_left[2]
        left_tf.transform.rotation.w = q_left[3]

        self.tf_broadcaster.sendTransform(left_tf)

        # base -> right wheel
        right_tf = TransformStamped()
        right_tf.header.stamp = current_time.to_msg()
        right_tf.header.frame_id = self.base_frame_id
        right_tf.child_frame_id = self.right_wheel_frame_id
        right_tf.transform.translation.x = self.right_wheel_offset_x
        right_tf.transform.translation.y = self.right_wheel_offset_y
        right_tf.transform.translation.z = self.right_wheel_offset_z

        q_right = tf_transformations.quaternion_from_euler(0.0, right_wheel_rotation, 0.0)
        right_tf.transform.rotation.x = q_right[0]
        right_tf.transform.rotation.y = q_right[1]
        right_tf.transform.rotation.z = q_right[2]
        right_tf.transform.rotation.w = q_right[3]

        self.tf_broadcaster.sendTransform(right_tf)


def main(args=None):
    rclpy.init(args=args)
    node = DiffDriveController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
