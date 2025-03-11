#!/usr/bin/env python
import rospy
import openai
import json
import os
from std_msgs.msg import String
from collections import deque

class GPTResponseNode:
    def __init__(self):
        rospy.init_node('gpt_response_node', anonymous=True)
        
        # Initialize OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            rospy.logerr("OPENAI_API_KEY environment variable not set!")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        openai.api_key = api_key
        
        # Initialize state
        self.current_grid_state = {}
        self.conversation_history = deque(maxlen=5)  # Keep last 5 exchanges
        self.last_action = None
        
        # Initialize publishers
        self.response_pub = rospy.Publisher('/gpt_response', String, queue_size=10)
        self.action_pub = rospy.Publisher('/robot/command', String, queue_size=10)
        self.speech_pub = rospy.Publisher('/audio/speak', String, queue_size=10)
        
        # Initialize subscribers
        rospy.Subscriber('/audio/speech_text', String, self.user_input_callback)
        rospy.Subscriber('/vision/grid_state_processed', String, self.grid_state_callback)
        rospy.Subscriber('/robot/status', String, self.robot_status_callback)
        
        self.system_prompt = """You are a helpful robot assistant controlling a Sawyer robot arm. You can see objects on a table arranged in a grid of 12 squares.
You can grab and place objects, and you should maintain awareness of the current state of objects on the table.

Respond in the following format:
speak: [what to say to the user]
actions: [commands like 'grab 1' or 'place 5' if needed]

Keep responses brief and natural. If asked about the table state, describe what you see clearly.
If asked to move objects, verify the move is possible before acting.
If you don't understand or need clarification, ask the user to rephrase."""

        rospy.loginfo("GPT Response Node initialized")

    def grid_state_callback(self, msg):
        """Handle updates to grid state"""
        try:
            self.current_grid_state = json.loads(msg.data)
            rospy.loginfo("Grid state updated")
        except json.JSONDecodeError as e:
            rospy.logerr(f"Error parsing grid state: {str(e)}")

    def robot_status_callback(self, msg):
        """Handle robot status updates"""
        try:
            status = json.loads(msg.data)
            if status.get('action_complete'):
                self.last_action = status
        except json.JSONDecodeError as e:
            rospy.logerr(f"Error parsing robot status: {str(e)}")

    def format_grid_state_prompt(self):
        """Format current grid state for GPT context"""
        state_desc = "Current table state:\n"
        for square, data in self.current_grid_state.get('state', {}).items():
            if data['color'] != 'empty':
                state_desc += f"Square {square}: {data['color']} {data['shape']}\n"
        return state_desc

    def get_gpt_response(self, user_input):
        """Get response from GPT with current context"""
        try:
            # Prepare conversation context
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": self.format_grid_state_prompt()}
            ]
            
            # Add conversation history
            for exchange in self.conversation_history:
                messages.extend([
                    {"role": "user", "content": exchange["user"]},
                    {"role": "assistant", "content": exchange["assistant"]}
                ])
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Get GPT response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-instruct",
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            return response['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            rospy.logerr(f"Error getting GPT response: {str(e)}")
            return "speak: I apologize, but I'm having trouble processing your request."

    def process_response(self, response):
        """Process GPT response into speech and actions"""
        try:
            # Split into speak and actions parts
            speak_part = ""
            actions_part = ""
            
            if "speak:" in response:
                parts = response.split("actions:")
                speak_part = parts[0].replace("speak:", "").strip()
                actions_part = parts[1].strip() if len(parts) > 1 else ""
            else:
                speak_part = response
            
            # Publish speech response
            if speak_part:
                speech_msg = String()
                speech_msg.data = speak_part
                self.speech_pub.publish(speech_msg)
            
            # Process and publish actions
            if actions_part:
                actions = actions_part.split()
                if len(actions) >= 2 and actions[0] in ['grab', 'place']:
                    try:
                        square = int(actions[1])
                        if 1 <= square <= 12:
                            action_msg = String()
                            action_msg.data = json.dumps({
                                'action': actions[0],
                                'square': square
                            })
                            self.action_pub.publish(action_msg)
                    except ValueError:
                        rospy.logerr("Invalid square number in action command")
            
            return speak_part, actions_part
            
        except Exception as e:
            rospy.logerr(f"Error processing response: {str(e)}")
            return "I encountered an error processing the response.", ""

    def user_input_callback(self, msg):
        """Handle user input"""
        try:
            # Parse speech recognition result
            input_data = json.loads(msg.data)
            user_input = input_data['text']
            
            rospy.loginfo(f"Processing user input: {user_input}")
            
            # Get GPT response
            response = self.get_gpt_response(user_input)
            
            # Process and publish response
            speak_part, actions_part = self.process_response(response)
            
            # Update conversation history
            self.conversation_history.append({
                "user": user_input,
                "assistant": response
            })
            
            # Publish complete response for logging
            response_msg = String()
            response_msg.data = json.dumps({
                "speak": speak_part,
                "actions": actions_part,
                "timestamp": rospy.Time.now().to_sec()
            })
            self.response_pub.publish(response_msg)
            
        except json.JSONDecodeError as e:
            rospy.logerr(f"Error parsing user input: {str(e)}")
        except Exception as e:
            rospy.logerr(f"Error in user input callback: {str(e)}")

def main():
    try:
        node = GPTResponseNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    except Exception as e:
        rospy.logerr(f"GPT response node error: {str(e)}")

if __name__ == '__main__':
    main()