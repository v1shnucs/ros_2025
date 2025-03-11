#!/usr/bin/env python
import rospy
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from std_msgs.msg import String
import json

MODEL1_PATH = "/home/vishnu/ros_2025/src/gpt_vision/src/models/grid_model_equalized_120epochs.h5"
MODEL2_PATH = "/home/vishnu/ros_2025/src/gpt_vision/src/models/grid_model_unequal_200epoch.keras"
IMG_RES = (230, 440)

# Features for object detection (space, color, shape)
FEATURES = [
    "s1yc",     # space 1, yellow circle
    "s1rc",     # space 1, red circle
    "s1bc",     # space 1, blue circle
    "s1gc",     # etc.
    "s1yt",
    "s1rt",
    "s1bt",
    "s1gt",
    "s1ys",
    "s1rs",
    "s1bs",
    "s1gs",
    "s1e",      # space 1 empty
    "s2yc",
    "s2rc",
    "s2bc",
    "s2gc",
    "s2yt",
    "s2rt",
    "s2bt",
    "s2gt",
    "s2ys",
    "s2rs",
    "s2bs",
    "s2gs",
    "s2e",
    "s3yc",
    "s3rc",
    "s3bc",
    "s3gc",
    "s3yt",
    "s3rt",
    "s3bt",
    "s3gt",
    "s3ys",
    "s3rs",
    "s3bs",
    "s3gs",
    "s3e",
    "s4yc",
    "s4rc",
    "s4bc",
    "s4gc",
    "s4yt",
    "s4rt",
    "s4bt",
    "s4gt",
    "s4ys",
    "s4rs",
    "s4bs",
    "s4gs",
    "s4e",
    "s5yc",
    "s5rc",
    "s5bc",
    "s5gc",
    "s5yt",
    "s5rt",
    "s5bt",
    "s5gt",
    "s5ys",
    "s5rs",
    "s5bs",
    "s5gs",
    "s5e",
    "s6yc",
    "s6rc",
    "s6bc",
    "s6gc",
    "s6yt",
    "s6rt",
    "s6bt",
    "s6gt",
    "s6ys",
    "s6rs",
    "s6bs",
    "s6gs",
    "s6e",
    "s7yc",
    "s7rc",
    "s7bc",
    "s7gc",
    "s7yt",
    "s7rt",
    "s7bt",
    "s7gt",
    "s7ys",
    "s7rs",
    "s7bs",
    "s7gs",
    "s7e",
    "s8yc",
    "s8rc",
    "s8bc",
    "s8gc",
    "s8yt",
    "s8rt",
    "s8bt",
    "s8gt",
    "s8ys",
    "s8rs",
    "s8bs",
    "s8gs",
    "s8e",
    "s9yc",
    "s9rc",
    "s9bc",
    "s9gc",
    "s9yt",
    "s9rt",
    "s9bt",
    "s9gt",
    "s9ys",
    "s9rs",
    "s9bs",
    "s9gs",
    "s9e",
    "s10yc",
    "s10rc",
    "s10bc",
    "s10gc",
    "s10yt",
    "s10rt",
    "s10bt",
    "s10gt",
    "s10ys",
    "s10rs",
    "s10bs",
    "s10gs",
    "s10e",
    "s11yc",
    "s11rc",
    "s11bc",
    "s11gc",
    "s11yt",
    "s11rt",
    "s11bt",
    "s11gt",
    "s11ys",
    "s11rs",
    "s11bs",
    "s11gs",
    "s11e",
    "s12yc",
    "s12rc",
    "s12bc",
    "s12gc",
    "s12yt",
    "s12rt",
    "s12bt",
    "s12gt",
    "s12ys",
    "s12rs",
    "s12bs",
    "s12gs",
    "s12e",
]

