import board
import neopixel
from PIL import Image, ImageTk
import tkinter as tk
import argparse
import datetime
import cv2
import os

pixels = neopixel.NeoPixel(board.D21, 24) 

class Application:
    def __init__(self, output_path = "./"):
        self.pixels = neopixel.NeoPixel(board.D21, 24)
        self.pixels.fill((150, 150, 150))

        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        self.vs = cv2.VideoCapture(0) # capture video frames, 0 is your default video camera
        self.output_path = output_path  # store output path
        self.current_image = None  # current image from the camera

        self.root = tk.Tk()  # initialize root window
        self.root.title("PyImageSearch PhotoBooth")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        self.r = tk.Scale(self.root, from_=0, to=200, orient=tk.HORIZONTAL)
        self.g = tk.Scale(self.root, from_=0, to=200, orient=tk.HORIZONTAL)
        self.b = tk.Scale(self.root, from_=0, to=200, orient=tk.HORIZONTAL)

        self.r.pack(fill="both", expand=True, padx=2, pady=0, side = tk.LEFT)
        self.g.pack(fill="both", expand=True, padx=2, pady=0, side = tk.LEFT)
        self.b.pack(fill="both", expand=True, padx=2, pady=0, side = tk.LEFT)

        # create a button, that when pressed, will take the current frame and save it to file
        btn = tk.Button(self.root, text="Snapshot!", command=self.take_snapshot)
        btn.pack(fill="both", expand=True, padx=10, pady=10, side = tk.BOTTOM)

        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.video_loop()

    def compress_img(self,imgx):
        frame = cv2.resize(imgx, (0, 0), fx = 0.5, fy = 0.5)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        current_image = Image.fromarray(cv2image)
        return current_image


    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            self.pixels.fill((int(self.r.get()), int(self.g.get()), int(self.b.get())))
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.compress_img(frame))  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        self.root.after(30, self.video_loop)  # call the same function after 30 milliseconds

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        ts = datetime.datetime.now() # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # construct filename
        p = os.path.join(self.output_path, filename)  # construct output path
        d_im = self.current_image.convert('RGB')
        d_im.save(p, "JPEG")  # save image as jpeg file
        print("[INFO] saved {}".format(filename))

    def destructor(self):
        self.pixels.fill((0, 0, 0))
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./",
    help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application(args["output"])
pba.root.mainloop()
