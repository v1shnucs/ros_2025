#!/usr/bin/env python3

import os
import rospy
from std_msgs.msg import String
from google.cloud import speech
from google.cloud.speech import SpeechClient, RecognitionConfig, RecognitionAudio
import sounddevice as sd
import numpy as np
import json

class SpeechRecognitionNode:
    def __init__(self):
        rospy.init_node('speech_recognition_node', anonymous=True)
        
        # Get credentials path from parameter
        self.credentials_path = rospy.get_param('~credentials_path')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
        
        # Initialize Google Cloud Speech client
        try:
            self.client = speech.SpeechClient()
            rospy.loginfo("Google Cloud Speech client initialized")
        except Exception as e:
            rospy.logerr(f"Failed to initialize Google Cloud Speech client: {str(e)}")
            raise
        
        # Audio recording parameters
        self.sample_rate = 16000
        self.recording_duration = 7
        self.max_attempts = 3
        
        # Publishers
        self.speech_pub = rospy.Publisher('/audio/speech_text', String, queue_size=10)
        self.status_pub = rospy.Publisher('/audio/status', String, queue_size=10)
        
        # State variables
        self.is_listening = False
        self.current_attempt = 0
        
        # Subscribe to control commands
        rospy.Subscriber('/audio/control', String, self.control_callback)
        
        rospy.loginfo("Speech recognition node initialized")

    def record_audio(self):
        """Record audio using sounddevice"""
        try:
            self.publish_status("recording")
            
            # Record audio
            audio_data = sd.rec(
                int(self.sample_rate * self.recording_duration),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.int16
            )
            
            sd.wait()  # Wait for recording to complete
            
            self.publish_status("processing")
            return audio_data.flatten().tobytes()
            
        except Exception as e:
            self.publish_status("error", str(e))
            rospy.logerr(f"Error recording audio: {str(e)}")
            return None

    def transcribe_speech(self):
        """Record and transcribe speech"""
        try:
            # Record audio
            audio_data = self.record_audio()
            if not audio_data:
                return None, 0.0

            # Create recognition config
            config = RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate,
                language_code="en-US",
                enable_automatic_punctuation=True
            )
            
            # Create recognition audio
            audio = RecognitionAudio(content=audio_data)
            
            # Perform recognition
            response = self.client.recognize(config=config, audio=audio)
            
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                
                if confidence > 0.6:  # Only accept high-confidence results
                    return transcript.lower(), confidence
            
            return None, 0.0
            
        except Exception as e:
            rospy.logerr(f"Transcription error: {str(e)}")
            return None, 0.0

    def publish_status(self, status_type, details=""):
        """Publish status updates"""
        try:
            status_msg = {
                'status': status_type,
                'details': details,
                'timestamp': rospy.Time.now().to_sec()
            }
            self.status_pub.publish(json.dumps(status_msg))
        except Exception as e:
            rospy.logerr(f"Error publishing status: {str(e)}")

    def process_speech(self):
        """Main speech processing loop"""
        while self.is_listening and self.current_attempt < self.max_attempts:
            self.current_attempt += 1
            
            # Get transcription
            transcript, confidence = self.transcribe_speech()
            
            if transcript:
                # Publish result
                msg = {
                    'text': transcript,
                    'confidence': confidence,
                    'attempt': self.current_attempt
                }
                self.speech_pub.publish(json.dumps(msg))
                
                self.publish_status("success", f"Text: {transcript}")
                self.is_listening = False
                self.current_attempt = 0
                return
            else:
                if self.current_attempt < self.max_attempts:
                    self.publish_status(
                        "retry",
                        f"Attempt {self.current_attempt}/{self.max_attempts}"
                    )
                else:
                    self.publish_status("error", "Max attempts reached")
                    self.is_listening = False
                    self.current_attempt = 0

    def control_callback(self, msg):
        """Handle control messages"""
        try:
            command = json.loads(msg.data)
            
            if command.get('action') == 'start':
                if not self.is_listening:
                    self.is_listening = True
                    self.current_attempt = 0
                    self.process_speech()
            
            elif command.get('action') == 'stop':
                self.is_listening = False
                self.current_attempt = 0
                self.publish_status("stopped")
            
        except json.JSONDecodeError:
            rospy.logerr("Invalid control message format")
        except Exception as e:
            rospy.logerr(f"Error in control callback: {str(e)}")

def main():
    """Main function"""
    try:
        node = SpeechRecognitionNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    except Exception as e:
        rospy.logerr(f"Speech recognition node error: {str(e)}")

if __name__ == '__main__':
    main()