#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp" // Include the message header


class imu_correction_node : public rclcpp::Node
{
public:
    imu_correction_node() : Node("imu_correction_node")
    {
        // Subscribe to the /imu/data topic
        subscription_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "/imu/data", 1,
            std::bind(&imu_correction_node::imuCallback, this, std::placeholders::_1));

        // Publish to the /imu/data/corrected topic
        publisher_ = this->create_publisher<sensor_msgs::msg::Imu>("/imu/data/corrected", 1);
    }

private:
    // Callback function to handle incoming IMU messages
    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        // Create a new IMU message for republishing
        auto corrected_msg = std::make_shared<sensor_msgs::msg::Imu>();
        
        // Copy the header
        corrected_msg->header.frame_id = "camera_imu_frame";//msg->header;
        // Copy the timestamp
        corrected_msg->header.stamp = msg->header.stamp;
        // Copy the orientation
        corrected_msg->orientation = msg->orientation;
        // Copy the angular velocity
        corrected_msg->angular_velocity = msg->angular_velocity;
        // Copy the linear acceleration
        corrected_msg->linear_acceleration = msg->linear_acceleration;
        // Copy the orientation_covriance
        corrected_msg->orientation_covariance = msg->orientation_covariance;
        // Copy the angular_velocity_covariance
        corrected_msg->angular_velocity_covariance = msg->angular_velocity_covariance;
        // Copy the linear_acceleration_covariance
        corrected_msg->linear_acceleration_covariance = msg->linear_acceleration_covariance;

        // Swap the angular velocity components
        corrected_msg->angular_velocity.x = msg->angular_velocity.z;
        corrected_msg->angular_velocity.y = -msg->angular_velocity.x;
        corrected_msg->angular_velocity.z = -msg->angular_velocity.y;

        // Swap the linear acceleration components
        corrected_msg->linear_acceleration.x = msg->linear_acceleration.z;
        corrected_msg->linear_acceleration.y = -msg->linear_acceleration.x;
        corrected_msg->linear_acceleration.z = msg->linear_acceleration.y;

        // Publish the corrected IMU message on the corrected topic
        publisher_->publish(*corrected_msg);
    }

    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr subscription_;
    rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr publisher_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<imu_correction_node>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

