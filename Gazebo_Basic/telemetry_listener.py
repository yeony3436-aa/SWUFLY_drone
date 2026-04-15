import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from mavros_msgs.msg import State
from geometry_msgs.msg import PoseStamped, TwistStamped
from sensor_msgs.msg import Imu, BatteryState


class TelemetryListener(Node):
    def __init__(self):
        super().__init__('telemetry_listener')

        # MAVROS 토픽용 QoS 설정
        mavros_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.current_state = State()
        self.current_pose = PoseStamped()
        self.current_velocity = TwistStamped()
        self.current_imu = Imu()
        self.current_battery = BatteryState()

        self.state_received = False
        self.pose_received = False
        self.vel_received = False
        self.imu_received = False
        self.battery_received = False

        self.state_sub = self.create_subscription(
            State,
            '/mavros/state',
            self.state_callback,
            mavros_qos
        )

        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/mavros/local_position/pose',
            self.pose_callback,
            mavros_qos
        )

        self.velocity_sub = self.create_subscription(
            TwistStamped,
            '/mavros/local_position/velocity_local',
            self.velocity_callback,
            mavros_qos
        )

        self.imu_sub = self.create_subscription(
            Imu,
            '/mavros/imu/data',
            self.imu_callback,
            mavros_qos
        )

        self.battery_sub = self.create_subscription(
            BatteryState,
            '/mavros/battery_status',
            self.battery_callback,
            mavros_qos
        )

        self.timer = self.create_timer(1.0, self.print_telemetry)

    def state_callback(self, msg):
        self.current_state = msg
        self.state_received = True

    def pose_callback(self, msg):
        self.current_pose = msg
        self.pose_received = True

    def velocity_callback(self, msg):
        self.current_velocity = msg
        self.vel_received = True

    def imu_callback(self, msg):
        self.current_imu = msg
        self.imu_received = True

    def battery_callback(self, msg):
        self.current_battery = msg
        self.battery_received = True

    def print_telemetry(self):
        if not self.state_received or not self.pose_received:
            self.get_logger().info('telemetry 수신 대기 중...')
            return

        x = self.current_pose.pose.position.x
        y = self.current_pose.pose.position.y
        z = self.current_pose.pose.position.z

        vx = self.current_velocity.twist.linear.x if self.vel_received else 0.0
        vy = self.current_velocity.twist.linear.y if self.vel_received else 0.0
        vz = self.current_velocity.twist.linear.z if self.vel_received else 0.0

        battery = self.current_battery.percentage if self.battery_received else -1.0

        self.get_logger().info(
            f"connected={self.current_state.connected}, "
            f"armed={self.current_state.armed}, "
            f"mode={self.current_state.mode}, "
            f"pos=({x:.2f}, {y:.2f}, {z:.2f}), "
            f"vel=({vx:.2f}, {vy:.2f}, {vz:.2f}), "
            f"battery={battery:.2f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = TelemetryListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()