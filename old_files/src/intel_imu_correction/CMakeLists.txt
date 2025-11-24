cmake_minimum_required(VERSION 3.5)
project(intel_imu_correction)

# Add compiler options
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

# Add executable
add_executable(imu_correction_node src/imu_correction_node.cpp)

ament_target_dependencies(imu_correction_node rclcpp sensor_msgs)


# Install executable
install(TARGETS
    imu_correction_node
    DESTINATION lib/${PROJECT_NAME}
)


# Install package.xml
ament_package()
