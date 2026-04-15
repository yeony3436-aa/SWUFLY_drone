hover_node.py
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode


class HoverNode(Node):
    def __init__(self):
        super().__init__('hover_node')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.current_state = State()

        self.state_sub = self.create_subscription(
            State,
            '/mavros/state',
            self.state_callback,
            qos
        )

        self.setpoint_pub = self.create_publisher(
            PoseStamped,
            '/mavros/setpoint_position/local',
            10
        )

        self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.set_mode_client = self.create_client(SetMode, '/mavros/set_mode')

        while not self.arming_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('arming service 기다리는 중...')
        while not self.set_mode_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('set_mode service 기다리는 중...')

        self.target_pose = PoseStamped()
        self.target_pose.header.frame_id = 'map'
        self.target_pose.pose.position.x = 0.0
        self.target_pose.pose.position.y = 0.0
        self.target_pose.pose.position.z = 2.0
        self.target_pose.pose.orientation.w = 1.0

        self.timer = self.create_timer(0.05, self.timer_callback)  # 20Hz
        self.count = 0
        self.offboard_sent = False
        self.arm_sent = False

    def state_callback(self, msg):
        self.current_state = msg

    def timer_callback(self):
        self.target_pose.header.stamp = self.get_clock().now().to_msg()
        self.setpoint_pub.publish(self.target_pose)

        # OFFBOARD 들어가기 전에 setpoint를 충분히 먼저 보내야 함
        if self.count < 100:
            self.count += 1
            return

        if not self.offboard_sent:
            req = SetMode.Request()
            req.custom_mode = 'OFFBOARD'
            future = self.set_mode_client.call_async(req)
            self.get_logger().info('OFFBOARD 모드 요청 보냄')
            self.offboard_sent = True
            return

        if self.current_state.mode == 'OFFBOARD' and not self.arm_sent:
            req = CommandBool.Request()
            req.value = True
            future = self.arming_client.call_async(req)
            self.get_logger().info('ARM 요청 보냄')
            self.arm_sent = True
            return

        self.get_logger().info(
            f"mode={self.current_state.mode}, armed={self.current_state.armed}, target_z=2.0"
        )


def main(args=None):
    rclpy.init(args=args)
    node = HoverNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()