waypoint_node.py
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode, CommandTOL


class WaypointNode(Node):
    def __init__(self):
        super().__init__('waypoint_node')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.current_state = State()
        self.current_pose = PoseStamped()

        self.state_sub = self.create_subscription(
            State,
            '/mavros/state',
            self.state_callback,
            qos
        )

        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/mavros/local_position/pose',
            self.pose_callback,
            qos
        )

        self.setpoint_pub = self.create_publisher(
            PoseStamped,
            '/mavros/setpoint_position/local',
            10
        )

        self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.set_mode_client = self.create_client(SetMode, '/mavros/set_mode')
        self.land_client = self.create_client(CommandTOL, '/mavros/cmd/land')

        while not self.arming_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('arming service 기다리는 중...')
        while not self.set_mode_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('set_mode service 기다리는 중...')
        while not self.land_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('land service 기다리는 중...')

        self.waypoints = [
            [0.0, 0.0, 2.0],
            [2.0, 0.0, 2.0],
            [2.0, 2.0, 2.0],
            [0.0, 0.0, 2.0],
        ]
        self.current_wp_index = 0
        self.reached_tolerance = 0.3

        self.setpoint = PoseStamped()
        self.setpoint.header.frame_id = 'map'
        self.setpoint.pose.orientation.w = 1.0

        self.initial_setpoint_count = 0
        self.offboard_sent = False
        self.arm_sent = False
        self.mission_finished = False
        self.land_sent = False

        self.timer = self.create_timer(0.05, self.timer_callback)

    def state_callback(self, msg):
        self.current_state = msg

    def pose_callback(self, msg):
        self.current_pose = msg

    def get_distance(self, x1, y1, z1, x2, y2, z2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

    def publish_current_waypoint(self):
        target = self.waypoints[self.current_wp_index]
        self.setpoint.header.stamp = self.get_clock().now().to_msg()
        self.setpoint.pose.position.x = target[0]
        self.setpoint.pose.position.y = target[1]
        self.setpoint.pose.position.z = target[2]
        self.setpoint_pub.publish(self.setpoint)

    def timer_callback(self):
        self.publish_current_waypoint()

        if self.initial_setpoint_count < 100:
            self.initial_setpoint_count += 1
            return

        if not self.offboard_sent:
            req = SetMode.Request()
            req.custom_mode = 'OFFBOARD'
            self.set_mode_client.call_async(req)
            self.get_logger().info('OFFBOARD 모드 요청')
            self.offboard_sent = True
            return

        if self.current_state.mode == 'OFFBOARD' and not self.arm_sent:
            req = CommandBool.Request()
            req.value = True
            self.arming_client.call_async(req)
            self.get_logger().info('ARM 요청')
            self.arm_sent = True
            return

        target = self.waypoints[self.current_wp_index]
        x = self.current_pose.pose.position.x
        y = self.current_pose.pose.position.y
        z = self.current_pose.pose.position.z

        distance = self.get_distance(x, y, z, target[0], target[1], target[2])

        self.get_logger().info(
            f"mode={self.current_state.mode}, armed={self.current_state.armed}, "
            f"target={target}, current=({x:.2f}, {y:.2f}, {z:.2f}), dist={distance:.2f}"
        )

        if distance < self.reached_tolerance:
            self.get_logger().info(f'Waypoint {self.current_wp_index + 1} 도달')

            if self.current_wp_index < len(self.waypoints) - 1:
                self.current_wp_index += 1
                self.get_logger().info(f'다음 waypoint: {self.waypoints[self.current_wp_index]}')
            else:
                self.get_logger().info('모든 waypoint 도달 완료')
                self.mission_finished = True

        if self.mission_finished and not self.land_sent:
            land_req = CommandTOL.Request()
            land_req.min_pitch = 0.0
            land_req.yaw = 0.0
            land_req.latitude = 0.0
            land_req.longitude = 0.0
            land_req.altitude = 0.0

            self.land_client.call_async(land_req)
            self.get_logger().info('LAND 요청 보냄')
            self.land_sent = True


def main(args=None):
    rclpy.init(args=args)
    node = WaypointNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()