class VisionSystem:
    def __init__(self):
        rospy.init_node('vision_system', anonymous=True)
        
        # Initialize CV bridge
        self.bridge = CvBridge()
        
        # Load the models
        try:
            self.model1 = load_model(MODEL1_PATH)
            self.model2 = load_model(MODEL2_PATH)
            rospy.loginfo("Models loaded successfully")
        except Exception as e:
            rospy.logerr(f"Error loading models: {str(e)}")
            raise
        
        # Initialize publishers and subscribers
        self.image_sub = rospy.Subscriber(
            '/camera/color/image_raw',
            Image,
            self.image_callback,
            queue_size=1
        )
        self.grid_state_pub = rospy.Publisher(
            '/vision/grid_state',
            String,
            queue_size=1
        )
        self.state_request_sub = rospy.Subscriber(
            '/vision/request_state',
            String,
            self.state_request_callback
        )
        
        # Initialize state variables
        self.current_image = None
        self.last_processed_state = None
        self.processing_lock = False
        
        rospy.loginfo("Vision system initialized")
    
    def preprocess_image(self, cv_image):
        """Preprocess image for model input"""
        try:
            # Resize image to expected resolution
            resized = cv2.resize(cv_image, IMG_RES)
            # Normalize pixel values
            normalized = resized / 255.0
            # Add batch dimension
            return np.expand_dims(normalized, axis=0)
        except Exception as e:
            rospy.logerr(f"Error preprocessing image: {str(e)}")
            return None

    def process_predictions(self, predictions):
        """Process model predictions to determine grid state"""
        # Average predictions from both models (soft voting)
        avg_predictions = (predictions[0] + predictions[1]) / 2
        
        # Process each square's predictions
        grid_state = {}
        for square in range(1, 13):
            start_idx = (square - 1) * 13
            end_idx = start_idx + 13
            square_preds = avg_predictions[0, start_idx:end_idx]
            
            # Get the highest confidence prediction
            max_idx = np.argmax(square_preds)
            confidence = square_preds[max_idx]
            
            # Only include predictions with confidence > 0.5
            if confidence > 0.5:
                feature = FEATURES[start_idx + max_idx]
                # Parse feature code (e.g., 's1rc' -> square 1, red circle)
                color = 'empty' if 'e' in feature else (
                    'red' if 'r' in feature else
                    'blue' if 'b' in feature else
                    'green' if 'g' in feature else
                    'yellow' if 'y' in feature else 'unknown'
                )
                shape = 'empty' if 'e' in feature else (
                    'circle' if 'c' in feature else
                    'triangle' if 't' in feature else
                    'square' if 's' in feature else 'unknown'
                )
                
                grid_state[str(square)] = {
                    'color': color,
                    'shape': shape,
                    'confidence': float(confidence)
                }
            else:
                grid_state[str(square)] = {
                    'color': 'empty',
                    'shape': 'empty',
                    'confidence': float(confidence)
                }
        
        return grid_state

    def check_image_quality(self, cv_image):
        """Check if image quality is sufficient for processing"""
        try:
            # Check image is not empty
            if cv_image is None or cv_image.size == 0:
                return False, "Empty image"
            
            # Check image dimensions
            height, width = cv_image.shape[:2]
            if height < 100 or width < 100:
                return False, "Image too small"
            
            # Check for extreme brightness/darkness
            avg_brightness = np.mean(cv_image)
            if avg_brightness < 30 or avg_brightness > 225:
                return False, "Poor lighting conditions"
            
            return True, "Image quality acceptable"
        except Exception as e:
            return False, f"Error checking image quality: {str(e)}"

    def image_callback(self, msg):
        """Handle incoming camera images"""
        if self.processing_lock:
            return
            
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "rgb8")
            self.current_image = cv_image
        except CvBridgeError as e:
            rospy.logerr(f"Error converting image: {str(e)}")
    
    def state_request_callback(self, msg):
        """Handle requests for current grid state"""
        if self.processing_lock or self.current_image is None:
            rospy.logwarn("Cannot process state request - system busy or no image")
            return
            
        self.processing_lock = True
        try:
            # Check image quality
            quality_ok, message = self.check_image_quality(self.current_image)
            if not quality_ok:
                rospy.logwarn(f"Image quality check failed: {message}")
                return
                
            # Preprocess image
            processed_image = self.preprocess_image(self.current_image)
            if processed_image is None:
                return
                
            # Get predictions from both models
            pred1 = self.model1.predict(processed_image, verbose=0)
            pred2 = self.model2.predict(processed_image, verbose=0)
            
            # Process predictions to get grid state
            grid_state = self.process_predictions([pred1, pred2])
            
            # Publish grid state
            state_msg = String()
            state_msg.data = json.dumps(grid_state)
            self.grid_state_pub.publish(state_msg)
            
            self.last_processed_state = grid_state
            rospy.loginfo("Grid state published successfully")
            
        except Exception as e:
            rospy.logerr(f"Error processing grid state: {str(e)}")
        finally:
            self.processing_lock = False

def main():
    try:
        vision_system = VisionSystem()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    except Exception as e:
        rospy.logerr(f"Vision system error: {str(e)}")

if __name__ == '__main__':
    main()