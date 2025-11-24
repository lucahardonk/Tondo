import pygame
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init()

class ImageHandler:
    def __init__(self):
        self.pics = {}

    def loadFromFile(self, filename, id=None):
        if id is None:
            id = filename
        try:
            self.pics[id] = pygame.image.load(filename).convert()
            print(f"Loaded {filename} as {id}")
        except Exception as e:
            print(f"Failed to load {filename}: {e}")

    def render(self, surface, id, position=None, clear=False, size=None):
        if clear:
            surface.fill((0, 0, 0))  # Clear the screen with black color
        pic = self.pics.get(id)
        if pic:
            if position is None:
                position = (surface.get_width() // 2 - pic.get_width() // 2,
                            surface.get_height() // 2 - pic.get_height() // 2)
            if size:
                pic = pygame.transform.smoothscale(pic, size)
            surface.blit(pic, position)

# Get the current display info to set the appropriate full screen resolution
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h

# Set the display mode to full screen
#screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
screen = pygame.display.set_mode((2000, 2000))

handler = ImageHandler()

# Preload all images
for i in range(0, 23):
    handler.loadFromFile(f"/home/quantico/Downloads/Y6LIJwin/frame_{i:02d}_delay-0.09s.gif", str(i))

def face():
    A, B, x, y = 500, 500, 1280, 1280
    running = True
    t_pressed = False
    current_frame = 0
    
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    t_pressed = True
                if event.type == pygame.KEYUP and event.key == pygame.K_t:
                    t_pressed = False
            
            if t_pressed:
                frame_range = range(0, 6)  # Frames for when 'T' is pressed
                handler.render(screen, str(current_frame), (A, B), clear=True, size=(x, y))
                pygame.display.flip()
                time.sleep(0.1)  # Frame delay
            else:
                frame_range = range(12, 22)  # Frames for when 'T' is not pressed
                handler.render(screen, str(current_frame), (A, B), clear=True, size=(x, y))
                pygame.display.flip()
                time.sleep(0.2)  # Frame delay

            
            

            # Increment frame
            current_frame += 1
            if current_frame not in frame_range:
                current_frame = min(frame_range)  # Reset to start of range

    finally:
        pygame.quit()

face()
