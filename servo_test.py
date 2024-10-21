import tkinter as tk
from tkinter import ttk
from servo_driver import ServoDriver

class ServoTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Servo Motor Test GUI")
        
        # Initialize the servo driver
        self.servo_driver = ServoDriver()
        
        # Create frames for the different parts of the body
        self.create_controls("Right Arm", "right_arm", 0, 0)
        self.create_controls("Left Arm", "left_arm", 0, 1)
        self.create_controls("Neck Down", "neck_down", 1, 0)
        self.create_controls("Neck Up", "neck_up", 1, 1)
        self.create_controls("Neck Right", "neck_right", 2, 0)
        self.create_controls("Eye Right", "eye_right", 2, 1)
        self.create_controls("Eye Left", "eye_left", 3, 0)
        
        # Add buttons for predefined head movements
        self.add_head_movement_buttons()
    
    def create_controls(self, label, joint, row, col):
        """Create a slider and label for each servo joint."""
        frame = ttk.Frame(self.root)
        frame.grid(row=row, column=col, padx=10, pady=10)

        label_text = tk.Label(frame, text=label)
        label_text.pack()

        # Get the initial angle for the joint
        initial_angle = self.servo_driver.joint_angles.get(joint, 90)
        
        # Create a scale (slider) to adjust the servo angle
        scale = tk.Scale(frame, from_=0, to=180, orient=tk.HORIZONTAL, length=300, 
                         command=lambda val, j=joint: self.update_servo_angle(j, val))
        scale.set(initial_angle)
        scale.pack()

    def update_servo_angle(self, joint, angle):
        """Update the servo angle and move the motor."""
        target_angle = int(float(angle))
        self.servo_driver.set_absolute_servo_angle(joint, target_angle)

    def add_head_movement_buttons(self):
        """Add buttons for head movements."""
        frame = ttk.Frame(self.root)
        frame.grid(row=4, columnspan=2, padx=10, pady=10)

        # Head up button
        btn_head_up = tk.Button(frame, text="Head Up", command=self.servo_driver.head_up)
        btn_head_up.grid(row=0, column=0, padx=5, pady=5)

        # Head down button
        btn_head_down = tk.Button(frame, text="Head Down", command=self.servo_driver.head_down)
        btn_head_down.grid(row=0, column=1, padx=5, pady=5)

        # Head left button
        btn_head_left = tk.Button(frame, text="Head Left", command=self.servo_driver.head_left)
        btn_head_left.grid(row=1, column=0, padx=5, pady=5)

        # Head right button
        btn_head_right = tk.Button(frame, text="Head Right", command=self.servo_driver.head_right)
        btn_head_right.grid(row=1, column=1, padx=5, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServoTestGUI(root)
    root.mainloop()