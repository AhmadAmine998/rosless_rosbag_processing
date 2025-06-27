import sqlite3
import yaml
import struct
import matplotlib.pyplot as plt

# Path to the ROS 2 bag directory
rosbag_dir = "rosbag_sample"
db3_file = f"{rosbag_dir}/turtle_sim_sample_0.db3"
metadata_file = f"{rosbag_dir}/metadata.yaml"

# Load metadata
with open(metadata_file, 'r') as f:
    metadata = yaml.safe_load(f)

pose_topic = "/turtle1/pose"

conn   = sqlite3.connect(db3_file)
cursor = conn.cursor()

query = f"""
SELECT timestamp, data
FROM messages
WHERE topic_id = (
    SELECT id FROM topics WHERE name = '{pose_topic}'
)
"""
cursor.execute(query)
rows = cursor.fetchall()

timestamps     = []
x_positions    = []
y_positions    = []
linear_velocitys = []
angular_velocitys = []
headings       = []

for timestamp, data in rows:
    
    # Turtlsim pose message format is:
    # float32 x
    # float32 y
    # float32 theta

    # float32 linear_velocity
    # float32 angular_velocity

    # discard the 4-byte length header
    payload = data[0+4:]

    # now unpack just 5 floats
    x, y, theta, linear_velocity, angular_velocity = struct.unpack('<5f', payload)

    timestamps.append(timestamp)
    x_positions.append(x)
    y_positions.append(y)
    headings.append(theta)
    linear_velocitys.append(linear_velocity)
    angular_velocitys.append(angular_velocity)

conn.close()
fig, axs = plt.subplots(1, 3, figsize=(18, 6))

# 1) XY scatter colored by heading (theta)
sc0 = axs[0].scatter(x_positions, y_positions, c=headings, cmap='hsv')
axs[0].set_title("XY Colored by Theta")
axs[0].set_xlabel("X Position")
axs[0].set_ylabel("Y Position")
plt.colorbar(sc0, ax=axs[0], label="Theta")

# 2) XY scatter colored by linear velocity
sc1 = axs[1].scatter(x_positions, y_positions, c=linear_velocitys, cmap='viridis')
axs[1].set_title("XY Colored by Linear Velocity")
axs[1].set_xlabel("X Position")
plt.colorbar(sc1, ax=axs[1], label="Linear Velocity")

# 3) XY scatter colored by angular velocity
sc2 = axs[2].scatter(x_positions, y_positions, c=angular_velocitys, cmap='plasma')
axs[2].set_title("XY Colored by Angular Velocity")
axs[2].set_xlabel("X Position")
plt.colorbar(sc2, ax=axs[2], label="Angular Velocity")

plt.suptitle("Turtle1 Pose from ROS 2 Bag")
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
