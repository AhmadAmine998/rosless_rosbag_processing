import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

import matplotlib.pyplot as plt

BAG_DIR    = "rosbag_sample"
TOPIC      = "/turtle1/pose"
STORAGE_ID = "sqlite3"
FMT_IN     = "cdr"
FMT_OUT    = "cdr"

# open bag and grab topic→type mapping
reader = rosbag2_py.SequentialReader()
reader.open(
    rosbag2_py.StorageOptions(uri=BAG_DIR, storage_id=STORAGE_ID),
    rosbag2_py.ConverterOptions(
        input_serialization_format=FMT_IN,
        output_serialization_format=FMT_OUT,
    ),
)
topics_and_types = {
    topic.name: topic.type for topic in reader.get_all_topics_and_types()
}
reader.set_filter(rosbag2_py.StorageFilter(topics=[TOPIC]))

# read & deserialize
times, xs, ys, thetas, lin_vels, ang_vels = [], [], [], [], [], []
while reader.has_next():
    rec = reader.read_next()
    # dynamically get the Python class for this topic’s type
    MsgClass = get_message(topics_and_types[rec[0]])
    msg     = deserialize_message(rec[1], MsgClass)
    times  .append(rec[2])
    xs     .append(msg.x)
    ys     .append(msg.y)
    thetas .append(msg.theta)
    lin_vels.append(msg.linear_velocity)
    ang_vels.append(msg.angular_velocity)

# plot (unchanged)
fig, axs = plt.subplots(1, 3, figsize=(18, 6))
scatter = [
    (thetas,    "hsv",     "Theta"          ),
    (lin_vels,  "viridis", "Linear Velocity"),
    (ang_vels,  "plasma",  "Angular Velocity")
]
for ax, (cdata, cmap, label) in zip(axs, scatter):
    sc = ax.scatter(xs, ys, c=cdata, cmap=cmap)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(f"XY colored by {label}")
    plt.colorbar(sc, ax=ax, label=label)

plt.suptitle("Turtle1 Pose from ROS 2 Bag")
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
