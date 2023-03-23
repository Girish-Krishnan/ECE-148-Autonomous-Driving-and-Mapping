import cv2 as cv
import numpy as np
import open3d as o3d
import pyrealsense2 as rs

class RealSenseCamera:

    """
    
    Initialize a RealSenseCamera object with the following attributes:
    :param serial_number: The serial number of the RealSense camera
    
    """

    def __init__(self, serial_number) -> None:
        # Create RealSense D415 camera object and pipeline
        self.serial_number = serial_number
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_device(serial_number)
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)
        self.config.enable_stream(rs.stream.infrared, 640, 480, rs.format.y8, 60)

        # Start streaming
        self.pipeline.start(self.config)

        # Enable IR emitter and set max laser power
        self.profile = self.pipeline.get_active_profile()
        self.depth_sensor = self.profile.get_device().first_depth_sensor()
        self.depth_sensor.set_option(rs.option.emitter_enabled, 1)
        self.depth_sensor.set_option(rs.option.enable_auto_exposure, True)
        self.depth_sensor.set_option(rs.option.laser_power, 360)
        self.depth_sensor.set_option(rs.option.global_time_enabled, 1)

    def get_frames(self):
        """
        :return: The frameset of the RealSenseCamera object
        """
        return self.pipeline.wait_for_frames()
        
    def process_frames(self, frames):
        """
        
        :param frames: The frameset of the RealSenseCamera object

        """    
        aligned_frames = rs.align(rs.stream.depth).process(frames)

        # Get aligned frames
        self.aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        self.aligned_depth_frame = rs.decimation_filter(1).process(self.aligned_depth_frame)
        self.aligned_depth_frame = rs.disparity_transform(True).process(self.aligned_depth_frame)
        self.aligned_depth_frame = rs.spatial_filter().process(self.aligned_depth_frame)
        self.aligned_depth_frame = rs.temporal_filter().process(self.aligned_depth_frame)
        self.aligned_depth_frame = rs.disparity_transform(False).process(self.aligned_depth_frame)

        self.color_frame = aligned_frames.get_color_frame()
        self.raw_color_frame = frames.get_color_frame()

        # Convert images to numpy arrays
        self.depth_image = np.asanyarray(self.aligned_depth_frame.get_data())
        self.color_image = np.asanyarray(self.color_frame.get_data())

    def save_frames(self):
        """
        Save the frames of the RealSenseCamera object as .jpg and .npy files
        """
        
        raw_color_image = np.asanyarray(self.raw_color_frame.get_data())
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv.applyColorMap(cv.convertScaleAbs(self.depth_image, alpha=0.03), cv.COLORMAP_JET)

        # Save color as .jpg and depth as .npy
        cv.imwrite("./Camera_Data/" + self.serial_number + "/sample_images/image.jpg", self.color_image)
        cv.imwrite("./Camera_Data/" + self.serial_number + "/sample_images/raw_image.jpg", raw_color_image)
        np.save("./Camera_Data/" + self.serial_number + "/sample_images/depth_map.npy", self.depth_image)
        cv.imwrite("./Camera_Data/" + self.serial_number + "/sample_images/depth.png", depth_colormap)

    
    def get_point_cloud(self):
        """
        :return: The point cloud of the RealSenseCamera object
        """
       
       # Get intrinsics
        depth_intrinsics = self.aligned_depth_frame.profile.as_video_stream_profile().intrinsics

        self.fx = depth_intrinsics.fx
        self.fy = depth_intrinsics.fy
        self.cx = depth_intrinsics.ppx
        self.cy = depth_intrinsics.ppy

        mask = np.logical_or(self.depth_image > 2, self.depth_image < 0.75)
        grads = np.gradient(self.depth_image)
        grad = np.sqrt(grads[0] ** 2 + grads[1] ** 2)

        mask[grad > 0.05] = True

        erode_mask = cv.dilate(mask.astype(np.uint8), np.ones((7,7), dtype=np.uint8))

        self.depth_image[mask] = 0

        self.pcd = np.hstack(
            (np.transpose(np.nonzero(self.depth_image)), np.reshape(self.depth_image[np.nonzero(self.depth_image)], (-1,1)) )
        )  # (xxx, 3)
        self.pcd[:, [0, 1]] = self.pcd[:, [1, 0]]  # swap x and y axis since they are reversed in image coordinates

        self.pcd[:, 0] = (self.pcd[:, 0] - self.cx) * self.pcd[:, 2] / self.fx
        self.pcd[:, 1] = (self.pcd[:, 1] - self.cy) * self.pcd[:, 2] / self.fy

        self.colors = np.flip(self.color_image[np.nonzero(self.depth_image)], axis=1)

        self.pcd_o3d = o3d.geometry.PointCloud()
        self.pcd_o3d.points = o3d.utility.Vector3dVector(self.pcd)
        self.pcd_o3d.colors = o3d.utility.Vector3dVector(self.colors/255)

        self.pcd_o3d, _ = self.pcd_o3d.remove_radius_outlier(1000,radius=0.05)

        self.pcd = np.asarray(self.pcd_o3d.points)
        self.colors = np.asarray(self.pcd_o3d.colors)
    
    def convert_pcd_to_world_frame(self, rotation, translation):
        """
        :param rotation: Rotation matrix of the camera
        :param translation: Translation vector of the camera
        """
        self.pcd = rotation.T @ (self.pcd - translation)
        self.pcd_o3d.points = o3d.utility.Vector3dVector(self.pcd)
    
    def save_point_cloud(self):
        """
        Save the point cloud of the RealSenseCamera object as .ply file
        """
        o3d.io.write_point_cloud("./Camera_Data/" + self.serial_number + "/sample_point_clouds/point_cloud.ply", self.pcd_o3d)

