import json
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import shape, LineString
from shapely.ops import unary_union
from scipy.interpolate import splprep, splev

# Load SAME JSON
with open("real_river.geojson") as f:
    data = json.load(f)

feature = data["features"][0]
river_name = feature["properties"]["name"]
river_line = shape(feature["geometry"])

coords = np.array(river_line.coords)
x = coords[:, 0]
y = coords[:, 1]

# Smooth River Line
tck, u = splprep([x, y], s=0.0005)
u_fine = np.linspace(0, 1, 800)
x_smooth, y_smooth = splev(u_fine, tck)

smooth_line = LineString(np.column_stack([x_smooth, y_smooth]))

# Create River Polygon (Width Simulation)
river_width = 0.015
river_polygon = smooth_line.buffer(river_width)

# Find Safe Label Segment
length = smooth_line.length
label_length_ratio = 0.4  # portion of river for text

start_dist = length * 0.3
end_dist = length * 0.7

text_path = smooth_line.segmentize(0.001)

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_facecolor("#f2efe9")

# Draw river body
x_poly, y_poly = river_polygon.exterior.xy
ax.fill(x_poly, y_poly, color="#9bd3f5")

# Draw centerline
ax.plot(x_smooth, y_smooth, color="#1f78b4", linewidth=2)

# Curved Text Placement
text = river_name.upper()
char_positions = np.linspace(start_dist, end_dist, len(text))

for char, dist in zip(text, char_positions):
    point = smooth_line.interpolate(dist)
    before = smooth_line.interpolate(dist - 0.001)
    after = smooth_line.interpolate(dist + 0.001)

    dx = after.x - before.x
    dy = after.y - before.y
    angle = np.degrees(np.arctan2(dy, dx))

    # Ensure inside boundary
    if river_polygon.contains(point):
        ax.text(point.x, point.y, char,
                fontsize=14,
                rotation=angle,
                ha='center',
                va='center',
                color="#08306b",
                fontweight='bold')

ax.axis("off")
plt.title("Smart River Name Placement (Boundary Aware)")
plt.show()