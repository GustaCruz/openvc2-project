#########################################################################
#                      UCHL - Senior Project                            #
#                                                                       #
#   Team: I forgor [Skull emoji]                                        #
#                                                                       #
#   Memebers: Gustavo, Nicole, Drew, Dego, Ricardo                      #
#                                                                       #
#   Goal: Using CV2 to work on object detection and preform tasks       #
#                                                                       #
#   Notes: USE ANACONDA NAVIGATOR AS IT WORKS BEST WITH CV2             #
#   Link: https://www.anaconda.com/download launch and click VScode     #
#                                                                       #
#########################################################################
'''
USE PIP TO INSTALL THE FOLLOWING (ONE AT A TIME PLS):

pip install opencv-contrib-python
pip install cvlib # for object detection
pip install tensorflow --user
pip3 install PyObjC

'''

#Imports and Libs
import cv2, time, cvlib as cv # if you get "error: (-215:Assertion failed)" delete your cvlib folder
from threading import Thread  # in C:\Users\[USER]\.cvlib
from cvlib.object_detection import draw_bbox 

#Camera Selector
class ThreadedCamera(object):
    def __init__(self, src=0): # The SRC value is the camera selection usually 0-3
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        
        # FPS = 1/X
        # X = desired FPS, higher FPS results in jittery boxes
        self.FPS = 1/35 # 30-35 fps seems reasonable
        self.FPS_MS = int(self.FPS * 1000)
        
        # Start frame retrieval thread, at the cost of detection confidence
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
        
    def update(self): #ensures camera updates so no frame drops
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
            time.sleep(self.FPS)
    
    
    def detect_and_show_objects(self):
        if hasattr(self, 'frame'):
            
            # Increase sensitivity of detection by confidence %        vvvvvvvvvv     object trainer vvv  makes my pc go vroom
            bbox, label, conf = cv.detect_common_objects(self.frame, confidence=0.35, model='yolov4-tiny')
            
            # Filter only 'bottle' objects for testing purposes because they are "plentiful on my desk"
            bottle_indices = [i for i, lbl in enumerate(label) if lbl == 'bottle']
            filtered_bbox = [bbox[i] for i in bottle_indices]
            filtered_label = [label[i] for i in bottle_indices]
            filtered_conf = [conf[i] for i in bottle_indices]
            
            # Draw bounding boxes and crosshair, considering adding distance measurements but then we got to teach this thing how to count, no thanks.
            output_image, num_bottles = self.draw_bboxes_with_crosshair(self.frame, filtered_bbox, filtered_label, filtered_conf)
            
            # Add text overlay for the number of bottles displayed on the screen (planned on adding 99 bottles of beer joke :D )
            detect_text = f'# of bottles: {num_bottles}'
            #                                       x    y                            size    color  
            cv2.putText(output_image, detect_text, (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

            accHD_text = f'Acceleration Data:'
            cv2.putText(output_image, accHD_text, (10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)
            
            accx_text = f'X: [x value]'
            cv2.putText(output_image, accx_text, (10, 80), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            
            accy_text = f'Y: [y value]'
            cv2.putText(output_image, accy_text, (10, 100), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            
            accz_text = f'Z: [z value]'
            cv2.putText(output_image, accz_text, (10, 120), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            
            floor_text = f'Distance from Floor: [#]in'
            cv2.putText(output_image, floor_text, (10, 160), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

            
            cv2.imshow('frame', output_image)
            cv2.waitKey(self.FPS_MS)
    
    
    def draw_bboxes_with_crosshair(self, frame, bbox, label, conf):
        num_bottles = len(bbox)
        for box, lbl in zip(bbox, label):
            
            # Converting label to string
            lbl_str = str(lbl)
            
            # Calculate center coordinates of the box so the cross hair is accurate, also is nice little hack
            x_center = int((box[0] + box[2]) / 2)
            y_center = int((box[1] + box[3]) / 2)
            
            # Draw bounding box
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            
            # Draw label on top of the bounding box AS A STRING!!!! can modify this to look fancy!
            cv2.putText(frame, lbl_str, (box[0], box[1] - 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
            
            # Drawing crosshair at the center of the box from the lib 
            cv2.drawMarker(frame, (x_center, y_center), (0, 0, 255), cv2.MARKER_CROSS, 10, 2)
        
        return frame, num_bottles # this thing counts bottles yay


# Example usage
if __name__ == "__main__":
    threaded_camera = ThreadedCamera(src=0)
    while True:
        threaded_camera.detect_and_show_objects()
        if cv2.waitKey(1) & 0xFF == ord('q'): # this broke but i plan on doing something else down the line
                                              # dont touch it, it brings me joy :v
            break
